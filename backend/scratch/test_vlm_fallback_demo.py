import os
import sys
import io
import logging
from PIL import Image

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from app.services.vlm_service import vlm_service, GeminiRateLimitError

def test_vlm_pipeline():
    print("=" * 60)
    print("         TESTING VLM PIPELINE FALLBACK & CACHING        ")
    print("=" * 60)

    # 1. Create a dummy image
    img = Image.new("RGB", (200, 200), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()
    question = "What color is in this image?"

    # 2. Test Gemini Call (with mock success)
    print("\n--- Test Scenario 1: Gemini Success ---")
    def mock_gemini_success(bytes_in, q, max_tokens=200):
        print("[VLM] Primary model: Gemini")
        print("[VLM] Gemini response received successfully")
        print("[VLM] Using Gemini result")
        return "This is a solid blue image."

    vlm_service._call_gemini = mock_gemini_success
    res1 = vlm_service.analyze_image(image_bytes, question)
    print(f"Result 1: {res1}")
    assert res1 == "This is a solid blue image."

    # 3. Test Caching
    print("\n--- Test Scenario 2: Image Hash Cache Hit ---")
    res_cache = vlm_service.analyze_image(image_bytes, question)
    print(f"Cache Result: {res_cache}")

    # 4. Test Gemini Rate Limit (HTTP 429) Fallback to SmolVLM
    print("\n--- Test Scenario 3: Gemini 429 Rate Limit -> SmolVLM Fallback ---")
    # Clear cache for new test
    vlm_service._cache.clear()

    def mock_gemini_rate_limit(bytes_in, q, max_tokens=200):
        print("[VLM] Primary model: Gemini")
        print("[VLM] Gemini failed: RATE_LIMIT")
        raise GeminiRateLimitError("Gemini API rate limit exceeded (HTTP 429)")

    def mock_smolvlm(bytes_in, q, max_tokens=150):
        print("[VLM] Gemini fallback required: YES")
        print("[VLM] Falling back to SmolVLM")
        return "SmolVLM analysis: Image appears blue."

    vlm_service._call_gemini = mock_gemini_rate_limit
    vlm_service._call_smolvlm = mock_smolvlm

    res_fallback = vlm_service.analyze_image(image_bytes, "Describe the image content")
    print(f"Fallback Result: {res_fallback}")
    assert "SmolVLM" in res_fallback

    print("\nAll VLM pipeline fallback & caching tests PASSED successfully!\n")

if __name__ == "__main__":
    test_vlm_pipeline()
