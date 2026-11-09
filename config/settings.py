"""Application configuration and ATS scoring weights."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_API_KEY_ALT = os.getenv("GEMINI_API_KEY_ALT", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

# Pool of available Gemini API keys with sequential rotation and fallback
# Dynamically reads from GEMINI_API_KEYS (comma-separated list) or numbered GEMINI_API_KEY_1..10
_env_key_list = [k.strip() for k in os.getenv("GEMINI_API_KEYS", "").split(",") if k.strip()]
_numbered_keys = [
    os.getenv(f"GEMINI_API_KEY_{i}", "").strip() for i in range(1, 11)
]
_all_candidate_keys = _env_key_list + _numbered_keys + [GEMINI_API_KEY, GEMINI_API_KEY_ALT]
_seen_keys = set()
GEMINI_API_KEYS_POOL = [k for k in _all_candidate_keys if k and not (k in _seen_keys or _seen_keys.add(k))]

# YouTube Data API Key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") or os.getenv("NEXT_PUBLIC_YOUTUBE_API_KEY") or GEMINI_API_KEY

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
