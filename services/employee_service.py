from sqlalchemy.orm import Session
from schemas import EmployeeInput, EmployeeSearchResult
from core.vector_utils import normalize_vector
import crud 
from typing import List
from models import Employee


def register_employee(employee: EmployeeInput, db: Session) -> None:
    normalized = normalize_vector(employee.embedding)
    employee.embedding = normalized.tolist()

    crud.add_employee(db, employee)

def search_employees_by_prefix(prefix: str, db: Session) -> List[EmployeeSearchResult]:
    employees: List[Employee] = crud.get_employees_by_prefix(db, prefix)
    return [
        EmployeeSearchResult(
            employee_id=emp.employee_id,
            name=emp.name,
            role=emp.role
        ) for emp in employees
    ]

