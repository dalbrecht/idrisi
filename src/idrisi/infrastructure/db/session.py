"""Database engine and session factory utilities."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from idrisi.infrastructure.db.models import Base


def create_engine_and_tables(database_url: str) -> Engine:
    """Create a SQLAlchemy engine and initialize all tables.

    Args:
        database_url: SQLAlchemy-compatible database URL.

    Returns:
        The configured Engine instance.
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine: Engine) -> Session:
    """Create a new SQLAlchemy session bound to the given engine.

    Args:
        engine: The SQLAlchemy Engine to bind.

    Returns:
        A new Session instance.
    """
    return Session(bind=engine)
