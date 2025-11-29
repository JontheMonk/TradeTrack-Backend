from sqlalchemy.orm import Session
from schemas import VerifyFaceRequest
from core.vector_utils import normalize_vector, cosine_similarity
from core.errors import (
    FaceConfidenceTooLow,
    ServerMisconfigured,
)
from data.employee_repository import get_employee_by_id
from core.settings import Settings


def verify_face_embedding(
    req: VerifyFaceRequest,
    db: Session,
    settings: Settings,
) -> float:
    """
    Validate a submitted face embedding against a stored embedding.

    Includes:
        • dynamic validation based on injected settings
        • embedding-length enforcement
        • normalization and cosine similarity
        • low-confidence rejection
    """

    # ------------------------------------------------------------
    # Validate settings
    # ------------------------------------------------------------
    if settings.embedding_dim <= 0:
        raise ServerMisconfigured("Invalid embedding_dim configuration.")

    if settings.face_match_threshold <= 0:
        raise ServerMisconfigured("Invalid face_match_threshold configuration.")

    # ------------------------------------------------------------
    # Validate embedding length (done at runtime, not in schema)
    # ------------------------------------------------------------
    if len(req.embedding) != settings.embedding_dim:
        raise FaceConfidenceTooLow(
            f"Expected embedding_dim={settings.embedding_dim}, "
            f"got {len(req.embedding)}."
        )

    # ------------------------------------------------------------
    # Fetch employee
    # ------------------------------------------------------------
    emp = get_employee_by_id(db, req.employee_id)

    # ------------------------------------------------------------
    # Normalize vectors
    # ------------------------------------------------------------
    try:
        query_vec = normalize_vector(req.embedding)
    except ValueError:
        # Zero vector, NaNs, etc.
        raise FaceConfidenceTooLow("Invalid embedding: cannot normalize.")

    try:
        stored_vec = normalize_vector(emp.embedding)
    except ValueError:
        # If this ever happens, your DB stored garbage
        raise ServerMisconfigured("Stored embedding is invalid.")

    # ------------------------------------------------------------
    # Compute similarity
    # ------------------------------------------------------------
    score = cosine_similarity(query_vec, stored_vec)

    # ------------------------------------------------------------
    # Threshold check
    # ------------------------------------------------------------
    if score < settings.face_match_threshold:
        raise FaceConfidenceTooLow(
            f"Match confidence {score:.4f} below threshold "
            f"{settings.face_match_threshold:.4f}"
        )

    return score
