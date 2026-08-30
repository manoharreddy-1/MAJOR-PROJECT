"""Skill gap analysis using SBERT semantic matching."""
import logging
from typing import Any, Dict, List

from ai.embeddings import best_match_similarity, text_similarity
from config.settings import HIGH_SKILL_THRESHOLD, MEDIUM_SKILL_THRESHOLD
from utils.scoring import normalize_cosine_to_score

logger = logging.getLogger(__name__)


class SkillGapService:
    """
    Semantic skill matching using SBERT embeddings.

    For each required skill, finds the best semantic match among
    candidate skills and classifies as MATCHED, PARTIALLY MATCHED, or MISSING.
    """

    def analyze_skills(
        self,
        resume_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str] = None,
        resume_text: str = "",
    ) -> Dict[str, Any]:
        """Perform skill gap analysis."""
        preferred_skills = preferred_skills or []
        all_required = list(dict.fromkeys(required_skills + preferred_skills))

        if not all_required:
            return {
                "matched": [],
                "partial": [],
                "missing": [],
                "skill_score": 100.0,
                "total_required": 0,
            }

        # Include resume text snippets as additional skill evidence
        candidate_pool = list(resume_skills)
        if resume_text:
            candidate_pool.append(resume_text[:2000])

        matched, partial, missing = [], [], []

        for skill in all_required:
            best_sim, best_match, _ = best_match_similarity(skill, candidate_pool)
            importance = "High" if skill in required_skills else "Medium"

            entry = {
                "skill": skill,
                "importance": importance,
                "similarity": round(best_sim, 3),
                "best_match": best_match if best_match != resume_text[:2000] else None,
            }

            if best_sim >= HIGH_SKILL_THRESHOLD:
                entry["status"] = "MATCHED"
                matched.append(entry)
            elif best_sim >= MEDIUM_SKILL_THRESHOLD:
                entry["status"] = "PARTIALLY MATCHED"
                entry["reason"] = f"Resume shows related knowledge ('{best_match}') but not an exact match for '{skill}'."
                partial.append(entry)
            else:
                entry["status"] = "MISSING"
                entry["reason"] = self._missing_reason(skill, importance)
                entry["learning_objective"] = self._learning_objective(skill)
                missing.append(entry)

        skill_score = self._calculate_skill_score(matched, partial, missing, len(all_required))

        return {
            "matched": matched,
            "partial": partial,
            "missing": missing,
            "skill_score": skill_score,
            "total_required": len(all_required),
            "thresholds": {
                "high": HIGH_SKILL_THRESHOLD,
                "medium": MEDIUM_SKILL_THRESHOLD,
            },
        }

    def _calculate_skill_score(
        self,
        matched: List,
        partial: List,
        missing: List,
        total: int,
    ) -> float:
        """Calculate skill match score on 0-100 scale."""
        if total == 0:
            return 100.0
        matched_pts = len(matched) * 1.0
        partial_pts = len(partial) * 0.5
        score = ((matched_pts + partial_pts) / total) * 100
        return round(min(100.0, score), 1)

    def _missing_reason(self, skill: str, importance: str) -> str:
        return (
            f"The job description {'explicitly requires' if importance == 'High' else 'prefers'} "
            f"'{skill}', but no equivalent skill was found in the resume."
        )

    def _learning_objective(self, skill: str) -> str:
        objectives = {
            "AWS": "Learn AWS fundamentals: EC2, S3, IAM, and basic cloud deployment.",
            "Docker": "Learn containerization basics, Dockerfile creation, and Docker Compose.",
            "Kubernetes": "Understand pods, services, deployments, and basic cluster management.",
            "System Design": "Study scalability, load balancing, caching, and distributed systems patterns.",
            "Machine Learning": "Build ML projects covering data preprocessing, model training, and evaluation.",
            "Deep Learning": "Study neural networks, CNNs, RNNs, and frameworks like TensorFlow/PyTorch.",
        }
        for key, obj in objectives.items():
            if key.lower() in skill.lower():
                return obj
        return f"Build practical knowledge of {skill} through courses and hands-on projects before adding it to your resume."
