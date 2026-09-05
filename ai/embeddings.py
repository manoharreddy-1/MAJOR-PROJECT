"""Embedding utilities and cosine similarity calculations.

Supports two backends:
  1. SBERT (sentence-transformers) - full semantic similarity (local/GPU environments)
  2. Keyword fallback - TF-IDF based similarity (Vercel/serverless environments)

The backend is selected automatically based on available dependencies.
"""
import logging
import re
from collections import Counter
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# --- Detect available backend ---
_USE_SBERT = False
try:
    from ai.sbert_model import encode_single, encode_texts
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
    _USE_SBERT = True
    logger.info("SBERT backend available for semantic matching.")
except ImportError:
    logger.info("SBERT not available; using keyword-based fallback for matching.")


# Simple in-memory embedding cache (safe for serverless warm instances)
_embedding_cache: dict = {}
_CACHE_MAX_SIZE = 500


# ============================================================
# Keyword-based fallback (when SBERT/torch not installed)
# ============================================================
def _tokenize(text: str) -> List[str]:
    """Simple whitespace + punctuation tokenizer, lowercased."""
    return re.findall(r'\b[a-z0-9][\w+#.\-]*\b', text.lower())


def _keyword_similarity(text_a: str, text_b: str) -> float:
    """
    Compute keyword overlap similarity (Jaccard-like with frequency weighting).
    Returns a value in [0, 1].
    """
    if not text_a or not text_b:
        return 0.0
    tokens_a = Counter(_tokenize(text_a))
    tokens_b = Counter(_tokenize(text_b))
    if not tokens_a or not tokens_b:
        return 0.0
    # Intersection-over-union on token sets
    common = set(tokens_a.keys()) & set(tokens_b.keys())
    union = set(tokens_a.keys()) | set(tokens_b.keys())
    if not union:
        return 0.0
    return len(common) / len(union)


def _keyword_best_match(query: str, candidates: List[str]) -> Tuple[float, Optional[str], int]:
    """Find best keyword-overlap match for query among candidates."""
    if not query or not candidates:
        return 0.0, None, -1
    best_sim = 0.0
    best_text = None
    best_idx = -1
    for i, cand in enumerate(candidates):
        if not cand or not cand.strip():
            continue
        sim = _keyword_similarity(query, cand)
        if sim > best_sim:
            best_sim = sim
            best_text = cand
            best_idx = i
    return best_sim, best_text, best_idx


# ============================================================
# Public API (auto-selects backend)
# ============================================================
def _cache_key(text: str) -> str:
    return text.strip().lower()[:200]


def get_embedding(text: str, use_cache: bool = True) -> np.ndarray:
    """Get embedding for text with optional caching. Requires SBERT backend."""
    if not _USE_SBERT:
        # Return a dummy embedding; callers should use text_similarity() instead
        return np.zeros(384)

    if not text or not text.strip():
        return encode_single(" ")

    if use_cache:
        key = _cache_key(text)
        if key in _embedding_cache:
            return _embedding_cache[key]

    embedding = encode_single(text)

    if use_cache and len(_embedding_cache) < _CACHE_MAX_SIZE:
        _embedding_cache[_cache_key(text)] = embedding

    return embedding


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two embedding vectors."""
    if not _USE_SBERT:
        return 0.0
    if a is None or b is None:
        return 0.0
    a = a.reshape(1, -1)
    b = b.reshape(1, -1)
    sim = sklearn_cosine_similarity(a, b)[0][0]
    return float(sim)


def text_similarity(text_a: str, text_b: str) -> float:
    """Calculate similarity between two texts. Auto-selects backend."""
    if not text_a or not text_b:
        return 0.0
    if _USE_SBERT:
        emb_a = get_embedding(text_a)
        emb_b = get_embedding(text_b)
        return cosine_sim(emb_a, emb_b)
    else:
        return _keyword_similarity(text_a, text_b)


def text_similarity_score(text_a: str, text_b: str) -> float:
    """Return normalized 0-100 similarity score."""
    from utils.scoring import normalize_cosine_to_score
    return normalize_cosine_to_score(text_similarity(text_a, text_b))


def best_match_similarity(
    query: str, candidates: List[str]
) -> Tuple[float, Optional[str], int]:
    """
    Find best semantic match for query among candidates.

    Returns:
        (best_similarity, best_candidate, best_index)
    """
    if not query or not candidates:
        return 0.0, None, -1

    if _USE_SBERT:
        valid = [(i, c) for i, c in enumerate(candidates) if c and c.strip()]
        if not valid:
            return 0.0, None, -1
        indices, texts = zip(*valid)
        query_emb = get_embedding(query).reshape(1, -1)
        candidate_embs = encode_texts(list(texts))
        similarities = sklearn_cosine_similarity(query_emb, candidate_embs)[0]
        best_idx = int(np.argmax(similarities))
        return float(similarities[best_idx]), texts[best_idx], indices[best_idx]
    else:
        return _keyword_best_match(query, candidates)


def batch_similarity_scores(
    queries: List[str], candidates: List[str]
) -> np.ndarray:
    """Compute similarity matrix between queries and candidates."""
    if not queries or not candidates:
        return np.array([])

    if _USE_SBERT:
        query_embs = encode_texts(queries)
        candidate_embs = encode_texts(candidates)
        return sklearn_cosine_similarity(query_embs, candidate_embs)
    else:
        # Fallback: keyword similarity matrix
        result = np.zeros((len(queries), len(candidates)))
        for i, q in enumerate(queries):
            for j, c in enumerate(candidates):
                result[i, j] = _keyword_similarity(q, c)
        return result
