from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article, Category
from app.schemas.article import CategoryWithCount

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryWithCount])
def list_categories(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Category.id,
            Category.name,
            Category.slug,
            Category.sort_order,
            func.count(Article.id).label("article_count"),
        )
        .outerjoin(Article, Article.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.sort_order, Category.id)
    ).all()

    return [
        CategoryWithCount(
            id=row.id,
            name=row.name,
            slug=row.slug,
            sort_order=row.sort_order,
            article_count=row.article_count,
        )
        for row in rows
    ]
