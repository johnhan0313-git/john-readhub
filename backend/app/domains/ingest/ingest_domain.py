from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from rapidfuzz import fuzz

MIN_TITLE_LENGTH = 8
TITLE_DEDUP_THRESHOLD = 90

STRIP_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
}

CATEGORY_MAP: dict[str, str] = {
    "technology": "tech",
    "tech": "tech",
    "science": "tech",
    "business": "finance",
    "finance": "finance",
    "economy": "finance",
    "fortune": "finance",
    "world": "world",
    "international": "world",
    "general": "general",
    "nation": "china",
    "china": "china",
    "domestic": "china",
    "politics": "china",
    "sports": "sports",
    "sport": "sports",
    "entertainment": "entertainment",
    "arts": "entertainment",
    "health": "health",
    "medical": "health",
    "auto": "auto",
    "automotive": "auto",
    "cars": "auto",
    "education": "education",
    "edu": "education",
    "parenting": "parenting",
    "family": "parenting",
    "life": "parenting",
    "food": "food",
    "career": "career",
    "employment": "career",
    "recruitment": "recruitment",
    "jobs": "recruitment",
    "hiring": "recruitment",
    "it": "it",
    "programming": "it",
    "developer": "it",
    "devops": "it",
    "software": "it",
}

RETIRED_SOURCE_NAMES = frozenset({"拉勾"})


class SourceType(str, Enum):
    RSS = "rss"
    API = "api"
    SCRAPER = "scraper"


class FetchStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True)
class SourceRecord:
    id: int
    name: str
    type: SourceType
    endpoint: str
    config: dict
    enabled: bool
    last_fetched_at: int | None = None


@dataclass(frozen=True)
class RawArticle:
    title: str
    summary: str
    url: str
    author: str | None = None
    image_url: str | None = None
    published_at: datetime | None = None
    raw_category: str | None = None
    language: str | None = None


@dataclass(frozen=True)
class ArticleDraft:
    title: str
    summary: str | None
    url: str
    url_hash: str
    source_id: int
    category_id: int | None
    author: str | None
    image_url: str | None
    published_at: int | None
    fetched_at: int
    language: str | None


@dataclass(frozen=True)
class FetchOutcome:
    source_id: int
    status: FetchStatus
    articles_count: int
    error_message: str | None = None


@dataclass
class TitleDeduper:
    """In-memory fuzzy title dedup against a preloaded sample."""

    titles: list[str] = field(default_factory=list)
    threshold: int = TITLE_DEDUP_THRESHOLD

    def is_duplicate(self, title: str) -> bool:
        for existing in self.titles:
            if fuzz.token_sort_ratio(title, existing) >= self.threshold:
                return True
        return False

    def remember(self, title: str) -> None:
        self.titles.append(title)


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    query = parse_qs(parsed.query, keep_blank_values=False)
    filtered = {k: v for k, v in query.items() if k.lower() not in STRIP_PARAMS}
    normalized_query = urlencode(filtered, doseq=True)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme, parsed.netloc.lower(), path, "", normalized_query, ""))


def compute_url_hash(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode()).hexdigest()


def is_valid_candidate(title: str | None, url: str | None) -> bool:
    if not title or not url:
        return False
    return len(title.strip()) >= MIN_TITLE_LENGTH


def map_category_slug(raw_category: str | None, default_slug: str | None) -> str | None:
    slug = None
    if raw_category:
        slug = CATEGORY_MAP.get(raw_category.lower(), raw_category.lower())
    if not slug and default_slug:
        slug = default_slug
    return slug


def truncate(value: str | None, max_len: int) -> str | None:
    if value is None:
        return None
    return value[:max_len]
