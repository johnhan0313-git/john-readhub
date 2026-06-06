from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Article, Event
from app.schemas.article import ArticleBrief
from app.schemas.event import EventBrief, EventDetail

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventBrief])
def list_events(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Event, func.count(Article.id).label("article_count"))
        .outerjoin(Article, Article.event_id == Event.id)
        .group_by(Event.id)
        .order_by(Event.last_updated_at.desc())
        .limit(limit)
    ).all()

    return [
        EventBrief(
            id=event.id,
            title=event.title,
            summary=event.summary,
            first_seen_at=event.first_seen_at,
            last_updated_at=event.last_updated_at,
            article_count=count,
        )
        for event, count in rows
    ]


@router.get("/{event_id}", response_model=EventDetail)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.scalar(select(Event).where(Event.id == event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    articles = db.scalars(
        select(Article)
        .options(joinedload(Article.source), joinedload(Article.category))
        .where(Article.event_id == event_id)
        .order_by(Article.published_at.asc().nullsfirst())
    ).unique().all()

    return EventDetail(
        id=event.id,
        title=event.title,
        summary=event.summary,
        first_seen_at=event.first_seen_at,
        last_updated_at=event.last_updated_at,
        article_count=len(articles),
        articles=[ArticleBrief.model_validate(a) for a in articles],
    )
