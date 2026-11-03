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

    def _extract_academics(self, text: str) -> Dict[str, Optional[float]]:
        """Extract CGPA, 10th percentage, and 12th/Intermediate percentage from resume text."""
        return {
            "cgpa": self._extract_cgpa(text),
            "tenth_pct": self._extract_tenth_marks(text),
            "twelfth_pct": self._extract_twelfth_marks(text),
        }

    def _extract_cgpa(self, text: str) -> Optional[float]:
        """Extract CGPA/GPA value from text (normalized to 10 scale if <= 10)."""
        if not text:
            return None

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        degree_kw = r"(?i)\b(?:b\.?tech|b\.?e\.|bachelor|undergraduate|degree|bca|mca|m\.?tech)\b"
        for line in lines:
            if re.search(degree_kw, line):
                m_cgpa = re.search(r"\b([0-9]\.[0-9]{1,2})\b\s*(?:cgpa|gpa|/\s*10)?", line, re.I)
                if m_cgpa:
                    try:
                        val = float(m_cgpa.group(1))
                        if 1.0 <= val <= 10.0:
                            return round(val, 2)
                    except ValueError:
                        pass
                m_pct = re.search(r"\b([0-9]{2}(?:\.[0-9]+)?)\s*%", line)
                if m_pct:
                    try:
                        pct = float(m_pct.group(1))
                        if 40.0 <= pct <= 100.0:
                            return round(pct / 9.5, 2)
                    except ValueError:
                        pass

        patterns = [
            r"(?i)(?:cgpa|gpa|grade\s*point)\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)(?:\s*/\s*(?:10|4))?",
            r"(?i)\b([0-9]\.[0-9]{1,2})\s*(?:/\s*10)?\s*(?:cgpa|gpa)\b",
            r"(?i)\b([0-9]\.[0-9]{1,2})\s*/\s*10\.0?",
            r"(?i)(?:score|pointer|aggregate)\s*[:=-]?\s*([0-9]+\.[0-9]+)",
        ]

        for pat in patterns:
            m = re.search(pat, text)
            if m:
                try:
                    val = float(m.group(1))
                    if "/ 4" in m.group(0) or "/4" in m.group(0):
                        return round((val / 4.0) * 10.0, 2)
                    if 1.0 <= val <= 10.0:
                        return round(val, 2)
                    elif 40.0 <= val <= 100.0:
                        return round(val / 9.5, 2)
                except ValueError:
                    pass
        return None

    def _extract_tenth_marks(self, text: str) -> Optional[float]:
        """Extract 10th standard / SSC / Secondary school percentage."""
        if not text:
            return None

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        tenth_kw_pat = r"(?i)\b(?:10th|class\s*10\b|class\s*x\b|x\s*class\b|ssc\b|s\.s\.c\b|matriculation|secondary\s*school(?:\s*certificate)?|high\s*school)\b"

        # 1. Line-by-line inspection (table rows or bullet points)
        for line in lines:
            if re.search(tenth_kw_pat, line) and not re.search(r"(?i)\b(?:12th|intermediate|inter\b|xii\b|hsc|\+2)\b", line):
                # Marks out of 600 or 500
                m_marks = re.search(r"\b([0-9]{3})\s*/\s*(?:600|500)", line)
                if m_marks:
                    total = 600.0 if "600" in line else 500.0
                    return round((float(m_marks.group(1)) / total) * 100.0, 1)

                # Explicit percentage e.g. 95% or 95.5%
                m_pct = re.search(r"\b([0-9]{2}(?:\.[0-9]+)?)\s*%", line)
                if m_pct:
                    val = float(m_pct.group(1))
                    if 35.0 <= val <= 100.0:
                        return round(val, 1)

                # CGPA/GPA e.g. 9.8 CGPA, 10.0 CGPA, 10 CGPA, 9.8 / 10
                m_cgpa = re.search(r"\b([0-9]+(?:\.[0-9]+)?)\s*(?:cgpa|gpa|/\s*10)\b", line, re.I)
                if m_cgpa:
                    val = float(m_cgpa.group(1))
                    if val <= 10.0:
                        return round(val * 9.5 if val < 10.0 else 95.0, 1)
                    elif 35.0 <= val <= 100.0:
                        return round(val, 1)

                # Standalone numbers at end of line (e.g. table column)
                tokens = re.findall(r"\b([0-9]+(?:\.[0-9]+)?)\b", line)
                for tok in reversed(tokens):
                    try:
                        v = float(tok)
                        if 1990 <= v <= 2030:
                            continue
                        if 1.0 <= v <= 10.0:
                            return round(v * 9.5 if v < 10.0 else 95.0, 1)
                        if 35.0 <= v <= 100.0:
                            return round(v, 1)
                    except ValueError:
                        pass

        # 2. General regex patterns across text
        patterns = [
            r"(?i)(?:10th|class\s*x\b|ssc|matriculation|secondary(?:\s*school)?)\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%",
            r"(?i)(?:10th|class\s*x\b|ssc|matriculation|secondary(?:\s*school)?)[^\n\r]{1,50}?([0-9]{2}(?:\.[0-9]+)?)\s*%",
            r"(?i)([0-9]{2}(?:\.[0-9]+)?)\s*%\s*(?:in\s*)?(?:10th|class\s*x\b|ssc|matriculation|secondary)",
            r"(?i)(?:10th|class\s*x\b|ssc)\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cgpa|gpa|/10)",
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                try:
                    val = float(m.group(1))
                    if val <= 10.0:
                        return round(val * 9.5 if val < 10.0 else 95.0, 1)
                    if 35.0 <= val <= 100.0:
                        return round(val, 1)
                except ValueError:
                    pass
        return None

    def _extract_twelfth_marks(self, text: str) -> Optional[float]:
        """Extract 12th standard / HSC / Intermediate / Senior secondary percentage."""
        if not text:
            return None

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        twelfth_kw_pat = r"(?i)\b(?:12th|class\s*12\b|class\s*xii\b|xii\s*class\b|xii\b|intermediate|inter\b|hsc|senior\s*secondary|puc|plus\s*two|\+2\b|10\+2\b|junior\s*college)\b"

        # 1. Line-by-line inspection (table rows or bullet points)
        for line in lines:
            if re.search(twelfth_kw_pat, line) and not re.search(r"(?i)\b(?:10th|ssc|class\s*x\b)\b", line):
                # Marks out of 1000 e.g. 950/1000 or 950 / 1000
                m_marks = re.search(r"\b([0-9]{3})\s*/\s*1000", line)
                if m_marks:
                    return round(float(m_marks.group(1)) / 10.0, 1)

                # Marks out of 500 or 600
                m_marks2 = re.search(r"\b([0-9]{3})\s*/\s*(?:500|600)", line)
                if m_marks2:
                    tot = 600.0 if "600" in line else 500.0
                    return round((float(m_marks2.group(1)) / tot) * 100.0, 1)

                # Explicit percentage e.g. 95% or 95.5%
                m_pct = re.search(r"\b([0-9]{2}(?:\.[0-9]+)?)\s*%", line)
                if m_pct:
                    val = float(m_pct.group(1))
                    if 35.0 <= val <= 100.0:
                        return round(val, 1)

                # CGPA/GPA e.g. 9.5 CGPA, 10.0 CGPA, 9.5 / 10
                m_cgpa = re.search(r"\b([0-9]+(?:\.[0-9]+)?)\s*(?:cgpa|gpa|/\s*10)\b", line, re.I)
                if m_cgpa:
                    val = float(m_cgpa.group(1))
                    if val <= 10.0:
                        return round(val * 9.5 if val < 10.0 else 95.0, 1)
                    elif 35.0 <= val <= 100.0:
                        return round(val, 1)

                # Standalone numbers at end of line (e.g. table column)
                tokens = re.findall(r"\b([0-9]+(?:\.[0-9]+)?)\b", line)
                for tok in reversed(tokens):
                    try:
                        v = float(tok)
                        if 1990 <= v <= 2030:
                            continue
                        if 1.0 <= v <= 10.0:
                            return round(v * 9.5 if v < 10.0 else 95.0, 1)
                        if 35.0 <= v <= 100.0:
                            return round(v, 1)
                    except ValueError:
                        pass

        # 2. General regex patterns across text
        patterns = [
            r"(?i)(?:12th|class\s*xii\b|hsc|intermediate|inter\b|senior\s*secondary|puc|pre[- ]university)\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%",
            r"(?i)(?:12th|class\s*xii\b|hsc|intermediate|inter\b|senior\s*secondary|puc)[^\n\r]{1,50}?([0-9]{2}(?:\.[0-9]+)?)\s*%",
            r"(?i)([0-9]{2}(?:\.[0-9]+)?)\s*%\s*(?:in\s*)?(?:12th|class\s*xii\b|hsc|intermediate|inter\b|senior\s*secondary)",
            r"(?i)(?:12th|class\s*xii\b|hsc|intermediate|inter\b)\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cgpa|gpa|/10)",
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                try:
                    val = float(m.group(1))
                    if val <= 10.0:
                        return round(val * 9.5 if val < 10.0 else 95.0, 1)
                    if 35.0 <= val <= 100.0:
                        return round(val, 1)
                except ValueError:
                    pass
        return None
