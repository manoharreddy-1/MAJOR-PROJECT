"""Evaluation metrics for SBERT vs TF-IDF comparison."""
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.metrics.pairwise import cosine_similarity


def compute_cosine_similarity(emb_a: np.ndarray, emb_b: np.ndarray) -> float:
    """Compute cosine similarity between two embedding vectors."""
    a = emb_a.reshape(1, -1)
    b = emb_b.reshape(1, -1)
    return float(cosine_similarity(a, b)[0][0])


def normalize_similarity_to_score(similarity: float) -> float:
    """Map cosine similarity to 0-100 score."""
    return max(0.0, min(100.0, similarity * 100))


def compute_classification_metrics(
    y_true: list, y_pred: list, average: str = "binary"
) -> dict:
    """Compute precision, recall, F1 for binary classification."""
    return {
        "precision": round(precision_score(y_true, y_pred, average=average, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, average=average, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, average=average, zero_division=0), 4),
    }


def mean_reciprocal_rank(relevance_scores: list) -> float:
    """Compute MRR from a list of ranked relevance scores."""
    for i, score in enumerate(relevance_scores):
        if score >= 1:
            return 1.0 / (i + 1)
    return 0.0


def recall_at_k(relevant_items: set, retrieved_items: list, k: int) -> float:
    """Compute Recall@K."""
    if not relevant_items:
        return 0.0
    retrieved_k = set(retrieved_items[:k])
    return len(relevant_items & retrieved_k) / len(relevant_items)
