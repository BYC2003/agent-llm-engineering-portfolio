"""内存向量库（InMemoryVectorStore）的最小演示脚本。

目的：亲眼看到向量库内部到底存了什么、search() 到底做了哪几步。

注意：
- 本脚本用的是 2 维“教学向量”，不是真实文字的 Embedding。
- 真实项目里向量由 Embedding 模型产出，这里手写出来方便观察。

运行方式（在 industrial-quality-agent 目录下执行）：
    & "..\实战项目\python-foundation\.venv\Scripts\python.exe" rag_demo_vector_store.py
"""

from pathlib import Path

from rag.documents import KnowledgeChunk          # 知识片段：真正要交给大模型阅读的正文
from rag.similarity import cosine_similarity      # 余弦相似度：判断两个向量方向像不像
from rag.vector_store import InMemoryVectorStore  # 本次主角：内存向量库


def make_chunk(chunk_id: str, content: str) -> KnowledgeChunk:
    """按真实字段构造一个知识片段（真实项目里这些字段由文档加载和切分产生）。"""
    return KnowledgeChunk(
        chunk_id=chunk_id,               # 片段编号：用于定位和引用
        doc_id="sop_dispensing",         # 所属文档编号
        title="点胶作业参数",              # 所属文档标题
        content=content,                 # 正文：最终要交给大模型阅读的内容
        source_path=Path("data/synthetic_demo/knowledge/sop_dispensing.md"),  # 来源文件
    )


def main() -> None:
    store = InMemoryVectorStore()  # 新建一个空的向量库

    # 往库里放 3 个片段，每个片段都配一个“意思坐标”（2 维教学向量）
    store.add(make_chunk("chunk_a", "点胶量偏高容易溢胶和拉丝。"), [1.0, 0.0])
    store.add(make_chunk("chunk_b", "清洗喷嘴可以恢复点胶一致性。"), [0.6, 0.8])
    store.add(make_chunk("chunk_c", "设备点检表需要每天签字确认。"), [0.0, 1.0])

    query = [1.0, 0.0]  # 用户问题的“意思坐标”（真实场景由同一个 Embedding 模型产出）

    print("=== 第 1 步：向量库里一条记录存了哪两样东西 ===")
    for chunk, vector in store._records:  # 演示脚本故意偷看内部结构；正式代码应走公开方法
        print(f"  {chunk.chunk_id} | 向量={vector} | 正文={chunk.content}")

    print()
    print("=== 第 2 步：拿问题向量和每条记录的向量逐个算余弦相似度 ===")
    for chunk, vector in store._records:
        score = cosine_similarity(query, list(vector))  # 分数越高 = 方向越接近 = 意思越相关
        print(f"  问题 与 {chunk.chunk_id} 的相似度 = {score:.4f}")

    print()
    print("=== 第 3 步：按分数从高到低排序，取前 top_k 个 ===")
    for rank, result in enumerate(store.search(query, top_k=2), start=1):
        print(
            f"  第{rank}名 | {result.chunk.chunk_id} | 分数={result.score:.4f} "
            f"| 交给大模型的正文={result.chunk.content} "
            f"| 引用来源={result.chunk.source_path}"
        )
    print("  （注意：只返回了候选，答案还没有生成；写答案是大模型的事）")

    print()
    print("=== 第 4 步：不合法的向量会被拒绝 ===")
    bad_cases = [
        ([], "空向量"),
        ([0.0, 0.0], "零向量（长度为 0，没有方向）"),
        ([1.0, 0.0, 0.0], "维度与库中已有记录不一致"),
    ]
    for bad_vector, reason in bad_cases:
        try:
            store.add(make_chunk("chunk_bad", "不该进库的片段"), bad_vector)  # 尝试写入
        except ValueError as error:                                          # 被拒绝则捕获
            print(f"  拒绝 {reason} -> {error}")


if __name__ == "__main__":
    # 只有直接运行本文件时才执行 main()，被别的文件 import 时不执行
    main()
