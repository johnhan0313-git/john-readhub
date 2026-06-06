from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, articles, categories, events, sources, timeline
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.fetchers.scrapers.playwright_util import close_browser
from app.scheduler.jobs import (
    cleanup_articles_job,
    fetch_all_sources_job,
    fetch_rss_sources_job,
    fetch_scraper_sources_job,
)
from app.services.seed import seed_database

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    init_db()

    db = SessionLocal()
    try:
        result = seed_database(db)
        print(
            f"[seed] categories={result['categories']} "
            f"updated={result.get('categories_updated', 0)} "
            f"sources={result['sources']} "
            f"sources_updated={result.get('sources_updated', 0)}"
        )
    finally:
        db.close()

    if not settings.newsapi_key:
        print("[WARN] NEWSAPI_KEY 未配置，NewsAPI 来源将采集失败。")
    if not settings.gnews_api_key:
        print("[WARN] GNEWS_API_KEY 未配置，GNews 来源将采集失败。")
    if not settings.llm_config().is_configured:
        print("[WARN] AI_LLM_API_KEY 未配置，事件聚类功能将跳过。")
    if not settings.scraper_boss_cookie:
        print("[WARN] SCRAPER_BOSS_COOKIE 未配置，BOSS直聘爬虫将依赖 Playwright 且可能失败。")
    if not settings.scraper_lagou_cookie:
        print("[WARN] SCRAPER_LAGOU_COOKIE 未配置，拉勾爬虫将依赖 Playwright 且可能失败。")
    if not settings.scraper_maimai_cookie:
        print("[WARN] SCRAPER_MAIMAI_COOKIE 未配置，脉脉招聘爬虫可能无法获取职位。")

    scheduler.add_job(
        fetch_all_sources_job,
        "interval",
        minutes=settings.fetch_interval_minutes,
        id="fetch_all",
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
        asyncio.create_task(fetch_all_sources_job())

    yield
    scheduler.shutdown()
    await close_browser()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(articles.router, prefix="/api")
    app.include_router(categories.router, prefix="/api")
    app.include_router(timeline.router, prefix="/api")
    app.include_router(sources.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")
    app.include_router(events.router, prefix="/api")
    return app


app = create_app()
