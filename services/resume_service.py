"""Resume upload, extraction, and storage service."""
import logging
from typing import Any, Dict, Optional

from bson import ObjectId

from database.models import serialize_doc, utc_now
from database.mongodb import get_collection, COLLECTIONS
from parsers.pdf_parser import extract_text_from_pdf
from parsers.ocr_parser import extract_text_with_ocr
from parsers.resume_parser import ResumeParser
from ai.ner_model import NERModel
from utils.text_cleaner import clean_text

logger = logging.getLogger(__name__)


class ResumeService:
    """Handle resume upload, text extraction, and parsing."""

    def __init__(self):
        self.parser = ResumeParser(ner_model=NERModel())
        self.collection = get_collection(COLLECTIONS["resumes"])

    def process_upload(self, file_bytes: bytes, filename: str, user_id: str = None) -> Dict[str, Any]:
        """Extract text from PDF and parse resume information."""
        text, needs_ocr = extract_text_from_pdf(file_bytes)
        ocr_used = False

        if needs_ocr:
            ocr_text, ocr_used = extract_text_with_ocr(file_bytes)
            if ocr_text and len(ocr_text) > len(text):
                text = ocr_text

        text = clean_text(text)
        if len(text) < 50:
            raise ValueError(
                "We could not extract enough text from this PDF. "
                "Please upload a clearer resume or a text-based PDF."
            )

        parsed = self.parser.parse(text)

        doc = {
            "user_id": user_id,
            "filename": filename,
            "raw_text": text,
            "extracted": parsed,
            "ocr_used": ocr_used,
            "created_at": utc_now(),
        }

        result = self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id

        return {
            "resume_id": str(result.inserted_id),
            "filename": filename,
            "text_length": len(text),
            "ocr_used": ocr_used,
            "extracted": parsed,
        }

    def get_resume(self, resume_id: str) -> Optional[Dict]:
        """Retrieve resume by ID."""
        doc = self.collection.find_one({"_id": ObjectId(resume_id)})
        return serialize_doc(doc)

    def update_extracted(self, resume_id: str, extracted: Dict) -> bool:
        """Allow user to edit extracted information."""
        result = self.collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {"extracted": extracted, "updated_at": utc_now()}},
        )
        return result.modified_count > 0
