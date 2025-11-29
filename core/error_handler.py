# core/error_handler.py

import structlog
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from core.errors import AppException, ErrorCode
from core.api_response import fail

log = structlog.get_logger()


def add_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for the FastAPI application.

    Provides:
      • Structured handler for AppException (expected domain errors)
      • Catch-all structured handler for unexpected failures

    All logs are emitted through structlog so they become JSON in production
    and pretty in development.
    """

    @app.exception_handler(AppException)
    async def handle_app_exc(request: Request, exc: AppException):
        """
        Handle expected, domain-level application errors.

        Examples:
        - Employee not found
        - Duplicate employee ID
        - Face confidence too low
        """

        log.warning(
            "app_exception",
            path=request.url.path,
            method=request.method,
            status=exc.http_status,
            code=str(exc.code),
            message=exc.message,
        )

        # If chained exception exists, log the traceback of the cause
        if exc.__cause__:
            log.warning(
                "app_exception_cause",
                cause="".join(
                    traceback.format_exception(
                        type(exc.__cause__),
                        exc.__cause__,
                        exc.__cause__.__traceback__,
                    )
                ),
            )

        return JSONResponse(
            status_code=exc.http_status,
            content=fail(exc.code, exc.message).model_dump(),
        )

    @app.exception_handler(Exception)
    async def handle_unknown(request: Request, exc: Exception):
        """
        Handle unexpected runtime errors.

        These include:
        - bugs in code paths
        - broken dependencies
        - DB connection failures
        """

        log.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            traceback="".join(
                traceback.format_exception(
                    type(exc), exc, exc.__traceback__
                )
            ),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=fail(
                ErrorCode.UNKNOWN_ERROR,
                "Unexpected server error",
            ).model_dump(),
        )
