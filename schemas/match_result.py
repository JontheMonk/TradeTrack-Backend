from pydantic import BaseModel

class MatchResult(BaseModel):
    employee_id: str
    name: str
    role: str
    score: float