from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from core.settings import Settings
from core.security import build_admin_required
from core.error_handler import add_exception_handlers
from core.logging import init_logging
from core.request_id import RequestIDMiddleware
from data.database import make_get_session
from routers.employee import create_employee_router
from routers.health import router as health_router
from routers.clock import create_clock_router



def create_app(
    settings: Settings | None = None,
    engine=None,
    get_session_maker=make_get_session,
):
    """
    Application factory for the TradeTrack backend API.

    This function constructs a fully configured FastAPI application instance,
    wiring together:

        • Database engine + session dependency
        • Global exception handlers
        • CORS configuration
        • Rate limiting (SlowAPI)
        • Security dependencies (admin-only endpoints)
        • Feature routers (employees)

    The factory pattern ensures:
        • Testability — tests inject custom settings, engines, and sessions
        • Environment flexibility — dev/test/prod all share the same entrypoint
        • Clean separation of concerns — no global state or hard-coded behavior

    Parameters
    ----------
    settings : Settings | None
        Explicit application configuration (DB URL, thresholds, admin key).
        If omitted, a new Settings() instance is created automatically.

    engine : sqlalchemy.Engine | None
        Optional SQLAlchemy engine. Tests inject a custom in-memory engine.
        In production, the engine is created from settings.database_url.

    get_session_maker : callable
        Factory that produces a FastAPI-compatible get_session dependency.
        Tests override this to ensure isolated DB state per test.

    Returns
    -------
    FastAPI
        A fully initialized FastAPI application, ready to be served by Uvicorn.
    """
    # -----------------------------------------------------------------------
    # Resolve settings and database engine
    # -----------------------------------------------------------------------
    if settings is None:
        settings = Settings()

    # -----------------------------------------------------------------------
    # Initialize structured logging
    # Uses settings.env to decide JSON vs pretty logs.
    # -----------------------------------------------------------------------
    init_logging(settings.env)

    if engine is None:
        engine = create_engine(settings.database_url, future=True)

    # Build the FastAPI DB session dependency
    get_session = get_session_maker(engine)

    # -----------------------------------------------------------------------
    # Base FastAPI application
    # -----------------------------------------------------------------------
    app = FastAPI()

    # ---------------------------
    # Request ID middleware (MUST come first so logs have the ID)
    # ---------------------------
    app.add_middleware(RequestIDMiddleware)

    # -----------------------------------------------------------------------
    # Global exception handlers
    #
    # This ensures all AppException subclasses return structured JSON and
    # unexpected exceptions return a consistent 500 error envelope.
    # -----------------------------------------------------------------------
    add_exception_handlers(app)

    # -----------------------------------------------------------------------
    # CORS middleware
    #
    # Currently wide-open for development. In production, restrict origins.
    # -----------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------------
    # Rate limiting
    #
    # SlowAPI uses ASGI middleware + an app.state.limiter reference. Routes
    # define rate limits via decorators (@limiter.limit).
    # -----------------------------------------------------------------------
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # -----------------------------------------------------------------------
    # Security dependencies
    #
    # admin_required enforces the X-Admin-Key header on sensitive routes.
    # -----------------------------------------------------------------------
    admin_required = build_admin_required(settings)

    # -----------------------------------------------------------------------
    # Route registration
    #
    # Each router is created with its own dependencies injected to avoid
    # global state and improve testability.
    # -----------------------------------------------------------------------
    employee_router = create_employee_router(
        settings=settings,
        limiter=limiter,
        get_session=get_session,
        admin_required=admin_required,
    )

    clock_router = create_clock_router(
        limiter=limiter,
        get_session=get_session,
    )

    app.include_router(employee_router, prefix="/employees")

    app.include_router(clock_router, prefix="/clock")

    app.include_router(health_router)

    return app


# Uvicorn entrypoint for local development and production
app = create_app()
