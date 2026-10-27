"""Tests for scoring utilities."""
import pytest
from utils.scoring import (
    clamp_score,
    normalize_cosine_to_score,
    calculate_weighted_ats_score,
    score_breakdown,
    get_match_label,
)


class TestScoring:
    def test_clamp_score(self):
        assert clamp_score(50) == 50
        assert clamp_score(150) == 100
        assert clamp_score(-10) == 0

    def test_normalize_cosine(self):
        assert normalize_cosine_to_score(0.0) == 0.0
        assert normalize_cosine_to_score(1.0) == 100.0
        assert normalize_cosine_to_score(0.5) == 50.0

    def test_weighted_ats_score(self):
        score = calculate_weighted_ats_score(80, 70, 60, 90)
        expected = 80 * 0.45 + 70 * 0.30 + 60 * 0.15 + 90 * 0.10
        assert score == round(expected, 1)

    def test_score_breakdown(self):
        result = score_breakdown(86, 80, 78, 90)
        assert "overall" in result
        assert "components" in result
        assert result["components"]["semantic"]["score"] == 86

    def test_match_label(self):
        assert get_match_label(85) == "Excellent Match"
        assert get_match_label(70) == "Good Match"
        assert get_match_label(55) == "Moderate Match"
        assert get_match_label(30) == "Poor Match"
