from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.composition.container import build_container, set_container
from app.config import get_settings
from app.infrastructure.fetchers.scrapers.playwright_util import close_browser
from app.infrastructure.persistence.unit_of_work import init_db
from app.scheduler.jobs import (
    cleanup_articles_job,
    fetch_non_scraper_sources_job,
    fetch_rss_sources_job,
    fetch_scraper_sources_job,
)

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    settings = get_settings()
    init_db()
    container = build_container()
    set_container(container)

    result = container.ingest.seed_sources()
    logger.info(
        "seed categories_created=%s categories_updated=%s sources_created=%s "
        "sources_updated=%s sources_retired=%s",
        result.categories_created,
        result.categories_updated,
        result.sources_created,
        result.sources_updated,
        result.sources_retired,
    )

    if not settings.newsapi_key:
        logger.warning("NEWSAPI_KEY not configured; NewsAPI sources will fail")
    if not settings.gnews_api_key:
        logger.warning("GNEWS_API_KEY not configured; GNews sources will fail")
    if not settings.admin_token:
        logger.warning("ADMIN_TOKEN not configured; admin routes will return 503")
    if not settings.scraper_boss_cookie:
        logger.warning("SCRAPER_BOSS_COOKIE not configured")
    if not settings.scraper_maimai_cookie:
        logger.warning("SCRAPER_MAIMAI_COOKIE not configured")

    scheduler.add_job(
        fetch_non_scraper_sources_job,
        "interval",
        minutes=settings.fetch_interval_minutes,
        id="fetch_non_scraper",
    )
    scheduler.add_job(
        fetch_rss_sources_job,
        "interval",
        minutes=settings.rss_fetch_interval_minutes,
        id="fetch_rss",
    )
    scheduler.add_job(
        fetch_scraper_sources_job,
        "interval",
        minutes=settings.scraper_fetch_interval_minutes,
        id="fetch_scrapers",
    )
    scheduler.add_job(
        cleanup_articles_job,
        "cron",
        hour=3,
        minute=0,
        id="cleanup",
    )
    scheduler.start()

    if settings.run_fetch_on_startup:
        asyncio.create_task(fetch_non_scraper_sources_job())

    yield
    scheduler.shutdown()
    await close_browser()
    set_container(None)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_v1_router)
    return app


app = create_app()
