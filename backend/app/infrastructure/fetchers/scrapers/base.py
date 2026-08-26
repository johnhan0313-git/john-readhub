from __future__ import annotations

import os
from datetime import datetime, timezone

from app.config import get_settings
from app.infrastructure.fetchers.base import RawArticle

_SETTING_COOKIE_KEYS = {
    "SCRAPER_BOSS_COOKIE": "scraper_boss_cookie",
    "SCRAPER_MAIMAI_COOKIE": "scraper_maimai_cookie",
}


def cookie_value(cookie: str, name: str) -> str | None:
    prefix = f"{name}="
    for part in cookie.split(";"):
        part = part.strip()
        if part.startswith(prefix):
            return part[len(prefix) :]
    return None


def cookie_from_config(config: dict) -> str | None:
    env_key = config.get("cookie_env")
    if env_key:
        value = os.environ.get(env_key, "").strip()
        if value:
            return value
        attr = _SETTING_COOKIE_KEYS.get(env_key)
        if attr:
            settings_val = getattr(get_settings(), attr, "").strip()
            if settings_val:
                return settings_val
    return (config.get("cookies") or "").strip() or None


def build_job_article(
    *,
    title: str,
    company: str,
    salary: str,
    location: str,
    url: str,
    source_label: str,
    extra: str = "",
    language: str | None = "zh",
) -> RawArticle:
    summary_parts = [f"来源：{source_label}"]
    if company:
        summary_parts.append(f"公司：{company}")
    if salary:
        summary_parts.append(f"薪资：{salary}")
    if location:
        summary_parts.append(f"地点：{location}")
    if extra:
        summary_parts.append(extra)

    full_title = title
    if company and company not in title:
        full_title = f"{title} · {company}"
    if salary:
        full_title = f"{full_title}（{salary}）"

    return RawArticle(
        title=full_title[:500],
        summary=" | ".join(summary_parts)[:5000],
        url=url,
        author=company[:200] if company else None,
        published_at=datetime.now(timezone.utc),
        raw_category="recruitment",
        language=language,
    )
