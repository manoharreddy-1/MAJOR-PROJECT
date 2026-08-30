"""Score normalization and clamping utilities."""
from typing import Dict

from config.settings import ATS_WEIGHTS, SEMANTIC_SCORE_MIN, SEMANTIC_SCORE_MAX


def clamp_score(score: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamp score to valid range."""
    return max(min_val, min(max_val, score))


def normalize_cosine_to_score(similarity: float) -> float:
    """
    Convert raw cosine similarity to 0-100 score.

    MiniLM cosine similarities typically fall in [0, 1] for related texts.
    We linearly map from [SEMANTIC_SCORE_MIN, SEMANTIC_SCORE_MAX] to [0, 100].
    """
    sim = max(SEMANTIC_SCORE_MIN, min(SEMANTIC_SCORE_MAX, similarity))
    if SEMANTIC_SCORE_MAX == SEMANTIC_SCORE_MIN:
        return 0.0
    normalized = (sim - SEMANTIC_SCORE_MIN) / (SEMANTIC_SCORE_MAX - SEMANTIC_SCORE_MIN)
    return clamp_score(normalized * 100)


def calculate_weighted_ats_score(
    semantic: float,
    skills: float,
    experience: float,
    education: float,
    weights: Dict[str, float] = None,
) -> float:
    """
    Calculate overall ATS score from component scores.

    Each component should already be on 0-100 scale.
    """
    w = weights or ATS_WEIGHTS
    overall = (
        semantic * w["semantic"]
        + skills * w["skills"]
        + experience * w["experience"]
        + education * w["education"]
    )
    return round(clamp_score(overall), 1)


def score_breakdown(
    semantic: float,
    skills: float,
    experience: float,
    education: float,
    weights: Dict[str, float] = None,
) -> Dict:
    """Generate transparent score breakdown for display."""
    w = weights or ATS_WEIGHTS
    overall = calculate_weighted_ats_score(semantic, skills, experience, education, w)
    return {
        "overall": overall,
        "components": {
            "semantic": {
                "score": round(semantic, 1),
                "weight": w["semantic"],
                "weighted": round(semantic * w["semantic"], 1),
            },
            "skills": {
                "score": round(skills, 1),
                "weight": w["skills"],
                "weighted": round(skills * w["skills"], 1),
            },
            "experience": {
                "score": round(experience, 1),
                "weight": w["experience"],
                "weighted": round(experience * w["experience"], 1),
            },
            "education": {
                "score": round(education, 1),
                "weight": w["education"],
                "weighted": round(education * w["education"], 1),
            },
        },
        "weights": w,
        "formula": (
            f"({semantic:.0f}/100 × {w['semantic']*100:.0f}%) + "
            f"({skills:.0f}/100 × {w['skills']*100:.0f}%) + "
            f"({experience:.0f}/100 × {w['experience']*100:.0f}%) + "
            f"({education:.0f}/100 × {w['education']*100:.0f}%)"
        ),
    }


def get_match_label(score: float) -> str:
    """Return human-readable match label."""
    if score >= 80:
        return "Excellent Match"
    if score >= 65:
        return "Good Match"
    if score >= 50:
        return "Moderate Match"
    if score >= 35:
        return "Weak Match"
    return "Poor Match"
