from __future__ import annotations

import enum

from sqlalchemy import JSON, BigInteger, Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time_util import now_ms


class SourceType(str, enum.Enum):
    RSS = "rss"
    API = "api"
    SCRAPER = "scraper"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_fetched_at: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=now_ms)

    articles = relationship("Article", back_populates="source")
    fetch_logs = relationship("FetchLog", back_populates="source")
