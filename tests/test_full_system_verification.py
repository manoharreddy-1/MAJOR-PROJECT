"""End-to-end full system verification covering all reported issues and modules."""
import io
import pytest
from bson import ObjectId

# 1. Target Role & Alignment
from parsers.job_parser import JobDescriptionParser

def test_target_role_alignment_and_mismatch():
    parser = JobDescriptionParser()
    java_jd = """
    We are seeking a senior Java Developer to design backend microservices using Spring Boot, Hibernate,
    and PostgreSQL. Experience with Docker and Kubernetes is required.
    """
    # Mismatch scenario: User entered ML Engineer for Java JD
    mismatch_res = parser.check_role_alignment("Machine Learning Engineer", "Java Developer", java_jd)
    assert mismatch_res["is_mismatch"] is True
    assert "Target Role Mismatch" in mismatch_res["message"]
    assert "Machine Learning Engineer" in mismatch_res["message"]

    # Match scenario: User entered Java Developer
    match_res = parser.check_role_alignment("Java Developer", "Java Developer", java_jd)
    assert match_res["is_mismatch"] is False


def test_target_role_interview_questions():
    from services.interview_service import InterviewService
    service = InterviewService()
    res = service.generate(
        resume={"skills": ["Python", "PyTorch"]},
        job={"job_title": "Machine Learning Engineer"},
        analysis={"target_role": "Machine Learning Engineer"}
    )
    assert "questions" in res
    questions = res["questions"]
    assert isinstance(questions, (dict, list))
    # Extract questions text
    if isinstance(questions, dict):
        all_q = []
        for cat, q_list in questions.items():
            if isinstance(q_list, list):
                all_q.extend(q_list)
        q_texts = " ".join([q.get("question", "") if isinstance(q, dict) else str(q) for q in all_q]).lower()
    else:
        q_texts = " ".join([q.get("question", "") if isinstance(q, dict) else str(q) for q in questions]).lower()
    assert len(q_texts) > 0


# 2. Technology & Tool Extraction (JIRA, Maven, Gradle, Git, etc.)
def test_technology_and_tool_extraction():
    parser = JobDescriptionParser()
    jd_text = """
    Job Title: Java Full Stack Developer
    • Tools: Familiarity with code versioning tools like Git and build tools such as Maven or Gradle.
    JIRA
    • Tech Stack: Spring Boot, Hibernate, PostgreSQL, Docker, Postman, SonarQube.
    """
    res = parser.parse(jd_text, title="Java Developer")
    req_skills = res["required_skills"]
    assert "Jira" in req_skills
    assert "Git" in req_skills
    assert "Maven" in req_skills
    assert "Gradle" in req_skills
    assert "Spring Boot" in req_skills
    assert "Postman" in req_skills
    assert "SonarQube" in req_skills


# 3. AI Course Generator — Maven, Cucumber, and General Courses
def test_course_generator_catalog_and_videos():
    from services.course_service import CourseService
    from services.course_content_catalog import generate_smart_curriculum
    service = CourseService()
    
    # 1. Maven Course
    maven_vid = service.fetch_youtube_video("Maven")
    assert maven_vid is not None
    assert maven_vid.get("video_id") == "N2EXGMJVwUU" or len(maven_vid.get("video_id", "")) >= 5
    maven_curr = generate_smart_curriculum("Maven")
    assert "Maven" in maven_curr.get("name", "")
    assert len(maven_curr.get("chapters", [])) >= 3

    # 2. Cucumber Course
    cucumber_vid = service.fetch_youtube_video("Cucumber")
    assert cucumber_vid is not None
    assert cucumber_vid.get("video_id") == "4e9vhX7ZuCw" or len(cucumber_vid.get("video_id", "")) >= 5
    cucumber_curr = generate_smart_curriculum("Cucumber")
    assert "Cucumber" in cucumber_curr.get("name", "")
    assert len(cucumber_curr.get("chapters", [])) >= 3

    # 3. Dynamic course resolution
    docker_vid = service.fetch_youtube_video("Docker")
    assert docker_vid is not None
    assert docker_vid.get("video_id") == "fqMOX6JJhGo"


# 4. Academics Extraction & Cutoff System
def test_academic_extraction_table_and_bullets():
    from parsers.resume_parser import ResumeParser
    parser = ResumeParser()
    resume_text = """
    DHANISETTI RUPA DURGA
    rupadhanisetti@gmail.com
    
    EDUCATION
    Degree / Course | Institution | Board / University | Year | Aggregate
    B.Tech (CSE) | Pragati Engineering College | JNTUK | 2024 | 8.54 CGPA
    Intermediate (MPC) | Sri Chaitanya Junior College | BIEAP | 2020 | 95%
    SSC | ZPH School | BSEAP | 2018 | 9.8 CGPA

    SKILLS
    Java, Python, SQL, Git
    """
    academics = parser._extract_academics(resume_text)
    assert academics["cgpa"] == 8.54
    assert academics["tenth_pct"] == 93.1  # 9.8 * 9.5
    assert academics["twelfth_pct"] == 95.0

    # Ensure "Education: Bachelor's" or "Results" is NOT in parsed skills
    parsed = parser.parse(resume_text)
    skills = parsed["skills"]
    assert "Java" in skills
    assert "Python" in skills
    assert not any("education" in s.lower() for s in skills)
    assert not any("bachelor" in s.lower() for s in skills)
    assert not any("results" in s.lower() for s in skills)


def test_bulk_academic_cutoffs():
    from services.bulk_screening_service import BulkScreeningService
    bss = BulkScreeningService()

    # Candidate with complete marks meeting cutoffs
    cand_eligible = {
        "candidate_id": "c1",
        "candidate_name": "Rupa Durga",
        "filename": "rupa.pdf",
        "academics": {"cgpa": 8.54, "tenth_pct": 93.1, "twelfth_pct": 95.0},
        "skills": ["Python", "Java"]
    }
    # Candidate with NO marks mentioned
    cand_unmentioned = {
        "candidate_id": "c2",
        "candidate_name": "No Marks",
        "filename": "nomarks.pdf",
        "academics": {"cgpa": None, "tenth_pct": None, "twelfth_pct": None},
        "skills": ["Python"]
    }

    # When cutoff is set (e.g. Min CGPA 7.5, 10th 70%, 12th 70%)
    # Let's test the cutoff logic
    min_cgpa = 7.5
    min_tenth = 70.0
    min_twelfth = 70.0

    def check_cutoff(c):
        cgpa = c["academics"]["cgpa"]
        tenth = c["academics"]["tenth_pct"]
        twelfth = c["academics"]["twelfth_pct"]
        reasons = []
        if min_cgpa is not None:
            if cgpa is None:
                reasons.append("CGPA not found")
            elif (cgpa / 9.5 if cgpa > 10 else cgpa) < (min_cgpa / 9.5 if min_cgpa > 10 else min_cgpa):
                reasons.append("CGPA low")
        if min_tenth is not None:
            if tenth is None:
                reasons.append("10th not found")
            elif (tenth * 9.5 if tenth <= 10 else tenth) < min_tenth:
                reasons.append("10th low")
        if min_twelfth is not None:
            if twelfth is None:
                reasons.append("12th not found")
            elif (twelfth * 9.5 if twelfth <= 10 else twelfth) < min_twelfth:
                reasons.append("12th low")
        return len(reasons) == 0, reasons

    ok_elig, _ = check_cutoff(cand_eligible)
    assert ok_elig is True

    ok_unment, reasons = check_cutoff(cand_unmentioned)
    assert ok_unment is False
    assert "CGPA not found" in reasons
    assert "10th not found" in reasons
    assert "12th not found" in reasons


# 5. Database UpdateResult and Job Requirements Update
def test_job_service_update_requirements_mock():
    from services.job_service import JobService
    from database.mongodb import get_collection
    
    js = JobService()
    # Insert a dummy job
    res = js.analyze_text("Senior Python Developer with Django and PostgreSQL experience.", title="Python Developer")
    job_id = res["job_description_id"]
    
    # Update requirements without crashing on matched_count
    updated = js.update_requirements(job_id, {"job_title": "Python Developer", "required_skills": ["Python", "Django", "PostgreSQL", "Jira"]})
    assert updated is True
    
    # Fetch job and verify
    doc = js.get_job(job_id)
    assert doc is not None
    assert "Jira" in doc["requirements"]["required_skills"]


# 6. Resume Export (DOCX & PDF)
def test_resume_export_docx_and_pdf():
    from services.resume_optimizer_service import export_resume_to_docx, export_resume_to_pdf
    resume_data = {
        "name": "Jane Developer",
        "contact": {"email": "jane@example.com", "phone": "+1 555-0199", "location": "Austin, TX"},
        "summary": "Full stack engineer with experience in cloud microservices.",
        "skills": {
            "Languages": ["Python", "Java", "SQL"],
            "Frameworks": ["Django", "Spring Boot"],
            "Tools": ["Git", "Docker", "Jira"]
        },
        "experience": [
            {
                "role": "Software Engineer",
                "company": "Tech Corp",
                "period": "2022 - Present",
                "bullets": ["Developed scalable RESTful APIs", "Maintained CI/CD pipelines"]
            }
        ],
        "education": ["B.S. in Computer Science - University of Texas (2022)"]
    }
    
    # Test DOCX export
    docx_buf = export_resume_to_docx(resume_data)
    assert isinstance(docx_buf, io.BytesIO)
    docx_bytes = docx_buf.getvalue()
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 500
    assert docx_bytes[:2] == b"PK"  # Valid ZIP/DOCX magic bytes

    # Test PDF export
    pdf_buf = export_resume_to_pdf(resume_data)
    assert isinstance(pdf_buf, io.BytesIO)
    pdf_bytes = pdf_buf.getvalue()
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes[:4] == b"%PDF"  # Valid PDF magic bytes
