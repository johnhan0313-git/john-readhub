from __future__ import annotations

import asyncio

from app.infrastructure.fetchers.base import RawArticle
from app.infrastructure.fetchers.scrapers.base import build_job_article
from app.infrastructure.fetchers.scrapers.playwright_util import with_page
from app.domains.ingest.ingest_domain import SourceRecord as Source

LIEPIN_SEARCH_URL = "https://www.liepin.com/zhaopin/?key={keyword}&curPage=0"


class LiepinFetcher:
    """猎聘：Playwright 打开搜索页并拦截官方 JSON API（无需 Cookie）。"""

    async def fetch(self, source: Source) -> list[RawArticle]:
        config = source.config or {}
        keywords: list[str] = config.get("keywords") or ["Python", "Java", "前端"]
        max_per_kw: int = int(config.get("max_jobs_per_keyword", 20))
        articles: list[RawArticle] = []

        for keyword in keywords:
            payload = await self._capture_search_payload(keyword)
            if payload:
                articles.extend(self._parse_payload(payload, keyword))
            await asyncio.sleep(1)

        if not articles:
            raise RuntimeError("猎聘采集失败：未获取到职位列表")
        return articles[: max_per_kw * len(keywords)]

    async def _capture_search_payload(self, keyword: str) -> dict | None:
        captured: dict | None = None

        async def run(page):
            nonlocal captured

            async def on_response(resp):
                nonlocal captured
                if (
                    "pc-search-job" in resp.url
                    and "cond-init" not in resp.url
                    and resp.request.method == "POST"
                    and resp.status == 200
                ):
                    try:
                        captured = await resp.json()
                    except Exception:
                        pass

            page.on("response", on_response)
            await page.goto(
                LIEPIN_SEARCH_URL.format(keyword=keyword),
                wait_until="networkidle",
                timeout=60000,
            )
            await page.wait_for_timeout(3000)

        await with_page(run)
        return captured

    def _parse_payload(self, data: dict, keyword: str) -> list[RawArticle]:
        cards = (data.get("data") or {}).get("data", {}).get("jobCardList") or []
        articles: list[RawArticle] = []
        for card in cards:
            job = card.get("job") or {}
            comp = card.get("comp") or {}
            title = job.get("title")
            link = job.get("link")
            if not title or not link:
                continue
            if not link.startswith("http"):
                link = f"https://www.liepin.com{link}"
            articles.append(
                build_job_article(
                    title=title,
                    company=comp.get("compName") or "",
                    salary=job.get("salary") or "",
                    location=job.get("dq") or "",
                    url=link,
                    source_label="猎聘",
                    extra=f"关键词：{keyword}",
                )
            )
        return articles
