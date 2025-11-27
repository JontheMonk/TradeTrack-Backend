import pytest
from unittest.mock import MagicMock

from services.verify_face import verify_face_embedding
from schemas import VerifyFaceRequest
from core.errors import FaceConfidenceTooLow
from core.settings import settings


# ---------------------------------------------------------------------------
# HAPPY PATH: similarity >= threshold
# ---------------------------------------------------------------------------
def test_verify_face_embedding_success(monkeypatch):
    db = MagicMock()

    # Query embedding (raw, not normalized)
    query_vec = [3.0, 4.0] + [0.0] * 510  # norm = 5

    # Stored embedding (same direction)
    stored_vec = [6.0, 8.0] + [0.0] * 510  # norm = 10

    req = VerifyFaceRequest(
        employee_id="abc",
        embedding=query_vec
    )

    # Fake employee record returned from repository
    mock_emp = MagicMock()
    mock_emp.embedding = stored_vec

    # Mock repo call
    def mock_get_by_id(db_session, emp_id):
        mock_get_by_id.captured_id = emp_id
        mock_get_by_id.captured_db = db_session
        return mock_emp

    monkeypatch.setattr(
        "services.verify_face.get_employee_by_id",
        mock_get_by_id
    )

    # Act
    score = verify_face_embedding(req, db)

    # Assert: repository called correctly
    assert mock_get_by_id.captured_id == "abc"
    assert mock_get_by_id.captured_db == db

    # Cosine similarity of parallel vectors should be 1
    assert score == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# FAILURE: similarity < threshold
# ---------------------------------------------------------------------------
def test_verify_face_embedding_low_confidence(monkeypatch):
    db = MagicMock()

    # Query embedding
    query_vec = [1.0, 0.0] + [0.0] * 510

    # Stored embedding in opposite direction
    stored_vec = [-1.0, 0.0] + [0.0] * 510

    req = VerifyFaceRequest(
        employee_id="abc",
        embedding=query_vec
    )

    mock_emp = MagicMock()
    mock_emp.embedding = stored_vec

    # Mock repo
    def mock_get_by_id(_, __):
        return mock_emp

    monkeypatch.setattr(
        "services.verify_face.get_employee_by_id",
        mock_get_by_id
    )

    # Act + Assert
    with pytest.raises(FaceConfidenceTooLow):
        verify_face_embedding(req, db)


# ---------------------------------------------------------------------------
# FAILURE: employee not found → repository throws
# ---------------------------------------------------------------------------
def test_verify_face_embedding_employee_not_found(monkeypatch):
    db = MagicMock()

    req = VerifyFaceRequest(
        employee_id="missing",
        embedding=[1.0] * settings.embedding_dim
    )

    # Simulate repository raising EmployeeNotFound
    class FakeEmployeeNotFound(Exception):
        pass

    def mock_get_by_id(_, __):
        raise FakeEmployeeNotFound()

    monkeypatch.setattr(
        "services.verify_face.get_employee_by_id",
        mock_get_by_id
    )

    # Verify exception propagates
    with pytest.raises(FakeEmployeeNotFound):
        verify_face_embedding(req, db)


# ---------------------------------------------------------------------------
# Ensure normalization is applied before comparison
# ---------------------------------------------------------------------------
def test_verify_face_embedding_calls_normalize_vector(monkeypatch):
    db = MagicMock()

    # Build a valid embedding
    query_vec = [1.0] * settings.embedding_dim
    stored_vec = [1.0] * settings.embedding_dim

    req = VerifyFaceRequest(
        employee_id="abc",
        embedding=query_vec
    )

    mock_emp = MagicMock()
    mock_emp.embedding = stored_vec

    # Mock repo
    monkeypatch.setattr(
        "services.verify_face.get_employee_by_id",
        lambda _, __: mock_emp
    )

    # --- Spy on normalize_vector ---
    calls = {"count": 0}

    def mock_normalize(vec):
        calls["count"] += 1
        # use real normalization to avoid breaking code
        from core.vector_utils import normalize_vector as real_norm
        return real_norm(vec)

    monkeypatch.setattr(
        "services.verify_face.normalize_vector",
        mock_normalize
    )

    # Act
    verify_face_embedding(req, db)

    # Assert: normalization was called twice
    assert calls["count"] == 2

