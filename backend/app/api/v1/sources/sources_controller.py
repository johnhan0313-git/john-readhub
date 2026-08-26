from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.application.catalog.catalog_input import FetchLogsInput
from app.application.catalog.catalog_query import CatalogQueries
from app.composition.catalog_composition import get_catalog_queries

router = APIRouter(prefix="/sources", tags=["sources"])


class SourceResponse(BaseModel):
    id: int
    name: str
    type: str
    endpoint: str
    enabled: bool
    last_fetched_at: int | None


class FetchLogResponse(BaseModel):
    id: int
    source_id: int
    status: str
    articles_count: int
    error_message: str | None
    created_at: int


@router.get("", response_model=list[SourceResponse])
def list_sources(queries: CatalogQueries = Depends(get_catalog_queries)):
    result = queries.list_sources()
    return [
        SourceResponse(
            id=s.id,
            name=s.name,
            type=s.type,
            endpoint=s.endpoint,
            enabled=s.enabled,
            last_fetched_at=s.last_fetched_at,
        )
        for s in result.items
    ]


@router.get("/logs", response_model=list[FetchLogResponse])
def list_fetch_logs(
    limit: int = 50,
    queries: CatalogQueries = Depends(get_catalog_queries),
):
    result = queries.list_fetch_logs(FetchLogsInput(limit=limit))
    return [
        FetchLogResponse(
            id=log.id,
            source_id=log.source_id,
            status=log.status,
            articles_count=log.articles_count,
            error_message=log.error_message,
            created_at=log.created_at,
        )
        for log in result.items
    ]
