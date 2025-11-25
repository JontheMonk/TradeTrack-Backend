from sqlalchemy.orm import Session
from schemas import VerifyFaceRequest
from core.vector_utils import normalize_vector, cosine_similarity
from core.errors import FaceConfidenceTooLow
from employee_repository import get_employee_by_id
from core.settings import settings


def verify_face_embedding(req: VerifyFaceRequest, db: Session) -> float:
    """
    Validate a submitted face embedding against the stored embedding
    for a specific employee.

    This service normalizes both vectors, computes cosine similarity,
    and compares the score against the system-wide face match threshold.
    It raises an exception when the match is insufficient and returns
    the similarity score when verification succeeds.

    Parameters
    ----------
    req : VerifyFaceRequest
        Incoming request containing the employee ID and the raw embedding
        vector produced by the client-side face recognition model.
    db : Session
        SQLAlchemy session used to retrieve the employee record.

    Returns
    -------
    float
        The cosine similarity score between the query embedding and the
        stored embedding. Higher values indicate stronger matches.

    Raises
    ------
    FaceConfidenceTooLow
        If the similarity score falls below the configured threshold.
    EmployeeNotFound
        If no employee exists with the given ID.
    DatabaseError
        If any failure occurs while retrieving the employee.

    Notes
    -----
    - Both vectors are L2-normalized before comparison to ensure
      consistent distance metrics.
    - Threshold is configured in `settings.face_match_threshold`.
    - This service does **not** update timestamps or store logs — such
      behavior should be implemented in a higher-level workflow service
      if required.
    """
    emp = get_employee_by_id(db, req.employee_id)

    query_vec = normalize_vector(req.embedding)
    stored_vec = normalize_vector(emp.embedding)

    score = cosine_similarity(query_vec, stored_vec)

    if score < settings.face_match_threshold:
        raise FaceConfidenceTooLow(
            f"Score {score:.4f} below threshold {settings.face_match_threshold:.4f}"
        )

    return score
