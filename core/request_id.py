# core/request_id.py

import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Attach a per-request ID to structlog's contextvars.
    """

    async def dispatch(self, request, call_next):
        request_id = uuid.uuid4().hex

        # Attach request ID to request state
        request.state.request_id = request_id

        # Bind request ID to structlog context
        structlog.contextvars.bind_contextvars(request_id=request_id)

        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.clear_contextvars()

        # Add header for debugging / tracing
        response.headers["X-Request-ID"] = request_id
        return response
