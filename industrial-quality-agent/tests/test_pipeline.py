"""端到端检索测试：文档 → 清洗切分 → 向量 → 向量库 → 前 K 个候选。"""

from pathlib import Path

import pytest

from rag.pipeline import KnowledgeBase

# 测试使用的合成知识目录
KNOWLEDGE_DIR = Path("data/synthetic_demo/knowledge")


class FakeEmbedder:
    """假向量模型：记录被转换的文字，返回固定 2 维向量。

    作用：验证“流程有没有把正确的文字交给模型”，不依赖真实模型，跑得很快。
    """

    def __init__(self) -> None:
        self.calls: list[list[str]] = []  # 每次调用的原始输入，便于断言

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        # 所有片段返回同一个向量，保证排序结果只取决于稳定排序（插入顺序）
        return [[1.0, 0.0] for _ in texts]


@pytest.fixture(scope="module")
def knowledge_base() -> KnowledgeBase:
    """整个测试模块共用一个已建好索引的知识库，避免重复加载真实模型。"""
    base = KnowledgeBase(KNOWLEDGE_DIR)
    base.build()
    return base


def test_build_indexes_every_document() -> None:
    """4 份知识文档应各产生 1 个片段。"""
    base = KnowledgeBase(KNOWLEDGE_DIR)
    count = base.build()

    assert count == 4
    assert len(base.chunks) == 4
    assert {chunk.doc_id for chunk in base.chunks} == {
        "case_dirty_nozzle",
        "fmea_dispensing",
        "sop_cleaning",
        "sop_dispensing",
    }


def test_build_passes_chunk_content_to_embedder() -> None:
    """建索引时，交给向量模型的应该是片段正文。"""
    fake = FakeEmbedder()
    base = KnowledgeBase(KNOWLEDGE_DIR, embedder=fake)
    base.build()

    assert len(fake.calls) == 1                # 只调用一次，批量转换更高效
    assert len(fake.calls[0]) == 4             # 4 个片段
    assert any("喷嘴" in text for text in fake.calls[0])


def test_search_ignores_synthetic_notice() -> None:
    """演示声明行在入库前应被清洗掉，不会污染检索内容。"""
    fake = FakeEmbedder()
    base = KnowledgeBase(KNOWLEDGE_DIR, embedder=fake)
    base.build()

    assert all("合成演示内容" not in text for text in fake.calls[0])


def test_search_returns_expected_document(knowledge_base: KnowledgeBase) -> None:
    """语义检索应命中真正相关的文档，并带上来源。"""
    results = knowledge_base.search("胶量偏多可能是什么原因？", top_k=2)

    assert len(results) == 2
    assert results[0].chunk.source_path.name == "fmea_dispensing.md"
    assert "压力漂移" in results[0].chunk.content
    assert results[0].score > results[1].score


def test_search_ranks_nozzle_case_first(knowledge_base: KnowledgeBase) -> None:
    """喷嘴相关问题应首先命中 8D 案例。"""
    results = knowledge_base.search("喷嘴脏了要怎么处理？", top_k=2)

    assert results[0].chunk.doc_id == "case_dirty_nozzle"


def test_search_before_build_raises_error() -> None:
    """还没建索引就检索应直接报错，而不是返回空结果。"""
    fake = FakeEmbedder()
    base = KnowledgeBase(KNOWLEDGE_DIR, embedder=fake)

    with pytest.raises(RuntimeError, match="build"):
        base.search("任意问题")
