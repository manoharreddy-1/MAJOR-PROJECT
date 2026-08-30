"""Application configuration and ATS scoring weights."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "ai_resume_analyzer")

# Hugging Face
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HUGGINGFACE_LLM_MODEL = os.getenv(
    "HUGGINGFACE_LLM_MODEL", "HuggingFaceH4/zephyr-7b-beta"
)

# Gemini API (Google Generative AI)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBNl9TtEJKWC_feqFVjG71gIKKR4lRSW-A")
GEMINI_API_KEY_ALT = os.getenv("GEMINI_API_KEY_ALT", "AIzaSyAPF9Cxk0ut4XgV9jyai-lOFh98L1C5DH4")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# SBERT Model
SBERT_MODEL_NAME = os.getenv("SBERT_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
NER_MODEL_NAME = os.getenv("NER_MODEL_NAME", "dslim/bert-base-NER")

# File Upload
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}
MIN_PDF_TEXT_LENGTH = int(os.getenv("MIN_PDF_TEXT_LENGTH", "100"))

# ATS Score Weights (must sum to 1.0)
ATS_WEIGHTS = {
    "semantic": float(os.getenv("ATS_WEIGHT_SEMANTIC", "0.45")),
    "skills": float(os.getenv("ATS_WEIGHT_SKILLS", "0.30")),
    "experience": float(os.getenv("ATS_WEIGHT_EXPERIENCE", "0.15")),
    "education": float(os.getenv("ATS_WEIGHT_EDUCATION", "0.10")),
}

# Skill Matching Thresholds
HIGH_SKILL_THRESHOLD = float(os.getenv("HIGH_SKILL_THRESHOLD", "0.72"))
MEDIUM_SKILL_THRESHOLD = float(os.getenv("MEDIUM_SKILL_THRESHOLD", "0.55"))

# Semantic score normalization
# Cosine similarity range for MiniLM is typically [0, 1]; we scale to 0-100
SEMANTIC_SCORE_MIN = float(os.getenv("SEMANTIC_SCORE_MIN", "0.0"))
SEMANTIC_SCORE_MAX = float(os.getenv("SEMANTIC_SCORE_MAX", "1.0"))

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Rate limiting
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100 per hour")
