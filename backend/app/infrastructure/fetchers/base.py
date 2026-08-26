from __future__ import annotations

# Compatibility shim: RawArticle lives in domain; adapters import from here.
from app.domains.ingest.ingest_domain import RawArticle, SourceRecord

__all__ = ["RawArticle", "SourceRecord"]
