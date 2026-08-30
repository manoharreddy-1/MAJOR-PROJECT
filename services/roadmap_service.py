"""Personalized preparation roadmap service."""
import logging
from typing import Any, Dict

from ai.llm_model import LLMModel
from ai.prompts import roadmap_prompt
from database.models import utc_now
from database.mongodb import get_collection, COLLECTIONS

logger = logging.getLogger(__name__)


class RoadmapService:
    """Generate personalized interview preparation roadmaps."""

    def __init__(self):
        self.llm = LLMModel()
        self.collection = get_collection(COLLECTIONS["roadmaps"])

    def generate(
        self,
        resume: Dict,
        job: Dict,
        analysis: Dict,
        user_id: str = None,
        analysis_id: str = None,
    ) -> Dict[str, Any]:
        skill_analysis = analysis.get("skill_analysis", {})
        matched = [s["skill"] for s in skill_analysis.get("matched", [])]
        partial = [s["skill"] for s in skill_analysis.get("partial", [])]
        missing = [s["skill"] for s in skill_analysis.get("missing", [])]
        strengths = analysis.get("strengths", [])

        prompt = roadmap_prompt(
            job=job,
            resume=resume,
            matched_skills=matched,
            partial_skills=partial,
            missing_skills=missing,
            strengths=strengths,
        )

        roadmap = self.llm.generate_json(prompt)

        doc = {
            "user_id": user_id,
            "analysis_id": analysis_id,
            "target_role": analysis.get("target_role"),
            "roadmap": roadmap,
            "created_at": utc_now(),
        }
        result = self.collection.insert_one(doc)

        return {
            "roadmap_id": str(result.inserted_id),
            "roadmap": roadmap,
        }
