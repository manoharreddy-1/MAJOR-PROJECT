"""Resume improvement suggestions via Generative AI."""
import logging
from typing import Any, Dict, List

from ai.llm_model import LLMModel
from ai.prompts import resume_improvement_prompt

logger = logging.getLogger(__name__)


class ImprovementService:
    """Generate grounded resume improvement suggestions."""

    def __init__(self):
        self.llm = LLMModel()

    def generate(
        self,
        resume: Dict,
        job: Dict,
        analysis: Dict,
    ) -> Dict[str, Any]:
        matched = [s["skill"] for s in analysis.get("skill_analysis", {}).get("matched", [])]
        missing = [s["skill"] for s in analysis.get("skill_analysis", {}).get("missing", [])]
        weak_sections = self._identify_weak_sections(analysis)

        prompt = resume_improvement_prompt(
            resume=resume,
            job=job,
            matched_skills=matched,
            missing_skills=missing,
            weak_sections=weak_sections,
        )

        result = self.llm.generate_json(prompt)
        result["matched_skills"] = matched
        result["missing_skills"] = missing
        return result

    def _identify_weak_sections(self, analysis: Dict) -> List[str]:
        weak = []
        scores = analysis.get("scores", {})
        if scores.get("experience", 100) < 60:
            weak.append("experience")
        if scores.get("skills", 100) < 60:
            weak.append("skills")
        if scores.get("semantic", 100) < 60:
            weak.append("summary")
        semantic = analysis.get("semantic_details", {})
        if semantic.get("projects_semantic", 100) < 55:
            weak.append("projects")
        return weak
