from app.fetchers.scrapers.boss import BossZhipinFetcher
from app.fetchers.scrapers.liepin import LiepinFetcher
from app.fetchers.scrapers.maimai import MaimaiFetcher

_boss = BossZhipinFetcher()
_maimai = MaimaiFetcher()
_liepin = LiepinFetcher()

SCRAPER_FETCHERS = {
    "boss": _boss,
    "maimai": _maimai,
    "liepin": _liepin,
}


def get_scraper(provider: str):
    fetcher = SCRAPER_FETCHERS.get(provider)
    if not fetcher:
        raise ValueError(f"Unknown scraper provider: {provider}")
    return fetcher
