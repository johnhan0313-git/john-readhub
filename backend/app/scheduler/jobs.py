from __future__ import annotations

from app.database import SessionLocal
from app.services.ingest import IngestService


async def fetch_all_sources_job() -> None:
    db = SessionLocal()
    try:
        service = IngestService(db)
        logs = await service.fetch_all_enabled()
        success = sum(1 for log in logs if log.status.value == "success")
        failed = len(logs) - success
        total_articles = sum(log.articles_count for log in logs)
        print(f"[fetch] sources={len(logs)} success={success} failed={failed} new_articles={total_articles}")
    finally:
        db.close()


async def fetch_rss_sources_job() -> None:
    from sqlalchemy import select

    from app.models import Source, SourceType

    db = SessionLocal()
    try:
        service = IngestService(db)
        sources = db.scalars(
            select(Source).where(Source.enabled.is_(True), Source.type == SourceType.RSS)
        ).all()
        for source in sources:
            await service.fetch_source(source)
    finally:
        db.close()


async def cleanup_articles_job() -> None:
    db = SessionLocal()
    try:
        deleted = IngestService(db).cleanup_old_articles()
        print(f"[cleanup] deleted_articles={deleted}")
    finally:
        db.close()
