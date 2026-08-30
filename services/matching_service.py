"""SBERT-based semantic matching service."""
import logging
from typing import Any, Dict, List

from ai.embeddings import best_match_similarity, text_similarity, text_similarity_score
from utils.scoring import normalize_cosine_to_score

logger = logging.getLogger(__name__)


class MatchingService:
    """
    Section-aware SBERT semantic matching.

    Compares resume sections with corresponding job sections using
    sentence-transformers/all-MiniLM-L6-v2 embeddings and cosine similarity.
    """

    def compute_section_similarities(
        self, resume: Dict, job: Dict
    ) -> Dict[str, float]:
        """Calculate semantic similarity for each resume/job section pair."""
        resume_summary = resume.get("summary", "") or resume.get("raw_text", "")[:500]
        resume_skills = ", ".join(resume.get("skills", []))
        resume_experience = " ".join(resume.get("experience", []))
        resume_projects = " ".join(resume.get("projects", []))
        resume_education = " ".join(resume.get("education", []))

        job_text = job.get("raw_text", "")
        job_skills = ", ".join(job.get("required_skills", []) + job.get("preferred_skills", []))
        job_responsibilities = " ".join(job.get("responsibilities", []))
        job_education = " ".join(job.get("education", []))

        return {
            "overall_semantic": text_similarity(resume_summary, job_text),
            "skills": text_similarity(resume_skills, job_skills) if job_skills else 0.0,
            "experience": text_similarity(resume_experience, job_responsibilities) if job_responsibilities else 0.0,
            "projects": text_similarity(resume_projects, job_responsibilities) if job_responsibilities else 0.0,
            "education": text_similarity(resume_education, job_education) if job_education else None,
        }

    def compute_semantic_scores(self, resume: Dict, job: Dict) -> Dict[str, float]:
        """Convert raw similarities to normalized 0-100 scores."""
        sims = self.compute_section_similarities(resume, job)
        scores = {
            "semantic": normalize_cosine_to_score(sims["overall_semantic"]),
            "skills_semantic": normalize_cosine_to_score(sims["skills"]),
            "experience_semantic": normalize_cosine_to_score(sims["experience"]),
            "projects_semantic": normalize_cosine_to_score(sims["projects"]),
        }
        if sims["education"] is not None:
            scores["education_semantic"] = normalize_cosine_to_score(sims["education"])
        else:
            scores["education_semantic"] = None
        scores["raw_similarities"] = sims
        return scores

    def analyze_project_relevance(
        self, projects: List[str], responsibilities: List[str]
    ) -> Dict[str, List[Dict]]:
        """Classify projects by relevance to job responsibilities."""
        if not projects or not responsibilities:
            return {"relevant": [], "partially_relevant": [], "low_relevance": []}

        resp_text = " ".join(responsibilities)
        relevant, partial, low = [], [], []

        for project in projects:
            if not project.strip():
                continue
            sim = text_similarity(project, resp_text)
            score = normalize_cosine_to_score(sim)
            entry = {
                "project": project,
                "similarity": round(sim, 3),
                "score": round(score, 1),
            }

            if sim >= 0.65:
                entry["reason"] = "Strong semantic alignment with job responsibilities."
                relevant.append(entry)
            elif sim >= 0.45:
                entry["reason"] = "Partial relevance to some job responsibilities."
                partial.append(entry)
            else:
                entry["reason"] = "Limited direct relevance to target role responsibilities."
                low.append(entry)

        return {
            "relevant": relevant,
            "partially_relevant": partial,
            "low_relevance": low,
        }
