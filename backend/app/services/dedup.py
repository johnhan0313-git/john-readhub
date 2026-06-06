from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Article


STRIP_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
}


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    query = parse_qs(parsed.query, keep_blank_values=False)
    filtered = {k: v for k, v in query.items() if k.lower() not in STRIP_PARAMS}
    normalized_query = urlencode(filtered, doseq=True)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme, parsed.netloc.lower(), path, "", normalized_query, ""))


def url_hash(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode()).hexdigest()


def is_duplicate_title(db: Session, title: str, threshold: int = 90) -> bool:
    since = datetime.now(timezone.utc) - timedelta(days=7)
    recent = db.scalars(
        select(Article.title).where(Article.published_at >= since).limit(500)
    ).all()
    for existing in recent:
        if fuzz.token_sort_ratio(title, existing) >= threshold:
            return True
    return False
