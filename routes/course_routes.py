"""API endpoints for AI Course Generator."""
import logging
from flask import Blueprint, request

from routes.responses import error_response, success_response
from services.course_service import CourseService

logger = logging.getLogger(__name__)
course_bp = Blueprint("course", __name__)
course_service = CourseService()


@course_bp.route("/generate-layout", methods=["POST"])
def generate_course_layout():
    """Create a new course and generate its chapter outline layout."""
    data = request.get_json() or {}
    topic = data.get("topic") or data.get("name")
    if not topic or not topic.strip():
        return error_response("INVALID_TOPIC", "Course topic is required.")

    category = data.get("category", "Technology & Science")
    level = data.get("level", "Beginner")
    duration = data.get("duration", "1 Hour")
    num_chapters = int(data.get("num_chapters", 5))
    include_video = data.get("include_video", "Yes")
    description = data.get("description", "")
    user_name = data.get("user_name", "Student")
    user_id = data.get("user_id")

    try:
        result = course_service.generate_course_layout(
            topic=topic.strip(),
            category=category,
            level=level,
            duration=duration,
            num_chapters=num_chapters,
            include_video=include_video,
            description=description,
            user_name=user_name,
            user_id=user_id
        )
        return success_response(result, "Course layout generated successfully.", 201)
    except Exception as e:
        logger.exception("Error generating course layout: %s", e)
        return error_response("GENERATION_FAILED", str(e), 500)


@course_bp.route("/generate-content", methods=["POST"])
def generate_course_content():
    """Generate chapter explanations, code examples, and videos for the course."""
    data = request.get_json() or {}
    course_id = data.get("course_id")
    if not course_id:
        return error_response("MISSING_ID", "course_id is required.")

    try:
        result = course_service.generate_full_course_content(course_id)
        return success_response(result, "Course content generated and published successfully.")
    except ValueError as ve:
        return error_response("NOT_FOUND", str(ve), 404)
    except Exception as e:
        logger.exception("Error generating course content: %s", e)
        return error_response("CONTENT_GENERATION_FAILED", str(e), 500)


@course_bp.route("/<course_id>", methods=["GET"])
def get_course(course_id: str):
    """Retrieve full details and chapters of a generated course."""
    try:
        course = course_service.get_course_details(course_id)
        if not course:
            return error_response("NOT_FOUND", "Course not found.", 404)
        return success_response(course)
    except Exception as e:
        logger.exception("Error retrieving course %s: %s", course_id, e)
        return error_response("SERVER_ERROR", str(e), 500)


@course_bp.route("/list", methods=["GET"])
def list_courses():
    """Retrieve all generated courses for Explore & Dashboard."""
    try:
        courses = course_service.list_courses()
        return success_response(courses)
    except Exception as e:
        logger.exception("Error listing courses: %s", e)
        return error_response("SERVER_ERROR", str(e), 500)


@course_bp.route("/run-code", methods=["POST"])
def execute_code_challenge():
    """Execute code in real-time and validate against test cases."""
    from services.code_runner_service import run_code
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    test_cases = data.get("test_cases", [])

    if not code.strip():
        return error_response("EMPTY_CODE", "Code snippet cannot be empty.")

    # 1. Run user code directly
    raw_result = run_code(language, code)

    # 2. If test cases provided, evaluate output
    test_results = []
    all_passed = raw_result.get("success", False)
    output_str = raw_result.get("output", "").strip()

    for tc in test_cases:
        expected = str(tc.get("expected_output", "")).strip()
        passed = (expected in output_str) if (expected and output_str) else raw_result.get("success", False)
        test_results.append({
            "input": tc.get("input", ""),
            "expected_output": expected,
            "actual_output": output_str if output_str else ("Success" if raw_result.get("success") else "Error"),
            "passed": passed
        })

    return success_response({
        "raw_execution": raw_result,
        "test_results": test_results,
        "all_passed": all_passed and any(t["passed"] for t in test_results) if test_results else raw_result.get("success", False)
    })
