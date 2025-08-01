from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from db import get_db
import crud
from models import Employee
from schemas import FaceEmbedding, QueryEmbedding, MatchResult
from core.settings import settings
from core.errors import AppException, map_app_exception
from core.vector_utils import normalize_vector, cosine_similarity

router = APIRouter()


@router.post("/add-face")
def add_face(face: FaceEmbedding, db: Session = Depends(get_db)):
    if len(face.embedding) != 512:
        raise HTTPException(status_code=400, detail="Embedding must be 512 dimensions")

    try:
        normalized = normalize_vector(face.embedding)
        face.embedding = normalized.tolist()
        crud.add_employee(db, face)
        return {"status": "success", "message": f"Employee {face.name} added"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except AppException as e:
        raise map_app_exception(e)

    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected server error")


@router.post("/match-face", response_model=Optional[MatchResult])
def match_face(query: QueryEmbedding, db: Session = Depends(get_db)):
    try:
        employees = crud.get_all_employees(db)
    except AppException as e:
        raise map_app_exception(e)
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected server error")

    if not employees:
        raise HTTPException(status_code=404, detail="No embeddings found")

    try:
        best_match, best_score = find_best_match(query.embedding, employees)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if best_score < settings.face_match_threshold:
        raise HTTPException(status_code=404, detail="No matching face found")

    return best_match


def find_best_match(query_embedding: List[float], employees: List[Employee]) -> Tuple[Optional[MatchResult], float]:
    query_vec = normalize_vector(query_embedding)
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

    return best_match, best_score
