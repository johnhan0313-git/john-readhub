from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Article, Category, Source
from app.schemas.article import ArticleBrief, ArticleDetail, ArticleListResponse

router = APIRouter(prefix="/articles", tags=["articles"])


def _article_query(db: Session):
    return select(Article).options(
        joinedload(Article.source),
        joinedload(Article.category),
    )


@router.get("", response_model=ArticleListResponse)
def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    source_id: int | None = None,
    q: str | None = None,
    from_date: datetime | None = Query(None, alias="from"),
    to_date: datetime | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    query = _article_query(db)
    count_query = select(func.count(Article.id))

    if category:
        cat = db.scalar(select(Category).where(Category.slug == category))
        if not cat:
            return ArticleListResponse(items=[], total=0, page=page, page_size=page_size)
        query = query.where(Article.category_id == cat.id)
        count_query = count_query.where(Article.category_id == cat.id)

    if source_id:
        query = query.where(Article.source_id == source_id)
        count_query = count_query.where(Article.source_id == source_id)

    if q:
        pattern = f"%{q}%"
        condition = or_(Article.title.ilike(pattern), Article.summary.ilike(pattern))
        query = query.where(condition)
        count_query = count_query.where(condition)

    if from_date:
        query = query.where(Article.published_at >= from_date)
        count_query = count_query.where(Article.published_at >= from_date)

    if to_date:
        query = query.where(Article.published_at <= to_date)
        count_query = count_query.where(Article.published_at <= to_date)

    total = db.scalar(count_query) or 0
    items = db.scalars(
        query.order_by(Article.published_at.desc().nullslast(), Article.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).unique().all()

    return ArticleListResponse(
        items=[ArticleBrief.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.scalar(
        _article_query(db).where(Article.id == article_id)
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleDetail.model_validate(article)
