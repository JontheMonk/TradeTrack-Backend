import logging
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from core.errors import AppException, ErrorCode
from core.api_response import fail

log = logging.getLogger(__name__)

def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exc(_: Request, exc: AppException):
        log.warning(f"Handled AppException: {exc.code} - {exc.message}")

        if exc.__cause__:
            log.warning(
                "Caused by:\n" +
                "".join(traceback.format_exception(type(exc.__cause__), exc.__cause__, exc.__cause__.__traceback__))
            )

        return JSONResponse(
            status_code=exc.http_status,
            content=fail(exc.code, exc.message).model_dump()
        )

    @app.exception_handler(Exception)
    async def handle_unknown(_: Request, exc: Exception):
        log.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=fail(ErrorCode.UNKNOWN_ERROR, "Unexpected server error").model_dump()
        )
