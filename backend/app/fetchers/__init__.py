from app.fetchers.gnews import GNewsFetcher
from app.fetchers.newsapi import NewsAPIFetcher
from app.fetchers.rss import RSSFetcher
from app.fetchers.scrapers import get_scraper
from app.models import Source, SourceType

_rss = RSSFetcher()
_newsapi = NewsAPIFetcher()
_gnews = GNewsFetcher()


def get_fetcher(source: Source):
    if source.type == SourceType.RSS:
        return _rss

    if source.type == SourceType.SCRAPER:
        provider = (source.config or {}).get("provider", source.endpoint)
        return get_scraper(provider)

    provider = (source.config or {}).get("provider", source.endpoint)
    if provider == "newsapi":
        return _newsapi
    if provider == "gnews":
        return _gnews
    raise ValueError(f"Unknown API provider: {provider}")
