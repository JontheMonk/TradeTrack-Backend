# core/settings.py

from dataclasses import dataclass

@dataclass
class Settings:
    """
    Minimal configuration object.

    Tests can override fields by calling:
        Settings(admin_api_key="test")
    """

    # Database
    database_url: str = "sqlite:///:memory:"

    # Face recognition
    face_match_threshold: float = 0.5
    embedding_dim: int = 512

    # Security
    admin_api_key: str = "dev-key"
    
    #Environment
    env : str = "dev"
