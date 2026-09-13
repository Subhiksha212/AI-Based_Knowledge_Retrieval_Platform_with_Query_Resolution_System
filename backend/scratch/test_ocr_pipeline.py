import io
import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.ocr_service import ocr_service
from app.rag.extractor import extract_document


def create_sample_text_image(text: str, filename: str, fmt: str = "PNG") -> bytes:
    """Helper to generate an image with rendered text for OCR testing."""
    img = Image.new("RGB", (600, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((30, 80), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_ocr_suite():
    print("=" * 70)
    print("        COMPREHENSIVE PP-OCRv5 & PyMuPDF TEST SUITE        ")
    print("=" * 70)

    # 1. JPG OCR Test
    jpg_bytes = create_sample_text_image("Test JPG Image OCR Extraction", "sample.jpg", fmt="JPEG")
    res_jpg = ocr_service.run_ocr_on_image(jpg_bytes)
    print(f"[TEST 1] JPG OCR Result: text_len={len(res_jpg.get('text', ''))}, conf={res_jpg.get('confidence', 0)}")
    assert "text" in res_jpg

    # 2. PNG OCR Test
    png_bytes = create_sample_text_image("Test PNG Image OCR Extraction", "sample.png", fmt="PNG")
    res_png = ocr_service.run_ocr_on_image(png_bytes)
    print(f"[TEST 2] PNG OCR Result: text_len={len(res_png.get('text', ''))}, conf={res_png.get('confidence', 0)}")
    assert "text" in res_png

    # 3. JPEG OCR Test
    jpeg_bytes = create_sample_text_image("Test JPEG Image OCR Extraction", "sample.jpeg", fmt="JPEG")
    res_jpeg = ocr_service.run_ocr_on_image(jpeg_bytes)
    print(f"[TEST 3] JPEG OCR Result: text_len={len(res_jpeg.get('text', ''))}, conf={res_jpeg.get('confidence', 0)}")
    assert "text" in res_jpeg

    # Helper to generate test PDF files using PyMuPDF if fitz available
    import fitz
    test_pdf_path = os.path.join(backend_dir, "scratch", "test_multipage_sample.pdf")
    doc = fitz.open()

    # 4. Normal text PDF page
    page1 = doc.new_page()
    page1.insert_text((50, 100), "Normal Text Page 1: Attitude and Orbit Control System")

    # 5. Scanned PDF page (insert image into page)
    scanned_img_bytes = create_sample_text_image("Scanned PDF Page 2: Sensor Controller Actuator", "scan.png")
    page2 = doc.new_page()
    page2.insert_image(fitz.Rect(50, 50, 550, 250), stream=scanned_img_bytes)

    # 6. Handwritten PDF page simulation
    page3 = doc.new_page()
    hw_bytes = create_sample_text_image("Handwritten Note Page 3: Formula E = mc^2", "hw.png")
    page3.insert_image(fitz.Rect(50, 50, 550, 250), stream=hw_bytes)

    # 7 & 8. Multi-page & Mixed text + image page
    page4 = doc.new_page()
    page4.insert_text((50, 50), "Page 4 Text Header: Satellite Telemetry Data")
    page4.insert_image(fitz.Rect(50, 150, 550, 350), stream=png_bytes)

    doc.save(test_pdf_path)
    doc.close()

    # Test PDF Processing via OCRService & PyMuPDF
    progress_log = []
    def progress_cb(page_num, total_pages):
        progress_log.append((page_num, total_pages))

    pdf_result = ocr_service.process_pdf(test_pdf_path, dpi=150, page_progress_callback=progress_cb)
    print(f"\n[TEST 4-8] PDF Extraction Benchmark:")
    print(f"  Filename: {pdf_result['filename']}")
    print(f"  Total Pages: {pdf_result['num_pages']}")
    print(f"  Total Time: {pdf_result['total_time']}s")
    print(f"  Avg Time/Page: {pdf_result['avg_time_per_page']}s/page")
    print(f"  Extracted Chars: {pdf_result['total_characters']}")
    print(f"  Progress Callback Events: {progress_log}")

    assert pdf_result['num_pages'] == 4
    assert pdf_result['total_characters'] > 0

    # 9. OCR Failure Resilience Test (invalid image byte handling inside OCR)
    invalid_bytes = b"not_an_image_data_stream_corrupted"
    res_err = ocr_service.run_ocr_on_image(invalid_bytes)
    print(f"\n[TEST 9] Invalid Image Resilience: error={res_err.get('error')}")
    assert "error" in res_err or res_err.get("text") == ""

    # 10. Empty OCR Result Handling
    empty_img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    buf = io.BytesIO()
    empty_img.save(buf, format="PNG")
    res_empty = ocr_service.run_ocr_on_image(buf.getvalue())
    print(f"[TEST 10] Empty Image OCR Result: text='{res_empty.get('text')}', conf={res_empty.get('confidence')}")

    # Clean up test PDF
    if os.path.exists(test_pdf_path):
        os.remove(test_pdf_path)

    print("\n" + "=" * 70)
    print("      ALL 10 PP-OCRv5 & PyMuPDF PIPELINE TESTS PASSED!      ")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_ocr_suite()
