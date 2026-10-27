"""Tests for skill normalization."""
import pytest
from utils.skill_normalizer import normalize_skill_name, deduplicate_skills


class TestSkillNormalizer:
    def test_normalize_python_variants(self):
        assert normalize_skill_name("python3") == "Python"
        assert normalize_skill_name("Python Programming") == "Python"
        assert normalize_skill_name("PYTHON") == "PYTHON"

    def test_normalize_ml(self):
        assert normalize_skill_name("machine learning") == "Machine Learning"
        assert normalize_skill_name("tensorflow") == "TensorFlow"

    def test_deduplicate(self):
        skills = ["Python", "python3", "Python Programming", "JavaScript", "js"]
        result = deduplicate_skills(skills)
        assert "Python" in result
        assert "JavaScript" in result
        assert len(result) == 2

    def test_no_false_merge(self):
        skills = ["Java", "JavaScript"]
        result = deduplicate_skills(skills)
        assert "Java" in result
        assert "JavaScript" in result
