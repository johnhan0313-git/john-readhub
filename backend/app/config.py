from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = _BACKEND_DIR / ".env"


@dataclass(frozen=True)
class LLMConfig:
    base_url: str
    api_key: str
    model: str

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key.strip())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ReadHub"
    debug: bool = False
    database_url: str = "sqlite:///./data/readhub.db"
    cors_origins: str = "http://localhost:3001,http://127.0.0.1:3001"

    newsapi_key: str = ""
    gnews_api_key: str = ""

    fetch_interval_minutes: int = 30
    rss_fetch_interval_minutes: int = 15
    article_retention_days: int = 90
    run_fetch_on_startup: bool = True

    scraper_fetch_interval_minutes: int = 120
    scraper_boss_cookie: str = ""
    scraper_lagou_cookie: str = ""
    scraper_maimai_cookie: str = ""

    ai_llm_base_url: str = "https://api.openai.com/v1"
    ai_llm_api_key: str = ""
    ai_llm_model: str = "gpt-4o-mini"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def llm_config(self) -> LLMConfig:
        return LLMConfig(
            base_url=self.ai_llm_base_url.rstrip("/"),
            api_key=self.ai_llm_api_key,
            model=self.ai_llm_model,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
