"""
Health check endpoint.

Used to verify that the API process is running and responding to HTTP requests.
This endpoint is intentionally lightweight and does not depend on the database
or authentication.
"""

from fastapi import APIRouter
from core.api_response import ok, ApiResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=ApiResponse[None])
def health():
    """
    Returns a simple success response if the service is alive.
    """
    return ok()
