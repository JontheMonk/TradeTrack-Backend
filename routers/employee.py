from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from schemas import EmployeeInput, VerifyFaceRequest, EmployeeResult, VerifyFaceResponse
from services.verify_face_service import verify_face_embedding
from services.employee_service import register_employee, search_employees_by_prefix
from core.api_response import ApiResponse, ok 

router = APIRouter()

@router.post("/add-employee", response_model=ApiResponse[EmployeeResult])
def add_employee(employee: EmployeeInput, db: Session = Depends(get_db)):
    emp = register_employee(employee, db)
    return ok(emp)

@router.post("/verify-face", response_model=ApiResponse[VerifyFaceResponse])
def verify_face(req: VerifyFaceRequest, db: Session = Depends(get_db)):
    result = verify_face_embedding(req, db)
    return ok(result)

@router.get("/employees", response_model=ApiResponse[List[EmployeeResult]])
def get_employees(prefix: str = Query(..., min_length=3), db: Session = Depends(get_db)):
    results = search_employees_by_prefix(prefix, db)
    return ok(results)
