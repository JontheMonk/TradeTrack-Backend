# core/settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    face_match_threshold: float = 0.5

settings = Settings()
