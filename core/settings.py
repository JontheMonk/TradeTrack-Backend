"""
Application configuration — clean, explicit, and production-safe.

This module provides a single `Settings` object used by the entire backend.
Configuration values are loaded in this order (pydantic-settings v2 behavior):

    1. Environment variables (Render / AWS / system env)
    2. `.env` file (local development only)
    3. Default values defined in the Settings class

Design philosophy:
    • No hidden defaults for critical values (DB URL, admin key, env)
    • Fail fast if configuration is missing or wrong
    • Minimal surface area — no unnecessary validators or logic
    • Tests override Settings(...) and inject their own engine, so runtime
      settings never influence the test database
"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Strongly-typed configuration object for the entire application.

    Required fields:
        - database_url    (str)
        - admin_api_key   (str)
        - env             ("dev" | "test" | "prod")

    These MUST be provided by environment variables (or `.env` locally).
    If missing, pydantic raises a clear ValidationError immediately on import,
    preventing the application from starting with bad configuration.

    Optional fields with defaults:
        - face_match_threshold
        - embedding_dim

    These are stable, non-secret constants and safe to default.
    """

    # ------------------------------------------------------------------
    # Required — must be provided via env var or .env
    # ------------------------------------------------------------------
    database_url: str
    admin_api_key: str
    env: Literal["dev", "test", "prod"]

    # ------------------------------------------------------------------
    # Optional — safe, stable defaults
    # ------------------------------------------------------------------
    face_match_threshold: float = 0.5
    embedding_dim: int = 512

    # ------------------------------------------------------------------
    # Settings behavior (Pydantic v2)
    # ------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",               # Load .env automatically in local dev
        env_file_encoding="utf-8",     # Optional, UTF-8 is default
        extra="ignore",                 # Ignore extra/unknown env vars
        case_sensitive=False,           # Typical for environment variables
    )


# Global singleton — imported everywhere as `from core.settings import settings`
# This instantiation immediately validates configuration and throws fast
# if required values are missing.
settings = Settings()
