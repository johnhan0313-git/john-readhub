from __future__ import annotations

from dataclasses import dataclass

from app.application.catalog.catalog_query import CatalogQueries
from app.application.ingest.ingest_command import IngestCommands
from app.infrastructure.fetchers.registry import DefaultNewsFetcherRegistry
from app.infrastructure.persistence.catalog_repository_impl import SqlAlchemyCatalogRepository
from app.infrastructure.persistence.ingest_repository_impl import (
    SqlAlchemyArticleRepository,
    SqlAlchemySourceRepository,
)
from app.infrastructure.persistence.unit_of_work import make_uow_factory


@dataclass(frozen=True)
class AppContainer:
    ingest: IngestCommands
    catalog: CatalogQueries


_container: AppContainer | None = None


def build_container() -> AppContainer:
    uow_factory = make_uow_factory()
    sources = SqlAlchemySourceRepository()
    articles = SqlAlchemyArticleRepository()
    catalog_repo = SqlAlchemyCatalogRepository()
    fetchers = DefaultNewsFetcherRegistry()
    ingest = IngestCommands(uow_factory, sources, articles, fetchers)
    catalog = CatalogQueries(uow_factory, catalog_repo)
    return AppContainer(ingest=ingest, catalog=catalog)


def get_container() -> AppContainer:
    global _container
    if _container is None:
        _container = build_container()
    return _container


def set_container(container: AppContainer | None) -> None:
    global _container
    _container = container
