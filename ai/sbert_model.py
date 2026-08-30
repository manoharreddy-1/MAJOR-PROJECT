"""SBERT model singleton for semantic embeddings."""
import logging
import threading
from typing import List, Optional

import numpy as np

from config.settings import SBERT_MODEL_NAME

logger = logging.getLogger(__name__)

_model = None
_model_lock = threading.Lock()


def get_sbert_model():
    """
    Load and cache SentenceTransformer model (singleton).

    Uses sentence-transformers/all-MiniLM-L6-v2 by default.
    Model is loaded once and reused across requests.
    """
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SBERT model: %s", SBERT_MODEL_NAME)
            _model = SentenceTransformer(SBERT_MODEL_NAME)
            logger.info("SBERT model loaded successfully.")
            return _model
        except Exception as exc:
            logger.error("Failed to load SBERT model: %s", exc)
            raise RuntimeError(
                f"Could not load SBERT model '{SBERT_MODEL_NAME}'. "
                "Ensure sentence-transformers is installed."
            ) from exc


def encode_texts(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """Encode a list of texts into SBERT embeddings."""
    if not texts:
        return np.array([])
    model = get_sbert_model()
    # Filter empty strings
    valid_texts = [t if t and t.strip() else " " for t in texts]
    embeddings = model.encode(
        valid_texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings


def encode_single(text: str) -> np.ndarray:
    """Encode a single text string."""
    if not text or not text.strip():
        text = " "
    return encode_texts([text])[0]
