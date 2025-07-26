from sqlalchemy.orm import Session
from models import Employee
from schemas import FaceEmbedding
from typing import List
from core.operation_result import VoidResult, OperationResult
from core.error_codes import ErrorCode

def add_employee(db: Session, face: FaceEmbedding) -> VoidResult:
    existing = db.query(Employee).filter(Employee.employee_id == face.employee_id).first()
    if existing:
        return VoidResult.fail("Employee already exists", code=ErrorCode.EMPLOYEE_ALREADY_EXISTS)

    try:
        emp = Employee(**face.dict())
        db.add(emp)
        db.commit()
        return VoidResult.ok(f"Employee {face.name} added")
    except Exception as e:
        return VoidResult.fail(f"Error adding employee: {str(e)}", code=ErrorCode.DB_ERROR)


def update_employee(db: Session, face: FaceEmbedding) -> VoidResult:
    emp = db.query(Employee).filter(Employee.employee_id == face.employee_id).first()
    if not emp:
        return VoidResult.fail("Employee not found", code=ErrorCode.EMPLOYEE_NOT_FOUND)

    try:
        emp.name = face.name
        emp.embedding = face.embedding
        emp.role = face.role
        db.commit()
        return VoidResult.ok(f"Employee {face.name} updated")
    except Exception as e:
        return VoidResult.fail(f"Error updating employee: {str(e)}", code=ErrorCode.DB_ERROR)



def remove_employee_by_id(db: Session, employee_id: str) -> VoidResult:
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        return VoidResult.fail("Employee not found", code=ErrorCode.EMPLOYEE_NOT_FOUND)

    try:
        db.delete(emp)
        db.commit()
        return VoidResult.ok(f"Employee {employee_id} removed")
    except Exception as e:
        return VoidResult.fail(
            f"Error removing employee: {str(e)}",
            code=ErrorCode.DB_ERROR
        )


def get_all_employees(db: Session) -> OperationResult[List[Employee]]:
    try:
        employees = db.query(Employee).all()
        return OperationResult.ok(data=employees)
    except Exception as e:
        return OperationResult.fail(
            f"Failed to retrieve employees: {str(e)}",
            code=ErrorCode.DB_ERROR
        )
