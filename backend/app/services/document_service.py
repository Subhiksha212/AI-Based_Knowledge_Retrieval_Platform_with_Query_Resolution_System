from app.rag.chromadb_service import delete_documents
from app.services.metadata_service import (
    documents,
    processing_jobs,
    save_documents,
)


# Return all uploaded documents.
def get_all_documents():
    return list(
        documents.values()
    )


# Return the processing status of an upload job.
def get_upload_job_status(job_id):
    job = processing_jobs.get(
        job_id
    )

    # Return the active job if it exists.
    if job is not None:
        return job

    # Check completed documents if the job is no longer active.
    for document in documents.values():
        if document.get(
            "jobId"
        ) == job_id:
            return {
                "jobId": job_id,
                "documentId": document["id"],
                "filename": document["name"],
                "status": document.get(
                    "status",
                    "unknown",
                ),
                "stage": document.get(
                    "stage",
                    "unknown",
                ),
                "progress": document.get(
                    "progress",
                    0,
                ),
                "message": document.get(
                    "message",
                    "",
                ),
                "chunksCount": document.get(
                    "chunksCount",
                    0,
                ),
                "embeddingsCount": document.get(
                    "embeddingsCount",
                    0,
                ),
                "vectorsStored": document.get(
                    "vectorsStored",
                    0,
                ),
                "error": document.get(
                    "error"
                ),
            }

    # Return None if the job is not found.
    return None


# Delete a document and its indexed vectors.
def delete_document_by_id(document_id):

    # Return if the document does not exist.
    if document_id not in documents:
        return None

    # Remove document vectors from ChromaDB.
    delete_documents(
        document_id
    )

    # Remove document metadata.
    del documents[
        document_id
    ]

    # Save updated metadata.
    save_documents()

    # Find related upload jobs.
    document_job_ids = [
        job_id
        for job_id, job in processing_jobs.items()
        if job.get(
            "documentId"
        ) == document_id
    ]

    # Remove completed job records.
    for job_id in document_job_ids:
        processing_jobs.pop(
            job_id,
            None,
        )

    # Return success response.
    return {
        "status": "success",
        "message": "Document deleted successfully",
        "id": document_id,
    }