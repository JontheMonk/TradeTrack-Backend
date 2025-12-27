"""
Clock-in/clock-out business logic.

Orchestrates time entry operations with validation rules:
    • Cannot clock in if already clocked in
    • Cannot clock out if not clocked in
"""

from sqlalchemy.orm import Session
from structlog import get_logger

from data.models import TimeEntry
import data.time_entry_repository as repo
from core.errors import AlreadyClockedIn, NotClockedIn
from schemas import ClockStatus

log = get_logger()


# ---------------------------------------------------------------------------
# CLOCK IN
# ---------------------------------------------------------------------------

def clock_in(employee_id: str, db: Session) -> TimeEntry:
    """
    Clock in an employee.

    Raises:
        AlreadyClockedIn: If the employee has an open time entry.
    """
    log.info("clock_in_attempt", employee_id=employee_id)

    # Check for existing open entry
    existing = repo.get_open_entry(db, employee_id)
    if existing is not None:
        log.warning(
            "clock_in_rejected_already_clocked_in",
            employee_id=employee_id,
            existing_entry_id=existing.id,
        )
        raise AlreadyClockedIn()

    # Create new entry
    entry = repo.create_entry(db, employee_id)

    log.info(
        "clock_in_success",
        employee_id=employee_id,
        entry_id=entry.id,
        clock_in=entry.clock_in.isoformat(),
    )

    return entry


# ---------------------------------------------------------------------------
# CLOCK OUT
# ---------------------------------------------------------------------------

def clock_out(employee_id: str, db: Session) -> TimeEntry:
    """
    Clock out an employee.

    Raises:
        NotClockedIn: If the employee has no open time entry.
    """
    log.info("clock_out_attempt", employee_id=employee_id)

    # Find open entry
    entry = repo.get_open_entry(db, employee_id)
    if entry is None:
        log.warning(
            "clock_out_rejected_not_clocked_in",
            employee_id=employee_id,
        )
        raise NotClockedIn()

    # Close the entry
    closed = repo.close_entry(db, entry)

    log.info(
        "clock_out_success",
        employee_id=employee_id,
        entry_id=closed.id,
        clock_out=closed.clock_out.isoformat() if closed.clock_out else None,
    )

    return closed


# ---------------------------------------------------------------------------
# STATUS
# ---------------------------------------------------------------------------

def get_clock_status(employee_id: str, db: Session) -> ClockStatus:
    """
    Check if an employee is currently clocked in.
    """
    entry = repo.get_open_entry(db, employee_id)

    if entry is None:
        return ClockStatus(is_clocked_in=False)

    return ClockStatus(
        is_clocked_in=True,
        clock_in_time=entry.clock_in,
    )