from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FetchLog, Source
from app.schemas.source import FetchLogResponse, SourceResponse

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    sources = db.scalars(select(Source).order_by(Source.id)).all()
    return [SourceResponse.model_validate(s) for s in sources]


@router.get("/logs", response_model=list[FetchLogResponse])
def list_fetch_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.scalars(
        select(FetchLog).order_by(FetchLog.created_at.desc()).limit(limit)
    ).all()
    return [FetchLogResponse.model_validate(log) for log in logs]
