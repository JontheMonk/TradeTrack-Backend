import pytest
from unittest.mock import MagicMock

from services.verify_face import verify_face_embedding
from schemas import VerifyFaceRequest
from core.errors import FaceConfidenceTooLow
from core.settings import Settings


# ---------------------------------------------------------------------------
# HAPPY PATH: similarity >= threshold
# ---------------------------------------------------------------------------
def test_verify_face_embedding_success(monkeypatch):
    db = MagicMock()

    # Inject test settings
    settings = Settings(
        embedding_dim=512,
        face_match_threshold=0.5,
    )

    # Query embedding (raw, not normalized)
    query_vec = [3.0, 4.0] + [0.0] * 510  # norm = 5

    # Stored embedding (same direction)
    stored_vec = [6.0, 8.0] + [0.0] * 510  # norm = 10

    req = VerifyFaceRequest(
        employee_id="abc",
        embedding=query_vec,
    )

    # Fake employee returned from repository
    mock_emp = MagicMock()
    mock_emp.embedding = stored_vec

    def mock_get_by_id(db_session, emp_id):
        mock_get_by_id.captured_id = emp_id
        mock_get_by_id.captured_db = db_session
        return mock_emp

    monkeypatch.setattr(
        "services.verify_face.get_employee_by_id",
        mock_get_by_id,
    )

    # Act
    score = verify_face_embedding(req, db, settings)

    # Assert
    assert mock_get_by_id.captured_id == "abc"
    assert mock_get_by_id.captured_db == db
    assert score == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# FAILURE: similarity < threshold
# ---------------------------------------------------------------------------
def test_verify_face_embedding_low_confidence(monkeypatch):
    db = MagicMock()
    settings = Settings(face_match_threshold=0.9)  # high threshold

    query_vec = [1.0, 0.0] + [0.0] * 510
    stored_vec = [-1.0, 0.0] + [0.0] * 510  # opposite direction

    req = VerifyFaceRequest(
        employee_id="abc",
        embedding=query_vec,
    )

    mock_emp = MagicMock()
    mock_emp.embedding = stored_vec

    monkeypatch.setattr(
        "services.verify_face.get_employee_by_id",
        lambda *_: mock_emp,
    )

    # Expect failure
    with pytest.raises(FaceConfidenceTooLow):
        verify_face_embedding(req, db, settings)


# ---------------------------------------------------------------------------
# FAILURE: employee not found → repository throws
# ---------------------------------------------------------------------------
def test_verify_face_embedding_employee_not_found(monkeypatch):
    db = MagicMock()
    settings = Settings()

    req = VerifyFaceRequest(
        employee_id="missing",
        embedding=[1.0] * settings.embedding_dim,
    )

    class FakeEmployeeNotFound(Exception):
        pass

    def mock_get_by_id(*_):
        raise FakeEmployeeNotFound()

    monkeypatch.setattr(
        "services.verify_face.get_employee_by_id",
        mock_get_by_id,
    )

    with pytest.raises(FakeEmployeeNotFound):
        verify_face_embedding(req, db, settings)


# ---------------------------------------------------------------------------
# Ensure normalization is applied before comparison
# ---------------------------------------------------------------------------
def test_verify_face_embedding_calls_normalize_vector(monkeypatch):
    db = MagicMock()
    settings = Settings()

    # Valid embedding
    query_vec = [1.0] * settings.embedding_dim
    stored_vec = [1.0] * settings.embedding_dim

    req = VerifyFaceRequest(
        employee_id="abc",
        embedding=query_vec,
    )

    mock_emp = MagicMock()
    mock_emp.embedding = stored_vec

    monkeypatch.setattr(
        "services.verify_face.get_employee_by_id",
        lambda *_: mock_emp,
    )

    # Spy on normalize_vector
    calls = {"count": 0}

    def mock_norm(vec):
        calls["count"] += 1
        from core.vector_utils import normalize_vector as real
        return real(vec)

    monkeypatch.setattr(
        "services.verify_face.normalize_vector",
        mock_norm,
    )

    verify_face_embedding(req, db, settings)

    # Called for query vec + stored vec
    assert calls["count"] == 2
