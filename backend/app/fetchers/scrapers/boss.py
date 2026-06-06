from __future__ import annotations

import asyncio

import httpx

from app.fetchers.base import RawArticle
from app.fetchers.scrapers.base import build_job_article, cookie_from_config
from app.fetchers.scrapers.playwright_util import with_page
from app.models import Source

BOSS_SEARCH_API = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json"
BOSS_JOB_URL = "https://www.zhipin.com/job_detail/{job_id}.html"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.zhipin.com/web/geek/job",
    "X-Requested-With": "XMLHttpRequest",
}


class BossZhipinFetcher:
    async def fetch(self, source: Source) -> list[RawArticle]:
        config = source.config or {}
        cookie = cookie_from_config(config)
        keywords: list[str] = config.get("keywords") or ["Python", "Java", "前端"]
        city: str = config.get("city", "101010100")
        max_per_kw: int = int(config.get("max_jobs_per_keyword", 15))

        if cookie:
            articles = await self._fetch_via_api(cookie, keywords, city, max_per_kw)
            if articles:
                return articles

        articles = await self._fetch_via_playwright(keywords, city, max_per_kw, cookie)
        if not articles:
            raise RuntimeError(
                "BOSS直聘采集失败：触发安全验证。"
                "请在 backend/.env 配置 SCRAPER_BOSS_COOKIE（浏览器登录 zhipin.com 后复制 Cookie）后重试。"
            )
        return articles

    async def _fetch_via_api(
        self,
        cookie: str,
        keywords: list[str],
        city: str,
        max_per_kw: int,
    ) -> list[RawArticle]:
        articles: list[RawArticle] = []
        headers = {**DEFAULT_HEADERS, "Cookie": cookie}

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
            for keyword in keywords:
                response = await client.get(
                    BOSS_SEARCH_API,
                    params={
                        "page": 1,
                        "pageSize": max_per_kw,
                        "city": city,
                        "query": keyword,
                    },
                )
                response.raise_for_status()
                data = response.json()
                if data.get("code") != 0:
                    continue
                articles.extend(self._parse_joblist(data, keyword))
                await asyncio.sleep(1)
        return articles

    async def _fetch_via_playwright(
        self,
        keywords: list[str],
        city: str,
        max_per_kw: int,
        cookie: str | None,
    ) -> list[RawArticle]:
        articles: list[RawArticle] = []

        async def run(page):
            nonlocal articles
            if cookie:
                for item in _cookie_header_to_playwright(cookie, "zhipin.com"):
                    await page.context.add_cookies([item])

            for keyword in keywords:
                captured: dict | None = None

                async def on_response(resp):
                    nonlocal captured
                    if "joblist.json" in resp.url and resp.status == 200:
                        try:
                            payload = await resp.json()
                            if payload.get("code") == 0:
                                captured = payload
                        except Exception:
                            pass

                page.on("response", on_response)
                await page.goto(
                    f"https://www.zhipin.com/web/geek/job?query={keyword}&city={city}",
                    wait_until="networkidle",
                    timeout=60000,
                )
                await page.wait_for_timeout(3000)
                if captured:
                    articles.extend(self._parse_joblist(captured, keyword))
                await asyncio.sleep(1)

        await with_page(run)
        return articles[: max_per_kw * len(keywords)]

    def _parse_joblist(self, data: dict, keyword: str) -> list[RawArticle]:
        job_list = (data.get("zpData") or {}).get("jobList") or []
        articles: list[RawArticle] = []
        for item in job_list:
            job_name = item.get("jobName") or item.get("positionName")
            encrypt_id = item.get("encryptJobId") or item.get("jobId")
            if not job_name or not encrypt_id:
                continue
            articles.append(
                build_job_article(
                    title=job_name,
                    company=item.get("brandName") or item.get("companyName") or "",
                    salary=item.get("salaryDesc") or "",
                    location=item.get("cityName") or item.get("areaDistrict") or "",
                    url=BOSS_JOB_URL.format(job_id=encrypt_id),
                    source_label="BOSS直聘",
                    extra=f"关键词：{keyword}",
                )
            )
        return articles


def _cookie_header_to_playwright(cookie: str, domain: str) -> list[dict]:
    items: list[dict] = []
    for part in cookie.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        name, value = part.split("=", 1)
        items.append(
            {
                "name": name.strip(),
                "value": value.strip(),
                "domain": domain,
                "path": "/",
            }
        )
    return items
