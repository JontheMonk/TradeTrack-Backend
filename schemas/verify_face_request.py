from pydantic import BaseModel, Field
from typing import List

class VerifyFaceRequest(BaseModel):
    employee_id: str
    embedding: List[float] = Field(..., min_items=512, max_items=512)

    
    employee_id: str
    embedding: List[float]
