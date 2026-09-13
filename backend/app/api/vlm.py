from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.services.vlm_service import vlm_service

router = APIRouter(
    prefix="/vlm",
    tags=["Vision-Language Model"]
)

class VLMResponse(BaseModel):
    answer: str

@router.post("/analyze", response_model=VLMResponse)
async def analyze_image_endpoint(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    """
    Analyzes an uploaded image (JPG/PNG) and answers a question based on its visual content.
    """
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected an image.")
        
    try:
        image_bytes = await image.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read uploaded image data.")
        
    answer = vlm_service.analyze_image(image_bytes, question)
    
    return VLMResponse(answer=answer)
