"""Text cleaning utilities."""
import re
import unicodedata


def clean_text(text: str) -> str:
    """Normalize whitespace and remove control characters."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_skill(skill: str) -> str:
    """Basic skill normalization."""
    if not skill:
        return ""
    skill = skill.strip()
    skill = re.sub(r"\s+", " ", skill)
    # Title case for multi-word skills, preserve acronyms
    if skill.isupper() or len(skill) <= 4:
        return skill.upper() if skill.isupper() else skill.title()
    return skill.title()


def extract_section(text: str, section_keywords: list) -> str:
    """Extract text following a section header."""
    pattern = r"(?i)(" + "|".join(re.escape(k) for k in section_keywords) + r")\s*[:\-]?\s*"
    match = re.search(pattern, text)
    if not match:
        return ""
    start = match.end()
    next_section = re.search(
        r"\n\s*(?:EDUCATION|EXPERIENCE|SKILLS|PROJECTS|CERTIFICATIONS|ACHIEVEMENTS|SUMMARY|OBJECTIVE)\s",
        text[start:],
        re.IGNORECASE,
    )
    end = start + next_section.start() if next_section else len(text)
    return clean_text(text[start:end])


def truncate_text(text: str, max_length: int = 8000) -> str:
    """Truncate text for embedding."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
