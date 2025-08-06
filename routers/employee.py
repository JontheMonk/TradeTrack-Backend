from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from schemas import EmployeeInput, VerifyFaceRequest, EmployeeSearchResult
from core.errors import map_app_exception
from services.verify_face_service import verify_face_embedding
from services.employee_service import register_employee, search_employees_by_prefix
from typing import List

router = APIRouter()


@router.post("/add-employee", status_code=200)
def add_employee(employee: EmployeeInput, db: Session = Depends(get_db)):
    try:
        register_employee(employee, db)
    except Exception as e:
        raise map_app_exception(e)


@router.post("/verify-face", status_code=200)
def verify_face(req: VerifyFaceRequest, db: Session = Depends(get_db)):
    try:
        verify_face_embedding(req, db)
    except Exception as e:
        raise map_app_exception(e)


@router.get("/employees", response_model=List[EmployeeSearchResult])
def get_employees(prefix: str = Query(..., min_length=3), db: Session = Depends(get_db)):
    try:
        return search_employees_by_prefix(prefix, db)
    except Exception as e:
        raise map_app_exception(e)
