"""API endpoints for AI Course Generator."""
import logging
from flask import Blueprint, request

from routes.auth_routes import get_request_user
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

    clean_topic = topic.strip()
    category = data.get("category", "Technology & Science")
    level = data.get("level", "Beginner")
    duration = data.get("duration", "1 Hour")
    num_chapters = int(data.get("num_chapters", 5))
    include_video = data.get("include_video", "Yes")
    description = data.get("description", "")

    # Resolve authenticated user
    user = get_request_user(request)
    user_id = user.get("user_id") if user else (data.get("user_id") or request.cookies.get("user_id") or "anonymous")
    user_name = user.get("username") or user.get("name") if user else (data.get("user_name") or "Learner")

    # Duplicate check: If user already has a course for this skill and didn't force regenerate
    force_regenerate = bool(data.get("force_regenerate", False))
    if not force_regenerate and user_id and user_id != "anonymous":
        existing = course_service.get_user_course_by_skill(user_id, clean_topic)
        if existing:
            return success_response({
                "already_exists": True,
                "course_id": existing["course_id"],
                "course": existing,
                "message": f"You already have a course for {clean_topic}."
            }, "Existing course found for this skill.", 200)

    try:
        result = course_service.generate_course_layout(
            topic=clean_topic,
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
    user = get_request_user(request)
    user_id = user.get("user_id") if user else (
        request.headers.get("X-User-Id") or 
        request.args.get("user_id") or 
        request.cookies.get("user_id")
    )
    try:
        course = course_service.get_course_details(course_id, user_id=user_id)
        if not course:
            return error_response("NOT_FOUND", "Course not found.", 404)
        return success_response(course)
    except PermissionError as pe:
        return error_response("FORBIDDEN", str(pe), 403)
    except Exception as e:
        logger.exception("Error retrieving course %s: %s", course_id, e)
        return error_response("SERVER_ERROR", str(e), 500)


@course_bp.route("/<course_id>/progress", methods=["POST"])
def update_progress(course_id: str):
    """Update chapter completion state for the course in user account."""
    user = get_request_user(request)
    user_id = user.get("user_id") if user else (request.headers.get("X-User-Id") or request.cookies.get("user_id"))
    data = request.get_json() or {}
    chapter_id = data.get("chapter_id")
    completed = bool(data.get("completed", True))

    if chapter_id is None:
        return error_response("MISSING_CHAPTER", "chapter_id is required.")

    try:
        res = course_service.update_chapter_progress(course_id, user_id, int(chapter_id), completed)
        return success_response(res, "Progress updated successfully.")
    except PermissionError as pe:
        return error_response("FORBIDDEN", str(pe), 403)
    except ValueError as ve:
        return error_response("NOT_FOUND", str(ve), 404)
    except Exception as e:
        logger.exception("Error updating progress for course %s: %s", course_id, e)
        return error_response("SERVER_ERROR", str(e), 500)


@course_bp.route("/<course_id>", methods=["DELETE"])
def delete_course(course_id: str):
    """Delete a course and its chapters with ownership verification."""
    user = get_request_user(request)
    user_id = user.get("user_id") if user else (request.headers.get("X-User-Id") or request.cookies.get("user_id"))
    try:
        success = course_service.delete_course(course_id, user_id=user_id)
        if not success:
            return error_response("NOT_FOUND", "Course not found.", 404)
        return success_response({"deleted": True, "course_id": course_id}, "Course deleted successfully.")
    except PermissionError as pe:
        return error_response("FORBIDDEN", str(pe), 403)
    except Exception as e:
        logger.exception("Error deleting course %s: %s", course_id, e)
        return error_response("SERVER_ERROR", str(e), 500)


@course_bp.route("/check-duplicate", methods=["GET"])
def check_duplicate_course():
    """Check if the authenticated user already generated a course for this skill."""
    skill = request.args.get("skill") or request.args.get("topic")
    if not skill:
        return error_response("MISSING_SKILL", "Skill query parameter is required.")

    user = get_request_user(request)
    user_id = user.get("user_id") if user else (request.args.get("user_id") or request.cookies.get("user_id"))
    if not user_id:
        return success_response({"exists": False})

    existing = course_service.get_user_course_by_skill(user_id, skill)
    if existing:
        return success_response({
            "exists": True,
            "course_id": existing["course_id"],
            "name": existing.get("name"),
            "skill": existing.get("skill")
        })
    return success_response({"exists": False})


@course_bp.route("/list", methods=["GET"])
def list_courses():
    """Retrieve generated courses filtered strictly by authenticated user."""
    user = get_request_user(request)
    user_id = user.get("user_id") if user else (request.args.get("user_id") or request.cookies.get("user_id"))
    try:
        courses = course_service.list_courses(user_id=user_id)
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

