from datetime import datetime, timezone
import uuid

from app.core.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_FOLDER
from app.rag.chromadb_service import add_documents
from app.rag.chunking import chunk_text
from app.rag.embedding import embed_chunks, load_embedding_model
from app.rag.extractor import extract_document
from app.services.metadata_service import (
    documents,
    processing_jobs,
    save_documents,
    update_document_status,
    update_job,
)

# Create the upload directory if it does not exist.
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


# Validate the uploaded file type.
def validate_upload_filename(filename):
    if not filename:
        return {
            "status": "failed",
            "message": "No file selected",
        }

    extension = filename.suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return {
            "status": "failed",
            "message": (
                "Unsupported file type. "
                "Use PDF, DOCX, TXT or CSV."
            ),
        }

    return None


# Validate the uploaded file size and content.
def validate_upload_data(file_data):
    if len(file_data) == 0:
        return {
            "status": "failed",
            "message": "Uploaded file is empty",
        }

    if len(file_data) > MAX_FILE_SIZE:
        return {
            "status": "failed",
            "message": "File size exceeds 10 MB",
        }

    return None


# Save the uploaded file and create its processing job.
def create_upload_job(file, file_data, extension):
    document_id = uuid.uuid4().hex
    job_id = uuid.uuid4().hex

    unique_filename = (
        f"{document_id}{extension}"
    )

    file_path = (
        UPLOAD_FOLDER / unique_filename
    )

    # Save the uploaded file locally.
    with open(
        file_path,
        "wb",
    ) as output_file:
        output_file.write(
            file_data
        )

    uploaded_at = datetime.now(
        timezone.utc
    ).isoformat()

    # Store document metadata.
    document = {
        "id": document_id,
        "jobId": job_id,
        "name": file.filename,
        "size": len(file_data),
        "status": "processing",
        "stage": "uploaded",
        "progress": 10,
        "message": "File uploaded successfully.",
        "uploadedAt": uploaded_at,
        "chunksCount": 0,
        "embeddingsCount": 0,
        "vectorsStored": 0,
    }

    documents[
        document_id
    ] = document

    save_documents()

    # Initialize upload job status.
    processing_jobs[job_id] = {
        "jobId": job_id,
        "documentId": document_id,
        "filename": file.filename,
        "status": "processing",
        "stage": "uploaded",
        "progress": 10,
        "message": "File uploaded successfully.",
        "chunksCount": 0,
        "embeddingsCount": 0,
        "vectorsStored": 0,
        "error": None,
    }

    return document_id, job_id, file_path


# Process the uploaded document in the background.
def process_uploaded_document(
    job_id,
    document_id,
    file_path,
    original_filename,
    user_id=None,
):
    try:
        # Update status before extracting text.
        update_job(
            job_id,
            status="processing",
            stage="extracting",
            progress=20,
            message="Extracting text from document...",
        )

        update_document_status(
            document_id,
            status="processing",
            stage="extracting",
            progress=20,
            message="Extracting text from document...",
        )

        # Extract text from the uploaded document.
        extraction_result = extract_document(
            str(file_path)
        )

        if not extraction_result or not isinstance(extraction_result, dict):
            raise ValueError(
                "No text could be extracted from the file"
            )
            
        extracted_text = extraction_result["text"]
        extracted_images = extraction_result.get("images", [])

        if not extracted_text and not extracted_images:
            raise ValueError(
                "No content could be extracted from the file"
            )
            
        # Prepend the original filename to the text to ensure semantic matching works
        # when users search for specific files by name (especially important for images)
        if extracted_text:
            extracted_text = f"File Name: {original_filename}\n\n{extracted_text}"

        # Update status before chunk creation.
        update_job(
            job_id,
            stage="chunking",
            progress=40,
            message="Creating document chunks...",
        )

        update_document_status(
            document_id,
            stage="chunking",
            progress=40,
            message="Creating document chunks...",
        )

        # Split extracted text into chunks.
        chunks = []
        if extracted_text:
            from app.rag.chunking import chunk_text
            chunks = chunk_text(extracted_text)

        metadatas = [
            {
                "document_id": document_id,
                "filename": original_filename,
                "chunk_index": index,
                "source_type": "text",
                "user_id": user_id or "",
            }
            for index in range(len(chunks))
        ]

        # Add embedded image chunks
        for img in extracted_images:
            page_info = f"Page {img['metadata']['page_number']} " if "page_number" in img["metadata"] else ""
            img_content = f"File Name: {original_filename}\n{page_info}Image {img['metadata'].get('image_index', '?')}\n{img['content']}"
            chunks.append(img_content)
            
            img_metadata = img["metadata"]
            img_metadata.update({
                "document_id": document_id,
                "filename": original_filename,
                "chunk_index": len(chunks) - 1,
                "user_id": user_id or "",
            })
            metadatas.append(img_metadata)

        if not chunks:
            raise ValueError(
                "No chunks could be created from the file"
            )

        chunks_count = len(chunks)

        # Store chunk statistics.
        update_job(
            job_id,
            stage="chunking",
            progress=50,
            message=f"Created {chunks_count} document chunks.",
            chunks_count=chunks_count,
        )

        update_document_status(
            document_id,
            stage="chunking",
            progress=50,
            message=f"Created {chunks_count} document chunks.",
            chunks_count=chunks_count,
        )

        # Update status before embedding generation.
        update_job(
            job_id,
            stage="embedding",
            progress=60,
            message="Generating embeddings...",
        )

        update_document_status(
            document_id,
            stage="embedding",
            progress=60,
            message="Generating embeddings...",
        )

        # Load the embedding model and generate vectors.
        model = load_embedding_model()

        embeddings = embed_chunks(
            model,
            chunks,
        )

        if not embeddings:
            raise ValueError(
                "No embeddings could be generated"
            )

        embeddings_count = len(embeddings)

        # Store embedding statistics.
        update_job(
            job_id,
            stage="embedding",
            progress=75,
            message=f"Generated {embeddings_count} embeddings.",
            embeddings_count=embeddings_count,
        )

        update_document_status(
            document_id,
            stage="embedding",
            progress=75,
            message=f"Generated {embeddings_count} embeddings.",
            embeddings_count=embeddings_count,
        )

        # Update status before storing vectors.
        update_job(
            job_id,
            stage="storing",
            progress=85,
            message="Storing vectors in ChromaDB...",
        )

        update_document_status(
            document_id,
            stage="storing",
            progress=85,
            message="Storing vectors in ChromaDB...",
        )

        # Store embeddings in ChromaDB.
        add_documents(
            chunks,
            embeddings,
            metadatas=metadatas,
            document_id=document_id,
        )

        vectors_stored = len(chunks)

        # Update vector storage progress.
        update_job(
            job_id,
            stage="storing",
            progress=95,
            message=f"Stored {vectors_stored} vectors in ChromaDB.",
            vectors_stored=vectors_stored,
        )

        update_document_status(
            document_id,
            stage="storing",
            progress=95,
            message=f"Stored {vectors_stored} vectors in ChromaDB.",
            vectors_stored=vectors_stored,
        )

        completed_at = datetime.now(
            timezone.utc
        ).isoformat()

        document = documents.get(
            document_id
        )

        # Mark the document as successfully indexed.
        if document:
            document["status"] = "indexed"
            document["stage"] = "completed"
            document["progress"] = 100
            document["message"] = (
                "Document processed successfully"
            )
            document["chunksCount"] = chunks_count
            document["embeddingsCount"] = embeddings_count
            document["vectorsStored"] = vectors_stored
            document["processedAt"] = completed_at

            save_documents()

        # Update the final job status.
        update_job(
            job_id,
            status="completed",
            stage="completed",
            progress=100,
            message="Document processed successfully.",
            chunks_count=chunks_count,
            embeddings_count=embeddings_count,
            vectors_stored=vectors_stored,
        )

    # Handle any processing errors.
    except Exception as error:
        error_message = str(error)

        update_job(
            job_id,
            status="failed",
            stage="error",
            progress=100,
            message="Document processing failed.",
            error=error_message,
        )

        update_document_status(
            document_id,
            status="failed",
            stage="error",
            progress=100,
            message="Document processing failed.",
            error=error_message,
        )

    # Remove the temporary uploaded file.
    finally:
        if file_path.exists():
            file_path.unlink()