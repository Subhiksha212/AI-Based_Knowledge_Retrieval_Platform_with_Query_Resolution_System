"""
Prompt construction for the Response Generation Agent.

The prompt is domain-agnostic and instructs the LLM to:
1. Answer only from retrieved context.
2. Avoid unsupported claims.
3. Respect the section/topic requested by the user.
4. Preserve complete lists when the context contains them.
5. Clearly state when the context is insufficient.
6. Cite the retrieved chunks using [1], [2], etc.
"""

from __future__ import annotations

from typing import Any


def _get_chunk_id(
    chunk: dict[str, Any],
) -> str | None:
    """
    Return the canonical chunk ID.

    `chunk_id` is the current Retrieval Agent contract.
    `id` is retained as a backward-compatible fallback.
    """

    chunk_id = chunk.get("chunk_id")

    if chunk_id:
        return str(chunk_id)

    legacy_id = chunk.get("id")

    if legacy_id:
        return str(legacy_id)

    return None


def format_chunks(
    chunks: list[dict[str, Any] | str],
) -> str:
    """
    Format retrieved chunks into numbered source blocks.
    """

    if not chunks:
        return ""

    lines: list[str] = []

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        if isinstance(chunk, dict):

            content = str(
                chunk.get(
                    "content",
                    "",
                )
            ).strip()

            if not content:
                continue

            chunk_id = _get_chunk_id(
                chunk
            )

            metadata = chunk.get(
                "metadata",
                {},
            )

            if not isinstance(
                metadata,
                dict,
            ):
                metadata = {}

            filename = metadata.get(
                "filename"
            )

            chunk_index = metadata.get(
                "chunk_index"
            )

            source_parts: list[str] = []

            if filename:
                source_parts.append(
                    f"source={filename}"
                )

            if chunk_index is not None:
                source_parts.append(
                    f"chunk={chunk_index}"
                )

            if chunk_id:
                source_parts.append(
                    f"chunk_id={chunk_id}"
                )

            source_label = (
                " | ".join(source_parts)
                if source_parts
                else "source=unknown"
            )

            lines.append(
                f"[{index}] {source_label}\n"
                f"{content}"
            )

        else:

            content = str(
                chunk
            ).strip()

            if not content:
                continue

            lines.append(
                f"[{index}]\n{content}"
            )

    return "\n\n".join(
        lines
    )


def build_prompt(
    question: str,
    chunks: list[dict[str, Any] | str],
) -> str:
    """
    Build the grounded answer-generation prompt.
    """

    context = format_chunks(
        chunks
    )

    if not context:
        context = (
            "No relevant context was retrieved."
        )

    prompt = f"""
You are the Response Generation Agent of a knowledge retrieval system.

Answer the user's question using ONLY the retrieved context below.

GROUNDING RULES:
1. Do not use outside knowledge.
2. Do not invent facts, values, names, dates, policies, explanations,
   or list items.
3. Every factual statement in your answer must be supported by the
   retrieved context.
4. If the retrieved context does not contain enough information,
   clearly state that the available knowledge base does not contain
   enough information.
5. Never fill missing information using your general knowledge.

SECTION AND TOPIC RULES:
6. Identify what specific topic, section, list, or entity the user
   is asking about.
7. Answer only from context that is relevant to that requested topic.
8. Do not replace one section with another semantically related section.
   For example, do not answer an "Outcomes" question using "Milestones",
   "Modules", "Agents", or "Project Activities" unless the context
   explicitly shows that they are part of the requested answer.
9. If the user asks about a named section, prefer content belonging
   to that section and its continuation.
10. Do not combine unrelated sections merely because they contain
    similar words.

LIST AND COMPLETENESS RULES:
11. If the user asks for "all", "every", "the complete list",
    "what are the", "which are the", or otherwise requests a list,
    return all relevant items that are explicitly present in the
    retrieved context.
12. Do not invent a missing list item.
13. Do not silently replace missing items with information from
    another section.
14. If the retrieved context contains only part of a requested list,
    say that the available context is incomplete instead of guessing.

CITATION RULES:
15. Cite factual claims using the source labels assigned by this prompt:
    [1], [2], [3], etc.
16. The numbers [1], [2], [3], etc. refer ONLY to the retrieved
    context blocks created by this system.
17. IMPORTANT: Citation/reference numbers that appear inside the
    retrieved document content are part of the document itself.
    They are NOT source labels for this answer.
18. Never copy citation or reference numbers found inside the document
    text. For example, if a retrieved document contains "[7]" or
    "[7, 8]", do not use those numbers as citations unless the
    corresponding retrieved context block is actually numbered [7] or
    [8].
19. Use only source labels that exist in the retrieved context blocks.
20. Every citation must correspond to the retrieved chunk that directly
    supports the factual claim.
21. If multiple retrieved chunks support the answer, cite each relevant
    context-block label.
22. Never invent, guess, or derive citation numbers from the document
    content.
23. Keep citation formatting exactly like [1], [2], [3].
24. Do not use Unicode citation brackets such as 【1】.
25. Do not cite the document's own bibliography, footnotes, numbered
    references, list numbers, or cross-references as if they were
    retrieved-context source labels.

ANSWER STYLE:
26. Be concise and direct.
27. For a numbered list in the source, preserve the numbered-list
    structure when practical.
28. Do not mention retrieval internals unless necessary to explain
    why the requested information is unavailable.
29. If the user asks generally about a document (e.g. "tell me about..."),
    and the retrieved context contains ANY text from it (even sparse text like
    names, dates, or URLs), summarize whatever is available and cite it using
    [1], rather than claiming there is not enough information.

Retrieved Context:
------------------
{context}
------------------

User Question:
{question}

Answer:
"""

    return prompt.strip()


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
            "relevance_score": 0.91,
        },
        {
            "chunk_id": "chunk_002",
            "content": (
                "Sick leave requests longer than "
                "2 days require a medical certificate."
            ),
            "metadata": {
                "filename": "hr_policy.pdf",
                "chunk_index": 4,
            },
            "relevance_score": 0.82,
        },
    ]

    prompt = build_prompt(
        question=(
            "How many leave days do employees get?"
        ),
        chunks=sample_chunks,
    )

    print(prompt)