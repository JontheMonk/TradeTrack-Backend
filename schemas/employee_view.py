from pydantic import BaseModel

class EmployeeView(BaseModel):
    employee_id: str
    name: str
    role: str