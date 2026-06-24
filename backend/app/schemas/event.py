from __future__ import annotations

from pydantic import BaseModel

from app.schemas.article import ArticleBrief


class EventBrief(BaseModel):
    id: int
    title: str
    summary: str | None
    first_seen_at: int
    last_updated_at: int
    article_count: int = 0

    model_config = {"from_attributes": True}


class EventDetail(EventBrief):
    articles: list[ArticleBrief]


class EventClusterResponse(BaseModel):
    status: str
    events_created: int | None = None
    articles_linked: int | None = None
    reason: str | None = None
    count: int | None = None
