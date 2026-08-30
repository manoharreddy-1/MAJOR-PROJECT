"""Structured prompts for generative AI with hallucination control."""
import json
from typing import Any, Dict, List


SYSTEM_SAFETY = """You are an AI career assistant. Follow these rules strictly:
- Do NOT invent candidate information (experience, projects, certifications, skills, achievements).
- Only use information present in the provided resume and job description.
- If information is missing, explicitly state that it is missing.
- Do NOT create fake employment history or fake certifications.
- Do NOT claim guaranteed employment.
- If the candidate lacks a skill, suggest learning it before adding it to their resume.
- Respond ONLY with valid JSON matching the requested schema.
- Do not include markdown code fences in your response."""


def resume_improvement_prompt(
    resume: Dict,
    job: Dict,
    matched_skills: List[str],
    missing_skills: List[str],
    weak_sections: List[str],
) -> str:
    return f"""{SYSTEM_SAFETY}

Generate resume improvement suggestions based on the following data.

RESUME SUMMARY:
{resume.get('summary', 'Not provided')}

MATCHED SKILLS: {', '.join(matched_skills) or 'None'}
MISSING SKILLS: {', '.join(missing_skills) or 'None'}
WEAK SECTIONS: {', '.join(weak_sections) or 'None'}

JOB TITLE: {job.get('job_title', 'Not specified')}
JOB REQUIREMENTS: {', '.join(job.get('required_skills', []))}

Return JSON with this exact structure:
{{
    "general_suggestions": ["suggestion1", "suggestion2"],
    "section_suggestions": [
        {{"section": "skills", "suggestion": "...", "priority": "high|medium|low"}}
    ],
    "skill_highlighting": ["skill to emphasize and why"],
    "achievement_wording": ["improved achievement phrasing based on actual resume content"],
    "project_improvements": ["project description improvement based on actual projects"],
    "ats_wording": ["ATS-friendly phrasing suggestions"],
    "disclaimer": "Suggestions are based on your actual resume. Do not add skills or experience you do not have."
}}"""


def interview_questions_prompt(
    resume: Dict,
    job: Dict,
    target_role: str,
    missing_skills: List[str],
) -> str:
    projects = resume.get("projects", [])[:3]
    skills = resume.get("skills", [])[:10]

    return f"""{SYSTEM_SAFETY}

Generate interview questions for this candidate and role.

TARGET ROLE: {target_role}
CANDIDATE SKILLS: {', '.join(skills)}
PROJECTS: {'; '.join(projects) if projects else 'Not provided'}
MISSING SKILLS: {', '.join(missing_skills) or 'None'}
JOB REQUIREMENTS: {', '.join(job.get('required_skills', []))}
RESPONSIBILITIES: {'; '.join(job.get('responsibilities', [])[:5])}

Generate specific, relevant questions (not generic). Base technical questions on actual resume skills and projects.

Return JSON:
{{
    "technical": [{{"question": "...", "topic": "...", "difficulty": "easy|medium|hard"}}],
    "resume_based": [{{"question": "...", "focus": "..."}}],
    "project_based": [{{"question": "...", "project_reference": "..."}}],
    "behavioral": [{{"question": "...", "competency": "..."}}],
    "skill_gap": [{{"question": "...", "skill": "...", "learning_focus": "..."}}]
}}"""


def sample_answer_prompt(question: str, resume: Dict, category: str) -> str:
    return f"""{SYSTEM_SAFETY}

Provide a concise, interview-friendly sample answer for this question.
Use ONLY information from the candidate's resume. Use placeholders like [Your Project Name] if specific details are missing.
Do NOT fabricate personal experience.

QUESTION: {question}
CATEGORY: {category}
RESUME SKILLS: {', '.join(resume.get('skills', [])[:10])}
EXPERIENCE: {'; '.join(resume.get('experience', [])[:2]) or 'Not provided'}

Return JSON:
{{
    "answer": "concise interview answer (2-4 sentences)",
    "tips": ["tip1", "tip2"],
    "based_on_resume": true,
    "placeholders_used": ["list any placeholders used"]
}}"""


def roadmap_prompt(
    job: Dict,
    resume: Dict,
    matched_skills: List[str],
    partial_skills: List[str],
    missing_skills: List[str],
    strengths: List[str],
) -> str:
    return f"""{SYSTEM_SAFETY}

Create a personalized interview preparation roadmap.

TARGET ROLE: {job.get('job_title', 'Target Role')}
MATCHED SKILLS: {', '.join(matched_skills)}
PARTIALLY MATCHED: {', '.join(partial_skills)}
MISSING SKILLS: {', '.join(missing_skills)}
STRENGTHS: {', '.join(strengths)}
EXPERIENCE: {'; '.join(resume.get('experience', [])[:2]) or 'Limited'}

Return JSON:
{{
    "roadmap": [
        {{
            "priority": "HIGH|MEDIUM|LOW",
            "topic": "...",
            "reason": "...",
            "learning_objective": "...",
            "estimated_week": 1,
            "stage": "Foundation|Skill Building|Practice|Review"
        }}
    ],
    "interview_practice_phase": {{
        "focus_areas": ["..."],
        "recommended_activities": ["..."]
    }},
    "summary": "Brief personalized summary"
}}"""
