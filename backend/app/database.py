from __future__ import annotations

import logging
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings

logger = logging.getLogger(__name__)

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


class Base(DeclarativeBase):
    pass


def _sqlite_on_connect(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


def _is_postgresql(url: str) -> bool:
    return url.startswith("postgresql")


def ensure_engine() -> Engine:
    global _engine, _SessionLocal
    settings = get_settings()
    url = settings.database_url
    if _engine is not None and str(_engine.url) == url:
        return _engine

    if _engine is not None:
        _engine.dispose()
        _engine = None
        _SessionLocal = None

    connect_args: dict[str, object] = {}
    engine_kwargs: dict[str, object] = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        connect_args["timeout"] = 30
        if url.endswith(":memory:") or url.rstrip("/").endswith(":memory:"):
            engine_kwargs["poolclass"] = StaticPool
    elif _is_postgresql(url):
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

    _engine = create_engine(url, connect_args=connect_args, **engine_kwargs)
    if url.startswith("sqlite"):
        event.listen(_engine, "connect", _sqlite_on_connect)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_engine() -> Engine:
    return ensure_engine()


def SessionLocal() -> Session:
    ensure_engine()
    assert _SessionLocal is not None
    return _SessionLocal()


def reset_engine_for_tests() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    backend_dir = Path(__file__).resolve().parents[1]
    cfg = Config(str(backend_dir / "alembic.ini"))
    command.upgrade(cfg, "head")
    logger.info("Database migrations applied (alembic upgrade head)")


def init_db() -> None:
    settings = get_settings()
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        if db_path and not db_path.startswith(":"):
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    from app import models  # noqa: F401

    engine = get_engine()

    if settings.testing:
        Base.metadata.create_all(bind=engine)
        return

    insp = inspect(engine)
    has_alembic = insp.has_table("alembic_version")
    if settings.use_migrations or has_alembic:
        run_migrations()
        return

    Base.metadata.create_all(bind=engine)
