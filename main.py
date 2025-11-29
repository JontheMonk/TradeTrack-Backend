from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from core.settings import Settings
from core.security import build_admin_required
from core.error_handler import add_exception_handlers
from data.database import make_get_session
from routers.employee import create_employee_router


def create_app(
    settings: Settings | None = None,
    engine=None,
    get_session_maker=make_get_session,
):
    if settings is None:
        settings = Settings()

    if engine is None:
        engine = create_engine(settings.database_url, future=True)

    # ---------------------------
    # DB dependency
    # ---------------------------
    get_session = get_session_maker(engine)

    # ---------------------------
    # FastAPI app
    # ---------------------------
    app = FastAPI()

    # ---------------------------
    # Middleware, error handling
    # ---------------------------
    add_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------------------------
    # Rate limiting
    # ---------------------------
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # ---------------------------
    # Security dependencies
    # ---------------------------
    admin_required = build_admin_required(settings)

    # ---------------------------
    # Routers
    # ---------------------------
    employee_router = create_employee_router(
        settings=settings,
        limiter=limiter,
        get_session=get_session,
        admin_required=admin_required,
    )

    app.include_router(employee_router, prefix="/employees")

    return app


# Uvicorn entrypoint
app = create_app()
