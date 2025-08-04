from typing import List
from sqlalchemy.orm import Session
import crud
from models import Employee
from schemas import QueryEmbedding, EmployeeMatchResult, EmployeeView
from core.vector_utils import normalize_vector, cosine_similarity
from core.errors import NoEmployeesException, FaceConfidenceTooLow
from core.settings import settings

def get_best_match(query: QueryEmbedding, db: Session) -> EmployeeMatchResult:
    employees: List[Employee] = crud.get_all_employees(db)

    if not employees:
        raise NoEmployeesException()

    query_vec = normalize_vector(query.embedding)
    best_employee = None
    best_score = -1.0

    for emp in employees:
        score = cosine_similarity(query_vec, emp.embedding)
        if score > best_score:
            best_score = score
            best_employee = emp

    if best_score < settings.face_match_threshold or best_employee is None:
        raise FaceConfidenceTooLow()

    return EmployeeMatchResult(
        employee=EmployeeView(
            employee_id=best_employee.employee_id,
            name=best_employee.name,
            role=best_employee.role
        ),
        score=best_score
    )
