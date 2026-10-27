"""Text cleaning utilities."""
import re
import unicodedata


def clean_text(text: str, preserve_newlines: bool = False) -> str:
    """Normalize whitespace and remove control characters.

    If preserve_newlines is True, newlines are preserved while horizontal
    whitespace is collapsed.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    if preserve_newlines:
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_skill(skill: str) -> str:
    """Basic skill normalization."""
    if not skill:
        return ""
    skill = skill.strip()
    skill = re.sub(r"\s+", " ", skill)
    # Strip leading/trailing punctuation, bullets, or symbols
    skill = re.sub(r"^[\s&+\-•*.,/:;\\#]+", "", skill).strip()
    skill = re.sub(r"[\s&+\-•*.,/:;\\#]+$", "", skill).strip()
    if not skill:
        return ""
    # Title case for multi-word skills, preserve acronyms
    if skill.isupper() or len(skill) <= 4:
        return skill.upper() if skill.isupper() else skill.title()
    return skill.title()


def extract_section(text: str, section_keywords: list) -> str:
    """Extract text following a section header up to the next major section."""
    if not text or not section_keywords:
        return ""
    pattern = r"(?i)(?:^|\n|\r|\b)(" + "|".join(re.escape(k) for k in section_keywords) + r")\s*[:\-]?\s*"
    match = re.search(pattern, text)
    if not match:
        return ""
    start = match.end()
    next_section = re.search(
        r"(?:\n|\r)\s*(?:EDUCATION|EXPERIENCE|SKILLS|TECHNICAL\s+SKILLS|PROJECTS|CERTIFICATIONS|ACHIEVEMENTS|SUMMARY|OBJECTIVE|RESPONSIBILITIES|REQUIREMENTS|QUALIFICATIONS)\b",
        text[start:],
        re.IGNORECASE,
    )
    end = start + next_section.start() if next_section else len(text)
    return text[start:end].strip()


def truncate_text(text: str, max_length: int = 8000) -> str:
    """Truncate text for embedding."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
