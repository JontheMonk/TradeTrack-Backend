from pydantic import BaseModel

class EmployeeResult(BaseModel):
    employee_id: str
    name: str
    role: str
