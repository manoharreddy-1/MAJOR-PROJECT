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
        raw_resume_text = resume.get("raw_text", "").strip()
        resume_summary = resume.get("summary", "").strip()
        resume_skills = ", ".join(resume.get("skills", []))
        resume_experience = " ".join([str(e) for e in resume.get("experience", [])]).strip()
        resume_projects = " ".join([str(p) for p in resume.get("projects", [])]).strip()
        resume_education = " ".join([str(e) for e in resume.get("education", [])]).strip()

        # Build substantive resume content for overall semantic matching
        if raw_resume_text and len(raw_resume_text) > 150:
            resume_overall = raw_resume_text[:3500]
        else:
            resume_overall = " ".join(filter(None, [resume_summary, resume_skills, resume_experience, resume_projects])) or raw_resume_text[:500]

        job_raw = job.get("raw_text", "").strip()
        job_skills = ", ".join(job.get("required_skills", []) + job.get("preferred_skills", []))
        job_responsibilities = " ".join(job.get("responsibilities", [])).strip()
        job_education = " ".join(job.get("education", [])).strip()

        if not job_raw:
            job_raw = " ".join(
                filter(
                    None,
                    [
                        job.get("job_title", ""),
                        job_responsibilities,
                        job_skills,
                    ],
                )
            )
        job_overall = job_raw[:3500]

        # Target text for experience / project matching: use responsibilities or job overview
        job_exp_target = job_responsibilities if job_responsibilities else job_raw[:2000].strip()

        # Candidate technical work: formal experience or projects (for freshers/students)
        cand_experience = resume_experience if resume_experience else None
        cand_projects = resume_projects if resume_projects else None

        exp_similarity = (
            text_similarity(cand_experience, job_exp_target)
            if (cand_experience and job_exp_target)
            else None
        )
        proj_similarity = (
            text_similarity(cand_projects, job_exp_target)
            if (cand_projects and job_exp_target)
            else None
        )

        # Effective experience similarity: if formal experience is missing but projects exist, evaluate on projects
        if exp_similarity is not None and proj_similarity is not None:
            effective_experience_sim = max(exp_similarity, proj_similarity)
        elif exp_similarity is not None:
            effective_experience_sim = exp_similarity
        elif proj_similarity is not None:
            effective_experience_sim = proj_similarity
        else:
            effective_experience_sim = None

        # Document semantic similarity with natural range calibration
        doc_sim = text_similarity(resume_overall, job_overall)
        if doc_sim > 0.40:
            overall_semantic_sim = min(1.0, doc_sim + (doc_sim - 0.40) * 0.45)
        else:
            overall_semantic_sim = doc_sim

        # Education similarity with degree-level and field verification
        if job_education:
            edu_sim = text_similarity(resume_education, job_education) if resume_education else 0.0
            res_edu_lower = resume_education.lower()
            job_edu_lower = job_education.lower()

            has_bachelor = any(d in res_edu_lower for d in ["bachelor", "b.tech", "btech", "b.e", "be", "b.s", "bs", "bca", "undergraduate"])
            has_master = any(d in res_edu_lower for d in ["master", "m.tech", "mtech", "m.e", "me", "m.s", "ms", "mca", "postgraduate"])
            has_phd = any(d in res_edu_lower for d in ["phd", "ph.d", "doctorate"])

            req_bachelor = any(d in job_edu_lower for d in ["bachelor", "b.tech", "btech", "b.e", "b.s", "bs", "bca", "undergraduate"])
            req_master = any(d in job_edu_lower for d in ["master", "m.tech", "mtech", "m.e", "m.s", "ms", "mca", "postgraduate"])

            fields = ["computer science", "computer engineering", "information technology", "software", "engineering", "data science"]
            common_field = any((f in res_edu_lower and f in job_edu_lower) for f in fields)

            if (req_bachelor and (has_bachelor or has_master or has_phd)) or (req_master and (has_master or has_phd)):
                if common_field:
                    edu_sim = max(edu_sim, 0.95)
                else:
                    edu_sim = max(edu_sim, 0.85)
            elif (has_bachelor or has_master) and not (req_bachelor or req_master):
                edu_sim = max(edu_sim, 0.80)
        else:
            edu_sim = None

        return {
            "overall_semantic": overall_semantic_sim,
            "skills": text_similarity(resume_skills, job_skills) if job_skills else 0.0,
            "experience": effective_experience_sim,
            "projects": proj_similarity if proj_similarity is not None else 0.0,
            "education": edu_sim,
        }

    def compute_semantic_scores(self, resume: Dict, job: Dict) -> Dict[str, float]:
        """Convert raw similarities to normalized 0-100 scores."""
        sims = self.compute_section_similarities(resume, job)
        scores = {
            "semantic": normalize_cosine_to_score(sims["overall_semantic"]),
            "skills_semantic": normalize_cosine_to_score(sims["skills"]),
            "experience_semantic": (
                normalize_cosine_to_score(sims["experience"])
                if sims["experience"] is not None
                else None
            ),
            "projects_semantic": (
                normalize_cosine_to_score(sims["projects"])
                if sims["projects"] is not None
                else None
            ),
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
            p_text = f"{project.get('title', '')}: {' '.join([str(b) for b in project.get('bullets', [])])}" if isinstance(project, dict) else str(project)
            if not p_text.strip():
                continue
            sim = text_similarity(p_text, resp_text)
            score = normalize_cosine_to_score(sim)
            entry = {
                "project": p_text,
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
