from __future__ import annotations

import enum

from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time_util import now_ms


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
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=now_ms)

    source = relationship("Source", back_populates="fetch_logs")
