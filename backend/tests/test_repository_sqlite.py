from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.composition.container import AppContainer, set_container
from app.domains.ingest.ingest_domain import ArticleDraft, SourceType
from app.infrastructure.fetchers.registry import DefaultNewsFetcherRegistry
from app.infrastructure.persistence.catalog_repository_impl import SqlAlchemyCatalogRepository
from app.infrastructure.persistence.ingest_repository_impl import (
    SqlAlchemyArticleRepository,
    SqlAlchemySourceRepository,
)
from app.infrastructure.persistence.models import Base
from app.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
    _current_session,
    reset_engine_for_tests,
)
from app.application.ingest.ingest_command import IngestCommands
from app.application.catalog.catalog_query import CatalogQueries
from app.application.ingest.ingest_input import SeedSourcesInput
from app.utils.time_util import now_ms


@pytest.fixture()
def sqlite_uow(tmp_path, monkeypatch):
    reset_engine_for_tests()
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # SQLite does not like native Enum the same way; create tables from metadata
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    class TestUoW(SqlAlchemyUnitOfWork):
        def __enter__(self):
            self.session = SessionLocal()
            self._token = _current_session.set(self.session)
            self._committed = False
            return self

    def factory():
        return TestUoW()

    sources = SqlAlchemySourceRepository()
    articles = SqlAlchemyArticleRepository()
    catalog = SqlAlchemyCatalogRepository()
    ingest = IngestCommands(factory, sources, articles, DefaultNewsFetcherRegistry())
    queries = CatalogQueries(factory, catalog)
    set_container(AppContainer(ingest=ingest, catalog=queries))

    yield factory, sources, articles, queries

    set_container(None)
    reset_engine_for_tests()


def test_seed_and_list_categories(sqlite_uow):
    factory, sources, articles, queries = sqlite_uow
    from pathlib import Path

    seed = Path(__file__).resolve().parents[1] / "app" / "data" / "sources.seed.json"
    result = IngestCommands(
        factory, sources, articles, DefaultNewsFetcherRegistry()
    ).seed_sources(SeedSourcesInput(seed_file=str(seed)))
    assert result.categories_created > 0
    assert result.sources_created > 0

    cats = queries.list_categories()
    assert any(c.slug == "tech" for c in cats.items)


def test_article_repository_insert_and_catalog_read(sqlite_uow):
    factory, sources, articles, queries = sqlite_uow
    with factory() as uow:
        cat_id, _, _ = sources.upsert_category(name="科技", slug="tech", sort_order=1)
        source_id, _, _ = sources.upsert_source(
            name="Test RSS",
            source_type=SourceType.RSS,
            endpoint="https://example.com/rss",
            config={"default_category": "tech"},
            enabled=True,
        )
        articles.add_articles(
            [
                ArticleDraft(
                    title="Hello world article title",
                    summary="summary",
                    url="https://example.com/a",
                    url_hash="abc123",
                    source_id=source_id,
                    category_id=cat_id,
                    author=None,
                    image_url=None,
                    published_at=now_ms(),
                    fetched_at=now_ms(),
                    language="zh",
                )
            ]
        )
        uow.commit()

    from app.application.catalog.catalog_input import ListArticlesInput

    listed = queries.list_articles(ListArticlesInput(page=1, page_size=10))
    assert listed.total == 1
    assert listed.items[0].title.startswith("Hello")
    assert listed.items[0].source.name == "Test RSS"
