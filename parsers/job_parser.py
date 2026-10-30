"""Job description parsing and requirement extraction."""
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
from utils.clean_skill_extractor import split_compound_phrase, clean_missing_skills

logger = logging.getLogger(__name__)


class JobDescriptionParser:
    """Extract structured requirements from job descriptions."""

    REQUIRED_PATTERNS = [
        r"(?i)(?:required|must have|requirements|qualifications|technical skills)[:\s]*([^\n]+)",
    ]

    PREFERRED_PATTERNS = [
        r"(?i)(?:preferred|nice to have|bonus|desired)[:\s]*([^\n]+)",
    ]

    def parse(self, text: str, title: str = None) -> Dict[str, Any]:
        """Parse job description into structured requirements."""
        multiline_text = clean_text(text, preserve_newlines=True)
        if not multiline_text:
            raise ValueError("Job description is empty.")

        detected_title = self._extract_title(multiline_text)
        alignment = self.check_role_alignment(title, detected_title, multiline_text)
        job_title = title.strip() if (title and title.strip()) else detected_title

        return {
            "raw_text": multiline_text,
            "job_title": job_title,
            "detected_title": detected_title,
            "role_alignment": alignment,
            "required_skills": self._extract_required_skills(multiline_text),
            "preferred_skills": self._extract_preferred_skills(multiline_text),
            "education": self._extract_education_requirements(multiline_text),
            "experience": self._extract_experience_requirements(multiline_text),
            "responsibilities": self._extract_responsibilities(multiline_text),
            "tools": self._extract_tools(multiline_text),
            "technologies": extract_skills_from_text(multiline_text),
            "certifications": self._extract_certifications(multiline_text),
        }

    def check_role_alignment(self, entered_title: Optional[str], detected_title: str, text: str) -> Dict[str, Any]:
        """Verify whether entered target role matches the job description content."""
        if not entered_title or not entered_title.strip():
            return {
                "is_mismatch": False,
                "entered_role": detected_title,
                "detected_role": detected_title,
                "message": ""
            }

        entered = entered_title.strip()
        e_lower = entered.lower()
        d_lower = (detected_title or "").lower()
        t_lower = (text or "").lower()

        # Domain keywords mapping
        domain_keywords = {
            "data_ai": ["machine learning", "deep learning", "nlp", "computer vision", "data scientist", "data science", "data analyst", "data engineer", "ai engineer", "ai/ml", "artificial intelligence", "ml engineer"],
            "java": ["java", "spring boot", "spring", "hibernate", "jvm", "j2ee"],
            "qa_testing": ["qa", "testing", "test", "quality assurance", "sdet", "cucumber", "selenium", "automation engineer", "automation testing"],
            "frontend": ["frontend", "front-end", "react", "angular", "vue", "javascript", "typescript", "ui/ux", "web developer", "html", "css"],
            "devops": ["devops", "cloud", "aws", "docker", "kubernetes", "sre", "infrastructure", "terraform", "azure", "gcp"],
            "python": ["python", "django", "fastapi", "flask"],
            "mobile": ["android", "ios", "flutter", "swift", "kotlin", "react native"],
            "cybersecurity": ["security", "cyber", "infosec", "penetration", "soc analyst"]
        }

        def get_domain(s: str) -> Optional[str]:
            for dom, kws in domain_keywords.items():
                if any(kw in s for kw in kws):
                    return dom
            return None

        entered_domain = get_domain(e_lower)
        detected_domain = get_domain(d_lower) or get_domain(t_lower[:1500])

        is_mismatch = False
        if entered_domain and detected_domain and entered_domain != detected_domain:
            is_mismatch = True
        elif entered_domain and not detected_domain:
            # Check if entered domain keywords are completely absent from JD text
            kws = domain_keywords[entered_domain]
            if not any(k in t_lower for k in kws):
                is_mismatch = True

        msg = ""
        if is_mismatch:
            msg = (
                f"Target Role Mismatch: You entered '{entered}', but this job description appears to be for "
                f"'{detected_title}'. Proceeding with this mismatch will severely lower your ATS match score "
                f"and generate interview questions for the wrong field."
            )

        return {
            "is_mismatch": is_mismatch,
            "entered_role": entered,
            "detected_role": detected_title,
            "message": msg
        }

    def _extract_title(self, text: str) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:5]:
            clean_line = re.sub(r"^[#*\-\s]+", "", line).strip()
            if 3 < len(clean_line) < 60 and not clean_line.lower().startswith(("http", "www", "about", "company")):
                # Check if it looks like a job title
                if any(kw in clean_line.lower() for kw in ["engineer", "developer", "architect", "analyst", "scientist", "manager", "intern", "specialist", "administrator", "lead"]):
                    return clean_line
        if lines:
            first_line = re.sub(r"^[#*\-\s]+", "", lines[0]).strip()
            if len(first_line) < 60:
                return first_line
        return "Software Engineer"

    def _extract_required_skills(self, text: str) -> List[str]:
        skills = []

        # 1. First prioritize recognized industry skills found in the text
        known_found = extract_skills_from_text(text)
        skills.extend(known_found)

        # 2. Extract and parse items from the requirements section
        section = extract_section(text, ["requirements", "required skills", "must have", "qualifications", "what you need"])
        if section:
            raw_items = re.split(r"[,|•\n;\*]|\s+-\s+|(?:^|\n)\s*[-*•]\s*", section)
            for item in raw_items:
                for sub in split_compound_phrase(item):
                    candidate = clean_skill_candidate(sub)
                    if candidate:
                        norm = normalize_skill_name(candidate)
                        if norm:
                            skills.append(norm)

        # Clean and deduplicate
        deduped = clean_missing_skills(skills)
        return deduped[:25]

    def _extract_preferred_skills(self, text: str) -> List[str]:
        skills = []
        section = extract_section(text, ["preferred", "preferred skills", "nice to have", "bonus", "good to have"])
        if section:
            # First extract known skills from the preferred section
            skills.extend(extract_skills_from_text(section))
            raw_items = re.split(r"[,|•\n;\*]|\s+-\s+|(?:^|\n)\s*[-*•]\s*", section)
            for item in raw_items:
                for sub in split_compound_phrase(item):
                    candidate = clean_skill_candidate(sub)
                    if candidate:
                        norm = normalize_skill_name(candidate)
                        if norm:
                            skills.append(norm)

        return clean_missing_skills(skills)[:15]

    def _extract_education_requirements(self, text: str) -> List[str]:
        patterns = [
            r"(?i)(bachelor['']?s?\s+(?:degree\s+)?(?:in\s+)?[\w\s,]+)",
            r"(?i)(master['']?s?\s+(?:degree\s+)?(?:in\s+)?[\w\s,]+)",
            r"(?i)(ph\.?d\.?\s+(?:in\s+)?[\w\s,]+)",
            r"(?i)(b\.?tech|b\.?e\.?|m\.?tech|m\.?e\.?)\s*[\w\s,]*",
        ]
        found = []
        for p in patterns:
            for m in re.finditer(p, text):
                cleaned = clean_text(m.group(1))
                if len(cleaned) < 60:
                    found.append(cleaned)
        return list(dict.fromkeys(found))[:5]

    def _extract_experience_requirements(self, text: str) -> List[str]:
        patterns = [
            r"(?i)(\d+\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)[^\n.]*)",
            r"(?i)(experience\s+(?:with|in)\s+[^\n.]+)",
        ]
        found = []
        for p in patterns:
            for m in re.finditer(p, text):
                cleaned = clean_text(m.group(1))
                if len(cleaned) < 80:
                    found.append(cleaned)
        return list(dict.fromkeys(found))[:5]

    def _extract_responsibilities(self, text: str) -> List[str]:
        section = extract_section(text, ["responsibilities", "duties", "what you'll do", "role overview", "key responsibilities"])
        source = section if section else text

        items = re.split(r"\n\s*[•\-\*]\s*|\n\s*\d+\.\s*", source)
        cleaned = [clean_text(i) for i in items if 15 < len(i.strip()) < 200]
        return cleaned[:15]

    def _extract_tools(self, text: str) -> List[str]:
        return extract_skills_from_text(text)[:20]

    def _extract_certifications(self, text: str) -> List[str]:
        patterns = [
            r"(?i)(?:certified|certification)\s+(?:in\s+)?([^\n,.]+)",
            r"(?i)(AWS|Azure|GCP|PMP|CISSP|CKA|Oracle\s+Certified)\s*(?:certified|certification)?",
        ]
        found = []
        for p in patterns:
            for m in re.finditer(p, text):
                cleaned = clean_text(m.group(0))
                if len(cleaned) < 50:
                    found.append(cleaned)
        return list(dict.fromkeys(found))[:5]
