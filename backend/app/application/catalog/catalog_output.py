from __future__ import annotations

from dataclasses import dataclass

from app.domains.catalog.catalog_domain import (
    ArticleRead,
    CategoryWithCount,
    FetchLogRead,
    SourceRead,
    TimelineGroup,
)


@dataclass(frozen=True)
class ArticleListResult:
    items: list[ArticleRead]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class TimelineResult:
    groups: list[TimelineGroup]
    total: int


@dataclass(frozen=True)
class CategoryListResult:
    items: list[CategoryWithCount]


@dataclass(frozen=True)
class SourceListResult:
    items: list[SourceRead]


@dataclass(frozen=True)
class FetchLogListResult:
    items: list[FetchLogRead]
