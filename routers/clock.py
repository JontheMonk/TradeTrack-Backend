"""
Clock-in/clock-out API endpoints.

Provides routes for:
    - clock in (start shift)
    - clock out (end shift)
    - status check (are they clocked in?)
"""

from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from structlog import get_logger

from core.api_response import ApiResponse, ok
from schemas import ClockStatus
from services.clock_service import clock_in, clock_out, get_clock_status


log = get_logger()


def create_clock_router(
    limiter: Limiter,
    get_session,
) -> APIRouter:
    """
    Build a fresh APIRouter for clock endpoints, wired to:

        • limiter     – SlowAPI limiter instance
        • get_session – FastAPI DB dependency

    These endpoints are public (no admin key) but rate-limited.
    """
    router = APIRouter(tags=["Clock"])

    # ------------------------------------------------------------------
    # POST /clock/{employee_id}/in  → Clock in
    # ------------------------------------------------------------------
    @router.post("/{employee_id}/in", response_model=ApiResponse[None])
    @limiter.limit("10/minute")
    def do_clock_in(
        request: Request,
        employee_id: str = Path(..., min_length=1),
        db: Session = Depends(get_session),
    ):
        """
        Clock in an employee. Fails if already clocked in.
        """
        log.info("clock_in_request", employee_id=employee_id)

        clock_in(employee_id, db)

        log.info("clock_in_complete", employee_id=employee_id)

        return ok()

    # ------------------------------------------------------------------
    # POST /clock/{employee_id}/out  → Clock out
    # ------------------------------------------------------------------
    @router.post("/{employee_id}/out", response_model=ApiResponse[None])
    @limiter.limit("10/minute")
    def do_clock_out(
        request: Request,
        employee_id: str = Path(..., min_length=1),
        db: Session = Depends(get_session),
    ):
        """
        Clock out an employee. Fails if not clocked in.
        """
        log.info("clock_out_request", employee_id=employee_id)

        clock_out(employee_id, db)

        log.info("clock_out_complete", employee_id=employee_id)

        return ok()

    # ------------------------------------------------------------------
    # GET /clock/{employee_id}/status  → Check clock status
    # ------------------------------------------------------------------
    @router.get("/{employee_id}/status", response_model=ApiResponse[ClockStatus])
    @limiter.limit("30/minute")
    def get_status(
        request: Request,
        employee_id: str = Path(..., min_length=1),
        db: Session = Depends(get_session),
    ):
        """
        Check if an employee is currently clocked in.
        """
        log.info("clock_status_request", employee_id=employee_id)

        status = get_clock_status(employee_id, db)

        log.info(
            "clock_status_response",
            employee_id=employee_id,
            is_clocked_in=status.is_clocked_in,
        )

        return ok(status)

    return router