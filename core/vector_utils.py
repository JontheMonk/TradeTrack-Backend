import numpy as np
from typing import List

def normalize_vector(vec: List[float]) -> np.ndarray:
    """
    Normalize a numeric vector to unit length.

    Parameters:
        vec (List[float]):
            Input vector of floats (typically a face embedding).

    Returns:
        np.ndarray:
            The normalized vector such that ||v|| = 1.

    Raises:
        ValueError:
            If the vector has zero magnitude (norm == 0), which would make
            normalization undefined.

    Notes:
        Normalization is required before cosine similarity comparisons.
    """
    arr = np.array(vec)
    norm = np.linalg.norm(arr)
    if norm == 0:
        raise ValueError("Vector has zero magnitude")
    return arr / norm


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Cosine similarity is defined as:
        cos(theta) = (v1 · v2) / (||v1|| * ||v2||)
    After normalization, this reduces to just the dot product.

    Parameters:
        vec1 (List[float]):
            First vector.
        vec2 (List[float]):
            Second vector.

    Returns:
        float:
            Cosine similarity in the range [-1.0, 1.0].
            Values closer to 1.0 indicate higher similarity.

    Notes:
        Both vectors are normalized internally to ensure consistent
        comparisons, even if the raw embeddings differ in magnitude.
    """
    v1 = normalize_vector(vec1)
    v2 = normalize_vector(vec2)
    return float(np.dot(v1, v2))
