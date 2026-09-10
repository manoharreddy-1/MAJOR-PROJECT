"""PDF text extraction using PyMuPDF and pypdf (with pure-Python fallback)."""
import io
import logging
import re
from typing import Tuple

from config.settings import MIN_PDF_TEXT_LENGTH

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    _FITZ_AVAILABLE = True
except Exception:
    _FITZ_AVAILABLE = False
    logger.info("PyMuPDF not available.")

try:
    from pypdf import PdfReader
    _PYPDF_AVAILABLE = True
except Exception:
    _PYPDF_AVAILABLE = False
    logger.info("pypdf not available.")


def _extract_with_fitz(file_bytes: bytes) -> Tuple[str, bool]:
    """Extract text using PyMuPDF."""
    text_parts = []
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


def _extract_with_pypdf(file_bytes: bytes) -> Tuple[str, bool]:
    """Extract text using pure-Python pypdf."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    full_text = "\n".join(text_parts).strip()
    needs_ocr = len(full_text) < MIN_PDF_TEXT_LENGTH
    return full_text, needs_ocr


def _basic_pdf_extract(file_bytes: bytes) -> str:
    """Last-resort raw byte extraction."""
    try:
        text = file_bytes.decode('latin-1', errors='ignore')
        chunks = re.findall(r'\(([^)]+)\)', text)
        readable = []
        for chunk in chunks:
            cleaned = chunk.strip()
            if len(cleaned) > 2 and cleaned.isprintable():
                readable.append(cleaned)
        return ' '.join(readable)
    except Exception:
        return ""


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, bool]:
    """
    Extract text from PDF bytes.
    Tries PyMuPDF -> pypdf -> raw stream fallback.
    """
    if _FITZ_AVAILABLE:
        try:
            return _extract_with_fitz(file_bytes)
        except Exception as exc:
            logger.warning("PyMuPDF failed: %s; falling back to pypdf/basic.", exc)

    if _PYPDF_AVAILABLE:
        try:
            return _extract_with_pypdf(file_bytes)
        except Exception as exc:
            logger.warning("pypdf failed: %s; falling back to basic extraction.", exc)

    # Basic raw byte scan
    try:
        text = _basic_pdf_extract(file_bytes)
        if text and len(text) >= MIN_PDF_TEXT_LENGTH:
            return text, False
        return text, True
    except Exception as exc:
        logger.error("Basic PDF extraction failed: %s", exc)
        raise ValueError("Could not read PDF. Please ensure the file is a valid PDF.") from exc
