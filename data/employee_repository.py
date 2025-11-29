"""
Repository layer for Employee persistence.

This module interacts directly with the database using SQLAlchemy ORM.
All higher-level business logic belongs in the service layer.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import structlog

from data.models import Employee
from core.errors import (
    EmployeeAlreadyExists,
    EmployeeNotFound,
    DatabaseError,
)

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def add_employee(db: Session, payload: dict) -> Employee:
    """
    Insert a new Employee row into the database.
    """
    emp = Employee(**payload)
    db.add(emp)

    try:
        db.commit()
        db.refresh(emp)

        log.debug(
            "repo_add_employee_success",
            employee_id=emp.employee_id,
        )

        return emp

    except IntegrityError as e:
        db.rollback()
        log.warning(
            "repo_add_employee_duplicate",
            employee_id=payload.get("employee_id"),
        )
        raise EmployeeAlreadyExists() from e

    except Exception as e:
        db.rollback()
        log.error(
            "repo_add_employee_unhandled_error",
            employee_id=payload.get("employee_id"),
            error=str(e),
        )
        raise DatabaseError(f"Error adding employee: {e}") from e


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_employee_by_id(db: Session, employee_id: str) -> Employee:
    """
    Retrieve a single employee by ID.
    """
    try:
        emp = (
            db.query(Employee)
            .filter(Employee.employee_id == employee_id)
            .first()
        )
    except Exception as e:
        log.error(
            "repo_get_employee_db_error",
            employee_id=employee_id,
            error=str(e),
        )
        raise DatabaseError(f"Failed to retrieve employee: {e}") from e

    if not emp:
        log.info(
            "repo_employee_not_found",
            employee_id=employee_id,
        )
        raise EmployeeNotFound()

    return emp


def get_employees_by_prefix(db: Session, prefix: str) -> List[Employee]:
    """
    Prefix-based search on employee_id or name.
    """
    try:
        employees = (
            db.query(Employee)
            .filter(
                (Employee.name.ilike(f"{prefix}%"))
                | (Employee.employee_id.ilike(f"{prefix}%"))
            )
            .all()
        )

        if not employees:
            log.debug(
                "repo_search_no_results",
                prefix=prefix,
            )

        return employees

    except Exception as e:
        log.error(
            "repo_prefix_search_error",
            prefix=prefix,
            error=str(e),
        )
        raise DatabaseError(f"Failed to search employees by prefix: {e}") from e


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def update_employee(
    db: Session,
    employee_id: str,
    *,
    name: Optional[str] = None,
    role: Optional[str] = None,
    embedding: Optional[list] = None
) -> Employee:
    """
    Update a subset of fields for an employee.
    """
    emp = get_employee_by_id(db, employee_id)

    try:
        if name is not None:
            emp.name = name
        if embedding is not None:
            emp.embedding = embedding
        if role is not None:
            emp.role = role

        db.commit()
        db.refresh(emp)

        log.debug(
            "repo_update_employee_success",
            employee_id=employee_id,
        )

        return emp

    except Exception as e:
        db.rollback()
        log.error(
            "repo_update_employee_error",
            employee_id=employee_id,
            error=str(e),
        )
        raise DatabaseError(f"Error updating employee: {e}") from e


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def remove_employee_by_id(db: Session, employee_id: str) -> None:
    """
    Permanently delete an employee record.
    """
    emp = get_employee_by_id(db, employee_id)

    try:
        db.delete(emp)
        db.commit()

        log.debug(
            "repo_delete_employee_success",
            employee_id=employee_id,
        )

    except Exception as e:
        db.rollback()
        log.error(
            "repo_delete_employee_error",
            employee_id=employee_id,
            error=str(e),
        )
        raise DatabaseError(f"Error removing employee: {e}") from e
