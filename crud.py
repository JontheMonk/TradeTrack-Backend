from sqlalchemy.orm import Session
from models import Employee
from schemas import FaceEmbedding
from typing import List
from core.errors import (
    EmployeeAlreadyExists,
    EmployeeNotFound,
    DatabaseError
)

def add_employee(db: Session, face: FaceEmbedding):
    if db.query(Employee).filter(Employee.employee_id == face.employee_id).first():
        raise EmployeeAlreadyExists()

    try:
        emp = Employee(**face.dict())
        db.add(emp)
        db.commit()
    except Exception as e:
        raise DatabaseError(f"Error adding employee: {str(e)}")


def update_employee(db: Session, face: FaceEmbedding):
    emp = db.query(Employee).filter(Employee.employee_id == face.employee_id).first()
    if not emp:
        raise EmployeeNotFound()

    try:
        emp.name = face.name
        emp.embedding = face.embedding
        emp.role = face.role
        db.commit()
    except Exception as e:
        raise DatabaseError(f"Error updating employee: {str(e)}")


def remove_employee_by_id(db: Session, employee_id: str):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise EmployeeNotFound()

    try:
        db.delete(emp)
        db.commit()
    except Exception as e:
        raise DatabaseError(f"Error removing employee: {str(e)}")


def get_all_employees(db: Session) -> List[Employee]:
    try:
        return db.query(Employee).all()
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve employees: {str(e)}")
