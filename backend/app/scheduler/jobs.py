from __future__ import annotations

import logging

from app.application.ingest.ingest_input import CleanupArticlesInput, FetchSourcesInput
from app.composition.container import get_container
from app.config import get_settings
from app.domains.ingest.ingest_domain import SourceType

logger = logging.getLogger(__name__)


async def fetch_non_scraper_sources_job() -> None:
    result = await get_container().ingest.fetch_sources(
        FetchSourcesInput(exclude_scrapers=True)
    )
    success = sum(1 for log in result.logs if log.status.value == "success")
    failed = len(result.logs) - success
    total_articles = sum(log.articles_count for log in result.logs)
    logger.info(
        "fetch_non_scraper sources=%s success=%s failed=%s new_articles=%s",
        len(result.logs),
        success,
        failed,
        total_articles,
    )


async def fetch_rss_sources_job() -> None:
    result = await get_container().ingest.fetch_sources(
        FetchSourcesInput(source_type=SourceType.RSS)
    )
    logger.info("fetch_rss sources=%s", len(result.logs))


async def fetch_api_sources_job() -> None:
    result = await get_container().ingest.fetch_sources(
        FetchSourcesInput(source_type=SourceType.API)
    )
    logger.info("fetch_api sources=%s", len(result.logs))


async def fetch_scraper_sources_job() -> None:
    result = await get_container().ingest.fetch_sources(
        FetchSourcesInput(source_type=SourceType.SCRAPER)
    )
    logger.info("fetch_scrapers sources=%s", len(result.logs))


def cleanup_articles_job() -> None:
    settings = get_settings()
    result = get_container().ingest.cleanup_old_articles(
        CleanupArticlesInput(retention_days=settings.article_retention_days)
    )
    logger.info("cleanup deleted_articles=%s", result.deleted)
