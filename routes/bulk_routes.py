"""Bulk Resume Analysis & Screening API routes."""
import json
import logging
from flask import Blueprint, Response, request

from routes.auth_routes import is_bulk_authorized, get_request_user
from routes.responses import error_response, success_response
from services.bulk_screening_service import BulkScreeningService

logger = logging.getLogger(__name__)
bulk_bp = Blueprint("bulk", __name__)
screening_service = BulkScreeningService()


@bulk_bp.route("/analyze", methods=["POST"])
def analyze_bulk_resumes():
    """Analyze a batch of resumes against job requirements and academic cutoffs."""
    # Strict role verification: Student cannot access bulk routes
    if not is_bulk_authorized(request):
        return error_response(
            "FORBIDDEN",
            "Access denied. Bulk analysis is available for Placement Cell and Recruiters only.",
            403
        )

    user = get_request_user(request)
    user_id = user.get("user_id") if user else None

    # Handle multipart/form-data or json
    job_description = ""
    job_title = ""
    batch_name = ""
    cutoffs = {}
    uploaded_files = []

    if request.content_type and "multipart/form-data" in request.content_type:
        job_description = (request.form.get("job_description") or request.form.get("job_text") or "").strip()
        job_title = (request.form.get("job_title") or "").strip()
        batch_name = (request.form.get("batch_name") or "").strip()

        # Parse cutoffs
        min_cgpa = request.form.get("min_cgpa")
        min_tenth = request.form.get("min_tenth")
        min_twelfth = request.form.get("min_twelfth")
        if min_cgpa:
            cutoffs["min_cgpa"] = min_cgpa
        if min_tenth:
            cutoffs["min_tenth"] = min_tenth
        if min_twelfth:
            cutoffs["min_twelfth"] = min_twelfth

        # Collect files
        raw_files = request.files.getlist("files") or request.files.getlist("resumes")
        if not raw_files and "file" in request.files:
            raw_files = [request.files["file"]]

        for f in raw_files:
            if f and f.filename:
                uploaded_files.append((f.filename, f.read()))

    elif request.is_json:
        data = request.get_json() or {}
        job_description = (data.get("job_description") or data.get("job_text") or "").strip()
        job_title = (data.get("job_title") or "").strip()
        batch_name = (data.get("batch_name") or "").strip()
        cutoffs = data.get("cutoffs") or {}
        # Also handle raw text candidate resumes passed in JSON for direct/automated testing
        for item in data.get("resumes", []):
            if isinstance(item, dict):
                fname = item.get("filename") or f"{item.get('name', 'candidate')}.txt"
                content = (item.get("content") or item.get("text") or "").encode("utf-8")
                uploaded_files.append((fname, content))

    if not job_description:
        return error_response("VALIDATION_ERROR", "Job description is required for screening.")

    # Unpack archives (.zip) if present
    parsed_files = screening_service.unpack_uploaded_files(uploaded_files)

    if not parsed_files:
        return error_response(
            "VALIDATION_ERROR",
            "No valid resumes provided. Please upload PDF, DOCX, TXT files, or a ZIP archive containing resumes."
        )

    try:
        batch_result = screening_service.process_batch(
            job_description=job_description,
            files=parsed_files,
            job_title=job_title,
            cutoffs=cutoffs,
            user_id=user_id,
            batch_name=batch_name,
        )
        return success_response(batch_result, "Bulk screening completed successfully.", 201)
    except Exception as exc:
        logger.exception("Error processing bulk screening: %s", exc)
        return error_response("SERVER_ERROR", f"Screening process failed: {str(exc)}", 500)


@bulk_bp.route("/batches", methods=["GET"])
def list_batches():
    """List historical screening batches."""
    if not is_bulk_authorized(request):
        return error_response(
            "FORBIDDEN",
            "Access denied. Bulk analysis is available for Placement Cell and Recruiters only.",
            403
        )

    user = get_request_user(request)
    user_id = user.get("user_id") if user else None
    batches = screening_service.list_batches(user_id=user_id)
    return success_response(batches)


@bulk_bp.route("/batch/<batch_id>", methods=["GET"])
def get_batch_details(batch_id: str):
    """Get single batch with all ranked candidates."""
    if not is_bulk_authorized(request):
        return error_response(
            "FORBIDDEN",
            "Access denied. Bulk analysis is available for Placement Cell and Recruiters only.",
            403
        )

    batch = screening_service.get_batch(batch_id)
    if not batch:
        return error_response("NOT_FOUND", "Batch not found.", 404)
    return success_response(batch)


@bulk_bp.route("/export/<batch_id>", methods=["GET"])
def export_batch_csv(batch_id: str):
    """Download ranked candidates as CSV."""
    if not is_bulk_authorized(request):
        return error_response(
            "FORBIDDEN",
            "Access denied. Bulk analysis is available for Placement Cell and Recruiters only.",
            403
        )

    batch = screening_service.get_batch(batch_id)
    if not batch:
        return error_response("NOT_FOUND", "Batch not found.", 404)

    csv_content = screening_service.generate_csv_export(batch)
    safe_title = "".join(c for c in batch.get("job_title", "batch") if c.isalnum() or c in ("-", "_")).rstrip()
    filename = f"Screening_Results_{safe_title}_{batch_id}.csv"

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8",
        }
    )
