"""ATS scoring orchestration service."""
import logging
from typing import Any, Dict, List

from config.settings import ATS_WEIGHTS
from services.matching_service import MatchingService
from services.skill_gap_service import SkillGapService
from utils.scoring import calculate_weighted_ats_score, get_match_label, score_breakdown

logger = logging.getLogger(__name__)


class ATSService:
    """
    Transparent ATS score calculation.

    Overall = 45% Semantic + 30% Skills + 15% Experience + 10% Education
    All weights configurable in config/settings.py.
    """

    def __init__(self):
        self.matching = MatchingService()
        self.skill_gap = SkillGapService()

    def analyze(
        self,
        resume: Dict,
        job: Dict,
        target_role: str = None,
    ) -> Dict[str, Any]:
        """Run full ATS analysis and return comprehensive results."""
        # Section-level SBERT semantic scores
        semantic_scores = self.matching.compute_semantic_scores(resume, job)

        # Skill gap analysis
        skill_analysis = self.skill_gap.analyze_skills(
            resume_skills=resume.get("skills", []),
            required_skills=job.get("required_skills", []),
            preferred_skills=job.get("preferred_skills", []),
            resume_text=resume.get("raw_text", ""),
        )

        # Experience score from SBERT
        experience_score = semantic_scores["experience_semantic"]

        # Education score - only if job specifies requirements
        education_score = semantic_scores.get("education_semantic")
        if education_score is None:
            education_score = 75.0  # Neutral when not specified
            education_note = "Not specified in job description"
        else:
            education_note = None

        # Semantic match score (overall)
        semantic_score = semantic_scores["semantic"]
        skill_score = skill_analysis["skill_score"]

        # Weighted overall ATS score
        breakdown = score_breakdown(
            semantic=semantic_score,
            skills=skill_score,
            experience=experience_score,
            education=education_score,
        )

        # Project relevance
        project_analysis = self.matching.analyze_project_relevance(
            resume.get("projects", []),
            job.get("responsibilities", []),
        )

        # Strengths and improvements
        strengths = self._identify_strengths(skill_analysis, semantic_scores, resume)
        improvements = self._identify_improvements(skill_analysis, semantic_scores)

        return {
            "target_role": target_role or job.get("job_title", "Target Role"),
            "scores": {
                "overall": breakdown["overall"],
                "semantic": round(semantic_score, 1),
                "skills": round(skill_score, 1),
                "experience": round(experience_score, 1),
                "education": round(education_score, 1),
            },
            "match_label": get_match_label(breakdown["overall"]),
            "score_breakdown": breakdown,
            "education_note": education_note,
            "skill_analysis": skill_analysis,
            "project_analysis": project_analysis,
            "semantic_details": semantic_scores,
            "strengths": strengths,
            "improvements": improvements,
            "disclaimer": (
                "This is an AI-generated project-specific match score and is not "
                "an official score used by any particular company's ATS."
            ),
        }

    def _identify_strengths(
        self, skill_analysis: Dict, semantic_scores: Dict, resume: Dict
    ) -> List[str]:
        strengths = []
        matched = skill_analysis.get("matched", [])
        if matched:
            top = [m["skill"] for m in matched[:5]]
            strengths.append(f"Strong skill alignment: {', '.join(top)}")

        if semantic_scores.get("experience_semantic", 0) >= 70:
            strengths.append("Experience section shows good semantic relevance to job responsibilities.")

        if semantic_scores.get("projects_semantic", 0) >= 65:
            strengths.append("Projects demonstrate relevant technical work for this role.")

        if resume.get("certifications"):
            strengths.append(f"Certifications present: {', '.join(resume['certifications'][:3])}")

        if not strengths:
            strengths.append("Resume provides a foundation to build upon for this role.")

        return strengths

    def _identify_improvements(self, skill_analysis: Dict, semantic_scores: Dict) -> List[str]:
        improvements = []
        missing = skill_analysis.get("missing", [])
        if missing:
            top_missing = [m["skill"] for m in missing[:3]]
            improvements.append(f"Develop missing skills: {', '.join(top_missing)}")

        partial = skill_analysis.get("partial", [])
        if partial:
            top_partial = [p["skill"] for p in partial[:2]]
            improvements.append(f"Strengthen partially matched skills: {', '.join(top_partial)}")

        if semantic_scores.get("experience_semantic", 0) < 50:
            improvements.append("Reframe experience bullets to align with job responsibilities.")

        if semantic_scores.get("semantic", 0) < 60:
            improvements.append("Tailor resume summary to better match the job description language.")

        return improvements
