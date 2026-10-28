"""Tests for advanced features:
1. Target Role vs Job Description mismatch detection
2. Target Role grounded interview questions
3. ATS-compliant PDF generation with zero '?' corruption
4. Course generator video resolution and Cucumber curriculum
"""
import pytest
from parsers.job_parser import JobDescriptionParser
from ai.dynamic_generator import detect_domain, DOMAIN_TECHNICAL_QUESTIONS
from services.interview_service import InterviewService
from services.resume_optimizer_service import export_resume_to_pdf, export_resume_to_docx
from services.course_service import CourseService
from services.course_content_catalog import get_curated_course
import pypdf


class TestRoleMismatchAndGrounding:
    def setup_method(self):
        self.parser = JobDescriptionParser()

    def test_role_mismatch_detected(self):
        """User enters 'machine learning' but JD is for Fresher Java Developer."""
        jd_text = """
        Fresher Java Developer at Jocata
        
        Requirements:
        Core Java, Spring Boot, Hibernate, MySQL, REST APIs, OOP Concepts.
        
        Responsibilities:
        - Design and develop robust backend microservices in Java.
        - Write efficient database queries.
        """
        result = self.parser.parse(jd_text, title="machine learning")
        alignment = result["role_alignment"]
        assert alignment["is_mismatch"] is True
        assert alignment["entered_role"] == "machine learning"
        assert "Java Developer" in alignment["detected_role"]
        assert "Target Role Mismatch" in alignment["message"]

    def test_role_match_succeeds(self):
        """User enters 'Java Software Engineer' for Java JD."""
        jd_text = """
        Fresher Java Developer at Jocata
        Requirements: Core Java, Spring Boot, Hibernate, SQL
        """
        result = self.parser.parse(jd_text, title="Java Software Engineer")
        alignment = result["role_alignment"]
        assert alignment["is_mismatch"] is False

    def test_interview_domain_anchored_in_target_role(self):
        """Interview domain must strictly follow target role over candidate resume skills."""
        # Candidate has ML skills on resume, but target role is Java Developer
        candidate_skills = ["Machine Learning", "Python", "Deep Learning", "TensorFlow"]
        target_role = "Fresher Java Developer"
        
        domain = detect_domain(target_role, candidate_skills)
        assert domain == "java"
        
        # Conversely, candidate with Java skills applying for ML role
        candidate_skills_java = ["Java", "Spring Boot", "Hibernate"]
        target_role_ml = "Machine Learning Engineer"
        domain_ml = detect_domain(target_role_ml, candidate_skills_java)
        assert domain_ml == "data_ai"
        
        # Testing / QA role
        target_role_qa = "QA Automation Engineer (Cucumber / Selenium)"
        domain_qa = detect_domain(target_role_qa, candidate_skills)
        assert domain_qa == "qa_testing"


class TestATSPDFStructure:
    def test_pdf_clean_layout_and_no_question_marks(self):
        """Exported PDF must have valid ATS structure and zero '?' replacement characters."""
        resume_payload = {
            "name": "B. MANOHAR REDDY",
            "contact": {
                "email": "manoharreddy9590@gmail.com",
                "phone": "9133887959",
                "location": "Hyderabad, India",
                "linkedin": "linkedin.com/in/b-manohar-reddy",
                "github": "github.com/manoharreddy-1"
            },
            "summary": "Enthusiastic software engineer specializing in scalable backend services.",
            "skills": {
                "Languages": ["Python", "Java", "SQL"],
                "Frameworks": ["Spring Boot", "FastAPI", "React"]
            },
            "experience": [
                {
                    "title": "Software Engineering Intern",
                    "company": "Cognizant",
                    "duration": "Jan 2024 - Present",
                    "bullets": [
                        "• Engineered an end-to-end ATS resume analyzer with high-precision semantic matching.",
                        "• Designed and deployed high-performance microservices reducing query latency by 35%."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "AI ATS Platform",
                    "tech_stack": ["Python", "Flask", "Docker"],
                    "bullets": [
                        "• Implemented semantic cosine similarity matching and automated skill gap analysis."
                    ]
                }
            ],
            "education": [
                {"degree": "B.Tech in CSE", "institution": "JNTUH", "year": "2024"}
            ]
        }
        
        pdf_stream = export_resume_to_pdf(resume_payload)
        assert pdf_stream is not None
        pdf_bytes = pdf_stream.getvalue()
        assert pdf_bytes.startswith(b"%PDF-1.4")
        
        # Verify with pypdf
        reader = pypdf.PdfReader(pdf_stream)
        assert len(reader.pages) >= 1
        page_text = reader.pages[0].extract_text()
        
        # Critical assertion: No '?' replacing bullet points!
        assert "?" not in page_text
        assert "B. MANOHAR REDDY" in page_text
        assert "PROFESSIONAL SUMMARY" in page_text
        assert "TECHNICAL SKILLS" in page_text
        assert "PROFESSIONAL EXPERIENCE" in page_text

    def test_docx_export_succeeds(self):
        """DOCX export must generate a valid docx stream."""
        resume_payload = {
            "name": "Alex Taylor",
            "contact": {"email": "alex@example.com"},
            "summary": "Experienced engineer.",
            "skills": {"Languages": ["Python", "Java"]},
            "experience": [{"title": "Dev", "bullets": ["Built systems."]}],
            "projects": [{"title": "App", "bullets": ["Engineered app."]}],
            "education": [{"degree": "B.Tech"}]
        }
        docx_stream = export_resume_to_docx(resume_payload)
        assert len(docx_stream.getvalue()) > 1000


class TestCourseGeneratorVideosAndCurriculum:
    def setup_method(self):
        self.course_service = CourseService()

    def test_cucumber_video_resolution(self):
        """Cucumber query must resolve to verified tutorial video, not dead ID."""
        video = self.course_service.fetch_youtube_video("cucumber")
        assert video is not None
        assert video["video_id"] == "4e9vhX7ZuCw"
        assert "Cucumber" in video["title"]
        assert video["video_id"] != "bJzb-Ey42H0"

    def test_testing_video_resolution(self):
        """Automation testing query must resolve to verified test course."""
        video = self.course_service.fetch_youtube_video("automation testing")
        assert video is not None
        assert video["video_id"] == "HmQv8Z4om4I"
        assert video["video_id"] != "bJzb-Ey42H0"

    def test_universal_fallback_video_is_active(self):
        """Any unknown skill must fall back to Harvard CS50 / CS course, not dead link."""
        video = self.course_service.fetch_youtube_video("uncommon_custom_skill_xyz")
        assert video is not None
        assert video["video_id"] in ["8mAITcNt710", "tpIctyqH29Q"]
        assert video["video_id"] != "bJzb-Ey42H0"

    def test_cucumber_curriculum_modules(self):
        """Cucumber course must generate 5 distinct structured modules."""
        course = get_curated_course("cucumber")
        assert course is not None
        assert len(course["chapters"]) == 5
        chapter_names = [c["name"] for c in course["chapters"]]
        assert any("BDD" in n for n in chapter_names)
        assert any("Gherkin" in n for n in chapter_names)
        assert any("Step Definitions" in n for n in chapter_names)
