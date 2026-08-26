from __future__ import annotations

from app.domains.ingest.ingest_domain import RawArticle, SourceRecord, SourceType
from app.domains.ingest.ingest_repository import NewsFetcher, NewsFetcherRegistry
from app.infrastructure.fetchers.gnews import GNewsFetcher
from app.infrastructure.fetchers.newsapi import NewsAPIFetcher
from app.infrastructure.fetchers.rss import RSSFetcher
from app.infrastructure.fetchers.scrapers import get_scraper


class DefaultNewsFetcherRegistry:
    def __init__(self) -> None:
        self._rss = RSSFetcher()
        self._newsapi = NewsAPIFetcher()
        self._gnews = GNewsFetcher()

    def resolve(self, source: SourceRecord) -> NewsFetcher:
        if source.type == SourceType.RSS:
            return self._rss
        if source.type == SourceType.SCRAPER:
            provider = (source.config or {}).get("provider", source.endpoint)
            return get_scraper(provider)
        provider = (source.config or {}).get("provider", source.endpoint)
        if provider == "newsapi":
            return self._newsapi
        if provider == "gnews":
            return self._gnews
        raise ValueError(f"Unknown API provider: {provider}")


# Re-export RawArticle for adapters that still import from base
__all__ = ["DefaultNewsFetcherRegistry", "RawArticle", "SourceRecord"]
