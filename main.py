from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import get_all_embeddings, insert_face
import numpy as np

app = FastAPI()


# 🧠 Data Models
class FaceEmbedding(BaseModel):
    employee_id: str
    name: str
    embedding: list[float]

class QueryEmbedding(BaseModel):
    embedding: list[float]


# ➕ Register a new face
@app.post("/add-face")
def add_face(face: FaceEmbedding):
    if len(face.embedding) != 512:
        raise HTTPException(status_code=400, detail="Embedding must be 512 dimensions")
    
    try:
        insert_face(face.employee_id, face.name, face.embedding)
        return {"status": "success", "message": f"Face added for {face.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB insert failed: {str(e)}")


# 🔍 Match a face embedding to known employees
@app.post("/match-face")
def match_face(query: QueryEmbedding):
    if len(query.embedding) != 512:
        raise HTTPException(status_code=400, detail="Embedding must be 512 dimensions")

    all_embeddings = get_all_embeddings()  # Expected format: list of (employee_id, name, embedding_array)

    if not all_embeddings:
        raise HTTPException(status_code=404, detail="No embeddings found in database")

    query_vec = np.array(query.embedding)
    query_vec = query_vec / np.linalg.norm(query_vec)

    best_match = None
    best_score = -1

    for employee_id, name, emb in all_embeddings:
        emb_vec = np.array(emb)
        emb_vec = emb_vec / np.linalg.norm(emb_vec)

        similarity = float(np.dot(query_vec, emb_vec))  # cosine similarity

        if similarity > best_score:
            best_score = similarity
            best_match = {"employee_id": employee_id, "name": name, "score": similarity}

    if best_score < 0.5:
        return {"match": None, "score": best_score}

    return {"match": best_match}
