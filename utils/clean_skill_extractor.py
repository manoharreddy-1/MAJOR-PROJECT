"""Clean, atomic, canonical skill extraction and normalization pipeline.

Solves noisy extraction, sentence fragments, compound phrases, filler prefixes,
broken tokens, non-skills blacklist, and deduplication against matched skills.
"""
import logging
import re
from typing import List, Set, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Non-skills, filler words, junk phrases, and workplace environment noise
NON_SKILL_BLACKLIST: Set[str] = {
    "it",
    "learn",
    "learn.",
    "good to have",
    "nice to have",
    "must have",
    "plus",
    "bonus",
    "paced environment",
    "fast-paced environment",
    "fast paced environment",
    "environment",
    "academic or personal projects",
    "projects",
    "responsibilities",
    "requirements",
    "qualifications",
    "preferred qualifications",
    "required qualifications",
    "duties",
    "etc",
    "and",
    "or",
    "with",
    "candidate",
    "track record",
    "strong problem",  # partial broken fragment
    "problem",
    "solving",
    "degree",
    "bachelor",
    "bachelors",
    "master",
    "masters",
    "phd",
    "years of experience",
    "years experience",
    "work experience",
    "communication skills",
    "excellent communication",
    "team player",
    "fast learner",
    "self motivated",
    "& soft skills",
    "soft skills",
    "soft skill",
}

# Prefixes to strip from raw skill candidates
FILLER_PREFIX_PATTERNS = [
    r"^(?:exposure\s+to|familiarity\s+with|academic\s+or\s+personal\s+projects\s+in)\s*",
    r"^(?:hands[- ]on\s+(?:experience\s+)?(?:with|in)|experience\s+(?:with|in|of))\s*",
    r"^(?:working\s+knowledge\s+(?:with|in|of)|knowledge\s+(?:with|in|of))\s*",
    r"^(?:strong\s+)?proficien(?:cy|t)\s+(?:with|in)\s*",
    r"^(?:understanding|expertise)\s+(?:of|with|in)\s*",
    r"^(?:strong\s+)?(?:skills\s+in|knowledge\s+of)\s*",
    r"^(?:good\s+to\s+have|nice\s+to\s+have|must\s+have|preferred|required)\s*:\s*",
    r"^(?:proven\s+track\s+record\s+in|demonstrated\s+experience\s+in)\s*",
]

# Canonical casing & alias normalization dictionary
CANONICAL_SKILL_MAP: Dict[str, str] = {
    # AI / ML / Data Science
    "numpy": "NumPy",
    "pandas": "Pandas",
    "scikit": "scikit-learn",
    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "llms": "LLMs",
    "llm": "LLMs",
    "exposure to llms": "LLMs",
    "large language models": "LLMs",
    "generative ai": "Generative AI",
    "gen ai": "Generative AI",
    "genai": "Generative AI",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "ai/ml": "AI/ML",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "dsa": "Data Structures & Algorithms",
    "data structures & algorithms": "Data Structures & Algorithms",
    "data structures and algorithms": "Data Structures & Algorithms",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "hadoop": "Hadoop",

    # Core Engineering & Architecture
    "object-oriented programming": "Object-Oriented Programming",
    "object oriented programming": "Object-Oriented Programming",
    "oriented programming": "Object-Oriented Programming",  # Broken fragment repair
    "oop": "Object-Oriented Programming",
    "oops": "Object-Oriented Programming",
    "system design": "System Design",
    "design patterns": "Design Patterns",
    "microservices": "Microservices",
    "microservices architecture": "Microservices",
    "rest apis": "REST APIs",
    "rest api": "REST APIs",
    "restful apis": "REST APIs",
    "restful api": "REST APIs",
    "rest": "REST APIs",
    "graphql": "GraphQL",
    "websockets": "WebSockets",
    "agile": "Agile/Scrum",
    "scrum": "Agile/Scrum",
    "problem solving": "Problem Solving",
    "analytical skills": "Analytical Skills",
    "problem solving and analytical skills": "Problem Solving",

    # Programming Languages
    "python": "Python",
    "python3": "Python",
    "java": "Java",
    "core java": "Java",
    "c": "C",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    ".net": ".NET",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "scala": "Scala",
    "r": "R",
    "sql": "SQL",

    # Frameworks & Web
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "hibernate": "Hibernate",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "next.js": "Next.js",
    "angular": "Angular",
    "vue": "Vue.js",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",

    # Databases & Caching
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "oracle": "Oracle DB",
    "elasticsearch": "Elasticsearch",

    # Cloud & DevOps
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "ci/cd": "CI/CD",
    "jenkins": "Jenkins",
    "linux": "Linux",
    "bash": "Bash/Shell",
    "kafka": "Apache Kafka",
}


def strip_filler_words_and_punctuation(text: str) -> str:
    """Strip leading bullets, filler prefixes, trailing punctuation, and whitespace."""
    if not text:
        return ""

    cleaned = text.strip()

    # Remove leading bullets, numbers, dashes, quotes
    cleaned = re.sub(r"^[\s•\-\*\d\.\:\;\,\(\)\[\]\/\"\'\\]+", "", cleaned)

    # Strip recognized filler prefixes
    for pat in FILLER_PREFIX_PATTERNS:
        cleaned = re.sub(pat, "", cleaned, flags=re.I).strip()

    # Remove trailing punctuation, trailing periods, semicolons, commas, parenthesis
    cleaned = re.sub(r"[\s•\-\*\:\;\,\.\/\(\)\[\]\"\'\\]+$", "", cleaned)
    return cleaned.strip()


def repair_broken_fragment(text: str) -> Optional[str]:
    """Repair known broken grammatical or cut-off fragments."""
    lower = text.lower().strip()

    if lower in ("oriented programming", "oriented programming."):
        return "Object-Oriented Programming"

    if lower in ("scikit", "scikit.", "scikit learn"):
        return "scikit-learn"

    if lower in ("exposure to llms", "llms.", "llm"):
        return "LLMs"

    if lower in ("exposure to numpy", "numpy."):
        return "NumPy"

    return None


def split_compound_phrase(phrase: str) -> List[str]:
    """
    Split compound phrases like 'Pandas And Scikit' or 'Tensorflow Or Pytorch'
    into atomic candidates. Preserves atomic units like 'CI/CD' or 'AI/ML'.
    """
    cleaned = strip_filler_words_and_punctuation(phrase)
    if not cleaned:
        return []

    # Check for direct repairs first
    repaired = repair_broken_fragment(cleaned)
    if repaired:
        return [repaired]

    # Handle special cases: 'Strong Problem Solving And Analytical Skills'
    clean_lower = cleaned.lower()
    if "problem" in clean_lower and ("solving" in clean_lower or "analytical" in clean_lower):
        results = []
        if "problem" in clean_lower and "solving" in clean_lower:
            results.append("Problem Solving")
        if "analytical" in clean_lower:
            results.append("Analytical Skills")
        if results:
            return results

    # Compound delimiters: ' and ', ' or ', ' / ' (avoid splitting 'ci/cd' or 'ai/ml')
    # Use regex looking for words separated by and/or/as well as/,
    # Replace compound separators with a pipe delimiter if not inside atomic terms
    temp = cleaned

    # Protect atomic terms
    protect_map = {
        "ci/cd": "###CICD###",
        "ai/ml": "###AIML###",
        "c++": "###CPP###",
        "c#": "###CSHARP###",
        ".net": "###DOTNET###",
        "data structures & algorithms": "###DSA###",
        "data structures and algorithms": "###DSA###",
    }
    for orig, token in protect_map.items():
        temp = re.sub(r"(?i)\b" + re.escape(orig) + r"\b", token, temp)
        if "/" in orig:
            temp = re.sub(re.escape(orig), token, temp, flags=re.I)

    # Split on ' and ', ' or ', ' as well as ', ',', ';'
    parts = re.split(r"(?i)\s+(?:and|or|as\s+well\s+as)\s+|[,;]", temp)

    tokens = []
    for part in parts:
        # Restore protected terms
        p = part
        for orig, token in protect_map.items():
            if token in p:
                p = p.replace(token, orig)

        sub = strip_filler_words_and_punctuation(p)
        if sub:
            # Check repair for sub-part
            rep = repair_broken_fragment(sub)
            tokens.append(rep if rep else sub)

    return tokens if tokens else [cleaned]


def canonicalize_skill(skill: str) -> Optional[str]:
    """Map a skill string to its canonical atomic name and casing."""
    if not skill:
        return None

    cleaned = strip_filler_words_and_punctuation(skill)
    if not cleaned:
        return None

    lower = cleaned.lower()

    # Check non-skill blacklist
    if lower in NON_SKILL_BLACKLIST:
        return None

    # Check broken fragment repairs
    repaired = repair_broken_fragment(cleaned)
    if repaired:
        return repaired

    # Check canonical dictionary
    if lower in CANONICAL_SKILL_MAP:
        return CANONICAL_SKILL_MAP[lower]

    # Handle AI/ML variations
    if lower in ("ai/ml or data science", "ai/ml or data science."):
        return None  # Will be handled by compound splitter

    # Check partial mappings
    if lower.startswith("academic or personal projects in"):
        inner = re.sub(r"(?i)^academic\s+or\s+personal\s+projects\s+in\s*", "", lower).strip()
        return CANONICAL_SKILL_MAP.get(inner, inner.upper())

    # Reject if too short (unless recognized like C or R) or excessively long (> 35 chars)
    if len(cleaned) < 2 and lower not in ("c", "r"):
        return None
    if len(cleaned) > 35:
        return None

    # Reject non-skills containing generic filler
    if any(phrase in lower for phrase in ["paced environment", "good to have", "years of experience", "work experience"]):
        return None

    # Preserve all-caps technical acronyms (AWS, SQL, LLM, NLP, API, REST, etc.)
    if cleaned.isupper() and len(cleaned) <= 6:
        return cleaned

    # Default to clean title-cased string
    return cleaned.title()


def clean_missing_skills(
    raw_missing_skills: List[str],
    matched_skills: Optional[List[str]] = None,
) -> List[str]:
    """
    Transform raw, noisy missing skills into clean, atomic, canonical skills:
    1. Merge broken multi-line/sequential fragments ('Strong Problem' + 'Solving And Analytical Skills.')
    2. Split compound phrases ('Pandas And Scikit', 'Tensorflow Or Pytorch')
    3. Strip filler prefixes and trailing punctuation ('Exposure To Numpy' -> 'NumPy')
    4. Drop blacklisted non-skills ('Good To Have', 'Learn.', 'IT', 'Paced Environment.')
    5. Canonicalize casing and aliases ('NLP', 'LLMs', 'NumPy', 'scikit-learn', 'PyTorch')
    6. Deduplicate against Matched Skills.
    """
    matched_skills = matched_skills or []
    # Build normalized lookup for matched skills (both lower and canonical forms)
    matched_set: Set[str] = set()
    for m in matched_skills:
        clean_m = strip_filler_words_and_punctuation(m).lower()
        if clean_m:
            matched_set.add(clean_m)
            canonical_m = CANONICAL_SKILL_MAP.get(clean_m)
            if canonical_m:
                matched_set.add(canonical_m.lower())

    # Step 1: Pre-process input list to merge broken fragments across items
    # Example: ['Strong Problem', 'Solving And Analytical Skills.']
    merged_raw: List[str] = []
    i = 0
    n = len(raw_missing_skills)
    while i < n:
        curr = (raw_missing_skills[i] or "").strip()
        nxt = (raw_missing_skills[i + 1] or "").strip() if i + 1 < n else ""

        # Check if 'Strong Problem' is followed by 'Solving...'
        if curr.lower() in ("strong problem", "problem") and nxt.lower().startswith("solving"):
            merged_raw.append(f"{curr} {nxt}")
            i += 2
            continue

        merged_raw.append(curr)
        i += 1

    # Step 2: Split compound phrases and clean each part
    candidates: List[str] = []
    for item in merged_raw:
        if not item:
            continue
        splits = split_compound_phrase(item)
        for s in splits:
            cand = canonicalize_skill(s)
            if cand:
                candidates.append(cand)

    # Step 3: Deduplicate against matched skills and within results
    final_skills: List[str] = []
    seen: Set[str] = set()

    for skill in candidates:
        key = skill.lower()
        if key in NON_SKILL_BLACKLIST:
            continue
        # Deduplicate against matched skills
        if key in matched_set:
            continue
        # Also check canonical alias against matched set
        canonical_key = CANONICAL_SKILL_MAP.get(key, skill).lower()
        if canonical_key in matched_set:
            continue

        if key not in seen and canonical_key not in seen:
            seen.add(key)
            seen.add(canonical_key)
            final_skills.append(skill)

    return final_skills


def extract_clean_skills_with_llm(
    raw_missing_skills: List[str],
    matched_skills: Optional[List[str]] = None,
    llm_model: Any = None,
) -> List[str]:
    """
    Extract atomic canonical skills using an LLM step with fallback to deterministic pipeline.
    Validates output with canonical dictionary and deduplicates against matched skills.
    """
    clean_deterministic = clean_missing_skills(raw_missing_skills, matched_skills)

    if llm_model is None:
        try:
            from ai.llm_model import LLMModel
            llm_model = LLMModel()
        except Exception:
            llm_model = None

    if not llm_model or not getattr(llm_model, "api_keys", None):
        return clean_deterministic

    prompt = (
        "You are an expert ATS skill extraction system.\n"
        "From the following raw skill phrases, extract clean, atomic, canonical skills.\n"
        f"RAW ITEMS: {raw_missing_skills}\n"
        f"ALREADY MATCHED SKILLS (DO NOT INCLUDE): {matched_skills or []}\n\n"
        "REQUIREMENTS:\n"
        "- Split compound phrases: 'Pandas And Scikit' -> 'Pandas', 'scikit-learn'\n"
        "- Strip filler words and punctuation: 'Exposure To Numpy' -> 'NumPy', 'Exposure To Llms' -> 'LLMs'\n"
        "- Drop non-skills: 'Good To Have', 'Learn.', 'Paced Environment.', 'IT'\n"
        "- Repair broken fragments: 'Oriented Programming.' -> 'Object-Oriented Programming'\n"
        "- Return ONLY valid JSON: {\"skills\": [\"Skill1\", \"Skill2\"]}"
    )

    try:
        res = llm_model.generate_json(prompt)
        if isinstance(res, dict) and "skills" in res and isinstance(res["skills"], list):
            llm_skills = [str(s) for s in res["skills"] if s]
            if llm_skills:
                return clean_missing_skills(llm_skills, matched_skills)
    except Exception as exc:
        logger.warning("LLM skill extraction step failed: %s; using deterministic cleaner.", exc)

    return clean_deterministic
