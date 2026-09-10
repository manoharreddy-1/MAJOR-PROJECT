"""SBERT model singleton for semantic embeddings."""
import logging
import threading
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

_model = None
_model_lock = threading.Lock()

try:
    import numpy as np
    _HAS_NUMPY = True
except Exception:
    _HAS_NUMPY = False


def get_sbert_model():
    """Load and cache SentenceTransformer model (singleton)."""
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model
        try:
            from config.settings import SBERT_MODEL_NAME
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SBERT model: %s", SBERT_MODEL_NAME)
            _model = SentenceTransformer(SBERT_MODEL_NAME)
            logger.info("SBERT model loaded successfully.")
            return _model
        except Exception as exc:
            logger.warning("Failed to load SBERT model: %s", exc)
            raise


def encode_texts(texts: List[str], batch_size: int = 32) -> Any:
    """Encode a list of texts into SBERT embeddings."""
    if not texts:
        return np.array([]) if _HAS_NUMPY else []
    model = get_sbert_model()
    valid_texts = [t if t and t.strip() else " " for t in texts]
    embeddings = model.encode(
        valid_texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings


def encode_single(text: str) -> Any:
    """Encode a single text string."""
    if not text or not text.strip():
        text = " "
    return encode_texts([text])[0]
