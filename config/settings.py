"""Application configuration and ATS scoring weights."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _get_int(key: str, default: int) -> int:
    val = os.getenv(key)
    if not val or not val.strip():
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default


def _get_float(key: str, default: float) -> float:
    val = os.getenv(key)
    if not val or not val.strip():
        return default
    try:
        return float(val.strip())
    except ValueError:
        return default


# Flask
SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-change-in-production"
DEBUG = (os.getenv("FLASK_DEBUG") or "false").lower() == "true"

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI") or "mongodb://localhost:27017"
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME") or "ai_resume_analyzer"

# Hugging Face
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY") or ""
HUGGINGFACE_LLM_MODEL = os.getenv("HUGGINGFACE_LLM_MODEL") or "HuggingFaceH4/zephyr-7b-beta"

# Gemini API (Google Generative AI)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyBNl9TtEJKWC_feqFVjG71gIKKR4lRSW-A"
GEMINI_API_KEY_ALT = os.getenv("GEMINI_API_KEY_ALT") or "AIzaSyAPF9Cxk0ut4XgV9jyai-lOFh98L1C5DH4"
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"

# SBERT Model
SBERT_MODEL_NAME = os.getenv("SBERT_MODEL_NAME") or "sentence-transformers/all-MiniLM-L6-v2"
NER_MODEL_NAME = os.getenv("NER_MODEL_NAME") or "dslim/bert-base-NER"

# File Upload
MAX_UPLOAD_SIZE_MB = _get_int("MAX_UPLOAD_SIZE_MB", 10)
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}
MIN_PDF_TEXT_LENGTH = _get_int("MIN_PDF_TEXT_LENGTH", 100)

# ATS Score Weights (must sum to 1.0)
ATS_WEIGHTS = {
    "semantic": _get_float("ATS_WEIGHT_SEMANTIC", 0.45),
    "skills": _get_float("ATS_WEIGHT_SKILLS", 0.30),
    "experience": _get_float("ATS_WEIGHT_EXPERIENCE", 0.15),
    "education": _get_float("ATS_WEIGHT_EDUCATION", 0.10),
}

# Skill Matching Thresholds
HIGH_SKILL_THRESHOLD = _get_float("HIGH_SKILL_THRESHOLD", 0.72)
MEDIUM_SKILL_THRESHOLD = _get_float("MEDIUM_SKILL_THRESHOLD", 0.55)

# Semantic score normalization
SEMANTIC_SCORE_MIN = _get_float("SEMANTIC_SCORE_MIN", 0.0)
SEMANTIC_SCORE_MAX = _get_float("SEMANTIC_SCORE_MAX", 1.0)

# CORS
CORS_ORIGINS = (os.getenv("CORS_ORIGINS") or "*").split(",")

# Rate limiting
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT") or "100 per hour"
