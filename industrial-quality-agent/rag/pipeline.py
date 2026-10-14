"""端到端检索流程：加载文档 → 清洗切分 → 真实向量 → 内存向量库 → 返回前 K 个候选。

职责边界：
- 这一步只负责“找资料”，返回候选 chunk、分数和来源。
- 它不写答案：把候选正文交给大模型生成回答，是后面才做的事。
"""

from __future__ import annotations

from pathlib import Path

from rag.documents import KnowledgeChunk, load_markdown_documents, split_document_into_chunks
from rag.embeddings import EmbeddingModel
from rag.vector_store import InMemoryVectorStore, SearchResult


class KnowledgeBase:
    """把知识目录变成可检索的内存向量库。"""

    def __init__(
        self,
        knowledge_dir: Path,
        embedder: EmbeddingModel | None = None,
    ) -> None:
        self.knowledge_dir = knowledge_dir                                   # 知识文档所在目录
        # 允许从外部传入向量模型：测试时可以换成假模型，避免每次加载真实模型
        self.embedder: EmbeddingModel = embedder or EmbeddingModel()
        self.store = InMemoryVectorStore()                                   # 保存 chunk + 向量
        self.chunks: list[KnowledgeChunk] = []                               # 记住入库的片段，便于检查

    def build(self) -> int:
        """执行完整的建索引流程，返回入库的 chunk 数量。"""
        documents = load_markdown_documents(self.knowledge_dir)              # 第 1 步：加载 Markdown

        chunks: list[KnowledgeChunk] = []
        for document in documents:
            # 第 2 步：清洗掉演示声明，再按小标题切分成片段
            chunks.extend(split_document_into_chunks(document))

        if not chunks:
            raise ValueError("知识目录中没有可检索的内容")

        # 第 3 步：把所有片段正文一次性交给 Embedding 模型，转成向量
        vectors = self.embedder.embed_texts([chunk.content for chunk in chunks])

        # 第 4 步：把“片段 + 向量”成对写入向量库
        for chunk, vector in zip(chunks, vectors):
            self.store.add(chunk, vector)

        self.chunks = chunks
        return len(chunks)

    def search(self, question: str, top_k: int = 3) -> list[SearchResult]:
        """把问题转成向量并检索，返回最相似的前 K 个候选。"""
        if not self.chunks:
            raise RuntimeError("请先调用 build() 建立索引，再执行检索")

        # 问题必须和文档片段用同一个模型转成向量，才能在同一空间里比较
        question_vector = self.embedder.embed_texts([question])[0]
        return self.store.search(question_vector, top_k=top_k)


def main() -> None:
    """演示：对真实的 4 份知识文档提问，看检索结果和来源。"""
    knowledge_dir = Path("data/synthetic_demo/knowledge")
    base = KnowledgeBase(knowledge_dir)

    count = base.build()                                       # 第一次运行会加载模型（本地缓存，不再联网）
    print(f"知识目录：{knowledge_dir}")
    print(f"入库片段数：{count}")
    print()

    questions = [
        "胶量偏多可能是什么原因？",
        "喷嘴脏了要怎么处理？",
        "点胶前要确认哪些参数？",
    ]

    for question in questions:
        print(f"问题：{question}")
        for rank, result in enumerate(base.search(question, top_k=2), start=1):
            source = result.chunk.source_path.name        # 只显示文件名，更易读
            preview = result.chunk.content.replace("\n", " ")[:40]   # 预览前 40 个字
            print(f"  第{rank}名 分数={result.score:.4f} 来源={source}")
            print(f"        正文预览：{preview}...")
        print()


if __name__ == "__main__":
    main()  # 只有直接运行本文件时才执行
