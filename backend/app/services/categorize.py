from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category

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


def resolve_category_slug(
    db: Session,
    raw_category: str | None,
    default_slug: str | None,
) -> int | None:
    slug = None
    if raw_category:
        slug = CATEGORY_MAP.get(raw_category.lower(), raw_category.lower())
    if not slug and default_slug:
        slug = default_slug

    if not slug:
        return None

    category = db.scalar(select(Category).where(Category.slug == slug))
    if category:
        return category.id

    general = db.scalar(select(Category).where(Category.slug == "general"))
    return general.id if general else None
