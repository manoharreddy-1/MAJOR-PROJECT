"""Personalized preparation roadmap service with customizable timeline and day-wise activities."""
import logging
from typing import Any, Dict

from ai.llm_model import LLMModel
from ai.prompts import roadmap_prompt
from ai.dynamic_generator import generate_grounded_roadmap
from database.models import utc_now
from database.mongodb import get_collection, COLLECTIONS

logger = logging.getLogger(__name__)


class RoadmapService:
    """Generate personalized interview preparation roadmaps with day-by-day learning schedules."""

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
        weeks: int = 4,
        hours_per_week: int = 15,
        focus: str = "balanced",
    ) -> Dict[str, Any]:
        """Generate week-by-week and day-by-day preparation roadmap."""
        skill_analysis = analysis.get("skill_analysis", {})
        matched = [s["skill"] for s in skill_analysis.get("matched", [])]
        partial = [s["skill"] for s in skill_analysis.get("partial", [])]
        missing = [s["skill"] for s in skill_analysis.get("missing", [])]
        strengths = analysis.get("strengths", [])
        target_role = analysis.get("target_role") or job.get("job_title", "Software Engineer")

        # Prioritize missing skills that are high priority, followed by partial skills
        lagging_skills = list(missing)
        for p in partial:
            if p not in lagging_skills:
                lagging_skills.append(p)

        if not lagging_skills:
            lagging_skills = [
                f"{target_role} Advanced Architecture",
                "System Design & Scalability",
                "Production Coding Best Practices",
                "Mock Technical Interviews"
            ]

        # Enforce valid range for weeks and hours
        try:
            weeks = max(1, min(12, int(weeks or 4)))
        except (ValueError, TypeError):
            weeks = 4

        try:
            hours_per_week = max(5, min(40, int(hours_per_week or 15)))
        except (ValueError, TypeError):
            hours_per_week = 15

        prompt = roadmap_prompt(
            job=job,
            resume=resume,
            matched_skills=matched,
            partial_skills=partial,
            missing_skills=lagging_skills,
            strengths=strengths,
        )
        prompt += f"\nPREPARATION TIMELINE: {weeks} Weeks, {hours_per_week} Hours/Week (Total {weeks * hours_per_week} Hours)"

        # Try LLM generation, with dynamic grounded generator fallback
        roadmap = self.llm.generate_json(prompt)

        # Validate that the roadmap contains day-wise activities and weekly plan
        if (
            not roadmap
            or not isinstance(roadmap, dict)
            or "roadmap" not in roadmap
            or not roadmap.get("roadmap")
            or not roadmap.get("weekly_plan")
        ):
            roadmap = generate_grounded_roadmap(
                prompt=prompt,
                target_role=target_role,
                matched_skills=matched,
                missing_skills=lagging_skills,
                weeks=weeks,
                hours_per_week=hours_per_week,
            )

        # Ensure parameters are explicitly reflected
        roadmap["target_role"] = target_role
        roadmap["total_weeks"] = weeks
        roadmap["hours_per_week"] = hours_per_week
        roadmap["total_hours"] = weeks * hours_per_week
        roadmap["lagging_skills"] = lagging_skills

        doc = {
            "user_id": user_id,
            "analysis_id": analysis_id,
            "target_role": target_role,
            "weeks": weeks,
            "hours_per_week": hours_per_week,
            "roadmap": roadmap,
            "created_at": utc_now(),
        }
        result = self.collection.insert_one(doc)

        return {
            "roadmap_id": str(result.inserted_id),
            "roadmap": roadmap,
        }
