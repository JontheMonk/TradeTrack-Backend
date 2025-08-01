from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
import crud
from schemas import FaceEmbedding, QueryEmbedding, MatchResult, SuccessResponse
from core.settings import settings
from core.errors import map_app_exception
from core.vector_utils import normalize_vector
from services.face_match_service import get_best_match

router = APIRouter()


@router.post("/add-face", response_model=SuccessResponse)
def add_face(face: FaceEmbedding, db: Session = Depends(get_db)):
    try:
        normalized = normalize_vector(face.embedding)
        face.embedding = normalized.tolist()
        crud.add_employee(db, face)

        return SuccessResponse(
            message=f"Employee {face.name} added",
            data={
                "employee_id": face.employee_id,
                "name": face.name,
                "role": face.role
            }
        )

    except Exception as e:
        raise map_app_exception(e)



@router.post("/match-face", response_model=MatchResult)
def match_face(query: QueryEmbedding, db: Session = Depends(get_db)):
    try:
        return get_best_match(query.embedding, db)

    except Exception as e:
        raise map_app_exception(e)

