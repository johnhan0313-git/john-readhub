from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time_util import now_ms


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        Index("ix_articles_published_at", "published_at"),
        Index("ix_articles_category_id", "category_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    url_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    published_at: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    fetched_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=now_ms)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), nullable=True)

    source = relationship("Source", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    event = relationship("Event", back_populates="articles")
