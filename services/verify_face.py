from sqlalchemy.orm import Session
from structlog import get_logger

from schemas import VerifyFaceRequest
from core.vector_utils import normalize_vector, cosine_similarity
from core.errors import (
    FaceConfidenceTooLow,
    ServerMisconfigured,
)
from data.employee_repository import get_employee_by_id
from core.settings import Settings

log = get_logger()


def verify_face_embedding(
    req: VerifyFaceRequest,
    db: Session,
    settings: Settings,
) -> float:
    """
    Validate a submitted face embedding against a stored embedding.
    """

    log.info(
        "face_verify_start",
        employee_id=req.employee_id,
        embedding_length=len(req.embedding),
    )

    # ------------------------------------------------------------
    # Validate settings
    # ------------------------------------------------------------
    if settings.embedding_dim <= 0:
        log.error("face_verify_invalid_setting", field="embedding_dim")
        raise ServerMisconfigured("Invalid embedding_dim configuration.")

    if settings.face_match_threshold <= 0:
        log.error("face_verify_invalid_setting", field="face_match_threshold")
        raise ServerMisconfigured("Invalid face_match_threshold configuration.")

    # ------------------------------------------------------------
    # Validate embedding length
    # ------------------------------------------------------------
    if len(req.embedding) != settings.embedding_dim:
        log.warning(
            "face_verify_wrong_embedding_length",
            expected=settings.embedding_dim,
            got=len(req.embedding),
            employee_id=req.employee_id,
        )
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
        log.debug("face_verify_query_embedding_normalized")
    except ValueError:
        log.warning(
            "face_verify_invalid_query_embedding",
            employee_id=req.employee_id,
        )
        raise FaceConfidenceTooLow("Invalid embedding: cannot normalize.")

    try:
        stored_vec = normalize_vector(emp.embedding)
        log.debug("face_verify_stored_embedding_normalized")
    except ValueError:
        log.error(
            "face_verify_invalid_stored_embedding",
            employee_id=req.employee_id,
        )
        raise ServerMisconfigured("Stored embedding is invalid.")

    # ------------------------------------------------------------
    # Compute similarity
    # ------------------------------------------------------------
    score = cosine_similarity(query_vec, stored_vec)

    log.info(
        "face_verify_similarity_computed",
        employee_id=req.employee_id,
        similarity=round(score, 4),
        threshold=settings.face_match_threshold,
    )

    # ------------------------------------------------------------
    # Threshold check
    # ------------------------------------------------------------
    if score < settings.face_match_threshold:
        log.warning(
            "face_verify_low_confidence",
            employee_id=req.employee_id,
            similarity=round(score, 4),
            threshold=settings.face_match_threshold,
        )
        raise FaceConfidenceTooLow(
            f"Match confidence {score:.4f} below threshold "
            f"{settings.face_match_threshold:.4f}"
        )

    log.info(
        "face_verify_success",
        employee_id=req.employee_id,
        similarity=round(score, 4),
    )

    return score
