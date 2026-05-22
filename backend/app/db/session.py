"""Database engine and session helpers."""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings


def create_database_engine(database_url: str, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine for the configured database URL."""
    return create_engine(database_url, echo=echo, future=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a configured SQLAlchemy session factory."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_engine(settings: Settings | None = None) -> Engine:
    """Create an engine from runtime settings."""
    runtime_settings = settings or get_settings()
    return create_database_engine(runtime_settings.database_url, echo=runtime_settings.debug)


@lru_cache
def get_engine_for_url(database_url: str, echo: bool = False) -> Engine:
    """Return a cached engine for a database URL."""
    return create_database_engine(database_url, echo=echo)


@lru_cache
def get_session_factory_for_url(
    database_url: str,
    echo: bool = False,
) -> sessionmaker[Session]:
    """Return a cached session factory for a database URL."""
    return create_session_factory(get_engine_for_url(database_url, echo=echo))


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    settings = get_settings()
    session_factory = get_session_factory_for_url(settings.database_url, settings.debug)
    with session_factory() as session:
        yield session
