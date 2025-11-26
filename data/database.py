"""
Database configuration module.

Creates the SQLAlchemy engine, session factory, and declarative base
used throughout the application. The `get_session()` dependency
provides a per-request database session for FastAPI routes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.settings import settings

engine = create_engine(
    settings.database_url,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_session():
    """
    Dependency that provides a scoped SQLAlchemy session.

    Yields
    ------
    Session
        A database session that is closed automatically after the request.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
