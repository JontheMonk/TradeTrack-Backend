import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data.models import Base, Employee
import data.employee_repository as repo
from core.errors import (
    EmployeeAlreadyExists,
    EmployeeNotFound,
    DatabaseError,
)

# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture()
def db():
    """Create a fresh in-memory SQLite DB for each test."""
    engine = create_engine("sqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)

    Base.metadata.create_all(engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def make_emp(employee_id="abc123", name="Alice", role="employee", embedding=None):
    """Helper payload factory."""
    return {
        "employee_id": employee_id,
        "name": name,
        "role": role,
        "embedding": embedding or [0.1] * 512,
    }


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def test_add_employee_creates_row(db):
    payload = make_emp()
    emp = repo.add_employee(db, payload)

    assert emp.employee_id == payload["employee_id"]
    assert emp.name == payload["name"]

    # Check DB actually has it
    stored = db.get(Employee, payload["employee_id"])
    assert stored is not None


def test_add_employee_duplicate_key_raises(db):
    payload = make_emp()
    repo.add_employee(db, payload)

    with pytest.raises(EmployeeAlreadyExists):
        repo.add_employee(db, payload)


def test_add_employee_raises_database_error_on_commit_failure(db, monkeypatch):
    """Force a commit failure to ensure DatabaseError is raised."""
    payload = make_emp()

    def bad_commit():
        raise RuntimeError("DB died")

    monkeypatch.setattr(db, "commit", bad_commit)

    with pytest.raises(DatabaseError):
        repo.add_employee(db, payload)


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def test_get_employee_by_id_success(db):
    payload = make_emp()
    db.add(Employee(**payload))
    db.commit()

    emp = repo.get_employee_by_id(db, payload["employee_id"])
    assert emp.name == payload["name"]


def test_get_employee_by_id_not_found(db):
    with pytest.raises(EmployeeNotFound):
        repo.get_employee_by_id(db, "NOPE")


def test_get_employees_by_prefix_matches(db):
    db.add(Employee(**make_emp("abc123", "Alice")))
    db.add(Employee(**make_emp("abd999", "Alicia")))
    db.add(Employee(**make_emp("zzz999", "Bob")))
    db.commit()

    results = repo.get_employees_by_prefix(db, "ab")
    ids = {e.employee_id for e in results}

    assert ids == {"abc123", "abd999"}


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def test_update_employee_changes_fields(db):
    payload = make_emp()
    db.add(Employee(**payload))
    db.commit()

    updated = repo.update_employee(
        db,
        payload["employee_id"],
        name="NewName",
        role="admin"
    )

    assert updated.name == "NewName"
    assert updated.role == "admin"


def test_update_employee_not_found(db):
    with pytest.raises(EmployeeNotFound):
        repo.update_employee(db, "ghost", name="x")


def test_update_employee_raises_database_error(db, monkeypatch):
    """Force commit failure during update to ensure DatabaseError."""
    payload = make_emp()
    db.add(Employee(**payload))
    db.commit()

    def bad_commit():
        raise RuntimeError("commit failed")

    monkeypatch.setattr(db, "commit", bad_commit)

    with pytest.raises(DatabaseError):
        repo.update_employee(db, payload["employee_id"], name="X")


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def test_remove_employee_by_id_removes_row(db):
    payload = make_emp()
    db.add(Employee(**payload))
    db.commit()

    repo.remove_employee_by_id(db, payload["employee_id"])

    remaining = db.get(Employee, payload["employee_id"])
    assert remaining is None


def test_remove_employee_by_id_not_found(db):
    with pytest.raises(EmployeeNotFound):
        repo.remove_employee_by_id(db, "nope")
