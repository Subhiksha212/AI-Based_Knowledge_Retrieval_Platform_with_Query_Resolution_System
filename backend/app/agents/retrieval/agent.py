"""
Milestone 2 - Retrieval Agent.

Coordinates:
1. Semantic retrieval
2. Exact retrieval
3. Candidate merging
4. Query-aware reranking
5. Low-confidence filtering
6. Section-aware context expansion
7. Final context selection
"""

from __future__ import annotations

import re
from typing import Any

from app.agents.query_understanding.schemas import (
    QueryUnderstandingResult,
)
from app.agents.retrieval.exact_search import search_exact
from app.agents.retrieval.reranker import (
    diversify_results,
    rerank_results,
)
from app.agents.retrieval.semantic_search import search_semantic


class RetrievalAgent:
    """
    Query-aware Retrieval Agent.

    Uses Query Understanding output to control semantic search,
    exact search, reranking, filtering, and section-aware context
    expansion.
    """

    COMPLETENESS_TERMS = {
        "all",
        "every",
        "complete",
        "entire",
        "list",
        "lists",
        "enumerate",
        "enumerates",
        "enumerated",
    }

    COMPLETENESS_PHRASES = (
        "what are the",
        "which are the",
        "what are all",
        "list the",
        "list all",
        "all the",
        "complete list",
        "full list",
    )

    COMPLETENESS_CANDIDATE_MULTIPLIER = 2

    def __init__(
        self,
        *,
        default_k: int = 3,
        semantic_candidate_multiplier: int = 5,
        relevance_threshold: float = 0.20,
        enable_diversification: bool = True,
    ) -> None:

        if default_k < 1:
            raise ValueError(
                "default_k must be at least 1."
            )

        if semantic_candidate_multiplier < 1:
            raise ValueError(
                "semantic_candidate_multiplier must be at least 1."
            )

        if not 0.0 <= relevance_threshold <= 1.0:
            raise ValueError(
                "relevance_threshold must be between 0.0 and 1.0."
            )

        self.default_k = default_k
        self.semantic_candidate_multiplier = (
            semantic_candidate_multiplier
        )
        self.relevance_threshold = relevance_threshold
        self.enable_diversification = enable_diversification

    # Query-shape detection

    @classmethod
    def _is_completeness_query(
        cls,
        query_analysis: QueryUnderstandingResult,
    ) -> bool:
        """
        Detect queries asking for complete lists, sections,
        enumerations, or sets of items.
        """

        if not isinstance(
            query_analysis,
            QueryUnderstandingResult,
        ):
            return False

        query_text = (
            query_analysis.search_query
            + " "
            + " ".join(query_analysis.keywords)
        ).strip().lower()

        words = set(
            query_text.replace("?", " ")
            .replace(",", " ")
            .split()
        )

        if words.intersection(
            cls.COMPLETENESS_TERMS
        ):
            return True

        return any(
            phrase in query_text
            for phrase in cls.COMPLETENESS_PHRASES
        )

    # Candidate merging

    @staticmethod
    def _normalize_content(
        content: Any,
    ) -> str:

        if not isinstance(content, str):
            return ""

        return " ".join(
            content.lower().split()
        )

    @staticmethod
    def _merge_terms(
        first: list[str] | None,
        second: list[str] | None,
    ) -> list[str]:

        merged: list[str] = []
        seen: set[str] = set()

        for term in [
            *(first or []),
            *(second or []),
        ]:
            if not isinstance(term, str):
                continue

            cleaned = term.strip()

            if not cleaned:
                continue

            key = cleaned.lower()

            if key not in seen:
                seen.add(key)
                merged.append(cleaned)

        return merged

    def _merge_results(
        self,
        semantic_results: list[dict[str, Any]],
        exact_results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        merged: dict[str, dict[str, Any]] = {}

        for result in semantic_results:

            if not isinstance(result, dict):
                continue

            content = result.get("content", "")
            key = self._normalize_content(content)

            if not key:
                continue

            item = dict(result)

            item["matched_terms"] = list(
                result.get(
                    "matched_terms",
                    [],
                )
                or []
            )

            merged[key] = item

        for result in exact_results:

            if not isinstance(result, dict):
                continue

            content = result.get("content", "")
            key = self._normalize_content(content)

            if not key:
                continue

            if key not in merged:

                item = dict(result)

                item["matched_terms"] = list(
                    result.get(
                        "matched_terms",
                        [],
                    )
                    or []
                )

                merged[key] = item
                continue

            existing = merged[key]

            existing["matched_terms"] = (
                self._merge_terms(
                    existing.get("matched_terms"),
                    result.get("matched_terms"),
                )
            )

            if (
                existing.get("distance") is None
                and result.get("distance") is not None
            ):
                existing["distance"] = result["distance"]

        return list(
            merged.values()
        )

    # Validation

    @staticmethod
    def _validate_query_analysis(
        query_analysis: QueryUnderstandingResult,
    ) -> None:

        if not isinstance(
            query_analysis,
            QueryUnderstandingResult,
        ):
            raise TypeError(
                "query_analysis must be a "
                "QueryUnderstandingResult."
            )

        if not query_analysis.search_query.strip():
            raise ValueError(
                "QueryUnderstandingResult.search_query "
                "cannot be empty."
            )

    # Chunk metadata

    @staticmethod
    def _document_id(
        result: dict[str, Any],
    ) -> str | None:

        metadata = result.get(
            "metadata",
            {},
        )

        if not isinstance(metadata, dict):
            return None

        value = metadata.get("document_id")

        if value is None:
            return None

        return str(value)

    @staticmethod
    def _chunk_index(
        result: dict[str, Any],
    ) -> int | None:

        metadata = result.get(
            "metadata",
            {},
        )

        if not isinstance(metadata, dict):
            return None

        value = metadata.get("chunk_index")

        try:
            return int(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _chunk_key(
        result: dict[str, Any],
    ) -> tuple[str | None, int | None]:

        return (
            RetrievalAgent._document_id(result),
            RetrievalAgent._chunk_index(result),
        )

    # Section detection

    @staticmethod
    def _looks_like_heading(
        line: str,
    ) -> bool:
        """
        Generic heading detector.

        It does not depend on domain-specific words.
        """

        cleaned = line.strip()

        if not cleaned:
            return False

        if cleaned.endswith(":"):
            return True

        if re.match(
            r"^\d+(?:\.\d+)*\.?\s+\S+",
            cleaned,
        ):
            return True

        words = cleaned.split()

        if len(words) <= 8 and cleaned.isupper():
            return True

        return False

    @classmethod
    def _extract_heading(
        cls,
        content: str,
    ) -> str | None:
        """
        Return the first heading-like line in a chunk.
        """

        if not content:
            return None

        for line in content.splitlines():

            cleaned = line.strip()

            if cls._looks_like_heading(cleaned):
                return cleaned.rstrip(":").strip().lower()

        return None

    @classmethod
    def _query_section_terms(
        cls,
        query_analysis: QueryUnderstandingResult,
    ) -> list[str]:
        """
        Extract generic section terms from the query.

        Uses Query Understanding keywords rather than hard-coded
        domain names.
        """

        terms: list[str] = []

        for keyword in query_analysis.keywords:

            if not isinstance(keyword, str):
                continue

            cleaned = keyword.strip().lower()

            if not cleaned:
                continue

            if cleaned in cls.COMPLETENESS_TERMS:
                continue

            if len(cleaned) < 3:
                continue

            terms.append(cleaned)

        return terms

    @classmethod
    def _section_score(
        cls,
        result: dict[str, Any],
        section_terms: list[str],
    ) -> int:
        """
        Score a chunk for section relevance based on its heading.
        """

        heading = cls._extract_heading(
            str(
                result.get(
                    "content",
                    "",
                )
            )
        )

        if not heading:
            return 0

        score = 0

        for term in section_terms:
            if term in heading:
                score += 1

        return score

    # Section-aware context expansion

    def _expand_section_context(
        self,
        ranked_candidates: list[dict[str, Any]],
        candidate_pool: list[dict[str, Any]],
        query_analysis: QueryUnderstandingResult,
        final_k: int,
    ) -> list[dict[str, Any]]:
        """
        Preserve the logical section around the strongest relevant
        chunk when the query asks for a complete list/section.
        """

        if not ranked_candidates:
            return []

        section_terms = self._query_section_terms(
            query_analysis
        )

        pool_by_position: dict[
            tuple[str | None, int | None],
            dict[str, Any],
        ] = {}

        for candidate in candidate_pool:

            if not isinstance(candidate, dict):
                continue

            document_id = self._document_id(
                candidate
            )

            chunk_index = self._chunk_index(
                candidate
            )

            if (
                document_id is None
                or chunk_index is None
            ):
                continue

            pool_by_position[
                (
                    document_id,
                    chunk_index,
                )
            ] = candidate

        if not pool_by_position:
            return ranked_candidates[:final_k]

        selected: list[
            dict[str, Any]
        ] = []

        selected_keys: set[
            tuple[str | None, int | None]
        ] = set()

        # Prefer the strongest candidate whose heading matches
        # the query's section terms.
        anchor = None

        if section_terms:

            section_candidates = sorted(
                ranked_candidates,
                key=lambda item: (
                    self._section_score(
                        item,
                        section_terms,
                    ),
                    item.get(
                        "relevance_score",
                        0.0,
                    ),
                ),
                reverse=True,
            )

            for candidate in section_candidates:

                if self._section_score(
                    candidate,
                    section_terms,
                ) > 0:
                    anchor = candidate
                    break

        if anchor is None:
            anchor = (
                ranked_candidates[0]
                if ranked_candidates
                else None
            )

        if anchor is None:
            return []

        anchor_document = self._document_id(
            anchor
        )

        anchor_index = self._chunk_index(
            anchor
        )

        if (
            anchor_document is None
            or anchor_index is None
        ):
            return ranked_candidates[:final_k]

        selected_keys.add(
            (
                anchor_document,
                anchor_index,
            )
        )

        selected.append(anchor)

        # Prefer the immediately following chunks from the same
        # document because lists/sections usually continue forward.
        next_index = anchor_index + 1

        while len(selected) < final_k:

            next_key = (
                anchor_document,
                next_index,
            )

            next_chunk = pool_by_position.get(
                next_key
            )

            if next_chunk is None:
                break

            heading = self._extract_heading(
                str(
                    next_chunk.get(
                        "content",
                        "",
                    )
                )
            )

            # If a new strong heading begins, stop the current section.
            if heading:

                heading_score = self._section_score(
                    next_chunk,
                    section_terms,
                )

                if (
                    section_terms
                    and heading_score == 0
                ):
                    break

            if next_key not in selected_keys:

                selected_keys.add(
                    next_key
                )

                selected.append(
                    next_chunk
                )

            next_index += 1

        # If not enough continuation chunks were found, fill remaining
        # slots with the best ranked candidates.
        if len(selected) < final_k:

            for candidate in ranked_candidates:

                key = self._chunk_key(
                    candidate
                )

                if key in selected_keys:
                    continue

                selected_keys.add(key)
                selected.append(candidate)

                if len(selected) >= final_k:
                    break

        return selected[:final_k]

    # Main retrieval method

    def retrieve(
        self,
        query_analysis: QueryUnderstandingResult,
        *,
        k: int | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:

        self._validate_query_analysis(
            query_analysis
        )

        final_k = (
            k
            if k is not None
            else self.default_k
        )

        if final_k < 1:
            raise ValueError(
                "k must be at least 1."
            )

        search_query = (
            query_analysis.search_query.strip()
        )

        exact_terms = list(
            query_analysis.exact_terms
        )

        keywords = list(
            query_analysis.keywords
        )

        query_type = (
            query_analysis.query_type
        )

        is_completeness_query = (
            self._is_completeness_query(
                query_analysis
            )
        )

        # 1. Semantic candidate generation

        multiplier = (
            self.semantic_candidate_multiplier
            * self.COMPLETENESS_CANDIDATE_MULTIPLIER
            if is_completeness_query
            else self.semantic_candidate_multiplier
        )

        semantic_k = max(
            10,
            final_k * multiplier,
        )

        semantic_results = search_semantic(
            query=search_query,
            k=semantic_k,
            user_id=user_id,
        )

        if not isinstance(
            semantic_results,
            list,
        ):
            semantic_results = []

        # 2. Exact candidate generation

        exact_results: list[
            dict[str, Any]
        ] = []

        if exact_terms:

            exact_results = search_exact(
                exact_terms,
                user_id=user_id,
            )

            if not isinstance(
                exact_results,
                list,
            ):
                exact_results = []

        # 3. Merge semantic + exact candidates

        candidates = self._merge_results(
            semantic_results=semantic_results,
            exact_results=exact_results,
        )

        # 4. Query-aware reranking

        ranked_results = rerank_results(
            candidates,
            exact_terms=exact_terms,
            keywords=keywords,
            query_type=query_type,
            exact_candidates_found=bool(
                exact_results
            ),
            relevance_threshold=(
                self.relevance_threshold
            ),
        )

        # 5. Preserve a larger ranked pool for context assembly

        ranked_for_context = (
            ranked_results[
                :max(
                    final_k * 2,
                    6,
                )
            ]
            if is_completeness_query
            else ranked_results[:final_k]
        )

        # 6. Section-aware context expansion

        if is_completeness_query:

            final_results = (
                self._expand_section_context(
                    ranked_candidates=ranked_for_context,
                    candidate_pool=candidates,
                    query_analysis=query_analysis,
                    final_k=final_k,
                )
            )

        else:

            if self.enable_diversification:

                final_results = diversify_results(
                    ranked_results,
                    max_results=final_k,
                )

            else:

                final_results = ranked_results[
                    :final_k
                ]

        final_results = final_results[
            :final_k
        ]

        # 7. Return structured result

        return {
            "success": True,
            "query": query_analysis.original_query,
            "search_query": search_query,
            "query_type": query_type,
            "results": final_results,
            "count": len(final_results),
            "retrieval": {
                "semantic_candidates": len(
                    semantic_results
                ),
                "exact_candidates": len(
                    exact_results
                ),
                "merged_candidates": len(
                    candidates
                ),
                "returned_results": len(
                    final_results
                ),
                "completeness_query": (
                    is_completeness_query
                ),
            },
        }

    def run(
        self,
        query_analysis: QueryUnderstandingResult,
        *,
        k: int | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:

        return self.retrieve(
            query_analysis,
            k=k,
            user_id=user_id,
        )


if __name__ == "__main__":

    from app.core.llm import get_llm
    from app.agents.query_understanding.agent import (
        QueryUnderstandingAgent,
    )

    print("=" * 70)
    print("MILESTONE 2 - RETRIEVAL AGENT TEST")
    print("=" * 70)

    llm = get_llm()

    query_agent = QueryUnderstandingAgent(llm)

    retrieval_agent = RetrievalAgent(
        default_k=3,
        semantic_candidate_multiplier=5,
        relevance_threshold=0.20,
        enable_diversification=True,
    )

    test_queries = [
        "What are all five agents to be implemented in the project?",
        "What are the outcomes of the project?",
        "What is the email of Name_1?",
    ]

    for query in test_queries:

        print("\n" + "=" * 70)
        print("QUERY:")
        print(query)
        print("=" * 70)

        analysis = query_agent.run(query)

        print(
            "\nCompleteness query:",
            retrieval_agent._is_completeness_query(
                analysis
            ),
        )

        result = retrieval_agent.run(
            analysis,
            k=3,
        )

        print(
            "\nRetrieval statistics:"
        )
        print(
            result["retrieval"]
        )

        print(
            "\nResults:"
        )

        for index, item in enumerate(
            result["results"],
            start=1,
        ):

            print(
                f"\nResult {index}"
            )

            print(
                "Chunk ID:",
                item.get("chunk_id"),
            )

            print(
                "Metadata:",
                item.get("metadata"),
            )

            print(
                "Relevance:",
                item.get("relevance_score"),
            )

            print(
                "Content preview:",
                item.get(
                    "content",
                    "",
                )[:300].replace(
                    "\n",
                    " ",
                ),
            )