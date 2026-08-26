from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.application.ingest.ingest_command import IngestCommands
from app.application.ingest.ingest_input import FetchSourcesInput
from app.composition.ingest_composition import get_ingest_commands
from app.config import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])


class FetchLogResponse(BaseModel):
    id: int
    source_id: int
    status: str
    articles_count: int
    error_message: str | None
    created_at: int


class FetchTriggerResponse(BaseModel):
    logs: list[FetchLogResponse]


def require_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    settings = get_settings()
    expected = (settings.admin_token or "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="Admin token is not configured")
    if not x_admin_token or not secrets.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=401, detail="Invalid admin token")


@router.post("/fetch", response_model=FetchTriggerResponse, dependencies=[Depends(require_admin_token)])
async def trigger_fetch(commands: IngestCommands = Depends(get_ingest_commands)):
    result = await commands.fetch_sources(FetchSourcesInput(exclude_scrapers=True))
    return FetchTriggerResponse(
        logs=[
            FetchLogResponse(
                id=log.id,
                source_id=log.source_id,
                status=log.status.value,
                articles_count=log.articles_count,
                error_message=log.error_message,
                created_at=log.created_at,
            )
            for log in result.logs
        ]
    )
