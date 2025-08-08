from sqlalchemy.orm import Session
from schemas import VerifyFaceRequest, FaceResult
from core.vector_utils import cosine_similarity, normalize_vector
from core.errors import FaceConfidenceTooLow
from core.settings import settings
from crud import get_employee_by_id

def verify_face_embedding(req: VerifyFaceRequest, db: Session) -> FaceResult:
    emp = get_employee_by_id(db, req.employee_id)

    query_vec = normalize_vector(req.embedding)
    stored_vec = normalize_vector(emp.embedding)

    score = cosine_similarity(query_vec, stored_vec)

    if score < settings.face_match_threshold:
        raise FaceConfidenceTooLow(f"Score {score:.4f} below threshold {settings.face_match_threshold:.4f}")

    return FaceResult(
        employee_id=emp.employee_id,
        score=score,
    )
