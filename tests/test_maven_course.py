"""Tests for Maven Course Generation and Dynamic YouTube Video Search."""
import pytest
from services.course_content_catalog import get_curated_course, generate_smart_curriculum
from services.course_service import CourseService

def test_maven_curriculum_structure():
    course = get_curated_course("Maven")
    assert course["name"] == "Maven"
    assert course["category"] == "Build Tools & DevOps"
    assert len(course["chapters"]) == 5
    
    ch1 = course["chapters"][0]
    assert "POM.xml" in ch1["name"] or "Architecture" in ch1["name"]
    assert ch1["code_examples"][0]["language"] == "xml"
    assert "<project" in ch1["code_examples"][0]["code"]

def test_maven_youtube_video_mapping():
    cs = CourseService()
    video = cs.fetch_youtube_video("Maven")
    assert video is not None
    assert video["video_id"] == "N2EXGMJVwUU"
    assert "Maven" in video["title"]
    assert video["channel"] == "Coder Army"
    assert video["video_id"] != "8mAITcNt710"

def test_unrelated_video_fallback_never_pretends():
    cs = CourseService()
    # Harvard CS50 should have authentic title, never masquerading with a prefixed query
    fb = cs.fetch_youtube_video("CompletelyUnknownQueryThatDoesNotExistAnywhereXYZ123")
    if fb.get("video_id") == "8mAITcNt710":
        assert fb["title"] == "Computer Science & Software Engineering Fundamentals"
        assert "CompletelyUnknownQueryThatDoesNotExistAnywhereXYZ123" not in fb["title"]
