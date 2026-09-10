import io
import os
import torch
import logging
from PIL import Image
from fastapi import HTTPException
from transformers import AutoProcessor, AutoModelForImageTextToText

logger = logging.getLogger(__name__)

# Constants
VLM_MODEL = os.getenv("VLM_MODEL", "HuggingFaceTB/SmolVLM-256M-Instruct")
VLM_DEVICE = os.getenv("VLM_DEVICE", "auto")

class VLMService:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = None
        
    def _load_model(self):
        if self.model is not None and self.processor is not None:
            return

        logger.info(f"Loading VLM model: {VLM_MODEL}")
        
        # Determine device
        if VLM_DEVICE == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = VLM_DEVICE
            
        logger.info(f"Using device for VLM: {self.device}")
        
        try:
            dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
            
            self.processor = AutoProcessor.from_pretrained(VLM_MODEL)
            self.model = AutoModelForImageTextToText.from_pretrained(
                VLM_MODEL,
                torch_dtype=dtype,
                _attn_implementation="eager"
            ).to(self.device)
            
            self.model.eval()
            logger.info("VLM model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load VLM model: {str(e)}")
            raise RuntimeError("VLM model initialization failed.")

    def validate_and_preprocess_image(self, image_bytes: bytes) -> Image.Image:
        """Validates the image and returns a PIL Image in RGB format."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid or corrupted image data.")
            
        # Re-open after verify
        image = Image.open(io.BytesIO(image_bytes))
        
        format = image.format
        if format not in ["JPEG", "JPG", "PNG", "MPO"]:
            raise HTTPException(status_code=400, detail=f"Unsupported image format: {format}. Supported formats are JPG, JPEG, PNG.")
            
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Resize extremely large images to avoid OOM
        # Resize images to speed up inference significantly
        max_dim = 1024
        if image.width > max_dim or image.height > max_dim:
            image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
        return image

    def analyze_image(self, image_bytes: bytes, question: str, max_tokens: int = 150) -> str:
        """Analyzes an image and answers a question about it using SmolVLM."""
        if not question or not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")
            
        self._load_model()
        
        pil_image = self.validate_and_preprocess_image(image_bytes)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": f"Analyze the provided image carefully.\n\nAnswer the following question using only information that can be determined from the image:\n\n{question.strip()}\n\nIf the information is not visible or cannot be determined from the image, say that it cannot be determined from the image."}
                ]
            }
        ]
        
        try:
            prompt = self.processor.apply_chat_template(messages, add_generation_prompt=True)
            inputs = self.processor(text=prompt, images=[pil_image], return_tensors="pt")
            inputs = inputs.to(self.device)
            
            with torch.inference_mode():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=0.2,
                    do_sample=False
                )
            
            input_length = inputs.input_ids.shape[1]
            generated_ids_only = generated_ids[0][input_length:]
            answer = self.processor.decode(generated_ids_only, skip_special_tokens=True).strip()
            
            return answer
            
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal error during visual analysis.")

# Singleton instance
vlm_service = VLMService()
