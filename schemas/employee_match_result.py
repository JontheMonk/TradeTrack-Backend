from pydantic import BaseModel
from schemas import EmployeeView

class EmployeeMatchResult(BaseModel):
    employee: EmployeeView
    score: float