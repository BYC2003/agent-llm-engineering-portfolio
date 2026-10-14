from pathlib import Path

import pytest

from rag.documents import KnowledgeChunk
from rag.vector_store import InMemoryVectorStore


def make_chunk(chunk_id: str) -> KnowledgeChunk:
    """创建测试用 chunk，避免每个测试重复写完整对象。"""
    return KnowledgeChunk(
        chunk_id=chunk_id,
        doc_id="test_doc",
        title="测试文档",
        content=f"{chunk_id} 的正文",
        source_path=Path("test_doc.md"),
    )


def test_search_orders_by_similarity() -> None:
    """检索结果应按余弦相似度从高到低排列。"""
    store = InMemoryVectorStore()
    store.add(make_chunk("chunk_a"), [1.0, 0.0])
    store.add(make_chunk("chunk_b"), [0.8, 0.2])
    store.add(make_chunk("chunk_c"), [0.0, 1.0])

    results = store.search([1.0, 0.0], top_k=3)

    assert [result.chunk.chunk_id for result in results] == [
        "chunk_a",
        "chunk_b",
        "chunk_c",
    ]
    assert results[0].score == pytest.approx(1.0)
    assert results[1].score > results[2].score


def test_search_limits_results_by_top_k() -> None:
    """top_k 应限制最终返回的候选数量。"""
    store = InMemoryVectorStore()
    store.add(make_chunk("chunk_a"), [1.0, 0.0])
    store.add(make_chunk("chunk_b"), [0.8, 0.2])

    results = store.search([1.0, 0.0], top_k=1)

    assert len(results) == 1
    assert results[0].chunk.chunk_id == "chunk_a"


def test_ties_preserve_insertion_order() -> None:
    """分数相同时应保持插入顺序，保证结果可复现。"""
    store = InMemoryVectorStore()
    store.add(make_chunk("first"), [1.0, 0.0])
    store.add(make_chunk("second"), [1.0, 0.0])

    results = store.search([1.0, 0.0], top_k=2)

    assert [result.chunk.chunk_id for result in results] == ["first", "second"]


def test_add_rejects_mixed_vector_dimensions() -> None:
    """同一个向量库不能混用不同维度的向量。"""
    store = InMemoryVectorStore()
    store.add(make_chunk("chunk_a"), [1.0, 0.0])

    with pytest.raises(ValueError, match="维度与向量库现有记录不一致"):
        store.add(make_chunk("chunk_b"), [1.0, 0.0, 0.0])


def test_add_rejects_zero_vector() -> None:
    """零向量没有方向，不能写入向量库。"""
    store = InMemoryVectorStore()

    with pytest.raises(ValueError, match="零向量"):
        store.add(make_chunk("chunk_a"), [0.0, 0.0])


def test_search_rejects_invalid_top_k() -> None:
    """top_k 小于 1 时应拒绝执行检索。"""
    store = InMemoryVectorStore()

    with pytest.raises(ValueError, match="top_k 必须大于等于 1"):
        store.search([1.0, 0.0], top_k=0)


def test_search_rejects_query_with_wrong_dimension() -> None:
    """查询向量维度必须与库中向量一致。"""
    store = InMemoryVectorStore()
    store.add(make_chunk("chunk_a"), [1.0, 0.0])

    with pytest.raises(ValueError, match="维度必须相同"):
        store.search([1.0, 0.0, 0.0], top_k=1)
