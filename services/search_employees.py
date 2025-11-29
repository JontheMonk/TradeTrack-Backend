from typing import List
from sqlalchemy.orm import Session
from structlog import get_logger

from schemas import EmployeeResult
import data.employee_repository as employee_repository

log = get_logger()


def search_employees_by_prefix(prefix: str, db: Session) -> List[EmployeeResult]:
    """
    Search for employees whose ID or name begins with a given prefix.
    """

    log.info(
        "search_employees_start",
        prefix=prefix,
        prefix_length=len(prefix),
    )

    employees = employee_repository.get_employees_by_prefix(db, prefix)

    results = [
        EmployeeResult(
            employee_id=emp.employee_id,
            name=emp.name,
            role=emp.role
        )
        for emp in employees
    ]

    log.info(
        "search_employees_success",
        prefix=prefix,
        result_count=len(results),
    )

    return results
