import pytest
import numpy as np
from unittest.mock import MagicMock

from services.register_employee import register_employee
from schemas import EmployeeInput, EmployeeResult


def test_register_employee_normalizes_and_defaults_role(monkeypatch):
    # --- Arrange -------------------------------------------------------------

    # Fake database session
    db = MagicMock()

    # Input embedding (not normalized)
    raw_embedding = [0.0] * 511 + [5.0]   # norm ≈ 5
    employee_input = EmployeeInput(
        employee_id="123",
        name="Jon",
        embedding=raw_embedding,
        role=None  # force default role
    )

    # Mock repo return value
    mock_emp = MagicMock()
    mock_emp.employee_id = "123"
    mock_emp.name = "Jon"
    mock_emp.role = "Employee"

    # Mock the repository function
    def mock_add_employee(db_session, payload: dict):
        mock_add_employee.captured_payload = payload
        return mock_emp

    mock_add_employee.captured_payload = None

    monkeypatch.setattr(
        "services.register_employee.employee_repository.add_employee",
        mock_add_employee
    )

    # --- Act ----------------------------------------------------------------
    result = register_employee(employee_input, db)

    # --- Assert -------------------------------------------------------------

    # 1. Output type is correct
    assert isinstance(result, EmployeeResult)

    # 2. Returned data matches mock
    assert result.employee_id == "123"
    assert result.name == "Jon"
    assert result.role == "Employee"

    # 3. Embedding was normalized before being passed to repo
    payload = mock_add_employee.captured_payload

    assert isinstance(payload, dict), "Service must pass a dict to repo"

    embedding = payload["embedding"]
    norm = np.linalg.norm(embedding)
    assert pytest.approx(norm) == 1.0

    # 4. Role was defaulted
    assert payload["role"] == "Employee"

    # 5. Original object was NOT mutated
    assert employee_input.embedding == raw_embedding
    assert employee_input.role is None
