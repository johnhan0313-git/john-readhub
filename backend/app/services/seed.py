from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, Source, SourceType

SEED_FILE = Path(__file__).resolve().parents[1] / "data" / "sources.seed.json"


def seed_database(db: Session) -> dict[str, int]:
    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))

    categories_created = 0
    for item in data.get("categories", []):
        exists = db.scalar(select(Category).where(Category.slug == item["slug"]))
        if exists:
            continue
        db.add(
            Category(
                name=item["name"],
                slug=item["slug"],
                sort_order=item.get("sort_order", 0),
            )
        )
        categories_created += 1

    sources_created = 0
    for item in data.get("sources", []):
        exists = db.scalar(select(Source).where(Source.name == item["name"]))
        if exists:
            continue
        db.add(
            Source(
                name=item["name"],
                type=SourceType(item["type"]),
                endpoint=item["endpoint"],
                config=item.get("config", {}),
                enabled=item.get("enabled", True),
            )
        )
        sources_created += 1

    db.commit()
    return {"categories": categories_created, "sources": sources_created}
