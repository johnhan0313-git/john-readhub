from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.api.v1.articles.articles_controller import ArticleBriefResponse, _map_article
from app.application.catalog.catalog_input import TimelineInput
from app.application.catalog.catalog_query import CatalogQueries
from app.composition.catalog_composition import get_catalog_queries

router = APIRouter(prefix="/timeline", tags=["timeline"])


class TimelineGroupResponse(BaseModel):
    date: str
    articles: list[ArticleBriefResponse]


class TimelineResponse(BaseModel):
    groups: list[TimelineGroupResponse]
    total: int


@router.get("", response_model=TimelineResponse)
def get_timeline(
    category: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    queries: CatalogQueries = Depends(get_catalog_queries),
):
    result = queries.get_timeline(TimelineInput(category=category, limit=limit))
    return TimelineResponse(
        groups=[
            TimelineGroupResponse(
                date=g.date,
                articles=[_map_article(a) for a in g.articles],
            )
            for g in result.groups
        ],
        total=result.total,
    )
