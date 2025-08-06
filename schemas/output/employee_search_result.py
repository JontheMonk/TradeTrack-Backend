from pydantic import BaseModel

class EmployeeSearchResult(BaseModel):
    employee_id: str
    name: str
    role: str
