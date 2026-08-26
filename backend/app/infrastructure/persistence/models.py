from __future__ import annotations

import enum

from sqlalchemy import JSON, BigInteger, Boolean, Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.unit_of_work import Base
from app.utils.time_util import now_ms


class SourceType(str, enum.Enum):
    RSS = "rss"
    API = "api"
    SCRAPER = "scraper"


class FetchStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


class CategoryRow(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class SourceRow(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    type: Mapped[SourceType] = mapped_column(Enum(SourceType, name="sourcetype"), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_fetched_at: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=now_ms)


class ArticleRow(Base):
    __tablename__ = "articles"
    __table_args__ = (
        Index("ix_articles_published_at", "published_at"),
        Index("ix_articles_category_id", "category_id"),
        Index("ix_articles_source_id", "source_id"),
        Index("ix_articles_fetched_at", "fetched_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    url_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    published_at: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    fetched_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=now_ms)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)


class FetchLogRow(Base):
    __tablename__ = "fetch_logs"
    __table_args__ = (Index("ix_fetch_logs_source_id", "source_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[FetchStatus] = mapped_column(
        Enum(FetchStatus, name="fetchstatus"), nullable=False
    )
    articles_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=now_ms)
