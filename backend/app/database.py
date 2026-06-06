from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=not settings.database_url.startswith("sqlite"),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    db_url = settings.database_url
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        if db_path and not db_path.startswith(":"):
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
