import base64
import io
import os
import time
import hashlib
import logging
import requests
import torch
from PIL import Image
from fastapi import HTTPException
from transformers import AutoProcessor, AutoModelForImageTextToText

logger = logging.getLogger(__name__)

# Primary VLM Model Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_VLM_MODEL = os.getenv("GEMINI_VLM_MODEL", "gemini-3.6-flash")

# Fallback Local VLM Configuration
VLM_MODEL = os.getenv("VLM_MODEL", "HuggingFaceTB/SmolVLM-256M-Instruct")
VLM_DEVICE = os.getenv("VLM_DEVICE", "auto")


class GeminiRateLimitError(Exception):
    """Raised when Gemini API hits rate limit / quota (HTTP 429)."""
    pass


class GeminiQuotaError(Exception):
    """Raised when Gemini API quota is exceeded."""
    pass


class VLMService:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = None
        self.gemini_rate_limited_until = {}
        self._cache = {}

    def is_model_rate_limited(self, model_name: str = GEMINI_VLM_MODEL) -> tuple[bool, float]:
        """Checks whether Gemini model is currently under rate limit cooldown."""
        until = self.gemini_rate_limited_until.get(model_name, 0.0)
        now = time.time()
        if now < until:
            return True, round(until - now, 1)
        return False, 0.0

    def evaluate_gemini_quality(self, text: str) -> str:
        """
        Evaluates Gemini output quality for logging/informational purposes.
        Note: Quality score MUST NOT trigger fallback to SmolVLM under any circumstances.
        """
        if not text or len(text.strip()) < 100:
            return "POOR"
        return "GOOD"

    def _load_model(self):
        """Loads SmolVLM model lazily only when fallback is triggered."""
        if self.model is not None and self.processor is not None:
            return

        logger.info(f"Loading VLM model (SmolVLM): {VLM_MODEL}")
        
        # Determine device
        if VLM_DEVICE == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = VLM_DEVICE
            
        logger.info(f"Using device for SmolVLM: {self.device}")
        
        try:
            dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
            
            self.processor = AutoProcessor.from_pretrained(VLM_MODEL)
            self.model = AutoModelForImageTextToText.from_pretrained(
                VLM_MODEL,
                torch_dtype=dtype,
                _attn_implementation="eager"
            ).to(self.device)
            
            self.model.eval()
            logger.info("SmolVLM model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SmolVLM model: {str(e)}")
            raise RuntimeError("SmolVLM model initialization failed.")

    def validate_and_preprocess_image(self, image_bytes: bytes) -> Image.Image:
        """Validates the image and returns a PIL Image in RGB format."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid or corrupted image data.")
            
        # Re-open after verify
        image = Image.open(io.BytesIO(image_bytes))
        
        fmt = image.format
        if fmt not in ["JPEG", "JPG", "PNG", "MPO", "WEBP"]:
            raise HTTPException(status_code=400, detail=f"Unsupported image format: {fmt}. Supported formats are JPG, JPEG, PNG, WEBP.")
            
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Resize extremely large images to avoid high latency / OOM
        max_dim = 1024
        if image.width > max_dim or image.height > max_dim:
            image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
        return image

    def _call_gemini(self, image_bytes: bytes, question: str, max_tokens: int = 200) -> str:
        """
        Calls primary Gemini VLM model (gemini-3.6-flash).
        Returns result string on success.
        Raises exception on failure/rate limit to trigger SmolVLM fallback.
        """
        logger.info("[VLM] Primary model: Gemini")

        # Check circuit breaker
        is_limited, rem = self.is_model_rate_limited(GEMINI_VLM_MODEL)
        if is_limited:
            logger.warning(f"[VLM] Gemini failed: RATE_LIMIT (Cooldown active for {rem}s)")
            raise GeminiRateLimitError(f"Gemini model {GEMINI_VLM_MODEL} rate limited for {rem}s")

        api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
        if not api_key:
            logger.warning("[VLM] Gemini failed: NO_API_KEY")
            raise RuntimeError("GEMINI_API_KEY is not configured")

        pil_image = self.validate_and_preprocess_image(image_bytes)
        img_buf = io.BytesIO()
        pil_image.save(img_buf, format="PNG")
        b64_data = base64.b64encode(img_buf.getvalue()).decode("utf-8")

        prompt_text = (
            f"Analyze the provided image carefully.\n\n"
            f"Answer the following question using only information that can be determined from the image:\n\n"
            f"{question.strip()}\n\n"
            f"If the information is not visible or cannot be determined from the image, say that it cannot be determined from the image."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_VLM_MODEL}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"inline_data": {"mime_type": "image/png", "data": b64_data}},
                        {"text": prompt_text}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.2
            }
        }

        try:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 429:
                # Trigger circuit breaker cooldown
                self.gemini_rate_limited_until[GEMINI_VLM_MODEL] = time.time() + 60
                logger.warning("[VLM] Gemini failed: RATE_LIMIT")
                raise GeminiRateLimitError("Gemini API rate limit exceeded (HTTP 429)")

            if res.status_code != 200:
                logger.warning(f"[VLM] Gemini failed: HTTP_{res.status_code}")
                raise RuntimeError(f"Gemini API returned HTTP {res.status_code}: {res.text[:200]}")

            res_json = res.json()
            candidates = res_json.get("candidates", [])
            if not candidates:
                logger.warning("[VLM] Gemini failed: NO_CANDIDATES")
                raise RuntimeError("Gemini API returned no candidates")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts or "text" not in parts[0]:
                logger.warning("[VLM] Gemini failed: EMPTY_PARTS")
                raise RuntimeError("Gemini API returned empty parts")

            answer = parts[0]["text"].strip()
            if not answer:
                logger.warning("[VLM] Gemini failed: EMPTY_TEXT")
                raise RuntimeError("Gemini API returned empty text")

            logger.info("[VLM] Gemini response received successfully")
            logger.info("[VLM] Using Gemini result")
            return answer

        except requests.exceptions.RequestException as e:
            logger.warning(f"[VLM] Gemini failed: CONNECTION_ERROR ({str(e)})")
            raise RuntimeError(f"Gemini API connection error: {str(e)}")

    def _call_smolvlm(self, image_bytes: bytes, question: str, max_tokens: int = 150) -> str:
        """
        Executes SmolVLM local fallback inference.
        """
        logger.info("[VLM] Gemini fallback required: YES")
        logger.info("[VLM] Falling back to SmolVLM")

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

    def analyze_image(
        self,
        image_bytes: bytes,
        question: str,
        max_tokens: int = 200,
        user_id: str = None,
        document_id: str = None,
        page_number: int = None,
        image_index: int = None
    ) -> str:
        """
        Analyzes an image.
        1. Checks image-hash cache for previous result.
        2. Tries Gemini (Primary VLM: gemini-3.6-flash).
        3. If Gemini succeeds, ALWAYS returns Gemini result (no quality/length gate).
        4. If Gemini fails (429 rate limit, API error, connection error), falls back to SmolVLM.
        """
        if not question or not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        if user_id:
            logger.info(f"[VLM] User ID: {user_id}")

        # Image hash-based caching
        img_hash = hashlib.sha256(image_bytes).hexdigest()
        cache_key = f"{img_hash}_{hashlib.md5(question.strip().encode('utf-8')).hexdigest()}"
        if cache_key in self._cache:
            logger.info(f"[VLM] Cache hit for image (hash: {img_hash[:8]}). Reusing previous VLM result.")
            return self._cache[cache_key]

        # 1. Try Gemini (Primary VLM)
        try:
            result = self._call_gemini(image_bytes, question, max_tokens)
            if result:
                self._cache[cache_key] = result
                return result
        except (GeminiRateLimitError, GeminiQuotaError, Exception) as e:
            logger.warning(f"[VLM] Primary Gemini VLM attempt failed: {e}")

        # 2. Fallback to SmolVLM ONLY on Gemini failure
        result = self._call_smolvlm(image_bytes, question, max_tokens)
        if result:
            self._cache[cache_key] = result
        return result


# Singleton instance
vlm_service = VLMService()
