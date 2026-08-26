from __future__ import annotations

from dataclasses import dataclass

from app.domains.ingest.ingest_domain import FetchStatus


@dataclass(frozen=True)
class SeedResult:
    categories_created: int
    categories_updated: int
    sources_created: int
    sources_updated: int
    sources_retired: int


@dataclass(frozen=True)
class FetchLogResult:
    id: int
    source_id: int
    status: FetchStatus
    articles_count: int
    error_message: str | None
    created_at: int


@dataclass(frozen=True)
class FetchSourcesResult:
    logs: list[FetchLogResult]


@dataclass(frozen=True)
class CleanupResult:
    deleted: int
