"""Embedding utilities and cosine similarity calculations."""
import logging
from typing import List, Optional, Tuple, Union

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ai.sbert_model import encode_single, encode_texts
from utils.scoring import normalize_cosine_to_score

logger = logging.getLogger(__name__)

# Simple in-memory embedding cache (safe for serverless warm instances)
_embedding_cache: dict = {}
_CACHE_MAX_SIZE = 500


def _cache_key(text: str) -> str:
    return text.strip().lower()[:200]


def get_embedding(text: str, use_cache: bool = True) -> np.ndarray:
    """Get embedding for text with optional caching."""
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
    if a is None or b is None:
        return 0.0
    a = a.reshape(1, -1)
    b = b.reshape(1, -1)
    sim = cosine_similarity(a, b)[0][0]
    return float(sim)


def text_similarity(text_a: str, text_b: str) -> float:
    """Calculate cosine similarity between two texts using SBERT."""
    if not text_a or not text_b:
        return 0.0
    emb_a = get_embedding(text_a)
    emb_b = get_embedding(text_b)
    return cosine_sim(emb_a, emb_b)


def text_similarity_score(text_a: str, text_b: str) -> float:
    """Return normalized 0-100 similarity score."""
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

    valid = [(i, c) for i, c in enumerate(candidates) if c and c.strip()]
    if not valid:
        return 0.0, None, -1

    indices, texts = zip(*valid)
    query_emb = get_embedding(query).reshape(1, -1)
    candidate_embs = encode_texts(list(texts))

    similarities = cosine_similarity(query_emb, candidate_embs)[0]
    best_idx = int(np.argmax(similarities))
    return float(similarities[best_idx]), texts[best_idx], indices[best_idx]


def batch_similarity_scores(
    queries: List[str], candidates: List[str]
) -> np.ndarray:
    """Compute similarity matrix between queries and candidates."""
    if not queries or not candidates:
        return np.array([])

    query_embs = encode_texts(queries)
    candidate_embs = encode_texts(candidates)
    return cosine_similarity(query_embs, candidate_embs)
