from __future__ import annotations

import asyncio
import json

import httpx

from app.infrastructure.fetchers.base import RawArticle
from app.infrastructure.fetchers.scrapers.base import build_job_article, cookie_from_config
from app.infrastructure.fetchers.scrapers.playwright_util import with_page
from app.domains.ingest.ingest_domain import SourceRecord as Source

MAIMAI_SEARCH_PAGE = "https://maimai.cn/jobssearch?query={keyword}"
MAIMAI_API_CANDIDATES = [
    "https://maimai.cn/sdk/jobs/search",
    "https://open.maimai.cn/api/jobs/search",
]

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://maimai.cn/",
}


class MaimaiFetcher:
    async def fetch(self, source: Source) -> list[RawArticle]:
        config = source.config or {}
        cookie = cookie_from_config(config)
        keywords: list[str] = config.get("keywords") or ["Python", "Java", "产品经理"]
        max_per_kw: int = int(config.get("max_jobs_per_keyword", 15))

        if cookie:
            articles = await self._fetch_via_api(cookie, keywords, max_per_kw)
            if articles:
                return articles

        articles = await self._fetch_via_playwright(keywords, max_per_kw, cookie)
        if not articles:
            raise RuntimeError(
                "脉脉招聘采集失败：职位列表需登录态。"
                "请在 backend/.env 配置 SCRAPER_MAIMAI_COOKIE（浏览器登录 maimai.cn 后复制 Cookie）后重试。"
            )
        return articles

    async def _fetch_via_api(
        self,
        cookie: str,
        keywords: list[str],
        max_per_kw: int,
    ) -> list[RawArticle]:
        articles: list[RawArticle] = []
        headers = {**DEFAULT_HEADERS, "Cookie": cookie}

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
            for keyword in keywords:
                for api_url in MAIMAI_API_CANDIDATES:
                    response = await client.get(
                        api_url,
                        params={"query": keyword, "count": max_per_kw, "page": 0},
                    )
                    if response.status_code != 200:
                        continue
                    try:
                        data = response.json()
                    except json.JSONDecodeError:
                        continue
                    parsed = self._parse_payload(data, keyword)
                    if parsed:
                        articles.extend(parsed)
                        break
                await asyncio.sleep(1)
        return articles

    async def _fetch_via_playwright(
        self,
        keywords: list[str],
        max_per_kw: int,
        cookie: str | None,
    ) -> list[RawArticle]:
        articles: list[RawArticle] = []

        async def run(page):
            nonlocal articles
            if cookie:
                for part in cookie.split(";"):
                    part = part.strip()
                    if "=" in part:
                        name, value = part.split("=", 1)
                        await page.context.add_cookies(
                            [
                                {
                                    "name": name.strip(),
                                    "value": value.strip(),
                                    "domain": "maimai.cn",
                                    "path": "/",
                                }
                            ]
                        )

            for keyword in keywords:
                captured: list[dict] = []

                async def on_response(resp):
                    if resp.status != 200:
                        return
                    url = resp.url
                    if not any(x in url for x in ("job", "search", "position")):
                        return
                    try:
                        if "json" in (resp.headers.get("content-type") or ""):
                            payload = await resp.json()
                            captured.append(payload)
                    except Exception:
                        pass

                page.on("response", on_response)
                await page.goto(
                    MAIMAI_SEARCH_PAGE.format(keyword=keyword),
                    wait_until="networkidle",
                    timeout=60000,
                )
                await page.wait_for_timeout(4000)

                for payload in captured:
                    articles.extend(self._parse_payload(payload, keyword))

                links = await page.eval_on_selector_all(
                    'a[href*="/jobs/"], a[href*="/job/"]',
                    "els => els.map(e => ({href: e.href, text: e.innerText.trim()}))",
                )
                for link in links[:max_per_kw]:
                    text = (link.get("text") or "").strip()
                    href = link.get("href")
                    if not text or not href or len(text) < 4:
                        continue
                    articles.append(
                        build_job_article(
                            title=text.split("\n")[0][:200],
                            company="",
                            salary="",
                            location="",
                            url=href,
                            source_label="脉脉",
                            extra=f"关键词：{keyword}",
                        )
                    )
                await asyncio.sleep(1)

        await with_page(run)
        return _dedupe_articles(articles)[: max_per_kw * len(keywords)]

    def _parse_payload(self, data: dict | list, keyword: str) -> list[RawArticle]:
        items: list[dict] = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("jobs", "data", "list", "items", "result"):
                val = data.get(key)
                if isinstance(val, list):
                    items = val
                    break
                if isinstance(val, dict):
                    for sub in ("jobs", "list", "items"):
                        if isinstance(val.get(sub), list):
                            items = val[sub]
                            break

        articles: list[RawArticle] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("job_title") or item.get("name")
            url = item.get("url") or item.get("link") or item.get("job_url")
            if not title or not url:
                continue
            if not str(url).startswith("http"):
                url = f"https://maimai.cn{url}"
            articles.append(
                build_job_article(
                    title=str(title),
                    company=str(item.get("company") or item.get("company_name") or ""),
                    salary=str(item.get("salary") or ""),
                    location=str(item.get("city") or item.get("location") or ""),
                    url=str(url),
                    source_label="脉脉",
                    extra=f"关键词：{keyword}",
                )
            )
        return articles


def _dedupe_articles(articles: list[RawArticle]) -> list[RawArticle]:
    seen: set[str] = set()
    unique: list[RawArticle] = []
    for article in articles:
        if article.url in seen:
            continue
        seen.add(article.url)
        unique.append(article)
    return unique
