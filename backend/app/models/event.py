from __future__ import annotations

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time_util import now_ms


class Event(Base):
    """Phase 2: AI-clustered news events. Table created in MVP for future use."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_seen_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=now_ms)

    articles = relationship("Article", back_populates="event")
