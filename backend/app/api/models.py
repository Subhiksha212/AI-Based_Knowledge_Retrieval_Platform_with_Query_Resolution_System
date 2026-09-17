from typing import List, Optional, Union
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.rag.embedding import load_embedding_model
from app.services.ocr_service import OCRService

router = APIRouter(prefix="/api/models", tags=["ML Models"])

# Lazy-loaded OCR service singleton
_ocr_service_instance: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    global _ocr_service_instance
    if _ocr_service_instance is None:
        _ocr_service_instance = OCRService()
    return _ocr_service_instance


class EmbedRequest(BaseModel):
    text: Optional[str] = Field(None, description="Single text string to encode")
    texts: Optional[List[str]] = Field(None, description="List of text strings to encode")


class EmbedResponse(BaseModel):
    model: str = "all-MiniLM-L6-v2"
    dimension: int
    embeddings: List[List[float]]


@router.post("/embed", response_model=EmbedResponse, summary="Sentence Transformer Embedding")
async def generate_embeddings(payload: EmbedRequest):
    """
    Generate vector embeddings using Sentence Transformers (all-MiniLM-L6-v2).
    Pass either `text` (string) or `texts` (list of strings).
    """
    input_list = []
    if payload.text and payload.text.strip():
        input_list.append(payload.text.strip())
    if payload.texts:
        for t in payload.texts:
            if t and t.strip():
                input_list.append(t.strip())

    if not input_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide 'text' or a non-empty list of 'texts'.",
        )

    model = load_embedding_model()
    vectors = model.encode(input_list, convert_to_numpy=True).tolist()
    dimension = len(vectors[0]) if vectors else 384

    return EmbedResponse(
        model="all-MiniLM-L6-v2",
        dimension=dimension,
        embeddings=vectors,
    )


@router.post("/ocr", summary="OCR Pipeline (PaddleOCR & PyMuPDF)")
async def run_ocr_pipeline(file: UploadFile = File(...)):
    """
    Run the OCR pipeline on an uploaded Image (PNG/JPG) or PDF document.
    Returns extracted text, page breakdown, and spatial bounding boxes.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty.",
        )

    filename = file.filename
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    allowed_exts = {"png", "jpg", "jpeg", "bmp", "pdf"}
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Supported formats: {', '.join(allowed_exts)}",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    ocr_service = get_ocr_service()

    try:
        if ext == "pdf":
            result = ocr_service.run_ocr_on_pdf(file_bytes, filename=filename)
        else:
            result = ocr_service.run_ocr_on_image(file_bytes)

        return {
            "success": True,
            "filename": filename,
            "file_type": ext,
            "result": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR execution error: {str(e)}",
        )
