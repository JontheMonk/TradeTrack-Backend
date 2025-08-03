from sqlalchemy.orm import Session
from schemas import FaceEmbedding
from core.vector_utils import normalize_vector
from models import Employee
import crud


def register_face(face: FaceEmbedding, db: Session) -> Employee:
    normalized = normalize_vector(face.embedding)
    face.embedding = normalized.tolist()

    return crud.add_employee(db, face)
