from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
import re

import feedparser
import httpx

from app.fetchers.base import RawArticle
from app.models import Source


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    return unescape(cleaned).strip()


def _parse_published(entry: dict) -> datetime | None:
    if entry.get("published_parsed"):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if entry.get("updated_parsed"):
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    published = entry.get("published") or entry.get("updated")
    if published:
        return parsedate_to_datetime(published).astimezone(timezone.utc)
    return None


def _parse_feed(content: bytes) -> list[RawArticle]:
    parsed = feedparser.parse(content)
    if parsed.bozo and not parsed.entries:
        raise ValueError(parsed.bozo_exception or "Invalid RSS feed")

    articles: list[RawArticle] = []
    for entry in parsed.entries:
        url = entry.get("link")
        title = entry.get("title")
        if not url or not title:
            continue

        summary = (
            entry.get("summary")
            or entry.get("description")
            or entry.get("content", [{}])[0].get("value", "")
        )
        author = entry.get("author")
        image_url = None
        if entry.get("media_thumbnail"):
            image_url = entry.media_thumbnail[0].get("url")
        elif entry.get("media_content"):
            image_url = entry.media_content[0].get("url")

        articles.append(
            RawArticle(
                title=_strip_html(title),
                summary=_strip_html(summary) if summary else "",
                url=url.strip(),
                author=author,
                image_url=image_url,
                published_at=_parse_published(entry),
                language=parsed.feed.get("language"),
            )
        )
    return articles


DEFAULT_HEADERS = {
    "User-Agent": "ReadHub/1.0 (+https://github.com/readhub; news aggregator)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


class RSSFetcher:
    async def fetch(self, source: Source) -> list[RawArticle]:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(source.endpoint, headers=DEFAULT_HEADERS)
            response.raise_for_status()
            return await asyncio.to_thread(_parse_feed, response.content)
