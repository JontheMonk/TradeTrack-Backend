from sqlalchemy.orm import Session
from schemas import FaceEmbedding
from core.vector_utils import normalize_vector
from models import Employee
import crud
from core.errors import EmployeeAlreadyExists


def register_face(face: FaceEmbedding, db: Session) -> Employee:
    normalized = normalize_vector(face.embedding)
    face.embedding = normalized.tolist()

    existing = crud.get_employee_by_id(db, face.employee_id)
    if existing:
        raise EmployeeAlreadyExists()

    return crud.add_employee(db, face)
