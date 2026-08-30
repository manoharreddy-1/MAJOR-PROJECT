"""Skill normalization and deduplication."""
import re
from typing import List, Set

from utils.text_cleaner import normalize_skill

# Common skill aliases - extend as needed
SKILL_ALIASES = {
    "python3": "Python",
    "python 3": "Python",
    "python programming": "Python",
    "py": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "react.js": "React",
    "reactjs": "React",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "sql": "SQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "aws": "AWS",
    "amazon web services": "AWS",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "git": "Git",
    "github": "GitHub",
    "html5": "HTML",
    "html": "HTML",
    "css3": "CSS",
    "css": "CSS",
}


def normalize_skill_name(skill: str) -> str:
    """Normalize a skill name using alias mapping."""
    if not skill or not skill.strip():
        return ""
    cleaned = skill.strip()
    lower = cleaned.lower()
    if lower in SKILL_ALIASES:
        return SKILL_ALIASES[lower]
    return normalize_skill(cleaned)


def deduplicate_skills(skills: List[str]) -> List[str]:
    """Remove duplicate skills after normalization."""
    seen: Set[str] = set()
    result = []
    for skill in skills:
        normalized = normalize_skill_name(skill)
        if not normalized:
            continue
        key = normalized.lower()
        if key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def extract_skills_from_text(text: str, known_skills: List[str] = None) -> List[str]:
    """Extract skills from text using known skill list and patterns."""
    if not text:
        return []
    found = []
    text_lower = text.lower()

    # Check against known skills / aliases
    all_skills = list(SKILL_ALIASES.keys()) + list(SKILL_ALIASES.values())
    if known_skills:
        all_skills.extend(known_skills)

    for skill in set(all_skills):
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.append(normalize_skill_name(skill))

    return deduplicate_skills(found)
