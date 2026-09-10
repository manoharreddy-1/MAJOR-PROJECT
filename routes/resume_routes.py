"""Resume upload and extraction API routes."""
import logging

from flask import Blueprint, request

from routes.responses import error_response, success_response
from services.resume_service import ResumeService
from utils.validators import validate_upload

logger = logging.getLogger(__name__)
resume_bp = Blueprint("resume", __name__)
resume_service = ResumeService()


@resume_bp.route("/upload", methods=["POST"])
def upload_resume():
    """Upload and extract resume from PDF."""
    if "file" not in request.files:
        return error_response("NO_FILE", "Please upload a PDF resume.")

    file = request.files["file"]
    valid, msg = validate_upload(file)
    if not valid:
        return error_response("INVALID_FILE", msg)

    try:
        file_bytes = file.read()
        user_id = request.form.get("user_id")
        result = resume_service.process_upload(file_bytes, file.filename, user_id)
        return success_response(result, "Resume uploaded and extracted successfully.")
    except ValueError as exc:
        return error_response("EXTRACTION_FAILED", str(exc))
    except Exception as exc:
        logger.exception("Resume upload failed")
        return error_response("SERVER_ERROR", "Failed to process resume. Please try again.", 500)


@resume_bp.route("/extract/<resume_id>", methods=["GET"])
def get_resume(resume_id):
    """Get extracted resume information."""
    resume = resume_service.get_resume(resume_id)
    if not resume:
        return error_response("NOT_FOUND", "Resume not found.", 404)
    return success_response(resume)


@resume_bp.route("/extract/<resume_id>", methods=["PUT"])
def update_resume(resume_id):
    """Update extracted resume information after user verification."""
    data = request.get_json()
    if not data or "extracted" not in data:
        return error_response("INVALID_DATA", "Extracted data is required.")

    updated = resume_service.update_extracted(resume_id, data["extracted"])
    if not updated:
        return error_response("NOT_FOUND", "Resume not found.", 404)
    return success_response({"resume_id": resume_id}, "Resume information updated.")
