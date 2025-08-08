from sqlalchemy.orm import Session
from models import Employee
from schemas import EmployeeInput
from core.errors import (
    EmployeeAlreadyExists,
    EmployeeNotFound,
    DatabaseError
)
from typing import List


def add_employee(db: Session, employee: EmployeeInput) -> Employee:
    if db.query(Employee).filter(Employee.employee_id == employee.employee_id).first():
        raise EmployeeAlreadyExists()
    try:
        emp = Employee(**employee.model_dump())
        db.add(emp)
        db.commit()
        db.refresh(emp)  # get DB defaults/updates
        return emp
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error adding employee: {str(e)}") from e


def update_employee(db: Session, employee: EmployeeInput) -> Employee:
    emp = get_employee_by_id(db, employee.employee_id)
    try:
        emp.name = employee.name
        emp.embedding = employee.embedding
        emp.role = employee.role
        db.commit()
        db.refresh(emp)
        return emp
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error updating employee: {str(e)}") from e


def remove_employee_by_id(db: Session, employee_id: str) -> Employee:
    emp = get_employee_by_id(db, employee_id)
    try:
        # snapshot before deletion so we can return it
        removed = Employee(
            employee_id=emp.employee_id,
            name=emp.name,
            embedding=emp.embedding,
            role=emp.role,
        )
        db.delete(emp)
        db.commit()
        return removed
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error removing employee: {str(e)}") from e


def get_employee_by_id(db: Session, employee_id: str) -> Employee:
    try:
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve employee: {str(e)}") from e

    if not emp:
        raise EmployeeNotFound()

    return emp


def get_employees_by_prefix(db: Session, prefix: str) -> List[Employee]:
    try:
        return db.query(Employee).filter(
            (Employee.name.ilike(f"{prefix}%")) |
            (Employee.employee_id.ilike(f"{prefix}%"))
        ).all()
    except Exception as e:
        raise DatabaseError(f"Failed to search employees by prefix: {str(e)}") from e
