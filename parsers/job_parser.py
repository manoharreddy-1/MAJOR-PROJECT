"""Job description parsing and requirement extraction."""
import logging
import re
from typing import Any, Dict, List

from utils.text_cleaner import clean_text, extract_section
from utils.skill_normalizer import deduplicate_skills, extract_skills_from_text

logger = logging.getLogger(__name__)


class JobDescriptionParser:
    """Extract structured requirements from job descriptions."""

    REQUIRED_PATTERNS = [
        r"(?i)required[\s:]*([^\n]+)",
        r"(?i)must have[\s:]*([^\n]+)",
        r"(?i)requirements[\s:]*([^\n]+)",
        r"(?i)qualifications[\s:]*([^\n]+)",
    ]

    PREFERRED_PATTERNS = [
        r"(?i)preferred[\s:]*([^\n]+)",
        r"(?i)nice to have[\s:]*([^\n]+)",
        r"(?i)bonus[\s:]*([^\n]+)",
    ]

    def parse(self, text: str, title: str = None) -> Dict[str, Any]:
        """Parse job description into structured requirements."""
        text = clean_text(text)
        if not text:
            raise ValueError("Job description is empty.")

        return {
            "raw_text": text,
            "job_title": title or self._extract_title(text),
            "required_skills": self._extract_required_skills(text),
            "preferred_skills": self._extract_preferred_skills(text),
            "education": self._extract_education_requirements(text),
            "experience": self._extract_experience_requirements(text),
            "responsibilities": self._extract_responsibilities(text),
            "tools": self._extract_tools(text),
            "technologies": extract_skills_from_text(text),
            "certifications": self._extract_certifications(text),
        }

    def _extract_title(self, text: str) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:5]:
            if len(line) < 80 and not line.startswith(("http", "www")):
                return line
        return "Target Role"

    def _extract_required_skills(self, text: str) -> List[str]:
        skills = []
        
        # Try to extract the entire requirements section first
        section = extract_section(text, ["requirements", "required skills", "must have", "qualifications"])
        if section:
            skills.extend(re.split(r"[,|•\n;\-\*]", section))
        else:
            for pattern in self.REQUIRED_PATTERNS:
                for match in re.finditer(pattern, text):
                    chunk = match.group(1)
                    skills.extend(re.split(r"[,|•;\-\*]", chunk))
                    
        # Always supplement with explicitly known skills extracted from the whole text
        skills.extend(extract_skills_from_text(text))
        
        # Clean each skill from common prefixes and filter out long texts/sentences
        cleaned_skills = []
        for s in skills:
            s_clean = s.strip()
            # Remove leading list bullets and numbers
            s_clean = re.sub(r"^[•\-\*\d\.\s]+", "", s_clean)
            # Remove header prefixes
            s_clean = re.sub(r"(?i)^(skills|required|preferred|must have|nice to have|experience in|knowledge of|working knowledge of)\s*[:\-]?\s*", "", s_clean)
            s_clean = s_clean.strip()
            if s_clean and len(s_clean) < 40 and not re.search(r"\b(responsibilities|duties|description|requirements|preferred)\b", s_clean, re.I):
                cleaned_skills.append(s_clean)
                
        return deduplicate_skills(cleaned_skills)[:30]

    def _extract_preferred_skills(self, text: str) -> List[str]:
        skills = []
        
        # Try to extract the entire preferred section first
        section = extract_section(text, ["preferred", "preferred skills", "nice to have", "bonus"])
        if section:
            skills.extend(re.split(r"[,|•\n;\-\*]", section))
        else:
            for pattern in self.PREFERRED_PATTERNS:
                for match in re.finditer(pattern, text):
                    chunk = match.group(1)
                    skills.extend(re.split(r"[,|•;\-\*]", chunk))
        
        cleaned_skills = []
        for s in skills:
            s_clean = s.strip()
            s_clean = re.sub(r"^[•\-\*\d\.\s]+", "", s_clean)
            s_clean = re.sub(r"(?i)^(skills|required|preferred|must have|nice to have|experience in|knowledge of|working knowledge of)\s*[:\-]?\s*", "", s_clean)
            s_clean = s_clean.strip()
            if s_clean and len(s_clean) < 40 and not re.search(r"\b(responsibilities|duties|description|requirements|preferred)\b", s_clean, re.I):
                cleaned_skills.append(s_clean)
                
        return deduplicate_skills(cleaned_skills)[:20]

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
                found.append(clean_text(m.group(1)))
        return list(dict.fromkeys(found))[:5]

    def _extract_experience_requirements(self, text: str) -> List[str]:
        patterns = [
            r"(?i)(\d+\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)[^\n.]*)",
            r"(?i)(experience\s+(?:with|in)\s+[^\n.]+)",
        ]
        found = []
        for p in patterns:
            for m in re.finditer(p, text):
                found.append(clean_text(m.group(1)))
        return list(dict.fromkeys(found))[:5]

    def _extract_responsibilities(self, text: str) -> List[str]:
        section_match = re.search(
            r"(?i)(?:responsibilities|duties|what you['']ll do|role)[:\s]*(.+?)(?:\n\n|requirements|qualifications|$)",
            text,
            re.DOTALL,
        )
        if section_match:
            section = section_match.group(1)
        else:
            section = text

        items = re.split(r"\n\s*[•\-\*]\s*|\n\s*\d+\.\s*", section)
        return [clean_text(i) for i in items if len(i.strip()) > 15][:15]

    def _extract_tools(self, text: str) -> List[str]:
        return extract_skills_from_text(text)[:20]

    def _extract_certifications(self, text: str) -> List[str]:
        patterns = [
            r"(?i)(?:certified|certification)\s+(?:in\s+)?([^\n,.]+)",
            r"(?i)(AWS|Azure|GCP|PMP|CISSP|CKA)\s*(?:certified|certification)?",
        ]
        found = []
        for p in patterns:
            for m in re.finditer(p, text):
                found.append(clean_text(m.group(0)))
        return list(dict.fromkeys(found))[:5]
