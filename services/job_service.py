"""Job description analysis and storage service."""
import logging
from typing import Any, Dict, Optional

from bson import ObjectId

from database.models import serialize_doc, utc_now
from database.mongodb import get_collection, COLLECTIONS
from parsers.job_parser import JobDescriptionParser
from parsers.pdf_parser import extract_text_from_pdf
from utils.text_cleaner import clean_text
from utils.validators import validate_text

logger = logging.getLogger(__name__)


class JobService:
    """Handle job description input and requirement extraction."""

    def __init__(self):
        self.parser = JobDescriptionParser()
        self.collection = get_collection(COLLECTIONS["job_descriptions"])

    def analyze_text(self, text: str, title: str = None, user_id: str = None) -> Dict[str, Any]:
        """Parse pasted job description text."""
        valid, msg = validate_text(text, "Job description", min_length=20)
        if not valid:
            raise ValueError(msg)

        parsed = self.parser.parse(text, title=title)

        doc = {
            "user_id": user_id,
            "raw_text": clean_text(text),
            "requirements": parsed,
            "created_at": utc_now(),
        }
        result = self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id

        return {
            "job_description_id": str(result.inserted_id),
            "requirements": parsed,
        }

    def analyze_file(self, file_bytes: bytes, filename: str, title: str = None, user_id: str = None) -> Dict[str, Any]:
        """Extract and parse job description from uploaded file (PDF, DOCX, TXT)."""
        lower = filename.lower()
        if lower.endswith(".pdf"):
            text, _ = extract_text_from_pdf(file_bytes)
        elif lower.endswith(".docx"):
            text = self._extract_docx(file_bytes)
        else:
            text = file_bytes.decode("utf-8", errors="ignore")

        return self.analyze_text(text, title=title, user_id=user_id)

    def _extract_docx(self, file_bytes: bytes) -> str:
        """Extract text from docx bytes with graceful XML fallback."""
        try:
            import io
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            lines = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            lines.append(cell.text.strip())
            return "\n".join(lines)
        except Exception:
            try:
                import io
                import zipfile
                import xml.etree.ElementTree as ET
                zf = zipfile.ZipFile(io.BytesIO(file_bytes))
                xml_content = zf.read("word/document.xml")
                root = ET.fromstring(xml_content)
                texts = [elem.text for elem in root.iter() if elem.text]
                return " ".join(texts)
            except Exception:
                return file_bytes.decode("utf-8", errors="ignore")

    def get_job(self, job_id: str) -> Optional[Dict]:
        doc = self.collection.find_one({"_id": ObjectId(job_id)})
        return serialize_doc(doc)

    def update_requirements(self, job_id: str, requirements: Dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"requirements": requirements, "updated_at": utc_now()}},
        )
        return (getattr(result, "matched_count", 0) > 0) or (getattr(result, "modified_count", 0) > 0) or bool(result)
