"""Tests for Resume Analysis Mode Navigation & Role-Aware Bulk Screening."""
import io
import pytest
from app import create_app
from services.bulk_screening_service import BulkScreeningService


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestModeNavigation:
    def test_mode_selector_renders_both_options(self, client):
        """Mode selector page /resume-analysis must render Single Resume and Bulk Resumes."""
        res = client.get("/resume-analysis")
        assert res.status_code == 200
        html = res.data.decode("utf-8")
        assert "Single Resume" in html
        assert "Bulk Resumes" in html
        assert "Analyze one resume against a job description" in html
        assert "Upload up to 1000+ resumes" in html
        assert "/resume-analysis/single" in html
        assert "/resume-analysis/bulk" in html

    def test_single_resume_route_regression(self, client):
        """Both /resume-analysis/single and legacy /analyze must work seamlessly."""
        # New linkable single route
        res1 = client.get("/resume-analysis/single")
        assert res1.status_code == 200
        html1 = res1.data.decode("utf-8")
        assert "Upload Resume" in html1
        assert "Resume Analysis" in html1
        assert "Switch mode" in html1

        # Legacy route alias
        res2 = client.get("/analyze")
        assert res2.status_code == 200
        html2 = res2.data.decode("utf-8")
        assert "Upload Resume" in html2
        assert "Switch mode" in html2

    def test_student_cannot_access_bulk_routes(self, client):
        """Strict Rule: Student role must be rejected with 403 Forbidden by backend."""
        # 1. Page route rejection
        res_page = client.get("/resume-analysis/bulk", headers={"X-User-Role": "Student"})
        assert res_page.status_code == 403
        data_page = res_page.get_json() or {}
        assert "Access denied" in data_page.get("error", {}).get("message", "")

        # 2. Query param rejection
        res_query = client.get("/resume-analysis/bulk?role=Student")
        assert res_query.status_code == 403

        # 3. Token-based rejection
        res_token = client.get("/resume-analysis/bulk", headers={"Authorization": "Bearer token_usr_student"})
        assert res_token.status_code == 403

        # 4. API endpoint rejection
        res_api = client.post("/api/bulk/analyze", json={
            "job_description": "Python, Machine Learning Engineer",
            "resumes": [{"name": "Test", "content": "Python skills"}]
        }, headers={"X-User-Role": "Student"})
        assert res_api.status_code == 403
        data_api = res_api.get_json()
        assert data_api["success"] is False
        assert "Access denied" in data_api["error"]["message"]

        # 5. History and export rejection
        res_hist = client.get("/api/bulk/batches", headers={"X-User-Role": "Student"})
        assert res_hist.status_code == 403

        res_exp = client.get("/api/bulk/export/fake_batch_123", headers={"X-User-Role": "Student"})
        assert res_exp.status_code == 403

    def test_recruiter_and_placement_cell_can_access_bulk_routes(self, client):
        """Recruiter and Placement Cell roles must have full access (200 OK)."""
        # Recruiter role
        res_rec = client.get("/resume-analysis/bulk", headers={"X-User-Role": "Recruiter"})
        assert res_rec.status_code == 200
        assert "Bulk Resume Screening" in res_rec.data.decode("utf-8")

        # Placement Cell role
        res_plc = client.get("/resume-analysis/bulk", headers={"X-User-Role": "Placement Cell"})
        assert res_plc.status_code == 200

        # Placement token
        res_tok = client.get("/resume-analysis/bulk", headers={"Authorization": "Bearer token_usr_placement"})
        assert res_tok.status_code == 200

        # Batches list API
        res_api = client.get("/api/bulk/batches", headers={"X-User-Role": "Recruiter"})
        assert res_api.status_code == 200
        assert res_api.get_json()["success"] is True


class TestBulkScreeningProcessingAndRanking:
    def test_bulk_processing_cutoff_filtering_and_ranking(self):
        """Verify academic cutoffs, ATS score ranking from top performer to least, and CSV export."""
        service = BulkScreeningService()

        job_desc = """
        AI / Machine Learning Engineer
        Required Skills: Python, PyTorch, NumPy, Pandas, Scikit-learn, LLMs, NLP.
        """

        resume_1 = """
        Arun Kumar
        arun@example.com
        9876543210
        Education:
        B.Tech Computer Science - CGPA: 9.1/10
        12th Standard: 88.5%
        10th SSC: 91.0%
        Skills: Python, PyTorch, NumPy, Pandas, Scikit-learn, LLMs, NLP, Docker
        Projects: Built end-to-end LLM chatbot using PyTorch and Hugging Face.
        """

        resume_2 = """
        Bhavna Sharma
        bhavna@example.com
        9876543211
        Education:
        B.Tech Information Technology - CGPA: 6.2/10
        12th Standard: 68.0%
        10th SSC: 72.0%
        Skills: Python, PyTorch, NumPy, Pandas, Scikit-learn, LLMs
        Projects: Machine Learning pipeline in Python.
        """

        resume_3 = """
        Chetan Verma
        chetan@example.com
        9876543212
        Education:
        B.E. Electronics - CGPA: 7.8/10
        12th Standard: 78.0%
        10th SSC: 80.0%
        Skills: Python, Java, SQL, Git
        Projects: Web application backend.
        """

        files = [
            ("resume_arun.txt", resume_1.encode("utf-8")),
            ("resume_bhavna.txt", resume_2.encode("utf-8")),
            ("resume_chetan.txt", resume_3.encode("utf-8")),
        ]

        cutoffs = {
            "min_cgpa": 7.0,
            "min_tenth": 70.0,
            "min_twelfth": 70.0,
        }

        batch = service.process_batch(
            job_description=job_desc,
            files=files,
            job_title="AI Engineer",
            cutoffs=cutoffs,
            user_id="usr_recruiter"
        )

        assert batch["total_resumes"] == 3
        # Arun (CGPA 9.1) & Chetan (CGPA 7.8) are eligible; Bhavna (CGPA 6.2 < 7.0) is below cutoff
        assert batch["eligible_count"] == 2
        assert batch["below_cutoff_count"] == 1

        candidates = batch["candidates"]
        assert len(candidates) == 3

        # Rank 1 must be Arun Kumar (eligible and high ATS score)
        assert candidates[0]["rank"] == 1
        assert "Arun" in candidates[0]["candidate_name"]
        assert candidates[0]["is_eligible"] is True
        assert candidates[0]["cutoff_status"] == "Eligible"

        # Bhavna is below cutoff due to CGPA 6.2 < 7.0
        bhavna = next(c for c in candidates if "Bhavna" in c["candidate_name"])
        assert bhavna["is_eligible"] is False
        assert "CGPA" in bhavna["cutoff_status"]

        # Chetan is eligible
        chetan = next(c for c in candidates if "Chetan" in c["candidate_name"])
        assert chetan["is_eligible"] is True

        # CSV Export generation
        csv_out = service.generate_csv_export(batch)
        assert "Rank,Candidate Name,Eligibility Status,ATS Score (%)" in csv_out
        assert "Arun Kumar" in csv_out
        assert "Bhavna Sharma" in csv_out
        assert "Chetan Verma" in csv_out
