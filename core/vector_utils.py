import numpy as np
from typing import List

def normalize_vector(vec: List[float]) -> np.ndarray:
    arr = np.array(vec)
    norm = np.linalg.norm(arr)
    if norm == 0:
        raise ValueError("Vector has zero magnitude")
    return arr / norm

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    v1 = normalize_vector(vec1)
    v2 = normalize_vector(vec2)
    return float(np.dot(v1, v2))
