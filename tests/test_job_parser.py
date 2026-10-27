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
