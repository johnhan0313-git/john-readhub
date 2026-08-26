from __future__ import annotations

from collections import defaultdict

from app.application.catalog.catalog_input import (
    FetchLogsInput,
    GetArticleInput,
    ListArticlesInput,
    TimelineInput,
)
from app.application.catalog.catalog_output import (
    ArticleListResult,
    CategoryListResult,
    FetchLogListResult,
    SourceListResult,
    TimelineResult,
)
from app.domains.catalog.catalog_domain import TimelineGroup
from app.domains.catalog.catalog_repository import CatalogRepository
from app.application.unit_of_work import UnitOfWorkFactory
from app.utils.time_util import ms_to_date_key


class CatalogQueries:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        catalog: CatalogRepository,
    ) -> None:
        self._uow_factory = uow_factory
        self._catalog = catalog

    def list_articles(self, query: ListArticlesInput) -> ArticleListResult:
        with self._uow_factory():
            items, total = self._catalog.list_articles(
                page=query.page,
                page_size=query.page_size,
                category_slug=query.category,
                source_id=query.source_id,
                q=query.q,
                from_ms=query.from_ms,
                to_ms=query.to_ms,
            )
        return ArticleListResult(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
        )

    def get_article(self, query: GetArticleInput):
        with self._uow_factory():
            return self._catalog.get_article(query.article_id)

    def list_categories(self) -> CategoryListResult:
        with self._uow_factory():
            items = self._catalog.list_categories_with_counts()
        return CategoryListResult(items=items)

    def get_timeline(self, query: TimelineInput) -> TimelineResult:
        with self._uow_factory():
            articles = self._catalog.list_timeline(
                category_slug=query.category,
                limit=query.limit,
            )
        grouped: dict[str, list] = defaultdict(list)
        for article in articles:
            ts = article.published_at if article.published_at is not None else article.fetched_at
            grouped[ms_to_date_key(ts)].append(article)
        groups = [
            TimelineGroup(date=date, articles=items)
            for date, items in sorted(grouped.items(), reverse=True)
        ]
        return TimelineResult(groups=groups, total=len(articles))

    def list_sources(self) -> SourceListResult:
        with self._uow_factory():
            items = self._catalog.list_sources()
        return SourceListResult(items=items)

    def list_fetch_logs(self, query: FetchLogsInput) -> FetchLogListResult:
        with self._uow_factory():
            items = self._catalog.list_fetch_logs(limit=query.limit)
        return FetchLogListResult(items=items)
