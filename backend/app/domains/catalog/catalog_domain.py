from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CategoryBrief:
    id: int
    name: str
    slug: str


@dataclass(frozen=True)
class SourceBrief:
    id: int
    name: str


@dataclass(frozen=True)
class ArticleRead:
    id: int
    title: str
    summary: str | None
    url: str
    author: str | None
    image_url: str | None
    published_at: int | None
    fetched_at: int
    language: str | None
    source: SourceBrief
    category: CategoryBrief | None


@dataclass(frozen=True)
class CategoryWithCount:
    id: int
    name: str
    slug: str
    sort_order: int
    article_count: int


@dataclass(frozen=True)
class SourceRead:
    id: int
    name: str
    type: str
    endpoint: str
    enabled: bool
    last_fetched_at: int | None


@dataclass(frozen=True)
class FetchLogRead:
    id: int
    source_id: int
    status: str
    articles_count: int
    error_message: str | None
    created_at: int


@dataclass(frozen=True)
class TimelineGroup:
    date: str
    articles: list[ArticleRead]
