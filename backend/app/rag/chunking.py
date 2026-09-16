from __future__ import annotations

import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150
LAYOUT_COLUMN_BREAK = "--- Layout Column Break ---"

# Generic document-structure headings. These are intentionally domain-agnostic.

_MAJOR_HEADING_PATTERNS = (
    re.compile(
        r"^\s*(?:#+\s*)?"
        r"(?:milestone|chapter|section|phase|module|part|unit|appendix)"
        r"\b.*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:#+\s*)?"
        r"(?:table\s+of\s+contents|introduction|conclusion|"
        r"references|bibliography|abstract|summary)\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:#+\s*)?\d+(?:\.\d+)*[.)]?\s+"
        r"[A-Z][^\n]{2,120}$",
        re.IGNORECASE,
    ),
)

# Common "label:" headings such as:
# "Objectives:", "Agents to be Implemented:", "Features:", etc.
_LABEL_HEADING_PATTERN = re.compile(
    r"^\s*(?:#+\s*)?[A-Za-z][A-Za-z0-9 &/()_-]{2,100}:\s*$"
)


def _split_normal_text(text: str) -> list[str]:
    """Split ordinary document text using the project's existing strategy."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def _is_major_heading(line: str) -> bool:
    """
    Return True when a line is likely to introduce a logical document section.

    This is deliberately conservative. Numbered task lines such as
    "1. Build Retrieval Agent..." are NOT treated as headings unless they
    match a major-heading pattern or a clear heading label.
    """
    stripped = line.strip()

    if not stripped:
        return False

    # Markdown-style headings are always strong structural signals.
    if re.match(r"^#{1,6}\s+\S+", stripped):
        return True

    for pattern in _MAJOR_HEADING_PATTERNS:
        if pattern.match(stripped):
            return True

    if _LABEL_HEADING_PATTERN.match(stripped):
        return True

    return False


def _looks_like_task_or_bullet(line: str) -> bool:
    """
    Identify common list/task lines so they are not mistaken for section
    headings.
    """
    stripped = line.strip()

    if not stripped:
        return False

    if re.match(r"^[•●▪◦\-–—]\s+\S+", stripped):
        return True

    if re.match(r"^\d+[.)]\s+\S+", stripped):
        return True

    if re.match(r"^[a-zA-Z][.)]\s+\S+", stripped):
        return True

    return False


def _split_logical_sections(text: str) -> list[str]:
    """
    Preserve logical document sections when clear headings are present.

    A section begins at a recognized major heading and continues until the
    next recognized major heading. Text before the first recognized heading
    remains part of a leading section.

    This is useful for PDFs/DOCX/TXT that contain structured sections such as
    "Milestone 1", "Milestone 2", "Chapter 3", "Section 4", etc., while still
    falling back safely for ordinary prose.
    """
    lines = text.splitlines()

    if len(lines) < 2:
        return [text.strip()] if text.strip() else []

    sections: list[list[str]] = []
    current: list[str] = []
    found_heading = False

    for line in lines:
        stripped = line.strip()

        # Preserve blank lines inside the current section.
        if not stripped:
            if current:
                current.append("")
            continue

        is_heading = _is_major_heading(stripped)

        # Avoid interpreting numbered/bulleted tasks as major headings.
        if is_heading and _looks_like_task_or_bullet(stripped):
            is_heading = False

        if is_heading:
            found_heading = True

            if current:
                section_text = "\n".join(current).strip()
                if section_text:
                    sections.append(current)
                current = []

            current.append(stripped)
            continue

        current.append(line)

    if current:
        section_text = "\n".join(current).strip()
        if section_text:
            sections.append(current)

    if not found_heading:
        return [text.strip()] if text.strip() else []

    return [
        "\n".join(section).strip()
        for section in sections
        if "\n".join(section).strip()
    ]


def _chunk_logical_sections(
    text: str,
) -> list[str]:
    """
    Preserve detected logical sections as complete chunks whenever possible.

    If a logical section is larger than DEFAULT_CHUNK_SIZE, it is split using
    the existing recursive splitter. This keeps long sections scalable without
    changing the established fallback behavior.
    """
    logical_sections = _split_logical_sections(text)

    if not logical_sections:
        return []

    chunks: list[str] = []

    for section in logical_sections:
        if len(section) <= DEFAULT_CHUNK_SIZE:
            chunks.append(section)
        else:
            chunks.extend(_split_normal_text(section))

    return chunks


def _split_layout_aware_text(text: str) -> list[str]:
    """
    Split OCR text while respecting explicit layout-column boundaries.

    Each visual column is processed independently. Within each column, logical
    document sections are preserved before falling back to recursive splitting.
    """
    sections = [
        section.strip()
        for section in text.split(LAYOUT_COLUMN_BREAK)
        if section.strip()
    ]

    if len(sections) <= 1:
        return _chunk_logical_sections(text)

    chunks: list[str] = []

    for section in sections:
        chunks.extend(_chunk_logical_sections(section))

    return chunks


def chunk_text(text: str) -> list[str]:
    """
    Split extracted document text into retrieval-friendly chunks.

    Behavior:
      1. Empty input -> no chunks.
      2. Image/layout-aware OCR -> respect visual-column boundaries and then
         preserve logical document sections.
      3. Structured text with clear headings -> preserve each logical section
         as a chunk when it fits within the normal chunk size.
      4. Long sections -> use the existing RecursiveCharacterTextSplitter.
      5. Ordinary unstructured text -> retain the original splitter behavior.

    The important optimization is that a section such as:

        Milestone 3 (Week 5-6)
        1. ...
        2. ...
        3. ...
        4. ...

    stays together instead of being split arbitrarily between unrelated
    milestone chunks, while no domain-specific term is hard-coded.
    """
    if not text or not text.strip():
        return []

    if LAYOUT_COLUMN_BREAK in text:
        return _split_layout_aware_text(text)

    logical_sections = _split_logical_sections(text)

    # If no meaningful document structure was detected, retain the original
    # behavior exactly.
    if len(logical_sections) <= 1:
        return _split_normal_text(text)

    return _chunk_logical_sections(text)


if __name__ == "__main__":
    sample = """Project Milestones

Milestone 1 (Week 1-2)
1. Study RAG architecture.
2. Design system architecture.
3. Develop ingestion.
4. Validate retrieval.

Milestone 2 (Week 3-4)
1. Build Query Understanding Agent.
2. Build Retrieval Agent.
3. Build Response Generation Agent.
4. Implement orchestration.

Milestone 3 (Week 5-6)
1. Build Clarification Agent.
2. Build Conversation Memory Agent.
3. Integrate Voice Input and Text-to-Speech.
4. Build Response Transparency Panel.

Milestone 4 (Week 7-8)
1. Develop Analytics.
2. Conduct end-to-end testing.
3. Optimize retrieval quality.
4. Prepare documentation.
"""

    chunks = chunk_text(sample)

    print("Chunking check")
    print(f"Generated chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n--- CHUNK {index} ---")
        print(chunk)
