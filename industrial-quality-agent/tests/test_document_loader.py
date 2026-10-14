from pathlib import Path

import pytest

from rag.documents import (
    KnowledgeDocument,
    clean_markdown,
    load_markdown_documents,
    split_document_into_chunks,
)


def test_load_markdown_documents(tmp_path: Path) -> None:
    """加载器应只读取 Markdown，并提取稳定的文档信息。"""
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "sop.md").write_text(
        "# 点胶作业指导书\n\n检查胶量和温度。\n",
        encoding="utf-8",
    )
    (knowledge_dir / "case.md").write_text(
        "没有一级标题\n\n这是案例内容。\n",
        encoding="utf-8",
    )
    (knowledge_dir / "ignore.txt").write_text(
        "不应加载这个文件。",
        encoding="utf-8",
    )

    documents = load_markdown_documents(knowledge_dir)

    assert [document.doc_id for document in documents] == ["case", "sop"]
    assert documents[0].title == "case"
    assert documents[1].title == "点胶作业指导书"
    assert "检查胶量和温度" in documents[1].content
    assert documents[1].source_path == knowledge_dir / "sop.md"


def test_load_markdown_documents_requires_directory(tmp_path: Path) -> None:
    """目录不存在时应抛出清晰的 FileNotFoundError。"""
    missing_dir = tmp_path / "missing"

    with pytest.raises(FileNotFoundError, match="知识目录不存在"):
        load_markdown_documents(missing_dir)


def test_clean_markdown_removes_notice_and_extra_blank_lines() -> None:
    """清洗应删除固定声明、统一换行并压缩连续空行。"""
    markdown = (
        "> 本文档为合成演示内容，不来自任何公司。\r\n"
        "\r\n"
        "# 点胶作业指导书\r\n"
        "\r\n"
        "\r\n"
        "确认胶量和压力。\r\n"
        "\r\n"
        "\r\n"
    )

    cleaned = clean_markdown(markdown)

    assert cleaned == "# 点胶作业指导书\n\n确认胶量和压力。"
    assert "合成演示" not in cleaned


def test_split_document_without_subheadings_returns_one_chunk() -> None:
    """短文档没有子标题时，应保留标题和正文并生成一个片段。"""
    document = KnowledgeDocument(
        doc_id="sop_dispensing",
        title="点胶作业指导书",
        content="> 本文档为合成演示内容。\n\n# 点胶作业指导书\n\n确认胶量。\n",
        source_path=Path("sop_dispensing.md"),
    )

    chunks = split_document_into_chunks(document)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "sop_dispensing#0"
    assert chunks[0].content == "# 点胶作业指导书\n\n确认胶量。"
    assert chunks[0].doc_id == document.doc_id
    assert chunks[0].source_path == document.source_path


def test_split_document_by_subheadings_and_keeps_context() -> None:
    """多个子标题应按主题切分，并给后续片段补充文档标题。"""
    document = KnowledgeDocument(
        doc_id="sop_cleaning",
        title="清洗作业指导书",
        content=(
            "# 清洗作业指导书\n\n"
            "总则：发现异常时停止作业。\n\n"
            "## 开机检查\n\n"
            "检查喷嘴和清洗液液位。\n\n"
            "## 异常处理\n\n"
            "记录异常并通知设备负责人。\n"
        ),
        source_path=Path("sop_cleaning.md"),
    )

    chunks = split_document_into_chunks(document)

    assert [chunk.chunk_id for chunk in chunks] == [
        "sop_cleaning#0",
        "sop_cleaning#1",
        "sop_cleaning#2",
    ]
    assert "总则" in chunks[0].content
    assert chunks[1].content.startswith("# 清洗作业指导书")
    assert "## 开机检查" in chunks[1].content
    assert chunks[2].content.startswith("# 清洗作业指导书")
    assert "## 异常处理" in chunks[2].content
