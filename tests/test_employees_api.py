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

# ============================================================================
# ADD EMPLOYEE
# ============================================================================

def test_add_employee_success(make_client):
    client = make_client()

    payload = {
        "employee_id": "abc123",
        "name": "Alice",
        "role": "employee",
        "embedding": [0.1] * 512,
    }

    response = client.post("/employees/", json=payload,
                           headers={"X-Admin-Key": "dev-key"})

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
    client.post("/employees/", json=payload,
                headers={"X-Admin-Key": "dev-key"})

    # Duplicate insert must fail
    response = client.post("/employees/", json=payload,
                           headers={"X-Admin-Key": "dev-key"})

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["code"] == "EMPLOYEE_ALREADY_EXISTS"


def test_add_employee_missing_admin_key_returns_401(make_client):
    client = make_client()

    payload = {
        "employee_id": "noadmin",
        "name": "Charlie",
        "role": "employee",
        "embedding": [0.1] * 512,
    }

    response = client.post("/employees/", json=payload)
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["code"] == "UNAUTHORIZED"


def test_add_employee_invalid_admin_key(make_client):
    client = make_client()

    payload = {
        "employee_id": "badkey",
        "name": "Dana",
        "role": "employee",
        "embedding": [0.1] * 512,
    }

    response = client.post("/employees/", json=payload,
                           headers={"X-Admin-Key": "WRONG"})
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_add_employee_invalid_payload_schema(make_client):
    client = make_client()

    bad_payload = {
        "employee_id": "abc",
        "name": "Alice",
        "role": "employee",
        "embedding": "not-a-list",
    }

    response = client.post("/employees/", json=bad_payload,
                           headers={"X-Admin-Key": "dev-key"})
    assert response.status_code == 422


# ============================================================================
# SEARCH EMPLOYEES
# ============================================================================

def test_search_employees(make_client):
    client = make_client()

    employees = [
        {"employee_id": "alice1", "name": "Alice",   "role": "employee", "embedding": [0.1] * 512},
        {"employee_id": "alice2", "name": "Alicia",  "role": "employee", "embedding": [0.1] * 512},
        {"employee_id": "bob1",   "name": "Bob",     "role": "employee", "embedding": [0.1] * 512},
    ]

    for emp in employees:
        client.post("/employees/", json=emp,
                    headers={"X-Admin-Key": "dev-key"})

    response = client.get("/employees/search?prefix=ali")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    ids = {emp["employee_id"] for emp in body["data"]}
    assert ids == {"alice1", "alice2"}


def test_search_employees_no_results(make_client):
    client = make_client()

    response = client.get("/employees/search?prefix=zzz")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"] == []


def test_search_employees_short_prefix(make_client):
    client = make_client()

    # prefix < 3 triggers FastAPI validation
    response = client.get("/employees/search?prefix=ab")
    assert response.status_code == 422


# ============================================================================
# FACE VERIFICATION
# ============================================================================

def test_verify_face_success(make_client):
    client = make_client()

    payload = {
        "employee_id": "emp1",
        "name": "Alice",
        "role": "employee",
        "embedding": [0.0] * 511 + [1.0],
    }
    client.post("/employees/", json=payload,
                headers={"X-Admin-Key": "dev-key"})

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

    payload = {
        "employee_id": "emp2",
        "name": "Bob",
        "role": "employee",
        "embedding": [1.0] + [0.0] * 511,
    }
    client.post("/employees/", json=payload,
                headers={"X-Admin-Key": "dev-key"})

    verify_payload = {
        "employee_id": "emp2",
        "embedding": [0.0] * 512,
    }

    response = client.post("/employees/verify", json=verify_payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False
    assert body["code"] == "FACE_CONFIDENCE_TOO_LOW"


def test_verify_face_unknown_employee(make_client):
    client = make_client()

    payload = {
        "employee_id": "ghost",
        "embedding": [0.1] * 512,
    }

    response = client.post("/employees/verify", json=payload)
    assert response.status_code == 404

    body = response.json()
    assert body["code"] == "EMPLOYEE_NOT_FOUND"


def test_verify_face_invalid_embedding_length(make_client):
    client = make_client()

    bad_payload = {
        "employee_id": "empX",
        "embedding": [0.5, 0.6],  # too short!
    }

    response = client.post("/employees/verify", json=bad_payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False

