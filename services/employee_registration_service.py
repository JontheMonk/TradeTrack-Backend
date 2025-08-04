from sqlalchemy.orm import Session
from schemas import FaceRecord, EmployeeView
from core.vector_utils import normalize_vector
import crud


def register_employee(face: FaceRecord, db: Session) -> EmployeeView:
    normalized = normalize_vector(face.embedding)
    face.embedding = normalized.tolist()

    emp = crud.add_employee(db, face)
    return EmployeeView(
        employee_id=emp.employee_id,
        name=emp.name,
        role=emp.role
    )
