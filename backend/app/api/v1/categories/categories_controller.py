from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.application.catalog.catalog_query import CatalogQueries
from app.composition.catalog_composition import get_catalog_queries

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryWithCountResponse(BaseModel):
    id: int
    name: str
    slug: str
    sort_order: int
    article_count: int


@router.get("", response_model=list[CategoryWithCountResponse])
def list_categories(queries: CatalogQueries = Depends(get_catalog_queries)):
    result = queries.list_categories()
    return [
        CategoryWithCountResponse(
            id=c.id,
            name=c.name,
            slug=c.slug,
            sort_order=c.sort_order,
            article_count=c.article_count,
        )
        for c in result.items
    ]
