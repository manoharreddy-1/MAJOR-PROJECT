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

    def test_improve_resume_no_target_role_name_error(self, client):
        """Verify POST /api/resume/improve does not crash with target_role undefined NameError."""
        from database.mongodb import get_collection, COLLECTIONS
        from bson import ObjectId

        resumes_col = get_collection(COLLECTIONS["resumes"])
        jobs_col = get_collection(COLLECTIONS["job_descriptions"])
        analyses_col = get_collection(COLLECTIONS["analyses"])

        resume_id = str(resumes_col.insert_one({
            "raw_text": "Jane Doe. Python Developer.",
            "extracted": {
                "name": "Jane Doe",
                "skills": ["Python", "Django", "SQL"],
                "experience": [{"title": "Software Developer"}],
                "education": [{"degree": "B.Tech"}]
            }
        }).inserted_id)

        valid_jd = (
            "Job Title: Python Developer\n"
            "We are seeking an experienced Python Developer to build high-performance microservices and REST APIs. "
            "Responsibilities include designing clean data models in PostgreSQL, integrating caching with Redis, "
            "optimizing database queries, and writing robust automated unit tests. "
            "Requirements include a Bachelor's degree in Computer Science, 3+ years of professional backend software development experience, "
            "and deep familiarity with Python, Django, FastAPI, Docker, and Git version control."
        )

        job_id = str(jobs_col.insert_one({
            "raw_text": valid_jd,
            "requirements": {
                "job_title": "Python Developer",
                "required_skills": ["Python", "Django", "PostgreSQL"],
                "responsibilities": ["Develop REST APIs."]
            }
        }).inserted_id)

        analysis_id = str(analyses_col.insert_one({
            "resume_id": ObjectId(resume_id),
            "job_description_id": ObjectId(job_id),
            "target_role": "Python Developer",
            "scores": {"overall": 75.0},
            "skill_analysis": {
                "matched": ["Python", "Django"],
                "missing": ["PostgreSQL"]
            }
        }).inserted_id)

        res_imp = client.post("/api/resume/improve", json={"analysis_id": analysis_id})
        assert res_imp.status_code == 200
        data_imp = res_imp.get_json()
        assert data_imp["success"] is True
        assert "target_role" in data_imp["data"]
        assert data_imp["data"]["target_role"] == "Python Developer"

    def test_course_view_fast_loading_and_retrieval(self, client):
        """Verify course generation and details retrieval is fast and non-blocking."""
        res_gen = client.post("/api/course/generate-layout", json={"topic": "Spring Framework", "category": "Software & Coding"})
        assert res_gen.status_code in [200, 201]
        course_id = res_gen.get_json()["data"]["course_id"]

        # Fast GET
        res_get = client.get(f"/api/course/{course_id}")
        assert res_get.status_code == 200
        course_data = res_get.get_json()["data"]
        assert course_data["course_id"] == course_id
        assert len(course_data["chapters"]) > 0
