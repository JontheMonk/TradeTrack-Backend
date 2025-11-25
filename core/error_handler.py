import logging
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from core.errors import AppException, ErrorCode
from core.api_response import fail

log = logging.getLogger(__name__)

def add_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for the FastAPI application.

    This attaches:
      • A handler for AppException — your controlled, domain-level errors.
      • A fallback handler for all other Exceptions — unexpected failures.

    The goal is to ensure all errors return a consistent JSON envelope
    and that logs contain enough data to debug failures quickly.
    """

    @app.exception_handler(AppException)
    async def handle_app_exc(request: Request, exc: AppException):
        """
        Handle known application-level exceptions.

        These represent expected, validated failure states such as:
        - Face confidence too low
        - Employee not found
        - Duplicate registration

        Logs a warning including:
          • HTTP method + path
          • App-specific error code
          • Message
          • HTTP status

        If the exception was raised with a cause (via "raise X from Y"),
        the full traceback of the original cause is logged as well.
        """
        log.warning(
            f"Handled AppException "
            f"[status={exc.http_status}] "
            f"{request.method} {request.url.path} "
            f"{exc.code} - {exc.message}"
        )

        # Log the original cause if chained (e.g., raise A from B)
        if exc.__cause__:
            log.warning(
                "Caused by:\n" +
                "".join(traceback.format_exception(
                    type(exc.__cause__),
                    exc.__cause__,
                    exc.__cause__.__traceback__
                ))
            )

        # Return standardized failure envelope
        return JSONResponse(
            status_code=exc.http_status,
            content=fail(exc.code, exc.message).model_dump()
        )

    @app.exception_handler(Exception)
    async def handle_unknown(request: Request, exc: Exception):
        """
        Catch-all handler for unexpected exceptions.

        These represent bugs or infrastructure issues, not domain errors.
        - Database connection failures
        - Buggy logic
        - Unhandled edge cases
        - Bad imports, indexing errors, etc.

        Logs the full traceback and returns a generic 500 error with a
        consistent failure response format.
        """
        log.exception(
            f"Unhandled exception during {request.method} {request.url.path}",
            exc_info=exc
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=fail(
                ErrorCode.UNKNOWN_ERROR,
                "Unexpected server error"
            ).model_dump()
        )
