"""Resume information extraction using NLP and regex."""
import logging
import re
from typing import Any, Dict, List, Optional

from utils.text_cleaner import clean_text, extract_section
from utils.skill_normalizer import (
    clean_skill_candidate,
    deduplicate_skills,
    extract_skills_from_text,
    normalize_skill_name,
)

logger = logging.getLogger(__name__)

# Regex patterns for structured fields
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)
URL_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+")

SECTION_KEYWORDS = {
    "skills": ["technical skills", "skills", "core competencies", "technologies", "tech stack", "tools & technologies"],
    "experience": ["experience", "work experience", "employment", "professional experience", "internship", "internships"],
    "education": ["education", "academic background", "academics", "qualification", "qualifications"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "achievements": ["achievements", "awards", "honors", "accomplishments"],
}


class ResumeParser:
    """Extract structured information from resume text."""

    def __init__(self, ner_model=None):
        self.ner_model = ner_model

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse resume text into structured fields."""
        multiline_text = clean_text(text, preserve_newlines=True)
        if not multiline_text:
            raise ValueError("Resume text is empty.")

        result = {
            "raw_text": multiline_text,
            "name": self._extract_name(multiline_text),
            "email": self._extract_email(multiline_text),
            "phone": self._extract_phone(multiline_text),
            "urls": URL_PATTERN.findall(multiline_text),
            "skills": self._extract_skills(multiline_text),
            "experience": self._extract_experience(multiline_text),
            "education": self._extract_education(multiline_text),
            "projects": self._extract_projects(multiline_text),
            "certifications": self._extract_certifications(multiline_text),
            "achievements": self._extract_achievements(multiline_text),
            "technologies": [],
            "summary": self._extract_summary(multiline_text),
            "academics": self._extract_academics(multiline_text),
        }

        # Extract technologies from skills, projects, and experience
        tech_text = " ".join(result["skills"]) + " " + " ".join(result["projects"]) + " " + " ".join(result["experience"])
        result["technologies"] = extract_skills_from_text(tech_text, result["skills"])

        # Enrich with NER if available and name is not yet extracted
        if self.ner_model and not result.get("name"):
            try:
                entities = self.ner_model.extract_entities(multiline_text[:250])
                result["ner_entities"] = entities
                if entities.get("persons"):
                    result["name"] = entities["persons"][0]
            except Exception as exc:
                logger.warning("NER extraction failed: %s", exc)

        return result

    def _extract_email(self, text: str) -> Optional[str]:
        match = EMAIL_PATTERN.search(text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        match = PHONE_PATTERN.search(text)
        return match.group(0) if match else None

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name cleanly from header lines."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            return None
        for line in lines[:5]:
            if EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line) or URL_PATTERN.search(line):
                # If this line contains the name concatenated with contact info (e.g. 'John Doe | john@email.com')
                candidate = re.split(r"[|•\t]|(?:\s+-\s+)", line)[0].strip()
                candidate = EMAIL_PATTERN.sub("", candidate)
                candidate = PHONE_PATTERN.sub("", candidate)
                candidate = URL_PATTERN.sub("", candidate).strip(" ,.-|:")
                if 2 <= len(candidate.split()) <= 4 and len(candidate) < 40:
                    if not any(kw in candidate.lower() for kw in ["resume", "curriculum", "cv", "portfolio", "github", "linkedin", "http", "www."]):
                        return candidate
                continue
            if len(line.split()) <= 5 and len(line) < 60:
                if not any(kw in line.lower() for kw in ["resume", "curriculum", "cv", "portfolio", "github", "linkedin", "http", "www."]):
                    return line

        # Final fallback
        first = re.split(r"[|•\t]|(?:\s+-\s+)", lines[0])[0].strip()
        first = EMAIL_PATTERN.sub("", first)
        first = PHONE_PATTERN.sub("", first)
        first = URL_PATTERN.sub("", first).strip(" ,.-|:")
        if 2 <= len(first.split()) <= 5 and len(first) < 40:
            return first
        return "Candidate"

    def _extract_skills(self, text: str) -> List[str]:
        skills = []
        section = extract_section(text, SECTION_KEYWORDS["skills"])
        source = section if section else text

        # 1. Direct standard extraction across the section
        skills.extend(extract_skills_from_text(source))

        # 2. Parse subcategory items (e.g. Languages: Java, Python; Web: React, Node)
        raw_skills = re.split(r"[,|•\n;/\\]", source)
        for s in raw_skills:
            # If line has category prefix like 'Languages: Java', strip the category prefix
            if ":" in s:
                s = s.split(":", 1)[1]
            candidate = clean_skill_candidate(s)
            if candidate:
                norm = normalize_skill_name(candidate)
                if norm:
                    skills.append(norm)

        # 3. Also supplement with skills extracted from projects section
        projects_section = extract_section(text, SECTION_KEYWORDS["projects"])
        if projects_section:
            skills.extend(extract_skills_from_text(projects_section))

        return deduplicate_skills(skills)[:40]

    def _extract_experience(self, text: str) -> List[str]:
        section = extract_section(text, SECTION_KEYWORDS["experience"])
        if not section:
            return []
        entries = re.split(r"\n(?=[A-Z][^a-z]{0,3}[A-Za-z])", section)
        return [clean_text(e) for e in entries if len(e.strip()) > 20][:10]

    def _extract_education(self, text: str) -> List[str]:
        section = extract_section(text, SECTION_KEYWORDS["education"])
        if not section:
            return []
        entries = re.split(r"\n(?=[A-Z])", section)
        return [clean_text(e) for e in entries if len(e.strip()) > 10][:5]

    def _extract_projects(self, text: str) -> List[str]:
        section = extract_section(text, SECTION_KEYWORDS["projects"])
        if not section:
            return []
        entries = re.split(r"\n(?=[•\-\*]|\d+\.)", section)
        return [clean_text(e.lstrip("•-* ")) for e in entries if len(e.strip()) > 15][:10]

    def _extract_certifications(self, text: str) -> List[str]:
        section = extract_section(text, SECTION_KEYWORDS["certifications"])
        if not section:
            return []
        items = re.split(r"[,|•\n;]", section)
        return [clean_text(i) for i in items if len(i.strip()) > 3][:10]

    def _extract_achievements(self, text: str) -> List[str]:
        section = extract_section(text, SECTION_KEYWORDS["achievements"])
        if not section:
            return []
        items = re.split(r"[,|•\n;]", section)
        return [clean_text(i) for i in items if len(i.strip()) > 5][:10]

    def _extract_summary(self, text: str) -> str:
        summary = extract_section(text, ["summary", "objective", "profile", "about", "career objective", "professional summary"])
        if summary:
            return summary[:1000]
        return text[:500]

    def _extract_academics(self, text: str) -> Dict[str, Any]:
        """Extract CGPA, 10th percentage, 12th percentage, and standardized academic profile."""
        if not hasattr(self, "academic_parser") or self.academic_parser is None:
            from parsers.academic_parser import AcademicParser
            self.academic_parser = AcademicParser()
        return self.academic_parser.extract_academics(text, fallback_to_ai=False)

    def _extract_cgpa(self, text: str) -> Optional[float]:
        """Extract CGPA/GPA value from text (normalized to 10 scale if <= 10)."""
        res = self._extract_academics(text)
        return res.get("cgpa")

    def _extract_tenth_marks(self, text: str) -> Optional[float]:
        """Extract 10th standard / SSC / Secondary school percentage."""
        res = self._extract_academics(text)
        return res.get("tenth_pct")

    def _extract_twelfth_marks(self, text: str) -> Optional[float]:
        """Extract 12th standard / HSC / Intermediate / Senior secondary percentage."""
        res = self._extract_academics(text)
        return res.get("twelfth_pct")
