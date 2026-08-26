from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ListArticlesInput:
    page: int = 1
    page_size: int = 20
    category: str | None = None
    source_id: int | None = None
    q: str | None = None
    from_ms: int | None = None
    to_ms: int | None = None


@dataclass(frozen=True)
class GetArticleInput:
    article_id: int


@dataclass(frozen=True)
class TimelineInput:
    category: str | None = None
    limit: int = 100


@dataclass(frozen=True)
class FetchLogsInput:
    limit: int = 50
