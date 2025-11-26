from pydantic import BaseModel, Field
from typing import List
from core.settings import settings

class VerifyFaceRequest(BaseModel):
    """
    Schema for face verification requests.

    This payload is sent by the frontend when attempting to verify that
    a live-captured face embedding matches a stored employee embedding.

    Fields:
        employee_id (str):
            The ID of the employee whose identity is being verified.
            The backend will retrieve the stored embedding for this user
            and compare it against the provided one.

        embedding (List[float]):
            The face embedding produced by the client-side model for the
            current verification attempt. The length is strictly enforced
            to match `settings.embedding_dim` (typically 512).

    Notes:
        Validation occurs before hitting the verifier logic, ensuring that
        malformed or incorrect-length embeddings are rejected at the model
        parsing phase.
    """

    employee_id: str
    embedding: List[float] = Field(..., min_length=settings.embedding_dim,
                               max_length=settings.embedding_dim)

