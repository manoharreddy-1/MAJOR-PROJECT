"""OCR fallback for scanned PDFs using Tesseract and OpenCV."""
import logging
from typing import Optional

import cv2
import fitz
import numpy as np

logger = logging.getLogger(__name__)

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available; OCR will be disabled.")


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Preprocess image for better OCR accuracy."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def ocr_page_image(image: np.ndarray) -> str:
    """Run Tesseract OCR on a preprocessed image."""
    if not TESSERACT_AVAILABLE:
        return ""
    try:
        processed = preprocess_image(image)
        text = pytesseract.image_to_string(processed, config="--psm 3")
        return text.strip()
    except Exception as exc:
        logger.warning("OCR failed for page: %s", exc)
        return ""


def extract_text_with_ocr(file_bytes: bytes, dpi: int = 200):
    """
    Extract text from scanned PDF using OCR.

    Returns:
        (text, ocr_used)
    """
    if not TESSERACT_AVAILABLE:
        logger.warning("OCR requested but Tesseract is not available.")
        return "", False

    text_parts = []
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n
            )
            if pix.n == 4:
                img_data = cv2.cvtColor(img_data, cv2.COLOR_RGBA2BGR)
            elif pix.n == 1:
                img_data = cv2.cvtColor(img_data, cv2.COLOR_GRAY2BGR)

            page_text = ocr_page_image(img_data)
            if page_text:
                text_parts.append(page_text)

        doc.close()
        return "\n".join(text_parts).strip(), True

    except Exception as exc:
        logger.error("OCR extraction failed: %s", exc)
        return "", True
