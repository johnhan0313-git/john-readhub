from __future__ import annotations

import logging
from contextvars import ContextVar
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None
_current_session: ContextVar[Session | None] = ContextVar("readhub_session", default=None)


class Base(DeclarativeBase):
    pass


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

    _engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_engine() -> Engine:
    return ensure_engine()


def create_session() -> Session:
    ensure_engine()
    assert _SessionLocal is not None
    return _SessionLocal()


def get_current_session() -> Session:
    session = _current_session.get()
    if session is None:
        raise RuntimeError("No active UnitOfWork session")
    return session


def reset_engine_for_tests() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def run_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    backend_dir = Path(__file__).resolve().parents[3]
    cfg = Config(str(backend_dir / "alembic.ini"))
    command.upgrade(cfg, "head")
    logger.info("Database migrations applied (alembic upgrade head)")


def init_db() -> None:
    settings = get_settings()
    from app.infrastructure.persistence import models  # noqa: F401

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


class SqlAlchemyUnitOfWork:
    def __init__(self) -> None:
        self.session: Session | None = None
        self._token = None
        self._committed = False

    def commit(self) -> None:
        assert self.session is not None
        self.session.commit()
        self._committed = True

    def rollback(self) -> None:
        assert self.session is not None
        self.session.rollback()

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        self.session = create_session()
        self._token = _current_session.set(self.session)
        self._committed = False
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self.session is not None
        try:
            if exc_type is not None:
                self.rollback()
            elif not self._committed:
                self.rollback()
        finally:
            self.session.close()
            if self._token is not None:
                _current_session.reset(self._token)


def make_uow_factory():
    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork()

    return factory
