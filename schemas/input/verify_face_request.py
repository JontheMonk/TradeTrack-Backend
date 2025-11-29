from pydantic import BaseModel
from typing import List

class VerifyFaceRequest(BaseModel):
    employee_id: str
    embedding: List[float]
