from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class EmployeeInput(BaseModel):
    """
    Schema for incoming employee registration requests.

    This model defines the payload expected when creating or
    updating an employee in the system.

    Fields:
        employee_id (str):
            Unique identifier for the employee. Typically a UUID or
            database-generated string, but the format is flexible.

        name (str):
            Human-readable employee name. Used for display in the
            frontend dashboard.

        embedding (List[float]):
            Face embedding vector produced by the recognition model.
            Must contain exactly 512 floating-point values, enforced
            via Pydantic `min_items` and `max_items`.

        role (Optional[Literal["Admin", "Employee"]]):
            Optional authorization role for the employee.

            If omitted, the service layer automatically assigns the default role
            ``"Employee"``. The role controls which UI actions or API endpoints the
            account may access. Admin users may perform privileged actions such as
            registering employees or viewing analytics, while regular employees have
            restricted permissions.

            Acceptable values:
                - "Admin"
                - "Employee"

            When ``None`` is provided, no validation error is raised; the service
            will apply the default role.

    """

    employee_id: str
    name: str
    embedding: List[float] = Field(..., min_length=512, max_length=512)
    role: Optional[Literal["Admin", "Employee"]] = None
