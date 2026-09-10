"""
embedding.py

Loads the embedding model and generates embeddings
for text chunks using Sentence Transformers.
"""

from sentence_transformers import SentenceTransformer

def load_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model.
    Downloads the model only once and uses the local cache afterwards.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks(
    model: SentenceTransformer,
    chunks: list[str]
) -> list[list[float]]:
    """
    Generate embeddings for text chunks.

    Args:
        model: Loaded embedding model
        chunks: List of text chunks

    Returns:
        List of embedding vectors
    """

    if not chunks:
        return []

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings.tolist()


def get_embedding_dimension(model: SentenceTransformer) -> int:
    """
    Returns the embedding dimension.
    """
    return model.get_embedding_dimension()


if __name__ == "__main__":

    model = load_embedding_model()

    sample_chunks = [
        "Artificial Intelligence is transforming industries.",
        "Machine Learning is a subset of AI.",
        "RAG combines retrieval with generation."
    ]

    embeddings = embed_chunks(model, sample_chunks)

    print("Embedding Dimension:", get_embedding_dimension(model))
    print("Number of Chunks:", len(sample_chunks))
    print("Number of Embeddings:", len(embeddings))
    print("Vector Length:", len(embeddings[0]))