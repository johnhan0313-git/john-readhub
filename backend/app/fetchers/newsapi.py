from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.config import get_settings
from app.fetchers.base import RawArticle
from app.models import Source


class NewsAPIFetcher:
    BASE_URL = "https://newsapi.org/v2/top-headlines"

    async def fetch(self, source: Source) -> list[RawArticle]:
        settings = get_settings()
        if not settings.newsapi_key:
            raise ValueError("NEWSAPI_KEY is not configured")

        config = source.config or {}
        params: dict[str, str] = {
            "apiKey": settings.newsapi_key,
            "pageSize": "50",
        }
        if config.get("category"):
            params["category"] = config["category"]
        if config.get("country"):
            params["country"] = config["country"]
        if config.get("q"):
            params["q"] = config["q"]

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "ok":
            raise ValueError(data.get("message", "NewsAPI request failed"))

        articles: list[RawArticle] = []
        for item in data.get("articles", []):
            url = item.get("url")
            title = item.get("title")
            if not url or not title or title == "[Removed]":
                continue

            published_at = None
            if item.get("publishedAt"):
                published_at = datetime.fromisoformat(
                    item["publishedAt"].replace("Z", "+00:00")
                ).astimezone(timezone.utc)

            articles.append(
                RawArticle(
                    title=title.strip(),
                    summary=(item.get("description") or "").strip(),
                    url=url.strip(),
                    author=item.get("author"),
                    image_url=item.get("urlToImage"),
                    published_at=published_at,
                    raw_category=config.get("category"),
                    language=None,
                )
            )
        return articles
