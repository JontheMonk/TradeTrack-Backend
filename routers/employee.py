from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas import FaceRecord, QueryEmbedding, MatchResult, SuccessResponse
from core.errors import map_app_exception
from services.face_match_service import get_best_match
from services.face_registration_service import register_face

router = APIRouter()


@router.post("/add-face", response_model=SuccessResponse)
def add_face(face: FaceRecord, db: Session = Depends(get_db)):
    try:
        emp = register_face(face, db)
        return SuccessResponse(
            message=f"Employee {emp.name} added",
            data={
                "employee_id": emp.employee_id,
                "name": emp.name,
                "role": emp.role
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

