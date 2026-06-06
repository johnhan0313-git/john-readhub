from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event import EventClusterResponse
from app.schemas.source import FetchLogResponse, FetchTriggerResponse
from app.services.event_cluster import EventClusterService
from app.services.ingest import IngestService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/fetch", response_model=FetchTriggerResponse)
async def trigger_fetch(db: Session = Depends(get_db)):
    service = IngestService(db)
    logs = await service.fetch_all_enabled()
    return FetchTriggerResponse(
        logs=[FetchLogResponse.model_validate(log) for log in logs]
    )


@router.post("/cluster-events", response_model=EventClusterResponse)
async def trigger_event_cluster(db: Session = Depends(get_db)):
    result = await EventClusterService(db).cluster_recent()
    return EventClusterResponse(**result)
