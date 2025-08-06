from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from schemas import FaceRecord, VerifyFaceRequest, SuccessResponse, EmployeeSearchResult
from core.errors import map_app_exception
from services.verify_face_service import verify_face_embedding
from services.employee_service import register_employee, search_employees_by_prefix
from typing import List

router = APIRouter()


@router.post("/add-face", response_model=SuccessResponse)
def add_face(face: FaceRecord, db: Session = Depends(get_db)):
    try:
        register_employee(face, db)
        return SuccessResponse()
    except Exception as e:
        raise map_app_exception(e)


@router.post("/verify-face", response_model=SuccessResponse)
def verify_face(req: VerifyFaceRequest, db: Session = Depends(get_db)):
    try:
        verify_face_embedding(req, db)
        return SuccessResponse()
    except Exception as e:
        raise map_app_exception(e)


@router.get("/employees", response_model=List[EmployeeSearchResult])
def get_employees(prefix: str = Query(..., min_length=3), db: Session = Depends(get_db)):
    try:
        return search_employees_by_prefix(prefix, db)
    except Exception as e:
        raise map_app_exception(e)
