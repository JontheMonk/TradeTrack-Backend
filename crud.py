from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import Employee
from schemas import EmployeeInput
from core.errors import (
    EmployeeAlreadyExists,
    EmployeeNotFound,
    DatabaseError,
)

def add_employee(db: Session, employee: EmployeeInput) -> None:
    emp = Employee(**employee.model_dump())
    db.add(emp)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise EmployeeAlreadyExists() from e
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error adding employee: {e}") from e

def update_employee(db: Session, employee: EmployeeInput) -> None:
    emp = get_employee_by_id(db, employee.employee_id)
    try:
        emp.name = employee.name
        emp.embedding = employee.embedding
        emp.role = employee.role
        db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error updating employee: {e}") from e

def remove_employee_by_id(db: Session, employee_id: str) -> None:
    emp = get_employee_by_id(db, employee_id)
    try:
        db.delete(emp)
        db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error removing employee: {e}") from e

def get_employee_by_id(db: Session, employee_id: str) -> Employee:
    try:
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve employee: {e}") from e

    if not emp:
        raise EmployeeNotFound()

    return emp

def get_employees_by_prefix(db: Session, prefix: str) -> List[Employee]:
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
