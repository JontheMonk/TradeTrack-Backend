import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data.models import Base, Employee, TimeEntry
import data.time_entry_repository as repo
from core.errors import DatabaseError


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def employee(db):
    """Create a test employee for time entry tests."""
    emp = Employee(
        employee_id="emp123",
        name="Test Worker",
        role="employee",
        embedding=[0.1] * 512,
    )
    db.add(emp)
    db.commit()
    return emp


# ---------------------------------------------------------------------------
# GET OPEN ENTRY
# ---------------------------------------------------------------------------

def test_get_open_entry_returns_none_when_not_clocked_in(db, employee):
    result = repo.get_open_entry(db, employee.employee_id)
    assert result is None


def test_get_open_entry_returns_entry_when_clocked_in(db, employee):
    entry = TimeEntry(employee_id=employee.employee_id)
    db.add(entry)
    db.commit()

    result = repo.get_open_entry(db, employee.employee_id)
    
    assert result is not None
    assert result.employee_id == employee.employee_id
    assert result.clock_out is None


def test_get_open_entry_ignores_closed_entries(db, employee):
    # Create a closed entry (already clocked out)
    from datetime import datetime
    closed = TimeEntry(
        employee_id=employee.employee_id,
        clock_out=datetime.now()
    )
    db.add(closed)
    db.commit()

    result = repo.get_open_entry(db, employee.employee_id)
    assert result is None


# ---------------------------------------------------------------------------
# CREATE ENTRY
# ---------------------------------------------------------------------------

def test_create_entry_inserts_row(db, employee):
    entry = repo.create_entry(db, employee.employee_id)

    assert entry.id is not None
    assert entry.employee_id == employee.employee_id
    assert entry.clock_in is not None
    assert entry.clock_out is None


def test_create_entry_raises_database_error_on_failure(db, employee, monkeypatch):
    def bad_commit():
        raise RuntimeError("DB failed")

    monkeypatch.setattr(db, "commit", bad_commit)

    with pytest.raises(DatabaseError):
        repo.create_entry(db, employee.employee_id)


# ---------------------------------------------------------------------------
# CLOSE ENTRY
# ---------------------------------------------------------------------------

def test_close_entry_sets_clock_out(db, employee):
    # Create open entry
    entry = TimeEntry(employee_id=employee.employee_id)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    assert entry.clock_out is None

    # Close it
    closed = repo.close_entry(db, entry)

    assert closed.clock_out is not None


def test_close_entry_raises_database_error_on_failure(db, employee, monkeypatch):
    entry = TimeEntry(employee_id=employee.employee_id)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    def bad_commit():
        raise RuntimeError("commit failed")

    monkeypatch.setattr(db, "commit", bad_commit)

    with pytest.raises(DatabaseError):
        repo.close_entry(db, entry)