# services/face_match_service.py

from typing import List
from sqlalchemy.orm import Session
import crud
from models import Employee
from schemas import QueryEmbedding, MatchResult
from core.vector_utils import normalize_vector, cosine_similarity
from core.errors import NoEmployeesException, FaceConfidenceTooLow
from core.settings import settings

def get_best_match(query: QueryEmbedding, db: Session) -> MatchResult:
    employees: List[Employee] = crud.get_all_employees(db)

    if not employees:
        raise NoEmployeesException()

    query_vec = normalize_vector(query.embedding)
    best_match = None
    best_score = -1.0

    for emp in employees:
        score = cosine_similarity(query_vec, emp.embedding)
        if score > best_score:
            best_score = score
            best_match = MatchResult(
                employee_id=emp.employee_id,
                name=emp.name,
                role=emp.role,
                score=score
            )

    if best_score < settings.face_match_threshold:
        raise FaceConfidenceTooLow()

    return best_match
