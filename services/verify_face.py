from sqlalchemy.orm import Session
from schemas import VerifyFaceRequest
from core.vector_utils import normalize_vector, cosine_similarity
from core.errors import FaceConfidenceTooLow
from data.employee_repository import get_employee_by_id
from core.settings import settings


def verify_face_embedding(req: VerifyFaceRequest, db: Session) -> float:
    """
    Validate a submitted face embedding against the stored embedding.
    Normalizes vectors, computes cosine similarity, and compares against
    the global face-match threshold.
    """

    # Fetch employee from DB or raise EmployeeNotFound
    emp = get_employee_by_id(db, req.employee_id)

    # Normalize query vector — zero vectors are automatically invalid
    try:
        query_vec = normalize_vector(req.embedding)
    except ValueError:
        raise FaceConfidenceTooLow()

    # Normalize stored vector (always valid)
    stored_vec = normalize_vector(emp.embedding)

    # Cosine similarity score
    score = cosine_similarity(query_vec, stored_vec)

    # Reject low-confidence matches
    if score < settings.face_match_threshold:
        raise FaceConfidenceTooLow()

    return score
