from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FetchStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


class FetchLog(Base):
    __tablename__ = "fetch_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    status: Mapped[FetchStatus] = mapped_column(Enum(FetchStatus), nullable=False)
    articles_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    source = relationship("Source", back_populates="fetch_logs")
