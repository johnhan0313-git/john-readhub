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
    categories_updated = 0
    for item in data.get("categories", []):
        existing = db.scalar(select(Category).where(Category.slug == item["slug"]))
        if existing:
            changed = False
            if existing.name != item["name"]:
                existing.name = item["name"]
                changed = True
            if existing.sort_order != item.get("sort_order", 0):
                existing.sort_order = item.get("sort_order", 0)
                changed = True
            if changed:
                categories_updated += 1
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
    sources_updated = 0
    for item in data.get("sources", []):
        existing = db.scalar(select(Source).where(Source.name == item["name"]))
        if existing:
            changed = False
            new_type = SourceType(item["type"])
            if existing.type != new_type:
                existing.type = new_type
                changed = True
            if existing.endpoint != item["endpoint"]:
                existing.endpoint = item["endpoint"]
                changed = True
            new_config = item.get("config", {})
            if existing.config != new_config:
                existing.config = new_config
                changed = True
            if existing.enabled != item.get("enabled", True):
                existing.enabled = item.get("enabled", True)
                changed = True
            if changed:
                sources_updated += 1
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
    return {
        "categories": categories_created,
        "categories_updated": categories_updated,
        "sources": sources_created,
        "sources_updated": sources_updated,
    }
