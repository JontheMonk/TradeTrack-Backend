from sqlalchemy.orm import Session
from schemas import VerifyFaceRequest, VerifyFaceResponse
from core.vector_utils import cosine_similarity, normalize_vector
from core.errors import FaceConfidenceTooLow
from core.settings import settings
from crud import get_employee_by_id

def verify_face_embedding(req: VerifyFaceRequest, db: Session) -> VerifyFaceResponse:
    emp = get_employee_by_id(db, req.employee_id)

    query_vec = normalize_vector(req.embedding)
    stored_vec = normalize_vector(emp.embedding)
    score = cosine_similarity(query_vec, stored_vec)

    threshold = settings.face_match_threshold
    matched = score >= threshold
    if not matched:
        raise FaceConfidenceTooLow(
            f"Score {score:.4f} below threshold {threshold:.4f}"
        )

    return VerifyFaceResponse(
        employee_id=emp.employee_id,
        score=score,
        threshold=threshold
    )
