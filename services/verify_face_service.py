# services/face_service.py

from sqlalchemy.orm import Session
from schemas import VerifyFaceRequest
from models import Employee
from core.vector_utils import cosine_similarity, normalize_vector
from core.errors import FaceConfidenceTooLow, EmployeeNotFound
from core.settings import settings

def verify_face_embedding(req: VerifyFaceRequest, db: Session) -> None:
    emp = db.query(Employee).filter(Employee.employee_id == req.employee_id).first()
    if not emp:
        raise EmployeeNotFound()

    query_vec = normalize_vector(req.embedding)
    stored_vec = normalize_vector(emp.embedding)

    score = cosine_similarity(query_vec, stored_vec)

    if score < settings.face_match_threshold:
        raise FaceConfidenceTooLow()
