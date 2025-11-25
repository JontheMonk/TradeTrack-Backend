from pydantic import BaseModel, Field
from typing import List, Literal

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

        role (Literal["admin", "employee"]):
            Authorization role for the employee. Determines what UI
            actions or API calls the account can perform.
    """

    employee_id: str
    name: str
    embedding: List[float] = Field(..., min_items=512, max_items=512)
    role: Literal["admin", "employee"]
