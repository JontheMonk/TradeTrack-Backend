from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas import FaceRecord, QueryEmbedding, EmployeeMatchResult, EmployeeView
from core.errors import map_app_exception
from services.face_match_service import get_best_match
from services.employee_registration_service import register_employee

router = APIRouter()


@router.post("/add-face", response_model=EmployeeView)
def add_face(face: FaceRecord, db: Session = Depends(get_db)):
    try:
        return register_employee(face, db)
    except Exception as e:
        raise map_app_exception(e)



@router.post("/match-face", response_model=EmployeeMatchResult)
def match_face(query: QueryEmbedding, db: Session = Depends(get_db)):
    try:
        return get_best_match(query.embedding, db)

    except Exception as e:
        raise map_app_exception(e)

