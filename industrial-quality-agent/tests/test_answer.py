"""答案生成与拒答测试：全程使用假检索器和假生成器，不联网、不花钱、不加载真实模型。"""

from pathlib import Path

import pytest

from rag.answer import (
    REFUSAL_MESSAGE,
    SYSTEM_INSTRUCTION,
    AnswerGenerator,
    FakeGenerator,
    RagAnswerer,
    build_context_block,
    build_prompt,
)
from rag.documents import KnowledgeChunk
from rag.vector_store import SearchResult


def make_result(
    score: float,
    name: str = "fmea_dispensing.md",
    content: str = "失效模式：胶量偏多。",
) -> SearchResult:
    """造一条假的检索结果，用来单独测试“生成”和“拒答”逻辑。"""
    chunk = KnowledgeChunk(
        chunk_id="c1",
        doc_id=Path(name).stem,
        title="示例标题",
        content=content,
        source_path=Path(name),
    )
    return SearchResult(chunk=chunk, score=score)


class FakeRetriever:
    """假检索器：返回预先准备好的结果，把“检索”和“生成”隔离开。"""

    def __init__(self, results: list[SearchResult]) -> None:
        self._results = results
        self.questions: list[str] = []      # 记录被问了什么

    def search(self, question: str, top_k: int = 3) -> list[SearchResult]:
        self.questions.append(question)
        return self._results[:top_k]


def test_answer_generator_cannot_be_instantiated() -> None:
    """AnswerGenerator 是接口，不允许直接创建对象。"""
    with pytest.raises(TypeError):
        AnswerGenerator()      # type: ignore[abstract]


def test_prompt_has_three_sections() -> None:
    """提示词必须同时含系统指令、资料、用户问题三段。"""
    prompt = build_prompt("胶量偏多可能是什么原因？", [make_result(0.9)])

    assert "[系统指令]" in prompt
    assert "[资料]" in prompt
    assert "[用户问题]" in prompt
    assert SYSTEM_INSTRUCTION in prompt
    assert "胶量偏多可能是什么原因？" in prompt


def test_context_block_numbers_sources() -> None:
    """资料区要按顺序编号并写出来源文件名，模型才能照编号标注引用。"""
    block = build_context_block(
        [
            make_result(0.9),
            make_result(0.8, name="sop_cleaning.md", content="清洗喷嘴可以恢复一致性。"),
        ]
    )

    assert block.startswith("[1] 来源：fmea_dispensing.md")
    assert "[2] 来源：sop_cleaning.md" in block


def test_answer_calls_generator_and_returns_sources() -> None:
    """资料足够相关时，应调用生成器，并带回答案、资料和分数。"""
    generator = FakeGenerator(answer="压力漂移和设备温度异常。[1]")
    answerer = RagAnswerer(FakeRetriever([make_result(0.82)]), generator, min_score=0.5)

    result = answerer.answer("胶量偏多可能是什么原因？")

    assert result.refused is False
    assert result.answer == "压力漂移和设备温度异常。[1]"
    assert result.top_score == pytest.approx(0.82)
    assert len(result.contexts) == 1
    # 关键断言：生成器确实收到了问题，也收到了资料
    assert len(generator.calls) == 1
    assert generator.calls[0][0] == "胶量偏多可能是什么原因？"
    assert generator.calls[0][1][0].chunk.source_path.name == "fmea_dispensing.md"


def test_low_score_refuses_without_calling_generator() -> None:
    """最高分低于阈值时直接拒答，并且一次都不调用大模型。"""
    generator = FakeGenerator()
    answerer = RagAnswerer(FakeRetriever([make_result(0.31)]), generator, min_score=0.5)

    result = answerer.answer("公司年假有多少天？")

    assert result.refused is True
    assert result.answer == REFUSAL_MESSAGE
    assert generator.calls == []          # 没有调用生成器，省钱且不会幻觉


def test_score_equal_to_threshold_is_not_refused() -> None:
    """边界情况：分数正好等于阈值算通过（代码里用的是小于号）。"""
    generator = FakeGenerator()
    answerer = RagAnswerer(FakeRetriever([make_result(0.5)]), generator, min_score=0.5)

    result = answerer.answer("边界问题")

    assert result.refused is False
    assert len(generator.calls) == 1


def test_empty_contexts_refuses() -> None:
    """一条资料都没检索到时也要拒答，不能拿着空资料去问大模型。"""
    generator = FakeGenerator()
    answerer = RagAnswerer(FakeRetriever([]), generator, min_score=0.5)

    result = answerer.answer("任意问题")

    assert result.refused is True
    assert result.top_score == 0.0
    assert generator.calls == []


def test_top_k_limits_contexts() -> None:
    """top_k 要真的传到检索器，决定拿几段资料喂给大模型。"""
    retriever = FakeRetriever([make_result(0.9), make_result(0.8), make_result(0.7)])
    answerer = RagAnswerer(retriever, FakeGenerator(), min_score=0.5, top_k=2)

    result = answerer.answer("问题")

    assert len(result.contexts) == 2