"""
Dedicated embedding model for query-theme analysis.

This model is intentionally kept separate from the RAG embedding module so
the RAG embedding model can be optimized/replaced independently later.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer


THEME_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_theme_embedding_model() -> SentenceTransformer:
    """Load the analytics-only embedding model once per backend process."""
    return SentenceTransformer(THEME_EMBEDDING_MODEL)


def embed_queries(queries: list[str]) -> list[list[float]]:
    """Return normalized embeddings for the supplied query texts."""
    if not queries:
        return []

    model = load_theme_embedding_model()
    embeddings = model.encode(
        queries,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return embeddings.tolist()
