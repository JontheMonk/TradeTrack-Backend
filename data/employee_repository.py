"""
Repository layer for Employee persistence.

This module interacts directly with the database using SQLAlchemy ORM.
All higher-level business logic belongs in the service layer.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from data.models import Employee
from core.errors import (
    EmployeeAlreadyExists,
    EmployeeNotFound,
    DatabaseError,
)


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def add_employee(db: Session, payload: dict) -> Employee:
    """
    Insert a new Employee row into the database.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy session.
    payload : dict
        Dictionary containing the validated fields for the Employee model.
        Expected keys: employee_id, name, embedding, role.

    Returns
    -------
    Employee
        The newly created employee model instance.

    Raises
    ------
    EmployeeAlreadyExists
        If a duplicate primary key (employee_id) is inserted.
    DatabaseError
        For any unexpected DB failure.
    """
    emp = Employee(**payload)
    db.add(emp)

    try:
        db.commit()
        db.refresh(emp)
        return emp
    except IntegrityError as e:
        db.rollback()
        raise EmployeeAlreadyExists() from e
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error adding employee: {e}") from e


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_employee_by_id(db: Session, employee_id: str) -> Employee:
    """
    Retrieve a single employee by ID.

    Raises
    ------
    EmployeeNotFound
        If the employee does not exist.
    DatabaseError
        For unexpected DB lookup failures.
    """
    try:
        emp = (
            db.query(Employee)
            .filter(Employee.employee_id == employee_id)
            .first()
        )
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve employee: {e}") from e

    if not emp:
        raise EmployeeNotFound()

    return emp


def get_employees_by_prefix(db: Session, prefix: str) -> List[Employee]:
    """
    Prefix-based search on employee_id or name.
    """
    try:
        return (
            db.query(Employee)
            .filter(
                (Employee.name.ilike(f"{prefix}%"))
                | (Employee.employee_id.ilike(f"{prefix}%"))
            )
            .all()
        )
    except Exception as e:
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

    Parameters
    ----------
    employee_id : str
        ID of the employee.
    name : Optional[str]
        New name, if updating.
    role : Optional[str]
        New role ("employee" or "admin"), if updating.
    embedding : Optional[list]
        New 512-dim embedding, if updating.

    Returns
    -------
    Employee
        The updated employee instance.

    Raises
    ------
    EmployeeNotFound
        If the employee doesn't exist.
    DatabaseError
        For unexpected DB errors.
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
        return emp
    except Exception as e:
        db.rollback()
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
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error removing employee: {e}") from e
