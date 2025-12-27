# tests/test_clock_api.py

"""
API tests for the /clock endpoints.

These tests rely on:
    • make_client() from tests/conftest.py
    • a fully isolated database per test
    • realistic HTTP requests executed via TestClient

Each test:
    • gets a fresh FastAPI app
    • gets a clean DB schema
    • performs real API operations
"""


def _create_employee(client, employee_id="emp123"):
    """Helper to create an employee for clock tests."""
    payload = {
        "employee_id": employee_id,
        "name": "Test Worker",
        "role": "employee",
        "embedding": [0.1] * 512,
    }
    client.post("/employees/", json=payload, headers={"X-Admin-Key": "dev-key"})


# ============================================================================
# CLOCK IN
# ============================================================================

def test_clock_in_success(make_client):
    client = make_client()
    _create_employee(client, "emp1")

    response = client.post("/clock/emp1/in")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] is None


def test_clock_in_already_clocked_in_returns_409(make_client):
    client = make_client()
    _create_employee(client, "emp2")

    # First clock in succeeds
    client.post("/clock/emp2/in")

    # Second clock in fails
    response = client.post("/clock/emp2/in")

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["code"] == "ALREADY_CLOCKED_IN"


# ============================================================================
# CLOCK OUT
# ============================================================================

def test_clock_out_success(make_client):
    client = make_client()
    _create_employee(client, "emp3")

    # Clock in first
    client.post("/clock/emp3/in")

    # Then clock out
    response = client.post("/clock/emp3/out")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] is None


def test_clock_out_not_clocked_in_returns_400(make_client):
    client = make_client()
    _create_employee(client, "emp4")

    # Try to clock out without clocking in
    response = client.post("/clock/emp4/out")

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["code"] == "NOT_CLOCKED_IN"


# ============================================================================
# CLOCK STATUS
# ============================================================================

def test_clock_status_not_clocked_in(make_client):
    client = make_client()
    _create_employee(client, "emp5")

    response = client.get("/clock/emp5/status")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["is_clocked_in"] is False
    assert body["data"]["clock_in_time"] is None


def test_clock_status_clocked_in(make_client):
    client = make_client()
    _create_employee(client, "emp6")

    # Clock in
    client.post("/clock/emp6/in")

    # Check status
    response = client.get("/clock/emp6/status")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["is_clocked_in"] is True
    assert body["data"]["clock_in_time"] is not None


# ============================================================================
# FULL WORKFLOW
# ============================================================================

def test_full_clock_in_out_cycle(make_client):
    """Test a complete clock-in → status → clock-out → status cycle."""
    client = make_client()
    _create_employee(client, "emp7")

    # 1. Initially not clocked in
    status1 = client.get("/clock/emp7/status").json()
    assert status1["data"]["is_clocked_in"] is False

    # 2. Clock in
    clock_in = client.post("/clock/emp7/in")
    assert clock_in.status_code == 200

    # 3. Now clocked in
    status2 = client.get("/clock/emp7/status").json()
    assert status2["data"]["is_clocked_in"] is True

    # 4. Clock out
    clock_out = client.post("/clock/emp7/out")
    assert clock_out.status_code == 200

    # 5. No longer clocked in
    status3 = client.get("/clock/emp7/status").json()
    assert status3["data"]["is_clocked_in"] is False