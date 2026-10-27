"""Unit tests for AI Resume Optimization, anti-hallucination guardrails, and score recalculation."""
import io
import pytest
from ai.llm_model import LLMModel
from services.ats_service import ATSService
from services.resume_optimizer_service import (
    ResumeOptimizerService,
    export_resume_to_docx,
    export_resume_to_pdf,
)


@pytest.fixture
def optimizer():
    # Use offline LLM instance for fast deterministic unit tests
    return ResumeOptimizerService(llm_model=LLMModel(api_key=""))


@pytest.fixture
def ats_service():
    return ATSService()


def test_resume_missing_5_skills(optimizer, ats_service):
    """Test resume missing 5 key skills: NumPy, Pandas, scikit-learn, Docker, AWS."""
    resume = {
        "name": "Jordan Miller",
        "email": "jordan@example.com",
        "skills": ["Python", "SQL", "Git"],
        "projects": [
            {
                "title": "Machine Learning Prediction Service",
                "bullets": ["Developed Python-based model to analyze customer data and forecast churn."]
            }
        ],
        "experience": [
            {
                "title": "Junior Python Developer",
                "company": "DataTech Solutions",
                "bullets": ["Wrote SQL queries and Python scripts for data extraction."]
            }
        ],
        "education": ["B.S. in Computer Science, Tech University, 2023"],
        "raw_text": "Jordan Miller. Python Developer with SQL experience building predictive models.",
    }

    job = {
        "job_title": "Data Scientist",
        "required_skills": ["Python", "SQL", "NumPy", "Pandas", "scikit-learn", "Docker", "AWS"],
        "preferred_skills": ["Git"],
        "responsibilities": ["Build and deploy ML models using Python, scikit-learn, and cloud."],
        "raw_text": "Looking for Data Scientist proficient in Python, SQL, NumPy, Pandas, scikit-learn, Docker, and AWS.",
    }

    # Calculate real original ATS score
    orig_ats = ats_service.analyze(resume, job)
    orig_score = orig_ats["scores"]["overall"]

    # Run optimizer
    result = optimizer.optimize(
        resume_data=resume,
        job_data=job,
        current_score=orig_score,
    )

    # Assertions
    assert "optimized_resume" in result or "structured_optimized" in result
    structured = result.get("structured_optimized") or result.get("optimized_resume")
    assert structured is not None
    assert "summary" in structured
    assert "skills" in structured

    # Verify added skills
    added_names = [a["skill"].lower() for a in result.get("added_skills", [])]
    assert any("numpy" in s for s in added_names)
    assert any("pandas" in s for s in added_names)
    assert any("scikit-learn" in s for s in added_names)

    # Verify unevidenced skill (AWS or Docker with no prior cloud context) goes to needs_user_confirmation
    confirmation_names = [c["skill"].lower() for c in result.get("needs_user_confirmation", [])]
    assert any("aws" in c for c in confirmation_names)

    # Verify score recalculation
    assert result["old_score"] == orig_score
    assert result["new_score"] >= orig_score
    assert result["score_delta"] >= 0.0


def test_resume_missing_0_skills(optimizer, ats_service):
    """Test resume that already possesses all required skills (0 missing)."""
    resume = {
        "name": "Sarah Connor",
        "email": "sarah@example.com",
        "skills": ["Java", "Spring Boot", "Microservices", "REST APIs", "Docker", "PostgreSQL"],
        "summary": "Senior Java Backend Engineer with 5 years experience.",
        "projects": [{"title": "Payment Gateway", "bullets": ["Built Spring Boot microservices with Docker and PostgreSQL."]}],
        "experience": [{"title": "Senior Engineer", "company": "FinTech Corp", "bullets": ["Engineered REST APIs using Java and Spring Boot."]}],
        "education": ["B.Tech in Computer Science"],
        "raw_text": "Sarah Connor. Senior Java Developer with Spring Boot, Microservices, Docker, PostgreSQL.",
    }

    job = {
        "job_title": "Java Backend Engineer",
        "required_skills": ["Java", "Spring Boot", "Microservices", "REST APIs", "Docker", "PostgreSQL"],
        "preferred_skills": [],
        "responsibilities": ["Develop enterprise Java microservices."],
        "raw_text": "Java Backend Engineer required with Spring Boot and Microservices.",
    }

    orig_ats = ats_service.analyze(resume, job)
    orig_score = orig_ats["scores"]["overall"]

    # Missing skills empty
    result = optimizer.optimize(
        resume_data=resume,
        job_data=job,
        missing_skills=[],
        matched_skills=["Java", "Spring Boot", "Microservices", "REST APIs", "Docker", "PostgreSQL"],
        current_score=orig_score,
    )

    assert result["old_score"] == orig_score
    assert abs(result["new_score"] - orig_score) <= 5.0
    assert result["new_score"] >= 65.0
    assert isinstance(result["changes_summary"], str)


def test_empty_or_invalid_resume(optimizer):
    """Test handling of empty or invalid resume input."""
    # 1. Empty dict
    with pytest.raises(ValueError, match="Resume data is missing or empty"):
        optimizer.optimize(resume_data={}, job_data={"job_title": "Developer"})

    # 2. None
    with pytest.raises(ValueError, match="Resume data is missing or empty"):
        optimizer.optimize(resume_data=None, job_data={"job_title": "Developer"})

    # 3. Blank text and no skills
    with pytest.raises(ValueError, match="Resume does not contain readable text or technical skills"):
        optimizer.optimize(
            resume_data={"name": "Ghost", "raw_text": "   ", "skills": []},
            job_data={"job_title": "Developer"}
        )


def test_export_docx_and_pdf(optimizer):
    """Test generation of valid ATS DOCX and PDF files."""
    structured_resume = {
        "name": "Jane Smith",
        "contact": {
            "email": "jane@example.com",
            "phone": "+1-555-0199",
            "location": "Seattle, WA",
            "linkedin": "linkedin.com/in/janesmith",
            "github": "github.com/janesmith"
        },
        "summary": "Accomplished Software Engineer experienced in Python, Docker, and Cloud architectures.",
        "skills": {
            "Programming Languages": ["Python", "SQL", "Go"],
            "Frameworks": ["FastAPI", "React"],
            "Tools": ["Docker", "Git", "Kubernetes"]
        },
        "experience": [
            {
                "title": "Software Engineer",
                "company": "CloudScale Inc",
                "duration": "2022 - Present",
                "bullets": [
                    "Engineered FastAPI microservices handling 10M+ daily requests.",
                    "Containerized deployments using Docker and Kubernetes."
                ]
            }
        ],
        "projects": [
            {
                "title": "Distributed Task Queue",
                "tech_stack": ["Python", "Redis", "Docker"],
                "bullets": ["Architected asynchronous task queue processing 50k jobs/sec."]
            }
        ],
        "education": [
            {
                "degree": "B.S. in Software Engineering",
                "institution": "University of Washington",
                "year": "2022"
            }
        ]
    }

    # Test DOCX export
    docx_stream = export_resume_to_docx(structured_resume)
    assert isinstance(docx_stream, io.BytesIO)
    docx_bytes = docx_stream.getvalue()
    assert len(docx_bytes) > 1000  # Non-trivial valid docx file

    # Test PDF export
    pdf_stream = export_resume_to_pdf(structured_resume)
    assert isinstance(pdf_stream, io.BytesIO)
    pdf_bytes = pdf_stream.getvalue()
    assert len(pdf_bytes) > 500  # Non-trivial valid pdf file
    assert pdf_bytes.startswith(b"%PDF")
