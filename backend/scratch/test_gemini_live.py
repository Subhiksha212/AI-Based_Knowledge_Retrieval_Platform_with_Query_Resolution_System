import io
import sys
import os
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from backend/.env
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path=env_path)

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.vlm_service import vlm_service, GEMINI_API_KEY

def test_live_gemini():
    print("==================================================")
    print("       LIVE GEMINI VISION API TEST")
    print("==================================================")
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"Loaded GEMINI_API_KEY: {api_key[:10]}... (len: {len(api_key) if api_key else 0})")

    # Create a small valid test image with text
    img = Image.new("RGB", (200, 200), color="lightblue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    print("\nCalling analyze_image with live environment...")
    result = vlm_service.analyze_image(
        image_bytes=img_bytes,
        question="Describe the color and shape of this image.",
        user_id="live_test_user"
    )
    print("--------------------------------------------------")
    print(f"Result:\n{result}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    test_live_gemini()
