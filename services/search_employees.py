from typing import List
from sqlalchemy.orm import Session
from schemas import EmployeeResult
import employee_repository


def search_employees_by_prefix(prefix: str, db: Session) -> List[EmployeeResult]:
    """
    Search for employees whose ID or name begins with a given prefix.

    This service performs a partial lookup intended for use in search bars,
    autocomplete fields, and admin tools. It delegates the actual filtering
    to the employee repository and transforms database models into lightweight
    DTOs for frontend consumption.

    Parameters
    ----------
    prefix : str
        The string to match at the beginning of employee names or IDs.
        Matching is case-insensitive.
    db : Session
        SQLAlchemy session used to perform the query.

    Returns
    -------
    List[EmployeeResult]
        A list of employees whose ID or name starts with the given prefix.
        Embeddings and timestamps are intentionally omitted for performance
        and privacy.

    Notes
    -----
    - This operation performs an `ILIKE prefix%` query on both `name` and
      `employee_id`.
    - Any database-related issues are expected to be raised as `DatabaseError`
      by the underlying repository.
    """
    employees = employee_repository.get_employees_by_prefix(db, prefix)

    return [
        EmployeeResult(
            employee_id=emp.employee_id,
            name=emp.name,
            role=emp.role
        )
        for emp in employees
    ]
