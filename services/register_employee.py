from sqlalchemy.orm import Session
from schemas import EmployeeInput, EmployeeResult
from core.vector_utils import normalize_vector
import data.employee_repository as employee_repository
from structlog import get_logger

log = get_logger()


def register_employee(employee: EmployeeInput, db: Session) -> EmployeeResult:
    """
    Register a new employee in the system.

    This service handles preprocessing and validation before persisting an
    employee to the database.
    """

    log.info(
        "employee_register_service_start",
        employee_id=employee.employee_id,
        role=employee.role,
    )

    # Normalize embedding
    normalized = normalize_vector(employee.embedding)

    # Prepare payload
    payload = employee.model_copy(update={
        "embedding": normalized.tolist(),
        "role": employee.role or "employee"
    }).model_dump()

    log.info(
        "employee_register_prepared_payload",
        employee_id=payload["employee_id"],
        role=payload["role"],
        embedding_normalized=True,  # safe boolean info, no vectors logged
    )

    # Persist via repository layer
    emp = employee_repository.add_employee(db, payload)

    log.info(
        "employee_register_service_success",
        employee_id=emp.employee_id,
    )

    return EmployeeResult(
        employee_id=emp.employee_id,
        name=emp.name,
        role=emp.role
    )
