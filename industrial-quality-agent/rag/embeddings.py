"""把中文文字转换成向量的封装（基于 fastembed + ONNX Runtime，纯 CPU 运行）。

职责边界（和向量库对得上）：
- 只负责“文字 → 向量”。
- 不负责保存向量、不负责排序、不负责写答案；那些是向量库和大模型的事。

模型文件默认下载到 D:\AI-Models\fastembed，避免占用 C 盘。
"""

from __future__ import annotations

from pathlib import Path

# 默认模型：中文、512 维、约 95 MB、MIT 许可
DEFAULT_MODEL_NAME = "BAAI/bge-small-zh-v1.5"

# 模型缓存目录：按磁盘规则放 D 盘，不占 C 盘
DEFAULT_CACHE_DIR = Path(r"D:\AI-Models\fastembed")


class EmbeddingModel:
    """把文字转换成固定长度向量的模型封装。"""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        cache_dir: Path = DEFAULT_CACHE_DIR,
    ) -> None:
        # 延迟导入：只有真正创建对象时才加载 onnxruntime，启动更快
        from fastembed import TextEmbedding

        self.model_name = model_name                                              # 模型名字，便于日志和排查
        self.cache_dir = cache_dir                                                # 模型文件所在目录
        cache_dir.mkdir(parents=True, exist_ok=True)                              # 目录不存在时自动创建
        # 第一次运行会自动下载模型到 cache_dir；之后直接读本地缓存，不再联网
        self._model = TextEmbedding(model_name=model_name, cache_dir=str(cache_dir))

    @property
    def dimension(self) -> int:
        """返回向量维度（本模型为 512）。"""
        return len(self.embed_texts(["测试"])[0])

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """把多段文字转换成向量，返回普通 list（方便放进向量库）。"""
        if not texts:
            raise ValueError("待转换的文字列表不能为空")

        # fastembed 返回的是生成器，每次产出一个 numpy 数组；
        # 这里统一转成 Python 的 float 列表，避免后续代码依赖 numpy 类型。
        return [[float(value) for value in vector] for vector in self._model.embed(texts)]


def main() -> None:
    """演示：真实中文文字 → 真实向量 → 余弦相似度排序。"""
    from rag.similarity import cosine_similarity  # 复用上一节写好的余弦相似度

    model = EmbeddingModel()  # 第一次运行会下载模型（约 95 MB），之后走本地缓存

    # 三句“知识片段”和一句“用户问题”
    chunks = [
        "点胶量偏高容易溢胶和拉丝。",
        "清洗喷嘴可以恢复点胶一致性。",
        "设备点检表需要每天签字确认。",
    ]
    question = "点胶量偏高会有什么问题？"

    # 文字 → 向量（真实模型算出来的，不再是手写的 2 维教学数据）
    chunk_vectors = model.embed_texts(chunks)
    question_vector = model.embed_texts([question])[0]

    print(f"模型：{model.model_name}")
    print(f"向量维度：{len(question_vector)}")
    print(f"问题的前 5 个数字：{[round(value, 4) for value in question_vector[:5]]}")
    print()

    # 逐个算余弦相似度并按分数从高到低排序（这就是 search() 内部做的事）
    scored = [
        (chunk, cosine_similarity(question_vector, vector))
        for chunk, vector in zip(chunks, chunk_vectors)
    ]
    scored.sort(key=lambda item: item[1], reverse=True)

    print(f"问题：{question}")
    for rank, (chunk, score) in enumerate(scored, start=1):
        print(f"  第{rank}名 分数={score:.4f}  {chunk}")


if __name__ == "__main__":
    main()  # 只有直接运行本文件时才执行
