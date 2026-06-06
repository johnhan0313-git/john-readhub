from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.fetchers import get_fetcher
from app.models import Article, FetchLog, FetchStatus, Source
from app.services.categorize import resolve_category_slug
from app.services.dedup import is_duplicate_title, url_hash


class IngestService:
    def __init__(self, db: Session):
        self.db = db

    async def fetch_source(self, source: Source) -> FetchLog:
        fetcher = get_fetcher(source)
        log = FetchLog(source_id=source.id, status=FetchStatus.SUCCESS, articles_count=0)

        try:
            raw_articles = await fetcher.fetch(source)
            inserted = 0
            config = source.config or {}
            default_category = config.get("default_category")
            batch_hashes: set[str] = set()

            for raw in raw_articles:
                if not raw.title or not raw.url:
                    continue
                if len(raw.title.strip()) < 8:
                    continue

                hash_value = url_hash(raw.url)
                if hash_value in batch_hashes:
                    continue
                exists = self.db.scalar(
                    select(Article.id).where(Article.url_hash == hash_value)
                )
                if exists:
                    continue
                batch_hashes.add(hash_value)

                if is_duplicate_title(self.db, raw.title):
                    continue

                category_id = resolve_category_slug(
                    self.db,
                    raw.raw_category,
                    default_category,
                )
                language = raw.language or config.get("language")

                self.db.add(
                    Article(
                        title=raw.title[:500],
                        summary=raw.summary[:5000] if raw.summary else None,
                        url=raw.url[:2000],
                        url_hash=hash_value,
                        source_id=source.id,
                        category_id=category_id,
                        author=raw.author[:200] if raw.author else None,
                        image_url=raw.image_url[:2000] if raw.image_url else None,
                        published_at=raw.published_at,
                        language=language,
                    )
                )
                inserted += 1

            source.last_fetched_at = datetime.now(timezone.utc)
            log.articles_count = inserted
            self.db.add(log)
            self.db.commit()
            return log
        except Exception as exc:
            self.db.rollback()
            failed_log = FetchLog(
                source_id=source.id,
                status=FetchStatus.FAILED,
                articles_count=0,
                error_message=str(exc)[:2000],
            )
            self.db.add(failed_log)
            db_source = self.db.get(Source, source.id)
            if db_source:
                db_source.last_fetched_at = datetime.now(timezone.utc)
            self.db.commit()
            return failed_log

    async def fetch_all_enabled(self) -> list[FetchLog]:
        sources = self.db.scalars(
            select(Source).where(Source.enabled.is_(True)).order_by(Source.id)
        ).all()
        logs: list[FetchLog] = []
        for source in sources:
            logs.append(await self.fetch_source(source))
        return logs

    def cleanup_old_articles(self) -> int:
        settings = get_settings()
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.article_retention_days)
        result = self.db.execute(delete(Article).where(Article.fetched_at < cutoff))
        self.db.commit()
        return result.rowcount or 0
