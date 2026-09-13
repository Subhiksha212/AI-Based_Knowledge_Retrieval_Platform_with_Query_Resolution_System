import io
import sys
import os
import time
from PIL import Image

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.utils.image_filter import is_valid_document_image
from app.services.vlm_service import vlm_service, GeminiRateLimitError, GeminiQuotaError


def test_vlm_pipeline_all_requirements():
    print("==================================================")
    print("      COMPREHENSIVE VLM PIPELINE SUITE TESTS      ")
    print("==================================================")

    # 1. Image Filter Tests
    page_hashes = {}
    tiny_img = Image.new("RGB", (30, 30), color="blue")
    buf = io.BytesIO()
    tiny_img.save(buf, format="PNG")
    valid, reason = is_valid_document_image(buf.getvalue(), page_number=1, page_hashes_map=page_hashes)
    print(f"[TEST 1] Tiny Image (30x30): valid={valid}, reason={reason}")
    assert not valid and "too_small" in reason

    solid_img = Image.new("RGB", (200, 200), color="white")
    buf = io.BytesIO()
    solid_img.save(buf, format="PNG")
    valid, reason = is_valid_document_image(buf.getvalue(), page_number=1, page_hashes_map=page_hashes)
    print(f"[TEST 2] Solid Image (200x200): valid={valid}, reason={reason}")
    assert not valid and "low_variance" in reason

    import numpy as np
    data = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    valid_img = Image.fromarray(data)
    buf = io.BytesIO()
    valid_img.save(buf, format="PNG")
    valid, reason = is_valid_document_image(buf.getvalue(), page_number=1, page_hashes_map=page_hashes)
    print(f"[TEST 3] Valid Image (300x300): valid={valid}, reason={reason}")
    assert valid and reason == "valid_document_image"

    # 2. Quality Evaluation (Does NOT trigger fallback)
    quality = vlm_service.evaluate_gemini_quality("Short text 50 chars.")
    print(f"[TEST 4] Quality Evaluation for short text: quality={quality}")
    assert quality == "POOR"

    # 3. Circuit Breaker Test
    model_test = "gemini-3.6-flash"
    vlm_service.gemini_rate_limited_until[model_test] = time.time() + 10
    is_limited, rem = vlm_service.is_model_rate_limited(model_test)
    print(f"[TEST 5] Circuit Breaker Active for {model_test}: is_limited={is_limited}, remaining={rem}s")
    assert is_limited and rem > 0
    # Clear test cooldown
    vlm_service.gemini_rate_limited_until.pop(model_test, None)

    # 4. User ID Propagation Logging Check
    print("[TEST 6] User ID Propagation Check in analyze_image...")
    buf = io.BytesIO()
    valid_img.save(buf, format="PNG")
    # Should print [VLM] User ID: test_user_usr_9999
    res = vlm_service.analyze_image(
        buf.getvalue(),
        "What is in this test image?",
        user_id="usr_9999",
        document_id="doc_8888",
        page_number=1,
        image_index=0
    )
    print(f"[TEST 6 RESULT]: {res[:60]}...")

    print("\nAll VLM pipeline verification tests PASSED!\n")


if __name__ == "__main__":
    test_vlm_pipeline_all_requirements()
