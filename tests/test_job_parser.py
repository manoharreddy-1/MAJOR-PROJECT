"""Tests for job description parser."""
import pytest
from parsers.job_parser import JobDescriptionParser


class TestJobParser:
    def setup_method(self):
        self.parser = JobDescriptionParser()

    def test_parse_basic(self):
        text = """
        Machine Learning Engineer
        
        Responsibilities:
        - Develop ML models for production
        - Work with TensorFlow and PyTorch
        
        Requirements:
        Python, Machine Learning, Deep Learning, SQL
        """
        result = self.parser.parse(text)
        assert result["job_title"]
        assert len(result["responsibilities"]) > 0

    def test_extract_skills(self):
        text = "Required: Python, TensorFlow, AWS. Preferred: Docker, Kubernetes."
        result = self.parser.parse(text)
        assert len(result["required_skills"]) > 0 or len(result["technologies"]) > 0

    def test_education_no_false_positive_me(self):
        text = """
        Software Developer
        Join our team in an agile environment with exciting requirements and competitive benefits.
        """
        result = self.parser.parse(text)
        edu = result.get("education", [])
        assert "me" not in [e.lower() for e in edu]
        assert "be" not in [e.lower() for e in edu]

    def test_education_valid_degree(self):
        text = "Requirements: Bachelor's degree in Computer Science or B.Tech in IT."
        result = self.parser.parse(text)
        edu = result.get("education", [])
        assert len(edu) > 0
        assert any("bachelor" in e.lower() or "b.tech" in e.lower() for e in edu)

    def test_responsibilities_plain_text(self):
        text = """
        Backend Developer
        Responsibilities:
        You will build scalable web services and APIs using Python.
        You will maintain cloud deployments on AWS and monitor logs.
        """
        result = self.parser.parse(text)
        assert len(result.get("responsibilities", [])) >= 1
