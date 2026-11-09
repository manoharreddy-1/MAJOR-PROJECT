"""Unit and integration tests for Job Title vs Job Description alignment validation."""
import pytest
from app import create_app
from services.job_validator_service import JobValidatorService
from services.job_service import JobService


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestJobTitleAndJDValidation:
    def setup_method(self):
        self.validator = JobValidatorService()
        self.job_service = JobService()

    def test_ortho_doctor_with_python_developer_jd_rejected(self, client):
        """Guide test case 1: 'jr otho doctor' title with Python developer JD must be rejected."""
        title = "jr otho doctor"
        python_jd = """
        Job Title: Python Developer
        About the Role:
        We are looking for a skilled Python Developer to build backend web services.
        Responsibilities:
        - Design and implement REST APIs using Django and FastAPI.
        - Work with PostgreSQL databases, write queries, and optimize performance.
        - Deploy services with Docker and manage version control via Git.
        Requirements:
        Python, Django, FastAPI, PostgreSQL, REST APIs, Git, Docker.
        """
        # Direct validator test
        is_valid, msg, details = self.validator.validate_title_and_description(title, python_jd)
        assert is_valid is False
        assert "Invalid job title and job description" in msg
        assert "jr otho doctor" in msg

        # API endpoint test
        res = client.post("/api/job/analyze", json={
            "title": title,
            "text": python_jd
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "Invalid job title and job description" in data["error"]["message"]

    def test_resume_or_name_pasted_as_job_description_rejected(self, client):
        """Guide test case 2: 'ai intern' title with resume text / name in resume must be rejected."""
        title = "ai intern"
        resume_text = """
        Dhanisetti Rupa Durga
        Email: rupadhanisetti@gmail.com | Phone: +91 9876543210 | Andhra Pradesh, India
        LinkedIn: linkedin.com/in/rupadurga | GitHub: github.com/rupadurga
        
        CAREER OBJECTIVE:
        Seeking a challenging position in an organization where I can utilize my skills in software engineering.
        
        EDUCATION:
        B.Tech in Artificial Intelligence & Data Science (CGPA: 8.54 / 10)
        Intermediate: MPC (91.2%)
        SSC: 10th Standard (9.8 CGPA)
        
        PROJECTS:
        - Deep Learning Model for Image Classification using PyTorch
        - Sentiment Analysis on Twitter Data using Python
        
        DECLARATION:
        I hereby declare that the above-mentioned details are true to the best of my knowledge.
        """
        # Direct validator test
        is_valid, msg, details = self.validator.validate_title_and_description(title, resume_text)
        assert is_valid is False
        assert "Invalid job description" in msg

        # API endpoint test
        res = client.post("/api/job/analyze", json={
            "title": title,
            "text": resume_text
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "Invalid job description" in data["error"]["message"]

    def test_single_name_or_trivial_text_rejected(self, client):
        """Trivial text like 'name in the resume' or single name must be rejected."""
        title = "ai intern"
        res = client.post("/api/job/analyze", json={
            "title": title,
            "text": "Dhanisetti Rupa Durga"
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False

    def test_missing_job_title_rejected(self, client):
        """Empty or missing job title must be rejected with helpful prompt."""
        res = client.post("/api/job/analyze", json={
            "title": "",
            "text": "We are looking for a Python Developer with 3+ years experience in Django and PostgreSQL."
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "Target Role / Job Title is required" in data["error"]["message"]

    def test_valid_ai_intern_job_description_accepted(self, client):
        """Matching role and job description must be accepted and parsed."""
        title = "AI Intern"
        ai_jd = """
        Job Title: AI / Machine Learning Intern
        About the Role:
        We are looking for a passionate AI Intern to join our Artificial Intelligence research team.
        Responsibilities:
        - Train and fine-tune deep learning models using PyTorch and TensorFlow.
        - Perform exploratory data analysis and feature engineering on large datasets.
        - Collaborate with senior data scientists on NLP and computer vision pipelines.
        Requirements:
        - Python, PyTorch, TensorFlow, Machine Learning, Deep Learning.
        - Pursuing or completed B.Tech / M.Tech in Computer Science or related field.
        """
        res = client.post("/api/job/analyze", json={
            "title": title,
            "text": ai_jd
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["job_description_id"]
        reqs = data["data"]["requirements"]
        assert "Python" in reqs["required_skills"] or "Machine Learning" in reqs["required_skills"]

    def test_valid_python_developer_job_description_accepted(self, client):
        """Valid Python Developer role and JD must be accepted and parsed."""
        title = "Python Developer"
        python_jd = """
        Job Title: Python Developer
        About the Company:
        We are a leading fintech company looking for a Python Developer.
        Key Responsibilities:
        - Develop scalable backend microservices using Python, FastAPI, and Flask.
        - Design relational database schemas in PostgreSQL and MySQL.
        - Write robust unit tests and maintain CI/CD deployment pipelines.
        Required Qualifications:
        - Python, FastAPI, Flask, PostgreSQL, Docker, Git.
        - Experience with REST APIs and asynchronous programming.
        """
        res = client.post("/api/job/analyze", json={
            "title": title,
            "text": python_jd
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["job_description_id"]

    def test_bulk_screening_rejects_ortho_doctor_with_python_jd(self, client):
        """Bulk screening endpoint must reject mismatched job title and description."""
        res = client.post("/api/bulk/analyze", json={
            "job_title": "jr otho doctor",
            "job_description": "We are seeking a Python Developer with Django and PostgreSQL experience.",
            "resumes": [
                {"name": "Alice", "text": "Alice Software Engineer with Python and SQL experience."}
            ]
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "Invalid job title and job description" in data["error"]["message"]
