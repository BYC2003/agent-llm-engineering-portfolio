from dataclasses import dataclass
from pathlib import Path


SYNTHETIC_NOTICE_PREFIX = "> 本文档为合成演示内容"


@dataclass(frozen=True)
class KnowledgeDocument:
    """表示一份已经加载的知识文档。"""

    doc_id: str
    title: str
    content: str
    source_path: Path


@dataclass(frozen=True)
class KnowledgeChunk:
    """表示一份可被检索和引用的知识片段。"""

    chunk_id: str
    doc_id: str
    title: str
    content: str
    source_path: Path


def extract_title(markdown: str, fallback: str) -> str:
    """提取 Markdown 的第一个一级标题，找不到时使用回退标题。"""
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def load_markdown_documents(directory: Path) -> list[KnowledgeDocument]:
    """读取目录中的全部 Markdown 文件，并转换为文档对象。"""
    if not directory.exists():
        raise FileNotFoundError(f"知识目录不存在：{directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"知识路径不是目录：{directory}")

    documents: list[KnowledgeDocument] = []

    # 按文件名排序，确保每次加载顺序稳定。
    for path in sorted(directory.glob("*.md"), key=lambda item: item.name):
        # utf-8-sig 可以兼容带 BOM 的 UTF-8 Markdown 文件。
        content = path.read_text(encoding="utf-8-sig")
        documents.append(
            KnowledgeDocument(
                doc_id=path.stem,
                title=extract_title(content, fallback=path.stem),
                content=content,
                source_path=path,
            )
        )

    return documents


def clean_markdown(markdown: str) -> str:
    """移除固定演示声明，并统一换行和多余空行。"""
    # 先统一不同操作系统产生的换行符，避免后续规则互相干扰。
    normalized = markdown.replace("\r\n", "\n").replace("\r", "\n")
    cleaned_lines: list[str] = []
    previous_line_was_blank = False

    for line in normalized.splitlines():
        stripped = line.strip()

        # 合成数据声明是演示元数据，不应参与问题检索。
        if stripped.startswith(SYNTHETIC_NOTICE_PREFIX):
            continue

        # 连续空行只保留一个，文件开头和结尾的空行统一删除。
        if not stripped:
            if previous_line_was_blank:
                continue
            cleaned_lines.append("")
            previous_line_was_blank = True
            continue

        # 去掉行尾空格，但保留 Markdown 标题和正文的原始含义。
        cleaned_lines.append(line.rstrip())
        previous_line_was_blank = False

    return "\n".join(cleaned_lines).strip()


def split_document_into_chunks(document: KnowledgeDocument) -> list[KnowledgeChunk]:
    """把一份知识文档清洗后切分为检索片段。"""
    cleaned_content = clean_markdown(document.content)
    if not cleaned_content:
        return []

    sections = _split_markdown_sections(cleaned_content)
    chunks: list[KnowledgeChunk] = []

    for index, section in enumerate(sections):
        chunks.append(
            KnowledgeChunk(
                # 索引从 0 开始，便于看到片段在一份文档中的先后顺序。
                chunk_id=f"{document.doc_id}#{index}",
                doc_id=document.doc_id,
                title=document.title,
                content=section,
                source_path=document.source_path,
            )
        )

    return chunks


def _split_markdown_sections(markdown: str) -> list[str]:
    """按二级及更深标题切分，并给每个片段补充文档标题上下文。"""
    lines = markdown.splitlines()
    document_title = _find_document_title(lines)
    headings_indexes = [
        index
        for index, line in enumerate(lines)
        if _is_subheading(line.strip())
    ]

    # 当前小文档通常只有一个一级标题；没有子标题时整篇就是一个片段。
    if not headings_indexes:
        return [markdown.strip()]

    sections: list[str] = []
    first_heading_index = headings_indexes[0]

    # 第一个子标题之前的内容通常介绍整篇文档，单独保留为第一个片段。
    if first_heading_index > 0:
        intro = "\n".join(lines[:first_heading_index]).strip()
        if intro:
            sections.append(intro)

    for position, start_index in enumerate(headings_indexes):
        # 当前子标题到下个子标题之间的内容属于同一主题。
        end_index = (
            headings_indexes[position + 1]
            if position + 1 < len(headings_indexes)
            else len(lines)
        )
        section = "\n".join(lines[start_index:end_index]).strip()
        if not section:
            continue

        # 后续片段带上文档标题，避免脱离原文档后失去上下文。
        if document_title and not section.startswith(document_title):
            section = f"{document_title}\n\n{section}"
        sections.append(section)

    return sections


def _find_document_title(lines: list[str]) -> str:
    """找出 Markdown 中第一个一级标题。"""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped
    return ""


def _is_subheading(line: str) -> bool:
    """判断一行是否为二级到六级 Markdown 标题。"""
    marker = line.split(maxsplit=1)[0] if line else ""
    return 2 <= len(marker) <= 6 and set(marker) == {"#"}
