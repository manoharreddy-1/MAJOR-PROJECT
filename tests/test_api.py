"""Tests for API health endpoint."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealth:
    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "sbert_model" in data["data"]

    def test_index_page(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_analyze_page(self, client):
        response = client.get("/analyze")
        assert response.status_code == 200



class TestAuthSecurity:
    def test_unregistered_login_fails(self, client):
        """Strict Rule: Only registered credentials can log in."""
        res = client.post("/api/auth/login", json={
            "username": "non_existent_random_user_999",
            "password": "wrongpassword123"
        })
        assert res.status_code == 401
        data = res.get_json()
        assert data["success"] is False
        assert "Invalid username or password" in data["error"]["message"]

    def test_registered_user_login_succeeds(self, client):
        """Register account and verify successful login."""
        # 1. Register
        reg_res = client.post("/api/auth/register", json={
            "username": "candidate_test",
            "password": "mypassword123",
            "full_name": "Test Candidate",
            "email": "test@candidate.com"
        })
        assert reg_res.status_code in [201, 200, 400]  # If already registered or new

        # 2. Login
        login_res = client.post("/api/auth/login", json={
            "username": "candidate_test",
            "password": "mypassword123"
        })
        assert login_res.status_code == 200
        data = login_res.get_json()
        assert data["success"] is True
        assert data["data"]["user"]["username"] == "candidate_test"

    def test_preseeded_student_login_succeeds(self, client):
        """Verify pre-seeded student account can log in immediately."""
        res = client.post("/api/auth/login", json={
            "username": "student",
            "password": "student123"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["user"]["username"] == "student"


class TestResumeOptimizerAPI:
    def test_optimize_resume_api_success(self, client):
        """Test POST /api/optimize-resume endpoint with valid payload."""
        payload = {
            "resume_data": {
                "name": "Morgan Lee",
                "email": "morgan@example.com",
                "skills": ["Python", "SQL"],
                "projects": [{"title": "Web Application", "bullets": ["Built Python data processing backend."]}],
                "experience": ["Software Engineer at Alpha Corp"],
                "education": ["B.S. in Computer Science"],
                "raw_text": "Morgan Lee. Python developer with SQL experience."
            },
            "job_data": {
                "job_title": "Data Engineer",
                "required_skills": ["Python", "SQL", "Pandas", "NumPy", "Apache Spark"],
                "preferred_skills": ["Docker"],
                "responsibilities": ["Develop scalable data pipelines."]
            },
            "missing_skills": ["Pandas", "NumPy", "Apache Spark"],
            "matched_skills": ["Python", "SQL"],
            "current_score": 45.0
        }
        res = client.post("/api/optimize-resume", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        res_data = data["data"]
        assert "structured_optimized" in res_data
        assert "new_score" in res_data
        assert "added_skills" in res_data

    def test_optimize_resume_empty_fails(self, client):
        """Test POST /api/optimize-resume with empty resume."""
        res = client.post("/api/optimize-resume", json={
            "resume_data": {"raw_text": "   ", "skills": []}
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False

    def test_export_docx_endpoint(self, client):
        """Test POST /api/optimize-resume/export/docx."""
        payload = {
            "structured_optimized": {
                "name": "Alex Taylor",
                "contact": {"email": "alex@example.com"},
                "summary": "Experienced engineer.",
                "skills": {"Languages": ["Python", "Java"]},
                "experience": [{"title": "Dev", "bullets": ["Built systems."]}],
                "projects": [{"title": "App", "bullets": ["Engineered app."]}],
                "education": [{"degree": "B.Tech"}]
            }
        }
        res = client.post("/api/optimize-resume/export/docx", json=payload)
        assert res.status_code == 200
        assert res.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert len(res.data) > 1000

    def test_export_pdf_endpoint(self, client):
        """Test POST /api/optimize-resume/export/pdf."""
        payload = {
            "structured_optimized": {
                "name": "Alex Taylor",
                "contact": {"email": "alex@example.com"},
                "summary": "Experienced engineer.",
                "skills": {"Languages": ["Python", "Java"]},
                "experience": [{"title": "Dev", "bullets": ["Built systems."]}],
                "projects": [{"title": "App", "bullets": ["Engineered app."]}],
                "education": [{"degree": "B.Tech"}]
            }
        }
        res = client.post("/api/optimize-resume/export/pdf", json=payload)
        assert res.status_code == 200
        assert res.content_type == "application/pdf"
        assert res.data.startswith(b"%PDF")
