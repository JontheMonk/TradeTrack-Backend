import pytest
import numpy as np

from core.vector_utils import normalize_vector, cosine_similarity


# --- normalize_vector tests ---------------------------------------------------

def test_normalize_vector_basic():
    vec = [3.0, 4.0]
    result = normalize_vector(vec)

    expected = np.array([0.6, 0.8])
    assert np.allclose(result, expected)


def test_normalize_vector_length_is_one():
    vec = [10.0, 0.0]
    result = normalize_vector(vec)

    assert np.linalg.norm(result) == pytest.approx(1.0)


def test_normalize_vector_raises_on_zero_norm():
    vec = [0.0, 0.0]

    with pytest.raises(ValueError):
        normalize_vector(vec)


# --- cosine_similarity tests --------------------------------------------------

def test_cosine_similarity_identical_vectors():
    v1 = [1, 2, 3]
    v2 = [1, 2, 3]

    result = cosine_similarity(v1, v2)
    assert result == pytest.approx(1.0)


def test_cosine_similarity_opposite_vectors():
    v1 = [1, 0]
    v2 = [-1, 0]

    result = cosine_similarity(v1, v2)
    assert result == pytest.approx(-1.0)


def test_cosine_similarity_orthogonal_vectors():
    v1 = [1, 0]
    v2 = [0, 1]

    result = cosine_similarity(v1, v2)
    assert result == pytest.approx(0.0)


def test_cosine_similarity_handles_unnormalized_input():
    v1 = [2, 0]
    v2 = [4, 0]

    result = cosine_similarity(v1, v2)

    assert result == pytest.approx(1.0)
