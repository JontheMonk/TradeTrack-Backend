# tests/test_employees_api.py

"""
API tests for the /employees endpoints.

These tests rely on:
    • make_client() from tests/conftest.py
    • a fully isolated database per test
    • realistic HTTP requests executed via TestClient

Each test:
    • gets a fresh FastAPI app
    • gets a clean DB schema
    • performs real API operations
"""

# ---------------------------------------------------------------------------
# ADD EMPLOYEE
# ---------------------------------------------------------------------------

def test_add_employee_success(make_client):
    client = make_client()

    payload = {
        "employee_id": "abc123",
        "name": "Alice",
        "role": "employee",
        "embedding": [0.1] * 512,
    }

    response = client.post("/employees/", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert body["data"] is None
    assert body["code"] is None
    assert body["message"] is None


def test_add_employee_duplicate_id_returns_error(make_client):
    client = make_client()

    payload = {
        "employee_id": "dup",
        "name": "Bob",
        "role": "employee",
        "embedding": [0.1] * 512,
    }

    # First insert succeeds
    client.post("/employees/", json=payload)

    # Duplicate insert must fail
    response = client.post("/employees/", json=payload)

    assert response.status_code == 409
    body = response.json()

    assert body["success"] is False
    assert body["code"] == "EMPLOYEE_ALREADY_EXISTS"


# ---------------------------------------------------------------------------
# SEARCH EMPLOYEES
# ---------------------------------------------------------------------------

def test_search_employees(make_client):
    client = make_client()

    # Insert sample employees
    employees = [
        {"employee_id": "alice1", "name": "Alice",   "role": "employee", "embedding": [0.1] * 512},
        {"employee_id": "alice2", "name": "Alicia",  "role": "employee", "embedding": [0.1] * 512},
        {"employee_id": "bob1",   "name": "Bob",     "role": "employee", "embedding": [0.1] * 512},
    ]

    for emp in employees:
        client.post("/employees/", json=emp)

    response = client.get("/employees/search?prefix=ali")

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True

    results = body["data"]
    ids = {emp["employee_id"] for emp in results}

    assert ids == {"alice1", "alice2"}


# ---------------------------------------------------------------------------
# FACE VERIFICATION
# ---------------------------------------------------------------------------

def test_verify_face_success(make_client):
    client = make_client()

    # Register employee
    payload = {
        "employee_id": "emp1",
        "name": "Alice",
        "role": "employee",
        "embedding": [0.0] * 511 + [1.0],  # already normalized
    }
    client.post("/employees/", json=payload)

    # Verify with identical embedding
    verify_payload = {
        "employee_id": "emp1",
        "embedding": [0.0] * 511 + [1.0],
    }

    response = client.post("/employees/verify", json=verify_payload)

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True


def test_verify_face_low_confidence_failure(make_client):
    client = make_client()

    # Register employee
    payload = {
        "employee_id": "emp2",
        "name": "Bob",
        "role": "employee",
        "embedding": [1.0] + [0.0] * 511,
    }
    client.post("/employees/", json=payload)

    # Provide wildly different embedding
    verify_payload = {
        "employee_id": "emp2",
        "embedding": [0.0] * 512,
    }

    response = client.post("/employees/verify", json=verify_payload)

    assert response.status_code == 400
    body = response.json()

    assert body["success"] is False
    assert body["code"] == "FACE_CONFIDENCE_TOO_LOW"
