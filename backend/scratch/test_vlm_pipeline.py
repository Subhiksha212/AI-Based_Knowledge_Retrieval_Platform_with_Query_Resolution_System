import io
import sys
import os
from PIL import Image

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.utils.image_filter import is_valid_document_image
from app.services.vlm_service import vlm_service, GeminiRateLimitError


def test_image_filter():
    print("--- 1. Testing Image Filter ---")
    page_hashes_map = {}

    # Create a tiny 32x32 image (should be filtered)
    tiny_img = Image.new("RGB", (32, 32), color="red")
    buf = io.BytesIO()
    tiny_img.save(buf, format="PNG")
    valid, reason = is_valid_document_image(buf.getvalue(), page_number=1, page_hashes_map=page_hashes_map)
    print(f"Tiny Image (32x32): valid={valid}, reason={reason}")
    assert not valid, "Tiny image should be filtered"

    # Create a solid white 200x200 image (should be filtered for low variance)
    solid_img = Image.new("RGB", (200, 200), color="white")
    buf = io.BytesIO()
    solid_img.save(buf, format="PNG")
    valid, reason = is_valid_document_image(buf.getvalue(), page_number=1, page_hashes_map=page_hashes_map)
    print(f"Solid Image (200x200): valid={valid}, reason={reason}")
    assert not valid, "Solid image should be filtered"

    # Create a valid image with random noise/shapes (200x200)
    import numpy as np
    random_array = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    valid_img = Image.fromarray(random_array)
    buf = io.BytesIO()
    valid_img.save(buf, format="PNG")
    valid, reason = is_valid_document_image(buf.getvalue(), page_number=1, page_hashes_map=page_hashes_map)
    print(f"Valid Diagram Image (200x200): valid={valid}, reason={reason}")
    assert valid, "Valid image should pass filter"

    print("Image filter tests PASSED!\n")


def test_vlm_service():
    print("--- 2. Testing VLM Service Fallback & Gemini Acceptance ---")

    # Create a test image bytes
    import numpy as np
    data = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    img = Image.fromarray(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    # Test analyze_image call
    print("Calling analyze_image...")
    res = vlm_service.analyze_image(
        image_bytes=img_bytes,
        question="What is shown in this diagram?",
        user_id="test_user_123"
    )
    print(f"Analysis Result: {res[:100]}...\n")

    print("VLM Service tests completed!\n")


if __name__ == "__main__":
    test_image_filter()
    test_vlm_service()
