# core/logging.py

import structlog
import logging
from logging.config import dictConfig

def init_logging(env: str = "dev"):
    """
    Initialize structured logging.
    - dev: pretty console logs + DEBUG level
    - prod: JSON logs + INFO level
    """

    # Set Python logging level based on environment
    python_log_level = "DEBUG" if env == "dev" else "INFO"
    structlog_log_level = logging.DEBUG if env == "dev" else logging.INFO

    dictConfig({
        "version": 1,
        "formatters": {
            "plain": {"format": "%(message)s"},
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
            }
        },
        "root": {
            "handlers": ["default"],
            "level": python_log_level,
        },
    })

    # Renderer selection (pretty vs json)
    renderer = (
        structlog.dev.ConsoleRenderer()
        if env == "dev"
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(structlog_log_level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
