"""Analysis, history, improvement, interview, and roadmap API routes."""
import logging

from bson import ObjectId
from flask import Blueprint, request

from routes.responses import error_response, success_response
from database.models import serialize_doc, utc_now
from database.mongodb import get_collection, COLLECTIONS
from services.ats_service import ATSService
from services.improvement_service import ImprovementService
from services.interview_service import InterviewService
from services.job_service import JobService
from services.resume_service import ResumeService
from services.roadmap_service import RoadmapService

logger = logging.getLogger(__name__)
analysis_bp = Blueprint("analysis", __name__)

resume_service = ResumeService()
job_service = JobService()
ats_service = ATSService()
improvement_service = ImprovementService()
interview_service = InterviewService()
roadmap_service = RoadmapService()
analyses_collection = get_collection(COLLECTIONS["analyses"])


@analysis_bp.route("/analyze", methods=["POST"])
def run_analysis():
    """Run full SBERT-based ATS analysis."""
    data = request.get_json()
    if not data:
        return error_response("INVALID_DATA", "Request body is required.")

    resume_id = data.get("resume_id")
    job_id = data.get("job_description_id")
    target_role = data.get("target_role")

    if not resume_id or not job_id:
        return error_response("MISSING_IDS", "resume_id and job_description_id are required.")

    resume_doc = resume_service.get_resume(resume_id)
    job_doc = job_service.get_job(job_id)

    if not resume_doc:
        return error_response("NOT_FOUND", "Resume not found.", 404)
    if not job_doc:
        return error_response("NOT_FOUND", "Job description not found.", 404)

    resume = resume_doc.get("extracted", resume_doc)
    job = job_doc.get("requirements", job_doc)

    try:
        analysis_result = ats_service.analyze(resume, job, target_role)

        doc = {
            "user_id": data.get("user_id"),
            "resume_id": resume_id,
            "job_description_id": job_id,
            "target_role": analysis_result["target_role"],
            "scores": analysis_result["scores"],
            "match_label": analysis_result["match_label"],
            "score_breakdown": analysis_result["score_breakdown"],
            "skill_analysis": analysis_result["skill_analysis"],
            "project_analysis": analysis_result["project_analysis"],
            "strengths": analysis_result["strengths"],
            "improvements": analysis_result["improvements"],
            "disclaimer": analysis_result["disclaimer"],
            "created_at": utc_now(),
        }
        result = analyses_collection.insert_one(doc)

        return success_response(
            {"analysis_id": str(result.inserted_id), **analysis_result},
            "Analysis completed successfully.",
        )
    except Exception as exc:
        logger.exception("Analysis failed")
        return error_response("ANALYSIS_FAILED", "Analysis failed. Please try again.", 500)


@analysis_bp.route("/<analysis_id>", methods=["GET"])
def get_analysis(analysis_id):
    doc = analyses_collection.find_one({"_id": ObjectId(analysis_id)})
    if not doc:
        return error_response("NOT_FOUND", "Analysis not found.", 404)
    return success_response(serialize_doc(doc))


@analysis_bp.route("/history", methods=["GET"])
def get_history():
    user_id = request.args.get("user_id")
    limit = min(int(request.args.get("limit", 20)), 50)
    query = {"user_id": user_id} if user_id else {}
    cursor = analyses_collection.find(query).sort("created_at", -1).limit(limit)

    history = []
    for doc in cursor:
        item = serialize_doc(doc)
        missing = doc.get("skill_analysis", {}).get("missing", [])
        history.append({
            "analysis_id": item["_id"],
            "target_role": item.get("target_role"),
            "overall_score": item.get("scores", {}).get("overall"),
            "match_label": item.get("match_label"),
            "top_missing_skills": [s.get("skill") for s in missing[:3]],
            "created_at": item.get("created_at"),
        })

    return success_response(history)


@analysis_bp.route("/resume/improve", methods=["POST"])
def improve_resume():
    data = request.get_json()
    analysis_id = data.get("analysis_id") if data else None
    if not analysis_id:
        return error_response("MISSING_ID", "analysis_id is required.")

    doc = analyses_collection.find_one({"_id": ObjectId(analysis_id)})
    if not doc:
        return error_response("NOT_FOUND", "Analysis not found.", 404)

    resume_doc = resume_service.get_resume(doc["resume_id"])
    job_doc = job_service.get_job(doc["job_description_id"])
    resume = resume_doc.get("extracted", resume_doc)
    job = job_doc.get("requirements", job_doc)

    try:
        suggestions = improvement_service.generate(resume, job, serialize_doc(doc))
        return success_response(suggestions, "Resume improvement suggestions generated.")
    except Exception as exc:
        logger.exception("Improvement generation failed")
        return error_response("GENERATION_FAILED", "Failed to generate suggestions.", 500)


@analysis_bp.route("/interview/generate", methods=["POST"])
def generate_interview():
    data = request.get_json()
    analysis_id = data.get("analysis_id") if data else None
    if not analysis_id:
        return error_response("MISSING_ID", "analysis_id is required.")

    doc = analyses_collection.find_one({"_id": ObjectId(analysis_id)})
    if not doc:
        return error_response("NOT_FOUND", "Analysis not found.", 404)

    resume_doc = resume_service.get_resume(doc["resume_id"])
    job_doc = job_service.get_job(doc["job_description_id"])

    try:
        result = interview_service.generate(
            resume=resume_doc.get("extracted", resume_doc),
            job=job_doc.get("requirements", job_doc),
            analysis=serialize_doc(doc),
            user_id=data.get("user_id"),
            analysis_id=analysis_id,
        )
        return success_response(result, "Interview questions generated.")
    except Exception as exc:
        logger.exception("Interview generation failed")
        return error_response("GENERATION_FAILED", "Failed to generate interview questions.", 500)


@analysis_bp.route("/interview/sample-answer", methods=["POST"])
def sample_answer():
    data = request.get_json()
    if not data or not data.get("question"):
        return error_response("INVALID_DATA", "question is required.")

    resume_id = data.get("resume_id")
    resume_doc = resume_service.get_resume(resume_id) if resume_id else {}
    resume = resume_doc.get("extracted", {}) if resume_doc else {}

    try:
        answer = interview_service.generate_sample_answer(
            question=data["question"],
            resume=resume,
            category=data.get("category", "general"),
        )
        return success_response(answer)
    except Exception as exc:
        logger.exception("Sample answer generation failed")
        return error_response("GENERATION_FAILED", "Failed to generate sample answer.", 500)


@analysis_bp.route("/roadmap/generate", methods=["POST"])
def generate_roadmap():
    data = request.get_json()
    analysis_id = data.get("analysis_id") if data else None
    if not analysis_id:
        return error_response("MISSING_ID", "analysis_id is required.")

    doc = analyses_collection.find_one({"_id": ObjectId(analysis_id)})
    if not doc:
        return error_response("NOT_FOUND", "Analysis not found.", 404)

    resume_doc = resume_service.get_resume(doc["resume_id"])
    job_doc = job_service.get_job(doc["job_description_id"])

    try:
        result = roadmap_service.generate(
            resume=resume_doc.get("extracted", resume_doc),
            job=job_doc.get("requirements", job_doc),
            analysis=serialize_doc(doc),
            user_id=data.get("user_id"),
            analysis_id=analysis_id,
        )
        return success_response(result, "Preparation roadmap generated.")
    except Exception as exc:
        logger.exception("Roadmap generation failed")
        return error_response("GENERATION_FAILED", "Failed to generate roadmap.", 500)
