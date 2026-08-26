from __future__ import annotations

from dataclasses import dataclass

from app.domains.ingest.ingest_domain import FetchStatus, SourceType


@dataclass(frozen=True)
class SeedSourcesInput:
    seed_file: str | None = None


@dataclass(frozen=True)
class FetchSourcesInput:
    source_type: SourceType | None = None
    exclude_scrapers: bool = False


@dataclass(frozen=True)
class CleanupArticlesInput:
    retention_days: int
