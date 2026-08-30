"""PDF text extraction using PyMuPDF."""
import logging
from typing import Tuple

import fitz  # PyMuPDF

from config.settings import MIN_PDF_TEXT_LENGTH

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, bool]:
    """
    Extract text from PDF bytes.

    Returns:
        (extracted_text, needs_ocr)
    """
    text_parts = []
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if doc.page_count == 0:
            return "", False

        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text_parts.append(page_text)

        doc.close()
        full_text = "\n".join(text_parts).strip()
        needs_ocr = len(full_text) < MIN_PDF_TEXT_LENGTH
        return full_text, needs_ocr

    except Exception as exc:
        logger.error("PDF extraction failed: %s", exc)
        raise ValueError("Could not read PDF. The file may be corrupted.") from exc
