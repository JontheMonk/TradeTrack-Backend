# tests/conftest.py
"""
Test infrastructure for API tests.

This file sets up:
    • A shared in-memory SQLite database using StaticPool
    • A schema reset per test
    • A dependency-injected get_session for FastAPI
    • A make_client() fixture that produces a fresh TestClient per test

This approach avoids:
    • File-backed SQLite (slow, persistent)
    • SQLite connection issues (solved by StaticPool)
    • Transaction rollbacks (incompatible with FastAPI)
    • Table-loss between requests (StaticPool ensures a single connection)

API tests simulate full HTTP requests, so each test receives:
    • a clean database schema
    • a new FastAPI app
    • a new TestClient
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from data.models import Base
from data.database import build_session_dependency
from main import create_app
from core.settings import Settings


# ---------------------------------------------------------------------------
# SHARED TEST ENGINE (SESSION-SCOPED)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_engine():
    """
    Create a single in-memory SQLite engine for the entire test session.

    StaticPool ensures:
        • All sessions share the same underlying SQLite connection
        • The in-memory DB persists across multiple TestClient requests
        • Tables do not “disappear” between connections (SQLite quirk)

    This engine must not be used directly; tests inject their own
    get_session dependency through make_test_get_session().
    """
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )


# ---------------------------------------------------------------------------
# PER-TEST get_session FACTORY
# ---------------------------------------------------------------------------

def make_test_get_session(engine):
    """
    Build a new get_session FastAPI dependency for a SINGLE TEST.

    Steps:
        1. Drop all tables — ensures no state leaks across tests
        2. Create tables fresh
        3. Create and return a get_session() generator function

    The returned function behaves exactly like the production dependency:
        • Each request gets a NEW SQLAlchemy Session
        • Sessions are properly closed after use
        • No transaction rollbacks (SQLite + FastAPI unsafe)

    This function is called once per test via make_client().
    """

    # Reset schema for this test
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Return the dependency that FastAPI will call per request
    return build_session_dependency(engine)


# ---------------------------------------------------------------------------
# make_client FIXTURE — builds a fresh TestClient per test
# ---------------------------------------------------------------------------

@pytest.fixture()
def make_client(test_engine):
    """
    Factory fixture that produces a fresh TestClient per test.

    Usage:
        client = make_client()
        client = make_client(settings_overrides={...})

    Behavior:
        • Builds new Settings object (env="test" by default)
        • Applies optional test-specific overrides
        • Builds a new FastAPI app via create_app()
        • Injects a per-test database session dependency
        • Returns a TestClient wrapping the app

    This keeps API tests completely isolated:
        • No shared DB state across tests
        • No shared FastAPI app state
        • Each test behaves like a clean, cold start
    """

    def builder(settings_overrides=None):
        # Base test settings
        settings = Settings(env="test")

        # Apply user-provided test overrides (thresholds, admin keys, etc.)
        for key, value in (settings_overrides or {}).items():
            setattr(settings, key, value)

        # Build FastAPI app with the overridden get_session maker
        app = create_app(
            settings=settings,
            engine=test_engine,
            get_session_maker=make_test_get_session,
        )

        return TestClient(app)

    return builder
