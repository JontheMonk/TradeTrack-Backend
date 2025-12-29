from pydantic import BaseModel

class EmployeeResult(BaseModel):
    """
    Lightweight representation of an employee returned from read-only queries.

    This schema is used for:
      • prefix searches
      • listing employees
      • lookup results
      • any response where full embedding data is not required

    Fields:
        employee_id (str):
            Unique identifier of the employee.

        name (str):
            Human-readable display name.

        role (str):
            The user’s authorization role (e.g., "Admin" or "Employee").
            Returned as a plain string for convenience in frontend handling.
    """

    employee_id: str
    name: str
    role: str
