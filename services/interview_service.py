"""Interview question generation service."""
import logging
from typing import Any, Dict

from ai.llm_model import LLMModel
from ai.prompts import interview_questions_prompt, sample_answer_prompt
from database.models import serialize_doc, utc_now
from database.mongodb import get_collection, COLLECTIONS

logger = logging.getLogger(__name__)


class InterviewService:
    """Generate job-specific interview questions and sample answers."""

    def __init__(self):
        self.llm = LLMModel()
        self.collection = get_collection(COLLECTIONS["interview_preparations"])

    def generate(
        self,
        resume: Dict,
        job: Dict,
        analysis: Dict,
        user_id: str = None,
        analysis_id: str = None,
    ) -> Dict[str, Any]:
        missing = [s["skill"] for s in analysis.get("skill_analysis", {}).get("missing", [])]
        target_role = analysis.get("target_role", job.get("job_title", ""))

        prompt = interview_questions_prompt(
            resume=resume,
            job=job,
            target_role=target_role,
            missing_skills=missing,
        )

        questions = self.llm.generate_json(prompt)

        doc = {
            "user_id": user_id,
            "analysis_id": analysis_id,
            "target_role": target_role,
            "questions": questions,
            "created_at": utc_now(),
        }
        result = self.collection.insert_one(doc)

        return {
            "interview_id": str(result.inserted_id),
            "questions": questions,
        }

    def generate_sample_answer(
        self, question: str, resume: Dict, category: str
    ) -> Dict[str, Any]:
        prompt = sample_answer_prompt(question, resume, category)
        return self.llm.generate_json(prompt)
