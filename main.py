"""
Application entrypoint for the TradeTrack backend API.

Initializes the FastAPI app, configures logging, registers global exception
handlers, and mounts all HTTP routers.
"""

import logging
from fastapi import FastAPI
from routers import employee
from core.error_handler import add_exception_handlers

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TradeTrack API",
    description="Backend service for facial recognition clock-in and employee management.",
    version="1.0.0",
)

# Global exception handlers
add_exception_handlers(app)

# Routers
app.include_router(employee.router, prefix="/employees", tags=["Employees"])
