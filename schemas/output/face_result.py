from pydantic import BaseModel

class FaceResult(BaseModel):
    employee_id: str
    score: float