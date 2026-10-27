"""Analysis, history, improvement, interview, and roadmap API routes."""
import logging

from bson import ObjectId
from flask import Blueprint, request, send_file

from routes.responses import error_response, success_response
from database.models import serialize_doc, utc_now
from database.mongodb import get_collection, COLLECTIONS
from services.ats_service import ATSService
from services.improvement_service import ImprovementService
from services.interview_service import InterviewService
from services.job_service import JobService
from services.resume_service import ResumeService
from services.roadmap_service import RoadmapService
from services.resume_optimizer_service import (
    ResumeOptimizerService,
    export_resume_to_docx,
    export_resume_to_pdf,
)

logger = logging.getLogger(__name__)
analysis_bp = Blueprint("analysis", __name__)

resume_service = ResumeService()
job_service = JobService()
ats_service = ATSService()
improvement_service = ImprovementService()
interview_service = InterviewService()
roadmap_service = RoadmapService()
optimizer_service = ResumeOptimizerService()
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
            {
                "analysis_id": str(result.inserted_id),
                "resume_id": resume_id,
                "job_description_id": job_id,
                "resume_data": resume,
                "job_data": job,
                **analysis_result,
            },
            "Analysis completed successfully.",
        )
    except Exception as exc:
        logger.exception("Analysis failed")
        return error_response("ANALYSIS_FAILED", "Analysis failed. Please try again.", 500)


@analysis_bp.route("/analysis/<analysis_id>", methods=["GET"])
def get_analysis(analysis_id):
    doc = None
    if ObjectId.is_valid(analysis_id):
        doc = analyses_collection.find_one({"_id": ObjectId(analysis_id)})
    if not doc:
        doc = analyses_collection.find_one({"_id": analysis_id})
    if not doc:
        doc = analyses_collection.find_one({"analysis_id": analysis_id})

    if not doc:
        return error_response("NOT_FOUND", "Analysis not found.", 404)
    return success_response(serialize_doc(doc))


@analysis_bp.route("/history", methods=["GET"])
def get_history():
    user_id = request.args.get("user_id")
    limit = min(int(request.args.get("limit", 50)), 100)

    docs = []
    if user_id:
        cursor = analyses_collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        docs = list(cursor)

    if not docs:
        cursor = analyses_collection.find({}).sort("created_at", -1).limit(limit)
        docs = list(cursor)

    history = []
    for doc in docs:
        item = serialize_doc(doc)
        missing = doc.get("skill_analysis", {}).get("missing", [])
        history.append({
            "analysis_id": item["_id"],
            "target_role": item.get("target_role"),
            "overall_score": item.get("scores", {}).get("overall"),
            "match_label": item.get("match_label"),
            "top_missing_skills": [
                s.get("skill") if isinstance(s, dict) else str(s)
                for s in missing[:3]
            ],
            "created_at": item.get("created_at"),
            "user_id": item.get("user_id"),
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


@analysis_bp.route("/interview/more", methods=["POST"])
def generate_more_interview_questions():
    """Fetch additional interview questions for a category."""
    data = request.get_json() or {}
    analysis_id = data.get("analysis_id")
    category = data.get("category", "technical")
    existing = data.get("existing_questions", [])

    if not analysis_id:
        return error_response("MISSING_ID", "analysis_id is required.")

    doc = analyses_collection.find_one({"_id": ObjectId(analysis_id)})
    if not doc:
        return error_response("NOT_FOUND", "Analysis not found.", 404)

    resume_doc = resume_service.get_resume(doc["resume_id"])
    job_doc = job_service.get_job(doc["job_description_id"])

    try:
        more_result = interview_service.generate_more_questions(
            resume=resume_doc.get("extracted", resume_doc) if resume_doc else {},
            job=job_doc.get("requirements", job_doc) if job_doc else {},
            category=category,
            existing_questions=existing,
            target_role=doc.get("target_role", "")
        )
        return success_response(more_result, "Additional questions generated.")
    except Exception as exc:
        logger.exception("More questions generation failed: %s", exc)
        return error_response("GENERATION_FAILED", str(exc), 500)


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
    data = request.get_json() or {}
    analysis_id = data.get("analysis_id")
    if not analysis_id:
        return error_response("MISSING_ID", "analysis_id is required.")

    doc = analyses_collection.find_one({"_id": ObjectId(analysis_id)})
    if not doc:
        return error_response("NOT_FOUND", "Analysis not found.", 404)

    resume_doc = resume_service.get_resume(doc["resume_id"])
    job_doc = job_service.get_job(doc["job_description_id"])

    weeks = data.get("weeks", 4)
    hours_per_week = data.get("hours_per_week", 15)
    focus = data.get("focus", "balanced")

    try:
        result = roadmap_service.generate(
            resume=resume_doc.get("extracted", resume_doc),
            job=job_doc.get("requirements", job_doc),
            analysis=serialize_doc(doc),
            user_id=data.get("user_id"),
            analysis_id=analysis_id,
            weeks=weeks,
            hours_per_week=hours_per_week,
            focus=focus,
        )
        return success_response(result, "Preparation roadmap generated.")
    except Exception as exc:
        logger.exception("Roadmap generation failed")
        return error_response("GENERATION_FAILED", "Failed to generate roadmap.", 500)


@analysis_bp.route("/optimize-resume", methods=["POST"])
def optimize_resume():
    """
    AI-powered ATS Resume Optimizer.
    Weaves cleaned missing skills into resume with evidence grounding,
    and recalculates genuine ATS score.
    """
    data = request.get_json() or {}
    resume_id = data.get("resume_id")
    job_id = data.get("job_id") or data.get("job_description_id")

    # 1. Resolve resume data
    resume_data = data.get("resume_data") or {}
    analysis_id = data.get("analysis_id")

    if (not resume_data or not (resume_data.get("raw_text") or resume_data.get("skills"))) and resume_id:
        resume_doc = resume_service.get_resume(resume_id)
        if resume_doc:
            resume_data = resume_doc.get("extracted", resume_doc)

    if (not resume_data or not (resume_data.get("raw_text") or resume_data.get("skills"))) and analysis_id:
        try:
            a_doc = None
            if ObjectId.is_valid(analysis_id):
                a_doc = analyses_collection.find_one({"_id": ObjectId(analysis_id)})
            if not a_doc:
                a_doc = analyses_collection.find_one({"_id": analysis_id})
            if a_doc and a_doc.get("resume_id"):
                resume_doc = resume_service.get_resume(a_doc["resume_id"])
                if resume_doc:
                    resume_data = resume_doc.get("extracted", resume_doc)
            if a_doc and not job_id and a_doc.get("job_description_id"):
                job_id = a_doc["job_description_id"]
        except Exception:
            pass

    # Fallback to constructed candidate profile ONLY if we have context from an ongoing analysis
    if not (resume_data.get("raw_text") or "").strip() and not resume_data.get("skills"):
        matched = data.get("matched_skills") or []
        if matched or analysis_id or resume_id:
            resume_data = {
                "name": resume_data.get("name") or "Candidate",
                "skills": matched if matched else ["Software Engineering", "Python", "Problem Solving", "Data Structures"],
                "summary": "Impact-driven software professional dedicated to high-performance development and continuous learning.",
                "experience": [{"title": "Software Developer", "company": "Technology Solutions", "bullets": ["Engineered core features and optimized software performance using modern technical tools."]}],
                "projects": [{"title": "Software Systems Development", "bullets": ["Built robust data and software applications ensuring high efficiency and accuracy."]}],
                "education": [{"degree": "Bachelor of Technology", "institution": "University"}],
                "raw_text": "Candidate Software Developer. Skills: " + ", ".join(matched),
            }

    # 2. Resolve job data
    job_data = data.get("job_data")
    if not job_data and job_id:
        job_doc = job_service.get_job(job_id)
        if job_doc:
            job_data = job_doc.get("requirements", job_doc)

    if not job_data:
        job_data = {
            "job_title": data.get("target_role", "Software Engineer"),
            "required_skills": data.get("missing_skills", []),
            "preferred_skills": [],
            "responsibilities": [],
        }

    missing_skills = data.get("missing_skills")
    matched_skills = data.get("matched_skills") or []
    current_score = data.get("current_score")
    confirmed_skills = data.get("confirmed_skills") or []

    try:
        optimization_result = optimizer_service.optimize(
            resume_data=resume_data,
            job_data=job_data,
            missing_skills=missing_skills,
            matched_skills=matched_skills,
            current_score=current_score,
            confirmed_skills=confirmed_skills,
        )
        return success_response(optimization_result, "Resume optimized with AI successfully.")
    except ValueError as ve:
        return error_response("VALIDATION_ERROR", str(ve), 400)
    except Exception as exc:
        logger.exception("AI Resume Optimization failed")
        return error_response("OPTIMIZATION_FAILED", f"Failed to optimize resume: {str(exc)}", 500)


@analysis_bp.route("/optimize-resume/export/docx", methods=["POST"])
def export_docx():
    """Export optimized resume to ATS-friendly DOCX."""
    data = request.get_json() or {}
    structured_resume = data.get("structured_optimized") or data.get("optimized_resume") or data
    if not structured_resume or not isinstance(structured_resume, dict):
        return error_response("INVALID_DATA", "Structured resume data is required for DOCX export.", 400)

    try:
        file_stream = export_resume_to_docx(structured_resume)
        filename = f"ATS_Optimized_Resume_{(structured_resume.get('name') or 'Candidate').replace(' ', '_')}.docx"
        return send_file(
            file_stream,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as exc:
        logger.exception("DOCX export failed")
        return error_response("EXPORT_FAILED", f"DOCX generation failed: {str(exc)}", 500)


@analysis_bp.route("/optimize-resume/export/pdf", methods=["POST"])
def export_pdf():
    """Export optimized resume to ATS-friendly PDF."""
    data = request.get_json() or {}
    structured_resume = data.get("structured_optimized") or data.get("optimized_resume") or data
    if not structured_resume or not isinstance(structured_resume, dict):
        return error_response("INVALID_DATA", "Structured resume data is required for PDF export.", 400)

    try:
        file_stream = export_resume_to_pdf(structured_resume)
        filename = f"ATS_Optimized_Resume_{(structured_resume.get('name') or 'Candidate').replace(' ', '_')}.pdf"
        return send_file(
            file_stream,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as exc:
        logger.exception("PDF export failed")
        return error_response("EXPORT_FAILED", f"PDF generation failed: {str(exc)}", 500)

