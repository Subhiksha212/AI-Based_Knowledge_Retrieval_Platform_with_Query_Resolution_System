from fastapi import APIRouter, HTTPException

from app.services.document_service import (
    delete_document_by_id,
    get_all_documents,
)

# Router for document management.
router = APIRouter()


# Return all indexed documents.
@router.get("/documents")
def get_documents():
    return get_all_documents()


# Delete a document from the knowledge base.
@router.delete("/documents/{document_id}")
def delete_document(document_id: str):

    response = delete_document_by_id(
        document_id
    )

    # Return 404 if the document does not exist.
    if response is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return response