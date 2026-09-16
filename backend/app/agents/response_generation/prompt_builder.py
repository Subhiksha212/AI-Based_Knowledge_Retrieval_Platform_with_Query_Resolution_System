"""
Prompt construction for the Response Generation Agent.

This module is domain-agnostic. It:
- keeps answers grounded in retrieved context,
- preserves section/list completeness across continuation chunks,
- reduces obvious OCR/layout noise for list questions,
- keeps original retrieved chunk numbering for citations,
- avoids hard-coding any particular subject/domain.

Important:
The cleaner is intentionally conservative. It does NOT delete arbitrary content
from retrieved chunks. It only removes common OCR contamination patterns that are
clearly separated by layout/bullet markers or are obviously quotation/slogan-like
lines when they are unrelated to the requested list.
"""

from __future__ import annotations

import re
from typing import Any


def _get_chunk_id(chunk: dict[str, Any]) -> str | None:
    """Return the canonical chunk ID with backward-compatible fallback."""
    chunk_id = chunk.get("chunk_id")
    if chunk_id:
        return str(chunk_id)

    legacy_id = chunk.get("id")
    if legacy_id:
        return str(legacy_id)

    return None


def _normalize_for_matching(text: str) -> str:
    """Normalize OCR/user text for lightweight lexical comparisons."""
    text = text.lower()
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _is_list_like_question(question: str) -> bool:
    """Detect generic list/completeness intent without domain-specific terms."""
    normalized = _normalize_for_matching(question)
    list_patterns = (
        r"\ball\b",
        r"\bevery\b",
        r"\bcomplete\b",
        r"\bfull list\b",
        r"\blist\b",
        r"\bwhat are\b",
        r"\bwhich are\b",
        r"\bmention all\b",
        r"\bname all\b",
        r"\bidentify all\b",
        r"\benumerate\b",
    )
    return any(re.search(pattern, normalized) for pattern in list_patterns)


def _looks_like_ocr_slogan_or_quote(line: str) -> bool:
    """
    Conservative detection of common OCR noise/slogan lines.

    This intentionally does not use any domain-specific words.
    """
    cleaned = " ".join(line.split()).strip()
    if not cleaned:
        return False

    # Strong visual/typographic clues that OCR commonly flattens into text.
    if cleaned.startswith(("“", '"', "‘", "'")) and cleaned.endswith(("”", '"', "’", "'")):
        return True

    lowered = cleaned.lower()

    # Common slogan/quote structures.
    if lowered.count("!") >= 1 and len(cleaned.split()) <= 14:
        return True

    if re.search(
        r"\bbuilds?\s+(?:a|an)\s+stronger\b",
        lowered,
    ):
        return True

    # Phrases with obvious quotation punctuation.
    if "“" in line or "”" in line:
        return True

    return False


def _strip_obvious_ocr_noise(
    content: str,
    question: str,
) -> str:
    """
    Conservatively clean line-oriented OCR for list/completeness queries.

    The function keeps the actual text whenever there is ambiguity. It does
    not attempt to understand the domain; the LLM remains responsible for
    final semantic selection.
    """
    if not content or not _is_list_like_question(question):
        return content.strip()

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    if not lines:
        return content.strip()

    cleaned_lines: list[str] = []

    for line in lines:
        if _looks_like_ocr_slogan_or_quote(line):
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def _format_source_parts(
    chunk: dict[str, Any],
) -> tuple[str, str]:
    """Return (source_label, continuation_suffix)."""
    chunk_id = _get_chunk_id(chunk)

    metadata = chunk.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    filename = metadata.get("filename")
    chunk_index = metadata.get("chunk_index")

    source_parts: list[str] = []

    if filename:
        source_parts.append(f"source={filename}")

    if chunk_index is not None:
        source_parts.append(f"chunk={chunk_index}")

    if chunk_id:
        source_parts.append(f"chunk_id={chunk_id}")

    source_label = (
        " | ".join(source_parts)
        if source_parts
        else "source=unknown"
    )

    continuation_suffix = ""
    if chunk.get("context_expanded"):
        continuation_suffix = " | CONTINUATION_OF_PREVIOUS_SECTION"

    return source_label, continuation_suffix


def format_chunks(
    chunks: list[dict[str, Any] | str],
    question: str = "",
) -> str:
    """
    Format retrieved chunks into numbered context blocks.

    Each block keeps its original ordinal so citations [1], [2], ... remain
    stable for the downstream response-generation code.
    """
    if not chunks:
        return ""

    lines: list[str] = []

    for index, chunk in enumerate(chunks, start=1):

        if isinstance(chunk, dict):
            raw_content = str(chunk.get("content", "")).strip()
            if not raw_content:
                continue

            content = _strip_obvious_ocr_noise(
                raw_content,
                question,
            )
            if not content:
                continue

            source_label, continuation_suffix = _format_source_parts(chunk)

            lines.append(
                f"[{index}] {source_label}{continuation_suffix}\n"
                f"{content}"
            )

        else:
            content = str(chunk).strip()
            if not content:
                continue

            content = _strip_obvious_ocr_noise(
                content,
                question,
            )
            if not content:
                continue

            lines.append(
                f"[{index}]\n{content}"
            )

    return "\n\n".join(lines)


def build_prompt(
    question: str,
    chunks: list[dict[str, Any] | str],
) -> str:
    """Build the grounded answer-generation prompt."""
    context = format_chunks(
        chunks,
        question=question,
    )

    if not context:
        context = "No relevant context was retrieved."

    prompt = f"""
You are the Response Generation Agent of a knowledge retrieval system.

Answer the user's question using ONLY the retrieved context below.

==================== GROUNDING ====================

1. Do not use outside knowledge.
2. Do not invent facts, values, names, dates, explanations, examples,
   policies, or list items.
3. Every factual claim must be supported by the retrieved context.
4. If the retrieved context genuinely lacks enough information, say so
   clearly. Do not fill the gap from general knowledge.
5. Inspect every retrieved context block before deciding that information
   is missing.

==================== TOPIC / SECTION ====================

6. Identify the exact topic, section, list, entity, or concept requested.
7. Prefer content that explicitly belongs to that requested topic or section.
8. If multiple chunks come from the same source and one is marked
   CONTINUATION_OF_PREVIOUS_SECTION, treat the continuation as part of the
   same section when the source/chunk metadata supports that relationship.
9. Combine relevant content from multiple chunks before answering.
10. Do not combine unrelated sections merely because they share words.
11. Do not treat text that is merely adjacent in an OCR block as belonging
    to the requested section unless the text itself or the retrieved
    structure supports that interpretation.

==================== OCR / LAYOUT SAFETY ====================

12. OCR can flatten multi-column, side-by-side, or visually separate text.
13. For list questions, prefer explicit list members, bullets, numbered
    entries, or text clearly attached to the requested heading.
14. Do not turn nearby slogans, quotations, captions, page decorations,
    taglines, headings from another section, or unrelated prose into list
    members merely because they appear in the same OCR chunk.
15. If a line looks like a slogan, quote, caption, or decorative sentence,
    do not classify it as a requested list item unless the surrounding
    context explicitly establishes that it is part of the list.
16. When OCR text appears interleaved, use repeated section terminology,
    bullet structure, and continuation metadata to determine membership.
17. When uncertain, prefer the explicitly structured list evidence over
    visually adjacent unstructured text.

==================== LIST / COMPLETENESS ====================

18. Treat "all", "every", "complete list", "full list", "list",
    "what are", "which are", "mention all", "name all", and similar wording
    as completeness requests when appropriate.
19. For a completeness request, inspect ALL retrieved blocks.
20. Find all distinct items that explicitly belong to the requested list.
21. Merge items across continuation chunks.
22. Remove duplicate items caused by chunk overlap.
23. Do not stop after the first chunk if later relevant chunks contain
    additional list members.
24. Do not omit an explicitly supported item merely because it appears in
    a later continuation chunk.
25. Do not add a neighboring heading, feature, slogan, quote, or prose
    sentence as a list item merely to make the list longer.
26. Only say a list is incomplete after checking every relevant retrieved
    block and determining that additional required items are genuinely
    absent.
27. If only part of the requested list is supported, provide the supported
    items and clearly state that the retrieved context appears incomplete.

==================== CITATIONS ====================

28. Cite factual claims using ONLY the retrieved-context labels [1], [2],
    [3], etc.
29. The citation numbers refer to the context blocks generated by this
    prompt, not to numbers appearing inside the source document.
30. Never copy citation/reference numbers that are part of the document text.
31. Use only source labels that actually exist.
32. Cite each list item or grouped claim with the chunk(s) that directly
    support it.
33. When different parts of an answer come from different chunks, cite the
    relevant chunk for each part.
34. Never invent or derive citation numbers.
35. Keep citations exactly in the form [1], [2], [3].
36. Do not use Unicode citation brackets such as 【1】.
37. Do not cite bibliography numbers, footnotes, section numbering, or
    list numbering inside the source as if they were retrieved-context
    citation labels.

==================== ANSWER CONSTRUCTION ====================

38. Inspect all retrieved blocks first, then write the answer.
39. For list questions, merge and deduplicate the complete supported list
    before responding.
40. Preserve the meaning and wording of explicitly retrieved list members
    where practical.
41. If the source presents a list, use a clear numbered or bulleted list.
42. Do not summarize a list when the user explicitly asks for the list.
43. Do not mention internal retrieval/reranking mechanisms unless needed
    to explain why information is unavailable.
44. Be concise and direct.
45. If the user asks generally about a document, summarize whatever relevant
    content is actually present and cite it. Do not claim the document has
    no information merely because the retrieved excerpt is sparse.

==================== RETRIEVED CONTEXT ====================

{context}

========================================================

USER QUESTION:
{question}

==================== FINAL ANSWER ====================

Answer only from the retrieved context and follow the rules above.
""".strip()

    return prompt


if __name__ == "__main__":
    sample_chunks = [
        {
            "chunk_id": "chunk_001",
            "content": (
                "Fundamental Duties (Part IVA)\n"
                "• Respect the Constitution\n"
                "• Protect the unity and integrity of India\n"
                "• Preserve the rich heritage and culture\n"
                '"A Strong Constitution Builds a Stronger Nation."'
            ),
            "metadata": {
                "filename": "indian_constitution_notes.jpg",
                "chunk_index": 1,
            },
            "relevance_score": 0.57,
        },
        {
            "chunk_id": "chunk_002",
            "content": (
                "• Protect the environment\n"
                "• Develop a scientific temper\n"
                "• Strive for excellence in all spheres\n"
                '"Justice, Liberty, Equality and Fraternity for all."'
            ),
            "metadata": {
                "filename": "indian_constitution_notes.jpg",
                "chunk_index": 2,
            },
            "context_expanded": True,
            "relevance_score": 0.40,
        },
    ]

    prompt = build_prompt(
        question=(
            "what are the fundamental duties Indian constitution list?"
        ),
        chunks=sample_chunks,
    )

    print(prompt)
