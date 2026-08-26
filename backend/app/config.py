from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "news"
    debug: bool = False
    testing: bool = False
    database_url: str = "postgresql+psycopg://readhub:readhub-123@localhost:5432/readhub"
    use_migrations: bool = True
    cors_origins: str = "http://localhost:3001,http://127.0.0.1:3001"
    admin_token: str = ""

    newsapi_key: str = ""
    gnews_api_key: str = ""

    fetch_interval_minutes: int = 30
    rss_fetch_interval_minutes: int = 15
    article_retention_days: int = 90
    run_fetch_on_startup: bool = True

    scraper_fetch_interval_minutes: int = 120
    scraper_boss_cookie: str = ""
    scraper_maimai_cookie: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
