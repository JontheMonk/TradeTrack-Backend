# core/settings.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    This class defines all configurable runtime settings for the backend.
    Values are automatically read from:
      • Environment variables
      • A `.env` file (if present)
      • Any overrides passed to Settings()

    Attributes:
        database_url (str):
            Full PostgreSQL connection URL used by SQLAlchemy/psycopg2.
            Must be provided; no default is set.

        face_match_threshold (float):
            Minimum cosine similarity required to consider two embeddings
            a valid face match. Lower values make matching more lenient.
            Default: 0.5

        embedding_dim (int):
            Expected dimensionality of face embeddings produced by the
            recognition model (e.g., 512 for InsightFace-based models).
            Used for validation and consistency checks.

    Pydantic automatically performs type validation and ensures that
    invalid configuration values fail fast during application startup.
    """
    database_url: str = "sqlite:///:memory:"  # default for tests
    face_match_threshold: float = 0.5
    embedding_dim: int = 512


# Instantiate global settings for use throughout the app.
settings = Settings()
