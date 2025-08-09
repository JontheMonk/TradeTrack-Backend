from pydantic import BaseModel, Field
from typing import List, Literal

class EmployeeInput(BaseModel):
    employee_id: str
    name: str
    embedding: List[float] = Field(..., min_items=512, max_items=512)
    role: Literal["admin", "employee"]
