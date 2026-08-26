from __future__ import annotations

from app.application.catalog.catalog_query import CatalogQueries
from app.composition.container import get_container


def get_catalog_queries() -> CatalogQueries:
    return get_container().catalog
