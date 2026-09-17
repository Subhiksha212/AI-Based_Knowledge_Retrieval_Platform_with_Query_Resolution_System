"""
Shared SentenceTransformer model loader.

Supports both:
1. Local SentenceTransformer execution.
2. Remote ML execution via ngrok / REMOTE_MODEL_URL (ideal for Render deployment).
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Union

import requests
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


class RemoteEmbeddingModel:
    """
    HTTP Proxy client for Sentence Transformer models hosted via ngrok.
    Prevents high memory usage on cloud deployments like Render.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.endpoint = f"{self.base_url}/api/models/embed"

    def encode(
        self,
        sentences: Union[str, List[str]],
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
    ) -> List[List[float]]:
        if isinstance(sentences, str):
            sentences = [sentences]

        response = requests.post(
            self.endpoint,
            json={"texts": list(sentences)},
            headers={"User-Agent": "QueryNest-Render-Backend"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["embeddings"]

    def get_embedding_dimension(self) -> int:
        return 384


@lru_cache(maxsize=1)
def get_embedding_model() -> Union[SentenceTransformer, RemoteEmbeddingModel]:
    """
    Return the shared embedding model.
    Uses RemoteEmbeddingModel if REMOTE_MODEL_URL is defined, else local SentenceTransformer.
    """
    remote_url = os.getenv("REMOTE_MODEL_URL") or os.getenv("NGROK_MODEL_URL")
    if remote_url:
        print(f"[Embedding] Using remote ML model tunnel: {remote_url}")
        return RemoteEmbeddingModel(remote_url)

    print("[Embedding] Using local SentenceTransformer model.")
    return SentenceTransformer(EMBEDDING_MODEL_NAME)
