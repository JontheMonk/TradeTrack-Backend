import pytest
from unittest.mock import MagicMock

from services.search_employees import search_employees_by_prefix
from schemas import EmployeeResult


# ---------------------------------------------------------------------------
# HAPPY PATH: Normal prefix search
# ---------------------------------------------------------------------------
def test_search_employees_by_prefix(monkeypatch):
    db = MagicMock()

    # Fake DB rows
    mock_emp1 = MagicMock()
    mock_emp1.employee_id = "123"
    mock_emp1.name = "Jon"
    mock_emp1.role = "Employee"

    mock_emp2 = MagicMock()
    mock_emp2.employee_id = "124"
    mock_emp2.name = "Johnny"
    mock_emp2.role = "Admin"

    fake_results = [mock_emp1, mock_emp2]

    # Mock repo
    def mock_get(db_session, prefix):
        mock_get.captured_prefix = prefix
        mock_get.captured_db = db_session
        return fake_results

    mock_get.captured_prefix = None
    mock_get.captured_db = None

    monkeypatch.setattr(
        "services.search_employees.employee_repository.get_employees_by_prefix",
        mock_get
    )

    # Act
    result = search_employees_by_prefix("jo", db)

    # Assert: DTO types correct
    assert isinstance(result, list)
    assert all(isinstance(r, EmployeeResult) for r in result)

    # Repo called correctly
    assert mock_get.captured_prefix == "jo"
    assert mock_get.captured_db == db

    # Correct transformation
    assert result[0].employee_id == "123"
    assert result[0].name == "Jon"
    assert result[0].role == "Employee"

    assert result[1].employee_id == "124"
    assert result[1].name == "Johnny"
    assert result[1].role == "Admin"

    # Ensure returned objects are NOT the ORM objects
    assert result[0] is not mock_emp1
    assert result[1] is not mock_emp2

    # Ensure we didn't mutate mock ORM objects
    assert mock_emp1.name == "Jon"
    assert mock_emp1.role == "Employee"
    assert mock_emp2.name == "Johnny"
    assert mock_emp2.role == "Admin"



# ---------------------------------------------------------------------------
# EDGE CASE: No matches (empty list)
# ---------------------------------------------------------------------------
def test_search_employees_by_prefix_no_matches(monkeypatch):
    db = MagicMock()

    # Repo returns empty list
    def mock_get(db_session, prefix):
        mock_get.captured_prefix = prefix
        return []

    mock_get.captured_prefix = None

    monkeypatch.setattr(
        "services.search_employees.employee_repository.get_employees_by_prefix",
        mock_get
    )

    result = search_employees_by_prefix("xx", db)

    assert result == []
    assert isinstance(result, list)
    assert mock_get.captured_prefix == "xx"



# ---------------------------------------------------------------------------
# EDGE CASE: Repo objects have extra fields (ensure no leakage)
# ---------------------------------------------------------------------------
def test_search_employees_by_prefix_extra_fields_ignored(monkeypatch):
    db = MagicMock()

    mock_emp = MagicMock()
    mock_emp.employee_id = "999"
    mock_emp.name = "Alice"
    mock_emp.role = "Employee"
    mock_emp.secret_token = "DO_NOT_LEAK"  # Repo might have extra columns

    def mock_get(_, __):
        return [mock_emp]

    monkeypatch.setattr(
        "services.search_employees.employee_repository.get_employees_by_prefix",
        mock_get
    )

    result = search_employees_by_prefix("a", db)

    # Only allowed fields should appear
    dto = result[0]
    assert isinstance(dto, EmployeeResult)

    assert hasattr(dto, "employee_id")
    assert hasattr(dto, "name")
    assert hasattr(dto, "role")

    # Extra DB fields MUST NOT leak into DTO
    assert not hasattr(dto, "secret_token")
