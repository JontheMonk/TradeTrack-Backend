from sqlalchemy.orm import Session
from typing import List
from models import Employee
from schemas import EmployeeInput, EmployeeResult
from core.vector_utils import normalize_vector
import crud

def register_employee(employee: EmployeeInput, db: Session) -> EmployeeResult:
    normalized = normalize_vector(employee.embedding)
    payload = employee.model_copy(update={"embedding": normalized.tolist()})

    saved: Employee = crud.add_employee(db, payload)

    return EmployeeResult(
        employee_id=saved.employee_id,
        name=saved.name,
        role=saved.role,
    )

def search_employees_by_prefix(prefix: str, db: Session) -> List[EmployeeResult]:
    employees: List[Employee] = crud.get_employees_by_prefix(db, prefix)
    return [
        EmployeeResult(
            employee_id=emp.employee_id,
            name=emp.name,
            role=emp.role
        )
        for emp in employees
    ]
