from pydantic import BaseModel

class VerifyFaceResponse(BaseModel):
    employee_id: str 
    score: float
    threshold: float
