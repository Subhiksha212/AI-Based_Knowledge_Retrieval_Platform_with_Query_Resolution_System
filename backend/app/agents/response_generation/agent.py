"""
Milestone 2 - Response Generation Agent.

Pipeline:

    Retrieved chunks
          ↓
    Grounded prompt construction
          ↓
    Shared Groq LLM
          ↓
    Citation extraction
          ↓
    Retrieval-aware confidence
          ↓
    Validated LLMResponse

The agent is domain-agnostic and works with any retrieved
knowledge-base chunks.
"""

from __future__ import annotations

import re
from typing import Any

from .llm_call_groq import GroqHandler
from .prompt_builder import build_prompt
from .schemas import (
    LLMResponse,
    Source,
)


# ---------------------------------------------------------------------
# Shared LLM handler
# ---------------------------------------------------------------------

_handler: GroqHandler | None = None


def _get_handler() -> GroqHandler:
    """
    Return the shared Groq handler.

    The handler is created once and reused across requests.
    """

    global _handler

    if _handler is None:
        _handler = GroqHandler()

    return _handler


# ---------------------------------------------------------------------
# Chunk helpers
# ---------------------------------------------------------------------

def _get_chunk_metadata(
    chunk: Any,
) -> dict[str, Any]:
    """
    Safely extract metadata from a retrieved chunk.
    """

    if not isinstance(chunk, dict):
        return {}

    metadata = chunk.get("metadata", {})

    if not isinstance(metadata, dict):
        return {}

    return metadata


def _get_chunk_id(
    chunk: Any,
    index: int,
) -> str:
    """
    Return a stable chunk ID.

    Canonical field:
        chunk_id

    Backward-compatible fallback:
        id
    """

    if isinstance(chunk, dict):

        chunk_id = chunk.get("chunk_id")

        if chunk_id:
            return str(chunk_id)

        # Backward compatibility with older retrieval output.
        legacy_id = chunk.get("id")

        if legacy_id:
            return str(legacy_id)

    return f"chunk_{index}"


def _get_source_name(
    chunk: Any,
    chunk_id: str,
) -> str:
    """
    Get a human-readable source name.
    """

    metadata = _get_chunk_metadata(chunk)

    filename = metadata.get("filename")

    if filename:
        return str(filename)

    source = metadata.get("source")

    if source:
        return str(source)

    return chunk_id


def _get_relevance_score(
    chunk: Any,
) -> float | None:
    """
    Safely read the Retrieval Agent relevance score.
    """

    if not isinstance(chunk, dict):
        return None

    value = chunk.get("relevance_score")

    if value is None:
        return None

    try:
        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------
# Citation extraction
# ---------------------------------------------------------------------

def _extract_citation_numbers(
    answer: str,
    chunk_count: int,
) -> list[int]:
    """
    Extract valid citation numbers from the LLM answer.

    Supported formats:

        [1]
        [2]
        [3]

    and also:

        【1】
        【2】
        【3】

    The second form is handled defensively because some LLM outputs
    may use full-width Unicode brackets even when the prompt requests
    normal square brackets.

    Invalid citation numbers are ignored.
    """

    if not answer or chunk_count <= 0:
        return []

    matches = re.findall(
        r"(?:\[(\d+)\]|【(\d+)】)",
        answer,
    )

    numbers: set[int] = set()

    for normal_match, unicode_match in matches:

        value = (
            normal_match
            or unicode_match
        )

        try:
            number = int(value)
        except ValueError:
            continue

        if 1 <= number <= chunk_count:
            numbers.add(number)

    return sorted(numbers)


def _normalize_citation_markers(
    answer: str,
) -> str:
    """
    Normalize Unicode citation markers to the standard project format.

    Example:

        【1】 → [1]
        【2】 → [2]
    """

    if not answer:
        return answer

    return re.sub(
        r"【(\d+)】",
        r"[\1]",
        answer,
    )


# ---------------------------------------------------------------------
# Source construction
# ---------------------------------------------------------------------

def _build_sources(
    answer: str,
    chunks: list[dict[str, Any] | str],
) -> list[Source]:
    """
    Convert cited chunk numbers into Source objects.

    Each source preserves:

        - filename/source
        - reference number
        - chunk ID
        - relevance score
        - metadata
    """

    citation_numbers = _extract_citation_numbers(
        answer,
        len(chunks),
    )

    sources: list[Source] = []

    for number in citation_numbers:

        chunk = chunks[number - 1]

        chunk_id = _get_chunk_id(
            chunk,
            number,
        )

        metadata = _get_chunk_metadata(
            chunk,
        )

        source_name = _get_source_name(
            chunk,
            chunk_id,
        )

        relevance_score = _get_relevance_score(
            chunk,
        )

        sources.append(
            Source(
                source=source_name,
                reference=f"[{number}]",
                chunk_id=chunk_id,
                relevance_score=relevance_score,
                metadata=metadata,
            )
        )

    return sources


# ---------------------------------------------------------------------
# Confidence calculation
# ---------------------------------------------------------------------

def _calculate_citation_coverage(
    sources: list[Source],
    chunks: list[dict[str, Any] | str],
) -> float:
    """
    Measure how much of the supplied context was cited.

    This is a coverage signal, not a correctness probability.
    """

    if not chunks:
        return 0.0

    return min(
        1.0,
        len(sources) / len(chunks),
    )


def _calculate_retrieval_quality(
    sources: list[Source],
) -> float:
    """
    Calculate the average relevance score of cited chunks.

    If relevance scores are unavailable, use a conservative
    fallback for cited sources.
    """

    scores = [
        source.relevance_score
        for source in sources
        if source.relevance_score is not None
    ]

    if not scores:
        return 0.50 if sources else 0.0

    return sum(scores) / len(scores)


def _estimate_confidence(
    sources: list[Source],
    chunks: list[dict[str, Any] | str],
) -> float:
    """
    Estimate confidence from:

        1. Retrieval quality
        2. Citation coverage

    This is a heuristic confidence indicator, NOT a calibrated
    probability of factual correctness.
    """

    if not chunks:
        return 0.0

    if not sources:
        # Context was available but the model failed to produce
        # a recognizable citation.
        return 0.15

    retrieval_quality = (
        _calculate_retrieval_quality(
            sources
        )
    )

    citation_coverage = (
        _calculate_citation_coverage(
            sources,
            chunks,
        )
    )

    # Retrieval quality is intentionally dominant because not every
    # valid answer needs to cite every retrieved candidate.
    confidence = (
        retrieval_quality * 0.70
        + citation_coverage * 0.30
    )

    return round(
        max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        ),
        2,
    )


# ---------------------------------------------------------------------
# Main response-generation entry point
# ---------------------------------------------------------------------

def generate_response(
    question: str,
    chunks: list[dict[str, Any] | str],
) -> LLMResponse:
    """
    Generate a grounded answer from Retrieval Agent results.

    Args:
        question:
            Original user question.

        chunks:
            Final filtered/ranked chunks returned by the Retrieval Agent.

    Returns:
        Validated LLMResponse.
    """

    # ---------------------------------------------------------------
    # Validate question
    # ---------------------------------------------------------------

    if (
        not isinstance(question, str)
        or not question.strip()
    ):
        return LLMResponse(
            answer="",
            sources=[],
            confidence=0.0,
        )

    # ---------------------------------------------------------------
    # Validate retrieved context
    # ---------------------------------------------------------------

    valid_chunks = [
        chunk
        for chunk in (chunks or [])
        if (
            isinstance(chunk, dict)
            and str(
                chunk.get(
                    "content",
                    "",
                )
            ).strip()
        )
        or (
            isinstance(chunk, str)
            and chunk.strip()
        )
    ]

    if not valid_chunks:

        return LLMResponse(
            answer=(
                "I don't have enough information "
                "in the available knowledge base "
                "to answer that."
            ),
            sources=[],
            confidence=0.0,
        )

    # ---------------------------------------------------------------
    # Build grounded prompt
    # ---------------------------------------------------------------

    prompt = build_prompt(
        question,
        valid_chunks,
    )

    handler = _get_handler()

    # ---------------------------------------------------------------
    # Generate answer
    # ---------------------------------------------------------------

    try:

        answer = handler.generate(
            prompt
        )

    except (
        RuntimeError,
        ValueError,
    ):

        return LLMResponse(
            answer=(
                "Sorry, I couldn't generate "
                "an answer right now."
            ),
            sources=[],
            confidence=0.0,
        )

    # ---------------------------------------------------------------
    # Normalize citation formatting
    # ---------------------------------------------------------------

    answer = _normalize_citation_markers(
        answer
    )

    # ---------------------------------------------------------------
    # Extract sources
    # ---------------------------------------------------------------

    sources = _build_sources(
        answer,
        valid_chunks,
    )

    # ---------------------------------------------------------------
    # Estimate confidence
    # ---------------------------------------------------------------

    confidence = _estimate_confidence(
        sources,
        valid_chunks,
    )

    return LLMResponse(
        answer=answer,
        sources=sources,
        confidence=confidence,
    )


# ---------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------

if __name__ == "__main__":

    sample_chunks = [
        {
            "chunk_id": "chunk_001",
            "content": (
                "Employees are entitled to "
                "12 days of paid leave per year."
            ),
            "metadata": {
                "filename": "hr_policy.pdf",
                "chunk_index": 3,
            },
            "relevance_score": 0.92,
        },
        {
            "chunk_id": "chunk_002",
            "content": (
                "Sick leave longer than "
                "2 days requires a medical certificate."
            ),
            "metadata": {
                "filename": "hr_policy.pdf",
                "chunk_index": 4,
            },
            "relevance_score": 0.81,
        },
    ]

    result = generate_response(
        "How many leave days do employees get?",
        sample_chunks,
    )

    print(
        result.model_dump_json(
            indent=4
        )
    )