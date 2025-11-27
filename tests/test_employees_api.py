# ---------------------------------------------------------------------------
# POST /employees  → Register employee
# ---------------------------------------------------------------------------

def test_add_employee_success(client):
    payload = {
        "employee_id": "abc123",
        "name": "Alice",
        "role": "employee",
        "embedding": [0.1] * 512,
    }

    response = client.post("/employees/", json=payload)

    # Basic response validation
    assert response.status_code == 200
    data = response.json()

    # ApiResponse envelope validation
    assert data["success"] is True
    assert data["data"] is None
    assert data["code"] is None
    assert data["message"] is None


def test_add_employee_duplicate_id_returns_error(client):
    payload = {
        "employee_id": "dup",
        "name": "Bob",
        "role": "employee",
        "embedding": [0.1] * 512,
    }

    # First insert works
    client.post("/employees/", json=payload)

    # Second insert must fail
    response = client.post("/employees/", json=payload)

    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["code"] == "EMPLOYEE_ALREADY_EXISTS"



# ---------------------------------------------------------------------------
# GET /employees/search  → Prefix search
# ---------------------------------------------------------------------------

def test_search_employees(client):
    # Insert multiple employees via API
    employees = [
        {"employee_id": "alice1", "name": "Alice", "role": "employee", "embedding": [0.1] * 512},
        {"employee_id": "alice2", "name": "Alicia", "role": "employee", "embedding": [0.1] * 512},
        {"employee_id": "bob1",   "name": "Bob",   "role": "employee", "embedding": [0.1] * 512},
    ]

    for emp in employees:
        client.post("/employees/", json=emp)

    # Query prefix
    response = client.get("/employees/search?prefix=ali")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True

    results = data["data"]
    ids = {emp["employee_id"] for emp in results}

    # Only alice1 + alice2 should match
    assert ids == {"alice1", "alice2"}


# ---------------------------------------------------------------------------
# POST /employees/verify  → Face verification
# ---------------------------------------------------------------------------

def test_verify_face_success(client):
    # Register employee
    payload = {
        "employee_id": "emp1",
        "name": "Alice",
        "role": "employee",
        "embedding": [0.0] * 511 + [1.0],  # normalized vector
    }
    client.post("/employees/", json=payload)

    # Verify with same embedding → should succeed
    verify_payload = {
        "employee_id": "emp1",
        "embedding": [0.0] * 511 + [1.0],
    }
    response = client.post("/employees/verify", json=verify_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_verify_face_low_confidence_failure(client):
    # Register employee
    payload = {
        "employee_id": "emp2",
        "name": "Bob",
        "role": "employee",
        "embedding": [1.0] + [0.0] * 511,
    }
    client.post("/employees/", json=payload)

    # Verification embedding is FAR away → should fail
    verify_payload = {
        "employee_id": "emp2",
        "embedding": [0.0] * 512,
    }
    response = client.post("/employees/verify", json=verify_payload)

    # Should fail with 400 but not crash
    assert response.status_code == 400

    data = response.json()
    assert data["success"] is False
    assert data["code"] == "FACE_CONFIDENCE_TOO_LOW"
