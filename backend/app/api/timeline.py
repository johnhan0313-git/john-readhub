from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Article, Category
from app.schemas.article import ArticleBrief, TimelineGroup, TimelineResponse
from app.utils.time_util import ms_to_date_key

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.get("", response_model=TimelineResponse)
def get_timeline(
    category: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = (
        select(Article)
        .options(joinedload(Article.source), joinedload(Article.category))
        .order_by(Article.published_at.desc().nullslast(), Article.id.desc())
        .limit(limit)
    )

    if category:
        cat = db.scalar(select(Category).where(Category.slug == category))
        if not cat:
            return TimelineResponse(groups=[], total=0)
        query = query.where(Article.category_id == cat.id)

    articles = db.scalars(query).unique().all()
    grouped: dict[str, list[ArticleBrief]] = defaultdict(list)

    for article in articles:
        if article.published_at is not None:
            date_key = ms_to_date_key(article.published_at)
        else:
            date_key = ms_to_date_key(article.fetched_at)
        grouped[date_key].append(ArticleBrief.model_validate(article))

    groups = [
        TimelineGroup(date=date, articles=items)
        for date, items in sorted(grouped.items(), reverse=True)
    ]

    return TimelineResponse(groups=groups, total=len(articles))
