# data/database.py

"""
Build FastAPI DB dependency from an SQLAlchemy engine.

This is intentionally minimal. The app provides the engine,
and we return a get_session dependency bound to it.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

def build_session_dependency(engine: Engine):
    """
    Shared logic for creating a FastAPI-compatible session dependency
    from an engine. Used by both production and test setups.
    """
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    def get_session():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return get_session

def make_get_session(engine: Engine):
    return build_session_dependency(engine)

