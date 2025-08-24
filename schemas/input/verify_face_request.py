from pydantic import BaseModel, Field
from typing import List
from core.settings import settings

class VerifyFaceRequest(BaseModel):
    employee_id: str
    embedding: List[float] = Field(..., min_items=settings.embedding_dim, max_items=settings.embedding_dim)

