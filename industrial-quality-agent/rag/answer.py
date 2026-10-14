"""RAG 第八步：答案生成与拒答（阶段 0：先用假生成器把流程和测试跑通）。

这一层的职责边界：
- 负责：把检索到的资料拼成三段式提示词，再交给大模型生成回答。
- 不负责：找资料（那是 KnowledgeBase.search 的职责）。
- 不负责：把文字变成向量（那是 EmbeddingModel 的职责）。

为什么先写 FakeGenerator：
- 真实大模型慢、要联网、可能花钱，不适合放进自动化测试。
- 先把“检索 → 拼提示词 → 生成 → 带来源返回”这条流程用测试锁住，
  以后换模型只换实现，流程和测试都不用改。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from rag.vector_store import SearchResult

# 拒答时统一使用的固定文案。写成常量后，业务代码和测试引用同一个字符串，
# 将来改文案只需要改这一处。
REFUSAL_MESSAGE = "知识库中没有相关内容。"

# 系统指令：定角色、定规矩，是三段式提示词的第一段。
SYSTEM_INSTRUCTION = """你是工业质量知识库助手，只依据【资料】回答问题，不得编造。
如果【资料】中没有答案，必须回答：知识库中没有相关内容。
回答时请在句末标注来源编号，例如 [1]。"""


@dataclass(frozen=True)
class AnswerResult:
    """一次问答的完整结果。"""

    question: str                                              # 用户原始问题
    answer: str                                                # 最终回答，可能是拒答文案
    contexts: list[SearchResult] = field(default_factory=list)  # 这次用到的检索资料
    refused: bool = False                                      # 是否走了拒答分支
    top_score: float = 0.0                                     # 检索最高分，便于排查“为什么被拒答”


def build_context_block(contexts: list[SearchResult]) -> str:
    """把检索结果拼成提示词里的【资料】区：每段带编号和来源文件名。"""
    blocks: list[str] = []
    for index, result in enumerate(contexts, start=1):
        # 只显示文件名，不把完整本地路径交给模型，避免泄露无关信息。
        source_name = result.chunk.source_path.name
        content = result.chunk.content.strip()
        blocks.append(f"[{index}] 来源：{source_name}\n{content}")
    return "\n\n".join(blocks)


def build_prompt(question: str, contexts: list[SearchResult]) -> str:
    """按“系统指令 + 资料 + 用户问题”三段式拼出完整提示词。"""
    return (
        "[系统指令]\n"
        + SYSTEM_INSTRUCTION
        + "\n\n[资料]\n"
        + build_context_block(contexts)
        + "\n\n[用户问题]\n"
        + question.strip()
    )


class AnswerGenerator(ABC):
    """答案生成器接口：只规定“长什么样”，不规定“怎么实现”。"""

    @abstractmethod
    def generate(self, question: str, contexts: list[SearchResult]) -> str:
        """根据用户问题和检索资料，返回一段自然语言回答。"""
        raise NotImplementedError


class FakeGenerator(AnswerGenerator):
    """假生成器：不加载任何模型，直接返回固定回答。

    用途：让测试跑得快、不花钱、不联网，同时把“收到了什么问题、哪些资料”记录下来，
    这样测试就能断言流程有没有把正确的资料交给它。
    """

    def __init__(self, answer: str = "【假模型】根据资料，这里应该是真实回答。") -> None:
        self._answer = answer
        # 每次调用的入参都存下来，测试才能检查“到底有没有被调用”“传了什么进去”。
        self.calls: list[tuple[str, list[SearchResult]]] = []

    def generate(self, question: str, contexts: list[SearchResult]) -> str:
        self.calls.append((question, list(contexts)))
        return self._answer


class RagAnswerer:
    """把检索和生成串起来，并按分数阈值决定要不要拒答。"""

    def __init__(
        self,
        retriever: object,              # 任何带 search(question, top_k) 的对象，例如 KnowledgeBase
        generator: AnswerGenerator,     # 依赖注入：换模型不用改这个类的代码
        min_score: float = 0.5,         # 最高分低于它就拒答；真实阈值要用评测集校准
        top_k: int = 3,
    ) -> None:
        self.retriever = retriever
        self.generator = generator
        self.min_score = min_score
        self.top_k = top_k

    def answer(self, question: str) -> AnswerResult:
        """完整流程：检索 → 取最高分 → 拒答或生成。"""
        contexts = self.retriever.search(question, top_k=self.top_k)              # 第 1 步：找资料
        top_score = max((result.score for result in contexts), default=0.0)       # 第 2 步：看最高分

        # 第 3 步：资料不够相关就直接拒答。注意这里连大模型都不调用：
        # 既省钱，也不给幻觉留任何机会。
        if not contexts or top_score < self.min_score:
            return AnswerResult(
                question=question,
                answer=REFUSAL_MESSAGE,
                contexts=list(contexts),
                refused=True,
                top_score=top_score,
            )

        # 第 4 步：资料够相关，才拼提示词并调用生成器。
        answer = self.generator.generate(question, contexts)
        return AnswerResult(
            question=question,
            answer=answer,
            contexts=list(contexts),
            refused=False,
            top_score=top_score,
        )


def main() -> None:
    """演示：打印三段式提示词，并分别走“能回答”和“拒答”两条路径。"""
    from rag.pipeline import KnowledgeBase

    base = KnowledgeBase(Path("data/synthetic_demo/knowledge"))
    base.build()

    answerer = RagAnswerer(base, FakeGenerator(), min_score=0.5)

    question = "胶量偏多可能是什么原因？"
    print("=" * 64)
    print("三段式提示词长这样：")
    print("=" * 64)
    print(build_prompt(question, base.search(question, top_k=2)))
    print()

    print("=" * 64)
    print("完整流程演示（这里用假生成器，所以回答是固定的）：")
    print("=" * 64)
    for item in ["胶量偏多可能是什么原因？", "公司年假有多少天？"]:
        result = answerer.answer(item)
        tag = "拒答" if result.refused else "回答"
        print(f"[{tag}] {item}")
        print(f"        最高分={result.top_score:.4f}  回答={result.answer}")
    print()
    print("结论：只有分数过线才会调用真实大模型；拒答分支一次模型都不调用。")


if __name__ == "__main__":
    main()   # 只有直接运行本文件时才执行