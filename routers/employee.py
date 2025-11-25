"""
Employee-related API endpoints.

Provides routes for employee registration, face verification,
and prefix-based employee search.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_session
from schemas import EmployeeInput, VerifyFaceRequest, EmployeeResult
from services.verify_face import verify_face_embedding
from services.register_employee import register_employee
from services.search_employees import search_employees_by_prefix
from core.api_response import ApiResponse, ok

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post("/", response_model=ApiResponse[None])
def add_employee(employee: EmployeeInput, db: Session = Depends(get_session)):
    """Register a new employee with normalized face embedding."""
    register_employee(employee, db)
    return ok()


@router.post("/verify", response_model=ApiResponse[None])
def verify_face(req: VerifyFaceRequest, db: Session = Depends(get_session)):
    """Verify a face embedding against a stored employee embedding."""
    verify_face_embedding(req, db)
    return ok()


@router.get("/search", response_model=ApiResponse[List[EmployeeResult]])
def get_employees(
    prefix: str = Query(..., min_length=3),
    db: Session = Depends(get_session)
):
    """Search for employees whose name or ID begins with a prefix."""
    results = search_employees_by_prefix(prefix, db)
    return ok(results)
