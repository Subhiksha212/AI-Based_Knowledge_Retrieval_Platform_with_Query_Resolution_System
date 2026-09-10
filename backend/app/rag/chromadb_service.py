import re
import uuid

import chromadb

from app.core.config import CHROMA_DB_PATH

client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH)
)

collection = client.get_or_create_collection(
    name="ai_query_resolution"
)


def add_documents(
    chunks,
    embeddings,
    metadatas=None,
    document_id=None,
):
    # Validate that chunks and embeddings are available.
    if not chunks:
        print("No chunks to store.")
        return

    if not embeddings:
        print("No embeddings to store.")
        return

    # Each chunk must have one corresponding embedding.
    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks and embeddings must be the same."
        )

    # Create empty metadata when none is provided.
    if metadatas is None:
        metadatas = [{} for _ in chunks]

    if len(metadatas) != len(chunks):
        raise ValueError(
            "Number of chunks and metadata entries must be the same."
        )

    # Create a unique ID for every stored chunk.
    ids = [
        f"{document_id or uuid.uuid4().hex}_{i}"
        for i in range(len(chunks))
    ]

    # Store chunks, embeddings and metadata together.
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(
        f"{len(chunks)} chunks and embeddings "
        "stored successfully in ChromaDB."
    )


def delete_documents(document_id):
    # Delete all vectors belonging to the document.
    collection.delete(
        where={
            "document_id": document_id
        }
    )


def delete_documents_for_user(document_id, user_id):
    """Delete vectors for a specific document owned by user."""
    collection.delete(
        where={
            "$and": [
                {"document_id": document_id},
                {"user_id": user_id},
            ]
        }
    )


def search_documents(
    query_embedding,
    k=3,
):
    # Perform semantic vector search.
    return collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=k,
    )


def search_documents_for_user(
    query_embedding,
    user_id,
    k=3,
):
    """Semantic search filtered by user_id."""
    return collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=k,
        where={"user_id": user_id},
    )


def _contains_exact_term(
    content,
    term,
):
    """
    Check for a complete identifier instead of a substring.

    This prevents Name_1 from matching Name_10 or Name_11.
    """

    normalized_content = content.lower()
    normalized_term = term.lower()

    pattern = (
        r"(?<![\w@.-])"
        + re.escape(normalized_term)
        + r"(?![\w@.-])"
    )

    return re.search(
        pattern,
        normalized_content,
    ) is not None


def search_exact_documents(
    terms,
):
    """
    Search stored chunks for exact identifier matches.

    Useful for values such as Name_1, Name_7 or email addresses.
    """

    if not terms:
        return []

    # Read stored chunks and metadata from ChromaDB.
    stored_data = collection.get(
        include=[
            "documents",
            "metadatas",
        ]
    )

    return _process_exact_search_results(stored_data, terms)


def search_exact_documents_for_user(
    terms,
    user_id,
):
    """Exact search filtered by user_id."""
    if not terms:
        return []

    stored_data = collection.get(
        where={"user_id": user_id},
        include=[
            "documents",
            "metadatas",
        ]
    )

    return _process_exact_search_results(stored_data, terms)


def _process_exact_search_results(stored_data, terms):
    documents = (
        stored_data.get(
            "documents",
            []
        )
        or []
    )

    metadatas = (
        stored_data.get(
            "metadatas",
            []
        )
        or []
    )

    ids = (
        stored_data.get(
            "ids",
            []
        )
        or []
    )

    matches = []

    for index, content in enumerate(
        documents
    ):
        if not content:
            continue

        matched_terms = []

        for term in terms:
            if _contains_exact_term(
                content,
                term,
            ):
                matched_terms.append(term)

        if not matched_terms:
            continue

        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        document_id = (
            ids[index]
            if index < len(ids)
            else f"exact_{index}"
        )

        matches.append(
            {
                "id": document_id,
                "content": content,
                "metadata": metadata or {},
                "matched_terms": matched_terms,
                "distance": None,
            }
        )

    return matches


def format_results(
    query,
    results,
):
    # Convert ChromaDB results into the API response format.
    documents = (
        results.get(
            "documents",
            [[]]
        )[0]
        if results.get("documents")
        else []
    )

    metadatas = (
        results.get(
            "metadatas",
            [[]]
        )[0]
        if results.get("metadatas")
        else []
    )

    distances = (
        results.get(
            "distances",
            [[]]
        )[0]
        if results.get("distances")
        else []
    )

    formatted_results = []

    for index, content in enumerate(
        documents
    ):
        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        formatted_results.append(
            {
                "content": content,
                "metadata": metadata or {},
                "distance": distance,
            }
        )

    return {
        "success": True,
        "query": query,
        "results": formatted_results,
        "count": len(formatted_results),
    }


def search_by_filename(filename_query: str, raw_query: str = None) -> list[dict]:
    """
    Retrieve all chunks belonging to a document by its original filename.

    Used as a fallback when semantic search scores are too low — e.g.
    when the user asks about a specific file by name.
    """
    if not filename_query or not filename_query.strip():
        return []

    query_lower = filename_query.strip().lower()

    stored_data = collection.get(
        include=["documents", "metadatas", "embeddings"]
    )

    documents = stored_data.get("documents", []) or []
    metadatas = stored_data.get("metadatas", []) or []
    embeddings = stored_data.get("embeddings", [])
    if embeddings is None:
        embeddings = []
    ids = stored_data.get("ids", []) or []

    results = []
    
    import os
    
    # If we have a raw_query, we can embed it and calculate actual distances
    query_embedding = None
    if raw_query:
        try:
            from app.rag.embedding import load_embedding_model, embed_chunks
            model = load_embedding_model()
            query_embedding = embed_chunks(model, [raw_query])[0]
        except Exception as e:
            print(f"Failed to embed raw query for filename fallback: {e}")

    # To convert distance to relevance safely
    from app.agents.retrieval.reranker import semantic_score

    for index, content in enumerate(documents):
        meta = metadatas[index] if index < len(metadatas) else {}
        stored_name = str(meta.get("filename", ""))
        stored_name_lower = stored_name.lower()
        
        # Remove extension for flexible matching
        name_without_ext = os.path.splitext(stored_name_lower)[0]

        if (
            query_lower in stored_name_lower
            or stored_name_lower in query_lower
            or query_lower in name_without_ext
            or name_without_ext in query_lower
        ):
            # Calculate actual L2 distance if query embedding is available
            distance = None
            relevance = 0.0
            
            if query_embedding is not None and index < len(embeddings):
                chunk_embedding = embeddings[index]
                if chunk_embedding is not None:
                    # L2 distance (which is what ChromaDB uses by default)
                    import numpy as np
                    distance = float(np.sum((np.array(query_embedding) - np.array(chunk_embedding)) ** 2))
                    relevance = semantic_score(distance)
                    
                    print(f"\n--- DEBUG: RAW SCORE ---")
                    print(f"Query: {raw_query}")
                    print(f"Document: {stored_name}")
                    print(f"Raw retrieval score: {distance}")
                    print(f"Score type: distance")
                    print(f"Metric: L2 distance")
                    print(f"Calculated Relevance: {relevance}")
                    print(f"------------------------\n")

            results.append({
                "chunk_id": ids[index] if index < len(ids) else f"fn_{index}",
                "content": content,
                "metadata": meta or {},
                "distance": distance,
                "relevance_score": relevance,
                "semantic_score": relevance,
                "matched_terms": [stored_name],
            })

    return results



if __name__ == "__main__":

    # Run a simple storage check when this file is executed directly.
    print("ChromaDB service check")
    print(f"Database path: {CHROMA_DB_PATH}")
    print(f"Collection: {collection.name}")
    print(f"Stored vectors: {collection.count()}")
