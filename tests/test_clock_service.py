import pytest
from unittest.mock import MagicMock
from datetime import datetime

from services.clock_service import clock_in, clock_out, get_clock_status
from core.errors import AlreadyClockedIn, NotClockedIn
from schemas import ClockStatus


# ---------------------------------------------------------------------------
# CLOCK IN
# ---------------------------------------------------------------------------

def test_clock_in_success(monkeypatch):
    """Clock in succeeds when no open entry exists."""
    db = MagicMock()

    # Mock: no existing entry
    monkeypatch.setattr(
        "services.clock_service.repo.get_open_entry",
        lambda db, emp_id: None
    )

    # Mock: create_entry returns a new entry
    mock_entry = MagicMock()
    mock_entry.id = 1
    mock_entry.employee_id = "emp123"
    mock_entry.clock_in = datetime.now()
    mock_entry.clock_out = None

    def mock_create(db, emp_id):
        mock_create.called_with = emp_id
        return mock_entry

    monkeypatch.setattr(
        "services.clock_service.repo.create_entry",
        mock_create
    )

    # Act
    result = clock_in("emp123", db)

    # Assert
    assert result == mock_entry
    assert mock_create.called_with == "emp123"


def test_clock_in_already_clocked_in_raises(monkeypatch):
    """Clock in fails if employee already has an open entry."""
    db = MagicMock()

    # Mock: existing open entry
    existing_entry = MagicMock()
    existing_entry.id = 99

    monkeypatch.setattr(
        "services.clock_service.repo.get_open_entry",
        lambda db, emp_id: existing_entry
    )

    # Act & Assert
    with pytest.raises(AlreadyClockedIn):
        clock_in("emp123", db)


# ---------------------------------------------------------------------------
# CLOCK OUT
# ---------------------------------------------------------------------------

def test_clock_out_success(monkeypatch):
    """Clock out succeeds when an open entry exists."""
    db = MagicMock()

    # Mock: open entry exists
    open_entry = MagicMock()
    open_entry.id = 1
    open_entry.employee_id = "emp123"
    open_entry.clock_in = datetime(2025, 12, 27, 8, 0, 0)

    monkeypatch.setattr(
        "services.clock_service.repo.get_open_entry",
        lambda db, emp_id: open_entry
    )

    # Mock: close_entry returns the closed entry
    closed_entry = MagicMock()
    closed_entry.id = 1
    closed_entry.clock_out = datetime(2025, 12, 27, 17, 0, 0)

    def mock_close(db, entry):
        mock_close.called_with_entry = entry
        return closed_entry

    monkeypatch.setattr(
        "services.clock_service.repo.close_entry",
        mock_close
    )

    # Act
    result = clock_out("emp123", db)

    # Assert
    assert result == closed_entry
    assert mock_close.called_with_entry == open_entry


def test_clock_out_not_clocked_in_raises(monkeypatch):
    """Clock out fails if no open entry exists."""
    db = MagicMock()

    # Mock: no open entry
    monkeypatch.setattr(
        "services.clock_service.repo.get_open_entry",
        lambda db, emp_id: None
    )

    # Act & Assert
    with pytest.raises(NotClockedIn):
        clock_out("emp123", db)


# ---------------------------------------------------------------------------
# GET CLOCK STATUS
# ---------------------------------------------------------------------------

def test_get_clock_status_clocked_in(monkeypatch):
    """Returns is_clocked_in=True when open entry exists."""
    db = MagicMock()

    open_entry = MagicMock()
    open_entry.clock_in = datetime(2025, 12, 27, 8, 0, 0)

    monkeypatch.setattr(
        "services.clock_service.repo.get_open_entry",
        lambda db, emp_id: open_entry
    )

    # Act
    status = get_clock_status("emp123", db)

    # Assert
    assert isinstance(status, ClockStatus)
    assert status.is_clocked_in is True
    assert status.clock_in_time == datetime(2025, 12, 27, 8, 0, 0)


def test_get_clock_status_not_clocked_in(monkeypatch):
    """Returns is_clocked_in=False when no open entry."""
    db = MagicMock()

    monkeypatch.setattr(
        "services.clock_service.repo.get_open_entry",
        lambda db, emp_id: None
    )

    # Act
    status = get_clock_status("emp123", db)

    # Assert
    assert isinstance(status, ClockStatus)
    assert status.is_clocked_in is False
    assert status.clock_in_time is None