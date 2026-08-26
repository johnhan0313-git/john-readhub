from __future__ import annotations

from typing import Protocol

from app.domains.catalog.catalog_domain import (
    ArticleRead,
    CategoryWithCount,
    FetchLogRead,
    SourceRead,
)


class CatalogRepository(Protocol):
    def list_articles(
        self,
        *,
        page: int,
        page_size: int,
        category_slug: str | None = None,
        source_id: int | None = None,
        q: str | None = None,
        from_ms: int | None = None,
        to_ms: int | None = None,
    ) -> tuple[list[ArticleRead], int]: ...

    def get_article(self, article_id: int) -> ArticleRead | None: ...

    def list_categories_with_counts(self) -> list[CategoryWithCount]: ...

    def list_timeline(
        self,
        *,
        category_slug: str | None = None,
        limit: int = 100,
    ) -> list[ArticleRead]: ...

    def list_sources(self) -> list[SourceRead]: ...

    def list_fetch_logs(self, *, limit: int = 50) -> list[FetchLogRead]: ...
