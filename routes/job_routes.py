"""Job description analysis API routes."""
import logging

from flask import Blueprint, request

from routes.responses import error_response, success_response
from services.job_service import JobService
from utils.validators import validate_text, validate_upload

logger = logging.getLogger(__name__)
job_bp = Blueprint("job", __name__)
job_service = JobService()


@job_bp.route("/analyze", methods=["POST"])
def analyze_job():
    """Analyze job description from text or file upload."""
    user_id = request.form.get("user_id") or (request.get_json() or {}).get("user_id")

    # File upload
    if "file" in request.files and request.files["file"].filename:
        file = request.files["file"]
        valid, msg = validate_upload(file)
        if not valid:
            return error_response("INVALID_FILE", msg)
        try:
            result = job_service.analyze_file(file.read(), file.filename, user_id)
            return success_response(result, "Job description analyzed successfully.")
        except ValueError as exc:
            return error_response("INVALID_DATA", str(exc))

    # JSON text input
    data = request.get_json()
    if not data:
        return error_response("INVALID_DATA", "Job description text or file is required.")

    text = data.get("text", "")
    title = data.get("title")
    valid, msg = validate_text(text, "Job description", min_length=20)
    if not valid:
        return error_response("INVALID_DATA", msg)

    try:
        result = job_service.analyze_text(text, title=title, user_id=user_id)
        return success_response(result, "Job description analyzed successfully.")
    except ValueError as exc:
        return error_response("INVALID_DATA", str(exc))


@job_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    job = job_service.get_job(job_id)
    if not job:
        return error_response("NOT_FOUND", "Job description not found.", 404)
    return success_response(job)


@job_bp.route("/<job_id>", methods=["PUT"])
def update_job(job_id):
    data = request.get_json()
    if not data or "requirements" not in data:
        return error_response("INVALID_DATA", "Requirements data is required.")

    updated = job_service.update_requirements(job_id, data["requirements"])
    if not updated:
        return error_response("NOT_FOUND", "Job description not found.", 404)
    return success_response({"job_id": job_id}, "Job requirements updated.")
