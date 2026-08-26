from __future__ import annotations

import json
import logging
from pathlib import Path

from app.application.ingest.ingest_input import (
    CleanupArticlesInput,
    FetchSourcesInput,
    SeedSourcesInput,
)
from app.application.ingest.ingest_output import (
    CleanupResult,
    FetchLogResult,
    FetchSourcesResult,
    SeedResult,
)
from app.domains.ingest.ingest_domain import (
    RETIRED_SOURCE_NAMES,
    ArticleDraft,
    FetchOutcome,
    FetchStatus,
    SourceType,
    TitleDeduper,
    compute_url_hash,
    is_valid_candidate,
    map_category_slug,
    truncate,
)
from app.domains.ingest.ingest_repository import (
    ArticleRepository,
    NewsFetcherRegistry,
    SourceRepository,
)
from app.application.unit_of_work import UnitOfWorkFactory
from app.utils.time_util import days_ago_ms, dt_to_ms, now_ms

logger = logging.getLogger(__name__)

DEFAULT_SEED = Path(__file__).resolve().parents[2] / "data" / "sources.seed.json"


class IngestCommands:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        sources: SourceRepository,
        articles: ArticleRepository,
        fetchers: NewsFetcherRegistry,
    ) -> None:
        self._uow_factory = uow_factory
        self._sources = sources
        self._articles = articles
        self._fetchers = fetchers

    def seed_sources(self, command: SeedSourcesInput | None = None) -> SeedResult:
        path = Path(command.seed_file) if command and command.seed_file else DEFAULT_SEED
        data = json.loads(path.read_text(encoding="utf-8"))

        with self._uow_factory() as uow:
            categories_created = 0
            categories_updated = 0
            for item in data.get("categories", []):
                _id, created, changed = self._sources.upsert_category(
                    name=item["name"],
                    slug=item["slug"],
                    sort_order=item.get("sort_order", 0),
                )
                if created:
                    categories_created += 1
                elif changed:
                    categories_updated += 1

            sources_created = 0
            sources_updated = 0
            for item in data.get("sources", []):
                _id, created, changed = self._sources.upsert_source(
                    name=item["name"],
                    source_type=SourceType(item["type"]),
                    endpoint=item["endpoint"],
                    config=item.get("config", {}),
                    enabled=item.get("enabled", True),
                )
                if created:
                    sources_created += 1
                elif changed:
                    sources_updated += 1

            retired = self._sources.retire_named(RETIRED_SOURCE_NAMES)
            uow.commit()

        return SeedResult(
            categories_created=categories_created,
            categories_updated=categories_updated,
            sources_created=sources_created,
            sources_updated=sources_updated,
            sources_retired=retired,
        )

    async def fetch_sources(self, command: FetchSourcesInput) -> FetchSourcesResult:
        with self._uow_factory() as uow:
            if command.exclude_scrapers and command.source_type is None:
                sources = [
                    s
                    for s in self._sources.list_enabled(None)
                    if s.type != SourceType.SCRAPER
                ]
            else:
                sources = self._sources.list_enabled(command.source_type)

        logs: list[FetchLogResult] = []
        for source in sources:
            logs.append(await self._fetch_one(source.id))
        return FetchSourcesResult(logs=logs)

    async def _fetch_one(self, source_id: int) -> FetchLogResult:
        with self._uow_factory() as uow:
            source = self._sources.get(source_id)
            if source is None or not source.enabled:
                raise ValueError(f"Source {source_id} not found or disabled")

        try:
            fetcher = self._fetchers.resolve(source)
            raw_articles = await fetcher.fetch(source)
        except Exception as exc:
            logger.exception("fetch failed source_id=%s", source_id)
            return self._record_failure(source_id, str(exc)[:2000])

        with self._uow_factory() as uow:
            source = self._sources.get(source_id)
            assert source is not None

            recent = self._articles.recent_titles(days_ago_ms(7), limit=500)
            deduper = TitleDeduper(titles=list(recent))
            batch_hashes: set[str] = set()
            drafts: list[ArticleDraft] = []
            config = source.config or {}
            default_category = config.get("default_category")
            fetched_at = now_ms()

            candidates: list[tuple[str, object]] = []
            hashes: set[str] = set()
            for raw in raw_articles:
                if not is_valid_candidate(raw.title, raw.url):
                    continue
                hash_value = compute_url_hash(raw.url)
                if hash_value in batch_hashes:
                    continue
                batch_hashes.add(hash_value)
                hashes.add(hash_value)
                candidates.append((hash_value, raw))

            existing = self._articles.existing_url_hashes(hashes) if hashes else set()

            for hash_value, raw in candidates:
                if hash_value in existing:
                    continue
                if deduper.is_duplicate(raw.title):
                    continue
                deduper.remember(raw.title)

                slug = map_category_slug(raw.raw_category, default_category)
                category_id = None
                if slug:
                    category_id = self._articles.category_id_by_slug(slug)
                    if category_id is None:
                        category_id = self._articles.category_id_by_slug("general")

                language = raw.language or config.get("language")
                drafts.append(
                    ArticleDraft(
                        title=truncate(raw.title, 500) or "",
                        summary=truncate(raw.summary, 5000) if raw.summary else None,
                        url=truncate(raw.url, 2000) or raw.url,
                        url_hash=hash_value,
                        source_id=source.id,
                        category_id=category_id,
                        author=truncate(raw.author, 200),
                        image_url=truncate(raw.image_url, 2000),
                        published_at=dt_to_ms(raw.published_at),
                        fetched_at=fetched_at,
                        language=language,
                    )
                )

            inserted = self._articles.add_articles(drafts)
            self._sources.mark_fetched(source.id, fetched_at)
            outcome = FetchOutcome(
                source_id=source.id,
                status=FetchStatus.SUCCESS,
                articles_count=inserted,
            )
            log_id = self._sources.add_fetch_log(outcome, fetched_at)
            uow.commit()

        return FetchLogResult(
            id=log_id,
            source_id=source_id,
            status=FetchStatus.SUCCESS,
            articles_count=inserted,
            error_message=None,
            created_at=fetched_at,
        )

    def _record_failure(self, source_id: int, error: str) -> FetchLogResult:
        with self._uow_factory() as uow:
            fetched_at = now_ms()
            self._sources.mark_fetched(source_id, fetched_at)
            outcome = FetchOutcome(
                source_id=source_id,
                status=FetchStatus.FAILED,
                articles_count=0,
                error_message=error,
            )
            log_id = self._sources.add_fetch_log(outcome, fetched_at)
            uow.commit()
        return FetchLogResult(
            id=log_id,
            source_id=source_id,
            status=FetchStatus.FAILED,
            articles_count=0,
            error_message=error,
            created_at=fetched_at,
        )

    def cleanup_old_articles(self, command: CleanupArticlesInput) -> CleanupResult:
        with self._uow_factory() as uow:
            deleted = self._articles.delete_older_than(days_ago_ms(command.retention_days))
            uow.commit()
        return CleanupResult(deleted=deleted)
