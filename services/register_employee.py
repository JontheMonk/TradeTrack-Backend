from sqlalchemy.orm import Session
from schemas import EmployeeInput, EmployeeResult
from core.vector_utils import normalize_vector
import data.employee_repository as employee_repository


def register_employee(employee: EmployeeInput, db: Session) -> EmployeeResult:
    """
    Register a new employee in the system.

    This service handles all preprocessing and validation required before
    persisting an employee to the database. In particular, it normalizes the
    incoming embedding vector to ensure consistent cosine-based comparisons
    later on, applies a default role when none is provided, and delegates the
    actual creation to the CRUD layer.

    Parameters
    ----------
    employee : EmployeeInput
        Incoming employee payload containing the ID, name, raw embedding vector,
        and optional role.
    db : Session
        SQLAlchemy session used to perform the database transaction.

    Returns
    -------
    EmployeeResult
        A lightweight DTO containing the new employee's ID, name, and role.
        Embeddings and timestamps are intentionally excluded from the response.

    Notes
    -----
    - The embedding is L2-normalized before storage.
    - Role defaults to ``"employee"`` if not specified.
    - Any uniqueness or integrity violations (e.g., duplicate employee_id)
      are expected to be raised by the underlying repository layer.
    """

    # Normalize incoming embedding (critical for consistency)
    normalized = normalize_vector(employee.embedding)

    # We create a *new* Pydantic model instead of mutating the incoming request.
    #
    # Reasons:
    #   1. Pydantic models are designed to behave like immutable data objects.
    #      Modifying them in place is discouraged and can bypass validation.
    #
    #   2. `model_copy(update=...)` guarantees that updated fields are validated
    #      and applied atomically, producing a clean, consistent payload.
    #
    #   3. The original request object remains untouched, which makes debugging,
    #      logging, and reasoning about the flow far easier.
    #
    #   4. If the schema evolves (new defaults, new fields), `model_copy`
    #      automatically preserves the correct defaults without rewriting logic.
    #
    # In short: copy → update is the safe, Pydantic-idiomatic way to transform input.
    payload = employee.model_copy(update={
        "embedding": normalized.tolist(),
        "role": employee.role or "employee"
    })

    # Persist via repository layer
    emp = employee_repository.add_employee(db, payload)

    # Return DTO for frontend consumption
    return EmployeeResult(
        employee_id=emp.employee_id,
        name=emp.name,
        role=emp.role
    )
