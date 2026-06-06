from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Event(Base):
    """Phase 2: AI-clustered news events. Table created in MVP for future use."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    articles = relationship("Article", back_populates="event")
