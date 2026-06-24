from __future__ import annotations

from pydantic import BaseModel


class SourceResponse(BaseModel):
    id: int
    name: str
    type: str
    endpoint: str
    enabled: bool
    last_fetched_at: int | None

    model_config = {"from_attributes": True}


class FetchLogResponse(BaseModel):
    id: int
    source_id: int
    status: str
    articles_count: int
    error_message: str | None
    created_at: int

    model_config = {"from_attributes": True}


class FetchTriggerResponse(BaseModel):
    logs: list[FetchLogResponse]
