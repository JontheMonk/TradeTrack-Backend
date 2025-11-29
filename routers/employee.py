"""
Employee-related API endpoints.

Provides routes for:
    - employee registration (admin-only)
    - face verification (public, rate-limited)
    - prefix-based employee search (public, rate-limited)
"""

from typing import List

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from slowapi import Limiter

from core.api_response import ApiResponse, ok
from core.settings import Settings
from schemas import EmployeeInput, VerifyFaceRequest, EmployeeResult
from services.verify_face import verify_face_embedding
from services.register_employee import register_employee
from services.search_employees import search_employees_by_prefix


def create_employee_router(
    settings: Settings,
    limiter: Limiter,
    get_session,
    admin_required,
) -> APIRouter:
    """
    Build a fresh APIRouter for employee endpoints, wired to:

        • settings       – app configuration (reserved for future use)
        • limiter        – SlowAPI limiter instance
        • get_session    – FastAPI DB dependency
        • admin_required – dependency enforcing X-Admin-Key

    This keeps the router completely decoupled from global state.
    """
    router = APIRouter(tags=["Employees"])

    # ------------------------------------------------------------------
    # POST /employees/  → Admin-only registration
    # ------------------------------------------------------------------
    @router.post(
        "/",
        response_model=ApiResponse[None],
        dependencies=[Depends(admin_required)],
    )
    def add_employee(
        employee: EmployeeInput,
        db: Session = Depends(get_session),
    ):
        """
        Register a new employee with normalized face embedding.
        Requires a valid X-Admin-Key header.
        """
        register_employee(employee, db)
        return ok()

    # ------------------------------------------------------------------
    # POST /employees/verify  → Public, rate-limited
    # ------------------------------------------------------------------
    @router.post("/verify", response_model=ApiResponse[None])
    @limiter.limit("10/second")
    def verify_face(
        request: Request,  # required for SlowAPI
        req: VerifyFaceRequest,
        db: Session = Depends(get_session)
    ):
        """
        Verify a submitted face embedding against the stored employee embedding.
        Public endpoint, protected by rate limiting.
        """
        verify_face_embedding(req, db, settings=settings)
        return ok()

    # ------------------------------------------------------------------
    # GET /employees/search  → Public, rate-limited
    # ------------------------------------------------------------------
    @router.get("/search", response_model=ApiResponse[List[EmployeeResult]])
    @limiter.limit("5/second")
    def get_employees(
        request: Request,  # required for SlowAPI
        prefix: str = Query(..., min_length=3),
        db: Session = Depends(get_session),
    ):
        """
        Search for employees whose name or ID begins with a given prefix.
        """
        results = search_employees_by_prefix(prefix, db)
        return ok(results)

    return router
