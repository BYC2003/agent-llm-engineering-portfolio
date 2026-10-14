import pytest

from rag.similarity import cosine_similarity


def test_cosine_similarity_for_same_direction() -> None:
    """方向相同的向量相似度应为 1。"""
    result = cosine_similarity([1.0, 0.0], [2.0, 0.0])

    assert result == pytest.approx(1.0)


def test_cosine_similarity_for_similar_direction() -> None:
    """方向接近的向量相似度应接近 1。"""
    result = cosine_similarity([1.0, 0.0], [0.9, 0.1])

    assert result > 0.99


def test_cosine_similarity_for_orthogonal_vectors() -> None:
    """方向垂直的向量相似度应为 0。"""
    result = cosine_similarity([1.0, 0.0], [0.0, 1.0])

    assert result == pytest.approx(0.0)


def test_cosine_similarity_for_opposite_direction() -> None:
    """方向相反的向量相似度应为 -1。"""
    result = cosine_similarity([1.0, 0.0], [-1.0, 0.0])

    assert result == pytest.approx(-1.0)


def test_cosine_similarity_rejects_different_dimensions() -> None:
    """两个向量维度不同时应抛出清晰错误。"""
    with pytest.raises(ValueError, match="维度必须相同"):
        cosine_similarity([1.0, 0.0], [1.0])


def test_cosine_similarity_rejects_zero_vector() -> None:
    """零向量没有明确方向，不能计算余弦相似度。"""
    with pytest.raises(ValueError, match="零向量"):
        cosine_similarity([0.0, 0.0], [1.0, 0.0])
