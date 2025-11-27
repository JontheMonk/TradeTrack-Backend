"""
Database configuration and session management.

This module defines:
    • The SQLAlchemy engine (Postgres in production, SQLite in tests)
    • The session factory used by the application
    • The `get_session()` dependency for FastAPI routes

Why Base is NOT defined here:
-----------------------------
Base must come from data.models so both the application and pytest share the
same metadata registry. Defining Base here would create a second metadata tree,
leading to broken tables, test mismatches, and migration problems.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.settings import settings
from data.models import Base


# ---------------------------------------------------------------------------
# Engine Creation
# ---------------------------------------------------------------------------

def _build_connect_args():
    """
    Choose connect_args based on the database driver.

    - PostgreSQL requires sslmode for many hosted environments.
    - SQLite does NOT support sslmode, so connect_args must be empty.

    Returns
    -------
    dict
        Keyword arguments to supply to create_engine().
    """
    if settings.database_url.startswith("postgres"):
        return {"sslmode": "require"}
    return {}


engine = create_engine(
    settings.database_url,
    connect_args=_build_connect_args(),
    future=True,
)


# ---------------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ---------------------------------------------------------------------------
# FastAPI Session Dependency
# ---------------------------------------------------------------------------

def get_session():
    """
    Provide a database session to FastAPI endpoint handlers.

    Behavior:
        • Each request gets its own dedicated DB session.
        • Session is closed automatically after the request finishes.
        • Matches FastAPI's dependency-injection lifecycle.

    Yields
    ------
    Session
        SQLAlchemy ORM session bound to the application's engine.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
