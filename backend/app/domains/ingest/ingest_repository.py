from __future__ import annotations

from typing import Protocol

from app.domains.ingest.ingest_domain import (
    ArticleDraft,
    FetchOutcome,
    RawArticle,
    SourceRecord,
    SourceType,
)


class SourceRepository(Protocol):
    def list_enabled(self, source_type: SourceType | None = None) -> list[SourceRecord]: ...

    def get(self, source_id: int) -> SourceRecord | None: ...

    def upsert_category(
        self, *, name: str, slug: str, sort_order: int
    ) -> tuple[int, bool, bool]:
        """Return (id, created, changed)."""
        ...

    def upsert_source(
        self,
        *,
        name: str,
        source_type: SourceType,
        endpoint: str,
        config: dict,
        enabled: bool,
    ) -> tuple[int, bool, bool]: ...

    def retire_named(self, names: frozenset[str]) -> int: ...

    def mark_fetched(self, source_id: int, fetched_at: int) -> None: ...

    def add_fetch_log(self, outcome: FetchOutcome, created_at: int) -> int: ...


class ArticleRepository(Protocol):
    def url_hash_exists(self, url_hash: str) -> bool: ...

    def existing_url_hashes(self, hashes: set[str]) -> set[str]: ...

    def recent_titles(self, since_ms: int, limit: int = 500) -> list[str]: ...

    def add_articles(self, drafts: list[ArticleDraft]) -> int: ...

    def delete_older_than(self, cutoff_ms: int) -> int: ...

    def category_id_by_slug(self, slug: str) -> int | None: ...


class NewsFetcher(Protocol):
    async def fetch(self, source: SourceRecord) -> list[RawArticle]: ...


class NewsFetcherRegistry(Protocol):
    def resolve(self, source: SourceRecord) -> NewsFetcher: ...
