# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from data.models import Base
from data.database import get_session
from main import app


@pytest.fixture(scope="session")
def test_engine():
    """
    Shared in-memory SQLite engine backed by StaticPool so ALL tests and ALL
    FastAPI requests see the SAME database (tables included).
    """
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def db_session(test_engine):
    """
    Fresh DB state for every test.

    Even though we reuse the same engine (fast),
    we DROP and CREATE all tables before each test
    so no state leaks between tests.
    """

    # Wipe all tables to remove rows from previous tests
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)

    # Brand-new session for this test
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@pytest.fixture()
def client(db_session):
    """
    FastAPI TestClient that uses the SQLite in-memory test DB.
    """

    def override_get_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session

    return TestClient(app)
