import io
import gc
import os
import sys

# Ensure Windows PyTorch DLLs can be loaded by dependencies
if os.name == "nt":
    try:
        import site
        for p in site.getsitepackages():
            tlib = os.path.join(p, "torch", "lib")
            if os.path.exists(tlib):
                try:
                    os.add_dll_directory(tlib)
                except Exception:
                    pass
                os.environ["PATH"] = tlib + ";" + os.environ.get("PATH", "")
    except Exception:
        pass

try:
    import torch
except Exception:
    pass

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_DISABLE_ONEDNN"] = "1"
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["FLAGS_enable_pir_in_executor"] = "0"
os.environ["FLAGS_enable_pir_onednn"] = "0"

try:
    import paddle
    paddle.set_flags({
        "FLAGS_use_mkldnn": False,
        "FLAGS_enable_pir_api": False,
        "FLAGS_enable_pir_in_executor": False
    })
except Exception:
    pass

import time
import logging

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Try importing PyMuPDF (fitz)
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None


class OCRService:
    """
    Lightweight OCR Service using PP-OCRv5 Mobile (PaddleOCR) + PyMuPDF page rendering.
    Designed for deployment on Render Free (CPU, 512MB RAM).
    """

    def __init__(self):
        self._ocr_engine = None

    def _get_ocr_engine(self):
        """Lazy initialization of PP-OCRv5 Mobile engine."""
        if self._ocr_engine is not None:
            return self._ocr_engine

        try:
            if os.name == "nt":
                try:
                    import site
                    for p in site.getsitepackages():
                        tlib = os.path.join(p, "torch", "lib")
                        if os.path.exists(tlib):
                            os.add_dll_directory(tlib)
                except Exception:
                    pass
            from paddleocr import PaddleOCR
        except Exception as e:
            logger.warning(f"[OCR] PaddleOCR import failed ({e}). Falling back to PyMuPDF text extraction.")
            return None

        logger.info("[OCR] Initializing PP-OCRv5 Mobile engine on CPU...")
        try:
            # PP-OCRv5 Mobile / lightweight configuration
            try:
                self._ocr_engine = PaddleOCR(
                    use_angle_cls=True,
                    lang="en",
                    enable_mkldnn=False,
                )
            except Exception:
                try:
                    self._ocr_engine = PaddleOCR(
                        use_angle_cls=True,
                        lang="en",
                        enable_onednn=False,
                    )
                except Exception:
                    self._ocr_engine = PaddleOCR(
                        use_angle_cls=True,
                        lang="en",
                    )
            logger.info("[OCR] PP-OCRv5 Mobile engine loaded successfully.")
        except Exception as e:
            logger.error(f"[OCR] Failed to initialize PaddleOCR: {e}")
            self._ocr_engine = None

        return self._ocr_engine

    def run_ocr_on_image(self, image_bytes: bytes) -> dict:
        """
        Runs PP-OCRv5 Mobile on an image (JPG/PNG/JPEG).
        Returns dict containing 'text', 'confidence', and block details.
        """
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")
            img_np = np.array(pil_img)
        except Exception as e:
            logger.error(f"[OCR] Failed to decode image: {e}")
            return {"text": "", "confidence": 0.0, "error": str(e)}

        ocr_engine = self._get_ocr_engine()
        if ocr_engine is None:
            return {"text": "", "confidence": 0.0, "error": "OCR engine uninitialized"}

        try:
            try:
                results = ocr_engine.ocr(img_np)
            except TypeError:
                results = ocr_engine.ocr(img_np, cls=True)

            text_lines = []
            confidences = []

            if results:
                for res in results:
                    if isinstance(res, list):
                        for line in res:
                            if isinstance(line, (list, tuple)) and len(line) >= 2:
                                text_tuple = line[1]
                                if isinstance(text_tuple, (list, tuple)) and len(text_tuple) >= 2:
                                    text, conf = text_tuple[0], text_tuple[1]
                                    if text and str(text).strip():
                                        text_lines.append(str(text).strip())
                                        confidences.append(float(conf))
                    elif isinstance(res, dict):
                        rec_texts = res.get("rec_text", []) or res.get("rec_texts", [])
                        rec_scores = res.get("rec_score", []) or res.get("rec_scores", [])
                        if rec_texts:
                            for idx, text in enumerate(rec_texts):
                                if text and str(text).strip():
                                    text_lines.append(str(text).strip())
                                    if idx < len(rec_scores):
                                        confidences.append(float(rec_scores[idx]))

            full_text = "\n".join(text_lines)
            avg_conf = float(np.mean(confidences)) if confidences else 0.0

            return {
                "text": full_text,
                "confidence": round(avg_conf, 3),
                "lines_count": len(text_lines),
            }
        except Exception as e:
            logger.error(f"[OCR] Error during image OCR execution: {e}")
            return {"text": "", "confidence": 0.0, "error": str(e)}

    def process_pdf(
        self,
        file_path: str,
        dpi: int = 150,
        page_progress_callback=None
    ) -> dict:
        """
        Processes a PDF by rendering each page using PyMuPDF (fitz) at ~150 DPI,
        running PP-OCRv5 Mobile on each page sequentially, and compiling text & metadata.
        """
        start_time = time.time()
        filename = os.path.basename(file_path)

        if fitz is None:
            raise RuntimeError("PyMuPDF (fitz) is not installed.")

        try:
            doc = fitz.open(file_path)
        except Exception as e:
            logger.error(f"[OCR] Failed to open PDF '{filename}': {e}")
            raise ValueError(f"Corrupted or password-protected PDF: {e}")

        num_pages = len(doc)
        logger.info(f"[OCR] Starting PyMuPDF page rendering + PP-OCRv5 for '{filename}' ({num_pages} pages)...")

        pages_data = []
        full_text_blocks = []
        failed_pages = []

        matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)

        for page_index in range(num_pages):
            page_num = page_index + 1
            if page_progress_callback:
                page_progress_callback(page_num, num_pages)

            try:
                page = doc.load_page(page_index)

                # Direct PyMuPDF text extraction as fast fallback / hybrid base
                direct_text = page.get_text("text").strip()

                # Render page to 150 DPI image pixmap
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                img_bytes = pix.tobytes("png")

                # Perform PP-OCRv5 Mobile on rendered page image
                ocr_result = self.run_ocr_on_image(img_bytes)
                ocr_text = ocr_result.get("text", "")
                confidence = ocr_result.get("confidence", 0.0)

                # Clean up page pixmap memory immediately
                del pix
                del img_bytes

                # Combine OCR text and direct text if complementary
                page_text = ocr_text if ocr_text else direct_text
                if ocr_text and direct_text and direct_text not in ocr_text:
                    # Append any missed direct text lines
                    page_text = f"{ocr_text}\n{direct_text}"

                if page_text:
                    page_header = f"--- Page {page_num} (Confidence: {confidence:.2f}) ---"
                    full_text_blocks.append(f"{page_header}\n{page_text}")
                    pages_data.append({
                        "page_number": page_num,
                        "text": page_text,
                        "confidence": confidence,
                        "source": filename,
                        "content_type": "ocr",
                        "extraction_method": "ppocrv5"
                    })
                else:
                    logger.warning(f"[OCR] Page {page_num} yielded no text.")
            except Exception as e:
                logger.error(f"[OCR] Failed to process page {page_num} of '{filename}': {e}")
                failed_pages.append(page_num)
                continue

        doc.close()
        gc.collect()

        total_time = time.time() - start_time
        avg_time_per_page = total_time / max(num_pages, 1)
        full_text = "\n\n".join(full_text_blocks)
        total_chars = len(full_text)

        # Benchmark logging
        logger.info("=" * 60)
        logger.info(f"Document: {filename}")
        logger.info(f"Pages: {num_pages}")
        logger.info(f"OCR time: {total_time:.2f} seconds")
        logger.info(f"Average: {avg_time_per_page:.2f} sec/page")
        logger.info(f"Characters: {total_chars}")
        if failed_pages:
            logger.info(f"Failed pages: {failed_pages}")
        logger.info("=" * 60)

        return {
            "filename": filename,
            "num_pages": num_pages,
            "text": full_text,
            "pages": pages_data,
            "failed_pages": failed_pages,
            "total_time": round(total_time, 2),
            "avg_time_per_page": round(avg_time_per_page, 2),
            "total_characters": total_chars,
        }


# Singleton instance
ocr_service = OCRService()
