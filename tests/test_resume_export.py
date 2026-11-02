"""Test resume export for DOCX and PDF with both python-docx and pure-Python fallbacks."""
import pytest
from services.resume_optimizer_service import export_resume_to_docx, export_resume_to_pdf
import services.resume_optimizer_service as ros

def test_export_docx_normal():
    data = {
        "name": "Manohar Reddy",
        "contact": {"email": "manohar@example.com", "phone": "1234567890"},
        "summary": "Full Stack Engineer",
        "skills": {"Languages": ["Python", "Java"]},
        "experience": [{"title": "Software Engineer", "company": "Tech Corp", "duration": "2022 - Present", "bullets": ["Built APIs"]}],
        "education": [{"degree": "B.Tech", "institution": "University", "year": "2022"}]
    }
    stream = export_resume_to_docx(data)
    assert stream is not None
    assert len(stream.getvalue()) > 500

def test_export_docx_fallback_when_docx_missing():
    old_doc = ros.Document
    old_avail = ros._DOCX_AVAILABLE
    try:
        ros.Document = None
        ros._DOCX_AVAILABLE = False
        data = {
            "name": "Fallback Candidate",
            "contact": {"email": "fallback@example.com"},
            "summary": "Resilient developer",
            "skills": ["Python", "Flask", "Docker"]
        }
        stream = export_resume_to_docx(data)
        assert stream is not None
        # Must be valid zip archive
        import zipfile
        with zipfile.ZipFile(stream) as z:
            assert "word/document.xml" in z.namelist()
            assert "[Content_Types].xml" in z.namelist()
    finally:
        ros.Document = old_doc
        ros._DOCX_AVAILABLE = old_avail

def test_export_pdf():
    data = {
        "name": "Manohar Reddy",
        "contact": {"email": "manohar@example.com"},
        "summary": "Full Stack Engineer",
        "skills": {"Languages": ["Python", "Java"]}
    }
    stream = export_resume_to_pdf(data)
    assert stream is not None
    val = stream.getvalue()
    assert val.startswith(b"%PDF")
    assert b"%%EOF" in val
