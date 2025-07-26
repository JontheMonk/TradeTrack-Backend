from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import numpy as np
from typing import Optional
from db import get_db
import crud
from schemas import FaceEmbedding, QueryEmbedding, MatchResult
from core.operation_result import VoidResult, OperationResult
from core.settings import FACE_MATCH_THRESHOLD


router = APIRouter()


@router.post("/add-face")
def add_face(face: FaceEmbedding, db: Session = Depends(get_db)):
    # ✅ Validate embedding
    if len(face.embedding) != 512:
        raise HTTPException(status_code=400, detail="Embedding must be 512 dimensions")

    vec = np.array(face.embedding)
    norm = np.linalg.norm(vec)
    if norm == 0:
        raise HTTPException(status_code=400, detail="Embedding vector has zero magnitude")

    # ✅ Normalize embedding
    vec /= norm
    face.embedding = vec.tolist()

    result: VoidResult = crud.add_employee(db, face)

    if not result.success:
        if result.code == ErrorCode.EMPLOYEE_ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail=result.message)
        raise HTTPException(status_code=500, detail=result.message)


    return {"status": "success", "message": result.message}


@router.post("/match-face", response_model=Optional[MatchResult])
def match_face(query: QueryEmbedding, db: Session = Depends(get_db)):
    employee_result: OperationResult = crud.get_all_employees(db)

    if not employee_result.success:
        raise HTTPException(status_code=500, detail=employee_result.message)

    employees = employee_result.data
    if not employees:
        raise HTTPException(status_code=404, detail="No embeddings found")

    query_vec = np.array(query.embedding)
    query_vec /= np.linalg.norm(query_vec)

    best_match = None
    best_score = -1

    for emp in employees:
        emb_vec = np.array(emp.embedding)
        emb_vec /= np.linalg.norm(emb_vec)
        score = float(np.dot(query_vec, emb_vec))

        if score > best_score:
            best_score = score
            best_match = MatchResult(
                employee_id=emp.employee_id,
                name=emp.name,
                role=emp.role,
                score=score
            )

    if best_score < 0.5:
        return None

    return best_match
