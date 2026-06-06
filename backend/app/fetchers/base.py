from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.models import Source


@dataclass
class RawArticle:
    title: str
    summary: str
    url: str
    author: str | None = None
    image_url: str | None = None
    published_at: datetime | None = None
    raw_category: str | None = None
    language: str | None = None


class BaseFetcher(Protocol):
    async def fetch(self, source: Source) -> list[RawArticle]: ...
