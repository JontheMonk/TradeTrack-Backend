"""
Repository layer for TimeEntry persistence.

Handles clock-in/clock-out database operations. Business logic
(e.g., "reject if already clocked in") belongs in the service layer.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import structlog

from data.models import TimeEntry
from core.errors import DatabaseError

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_open_entry(db: Session, employee_id: str) -> Optional[TimeEntry]:
    """
    Find an open time entry (clock_out IS NULL) for the given employee.
    
    Returns None if the employee is not currently clocked in.
    """
    try:
        entry = (
            db.query(TimeEntry)
            .filter(
                TimeEntry.employee_id == employee_id,
                TimeEntry.clock_out.is_(None)
            )
            .first()
        )
        return entry

    except Exception as e:
        log.error(
            "repo_get_open_entry_error",
            employee_id=employee_id,
            error=str(e),
        )
        raise DatabaseError(f"Failed to query open entry: {e}") from e


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def create_entry(db: Session, employee_id: str) -> TimeEntry:
    """
    Create a new time entry (clock in).
    
    The clock_in timestamp is set automatically via server_default.
    """
    entry = TimeEntry(employee_id=employee_id)
    db.add(entry)

    try:
        db.commit()
        db.refresh(entry)

        log.debug(
            "repo_create_entry_success",
            employee_id=employee_id,
            entry_id=entry.id,
            clock_in=entry.clock_in.isoformat(),
        )

        return entry

    except Exception as e:
        db.rollback()
        log.error(
            "repo_create_entry_error",
            employee_id=employee_id,
            error=str(e),
        )
        raise DatabaseError(f"Failed to create time entry: {e}") from e


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def close_entry(db: Session, entry: TimeEntry) -> TimeEntry:
    """
    Close an open time entry (clock out).
    
    Sets clock_out to the current time.
    """
    try:
        entry.clock_out = func.now()
        db.commit()
        db.refresh(entry)

        log.debug(
            "repo_close_entry_success",
            employee_id=entry.employee_id,
            entry_id=entry.id,
            clock_out=entry.clock_out.isoformat() if entry.clock_out else None,
        )

        return entry

    except Exception as e:
        db.rollback()
        log.error(
            "repo_close_entry_error",
            entry_id=entry.id,
            error=str(e),
        )
        raise DatabaseError(f"Failed to close time entry: {e}") from e