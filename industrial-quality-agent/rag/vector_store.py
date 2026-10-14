from dataclasses import dataclass

from rag.documents import KnowledgeChunk
from rag.similarity import cosine_similarity


@dataclass(frozen=True)
class SearchResult:
    """表示一次向量检索命中的 chunk 和相似度分数。"""

    chunk: KnowledgeChunk
    score: float


class InMemoryVectorStore:
    """把 chunk 和向量保存在内存中，并按余弦相似度检索。"""

    def __init__(self) -> None:
        self._records: list[tuple[KnowledgeChunk, tuple[float, ...]]] = []
        self._vector_size: int | None = None

    def add(self, chunk: KnowledgeChunk, vector: list[float]) -> None:
        """把一个 chunk 及其向量加入内存向量库。"""
        if not vector:
            raise ValueError("向量不能为空")
        if all(value == 0.0 for value in vector):
            raise ValueError("零向量不能写入向量库")

        # 同一个向量库必须使用相同维度，否则不同记录无法互相比较。
        if self._vector_size is None:
            self._vector_size = len(vector)
        elif len(vector) != self._vector_size:
            raise ValueError("向量维度与向量库现有记录不一致")

        # tuple 是不可变类型，避免保存后被外部代码意外修改。
        self._records.append((chunk, tuple(vector)))

    def search(self, query_vector: list[float], top_k: int = 3) -> list[SearchResult]:
        """返回与查询向量最相似的前 K 个 chunk。"""
        if top_k < 1:
            raise ValueError("top_k 必须大于等于 1")
        if not self._records:
            return []

        # 计算每个 chunk 的相似度，并保留原始插入顺序。
        scored_records = [
            (chunk, cosine_similarity(query_vector, list(vector)))
            for chunk, vector in self._records
        ]

        # Python 的排序是稳定的，因此分数相同时会保持插入顺序。
        scored_records.sort(key=lambda item: item[1], reverse=True)

        return [
            SearchResult(chunk=chunk, score=score)
            for chunk, score in scored_records[:top_k]
        ]
