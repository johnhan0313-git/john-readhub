from __future__ import annotations

import json

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Article, Event
from app.utils.time_util import hours_ago_ms, now_ms


class EventClusterService:
    """Phase 2 skeleton: cluster recent articles into events via LLM."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def get_unclustered_articles(self, hours: int = 24) -> list[Article]:
        since = hours_ago_ms(hours)
        return list(
            self.db.scalars(
                select(Article)
                .where(Article.event_id.is_(None), Article.published_at >= since)
                .order_by(Article.published_at.desc())
                .limit(100)
            ).all()
        )

    async def cluster_recent(self) -> dict[str, int | str]:
        llm = self.settings.llm_config()
        if not llm.is_configured:
            return {"status": "skipped", "reason": "AI_LLM_API_KEY not configured"}

        articles = self.get_unclustered_articles()
        if len(articles) < 2:
            return {"status": "skipped", "reason": "not enough articles", "count": len(articles)}

        payload = [
            {"id": a.id, "title": a.title, "summary": (a.summary or "")[:300]}
            for a in articles
        ]
        prompt = (
            "Group these news articles into event clusters. "
            "Return JSON: {\"events\": [{\"title\": str, \"summary\": str, \"article_ids\": [int]}]}"
            f"\n\nArticles:\n{json.dumps(payload, ensure_ascii=False)}"
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{llm.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {llm.api_key}"},
                json={
                    "model": llm.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]

        result = json.loads(content)
        events_created = 0
        articles_linked = 0

        for group in result.get("events", []):
            article_ids = group.get("article_ids", [])
            if not article_ids:
                continue

            linked = list(
                self.db.scalars(
                    select(Article).where(
                        Article.id.in_(article_ids),
                        Article.event_id.is_(None),
                    )
                ).all()
            )
            if not linked:
                continue

            now = now_ms()
            published_times = [a.published_at for a in linked if a.published_at is not None]
            first_seen = min(published_times) if published_times else now
            last_updated = max(published_times) if published_times else now

            event = Event(
                title=group.get("title", linked[0].title)[:500],
                summary=(group.get("summary") or "")[:2000] or None,
                first_seen_at=first_seen,
                last_updated_at=last_updated,
            )
            self.db.add(event)
            self.db.flush()

            for article in linked:
                article.event_id = event.id
                articles_linked += 1

            events_created += 1

        self.db.commit()
        return {
            "status": "success",
            "events_created": events_created,
            "articles_linked": articles_linked,
        }
