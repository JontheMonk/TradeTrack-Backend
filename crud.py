from sqlalchemy.orm import Session
from models import Employee
from schemas import FaceRecord
from core.errors import (
    EmployeeAlreadyExists,
    EmployeeNotFound,
    DatabaseError
)
from typing import List


def add_employee(db: Session, face: FaceRecord) -> None:
    if db.query(Employee).filter(Employee.employee_id == face.employee_id).first():
        raise EmployeeAlreadyExists()
    try:
        emp = Employee(**face.dict())
        db.add(emp)
        db.commit()
    except Exception as e:
        raise DatabaseError(f"Error adding employee: {str(e)}")


def update_employee(db: Session, face: FaceRecord) -> None:
    emp = get_employee_by_id(db, face.employee_id)

    try:
        emp.name = face.name
        emp.embedding = face.embedding
        emp.role = face.role
        db.commit()
    except Exception as e:
        raise DatabaseError(f"Error updating employee: {str(e)}")


def remove_employee_by_id(db: Session, employee_id: str) -> None:
    emp = get_employee_by_id(db, employee_id)

    try:
        db.delete(emp)
        db.commit()
    except Exception as e:
        raise DatabaseError(f"Error removing employee: {str(e)}")


def get_employee_by_id(db: Session, employee_id: str) -> Employee:
    try:
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve employee: {str(e)}")

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
        raise DatabaseError(f"Failed to search employees by prefix: {str(e)}")


