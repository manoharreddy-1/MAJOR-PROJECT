"""Skill normalization, deduplication, and domain taxonomy."""
import re
from typing import List, Set, Optional

from utils.text_cleaner import normalize_skill

# Non-skill phrases, junk tokens, grammatical filler, and degrees to filter out
SKILL_BLACKLIST = {
    "& soft skills",
    "soft skills",
    "soft skill",
    "technical & soft skills",
    "information technology",
    "computer science",
    "computer science & engineering",
    "computer engineering",
    "bachelor",
    "bachelors",
    "master",
    "masters",
    "phd",
    "degree",
    "degree in computer science",
    "degree in information technology",
    "relevant field",
    "related field",
    "years of experience",
    "years experience",
    "year of experience",
    "experience",
    "work experience",
    "strong communication",
    "communication skills",
    "excellent communication",
    "good communication",
    "written communication",
    "interpersonal skills",
    "problem solving",
    "problem solving skills",
    "analytical skills",
    "critical thinking",
    "team player",
    "fast learner",
    "quick learner",
    "self motivated",
    "responsibilities",
    "requirements",
    "qualifications",
    "preferred qualifications",
    "required qualifications",
    "duties",
    "plus",
    "bonus",
    "minimum",
    "etc",
    "and",
    "or",
    "with",
    "candidate",
    "proven experience",
    "track record",
}

# Comprehensive technical skills and aliases mapping
SKILL_ALIASES = {
    # Java & JVM
    "java": "Java",
    "core java": "Java",
    "java 8": "Java",
    "java 11": "Java",
    "java 17": "Java",
    "java 21": "Java",
    "java se": "Java",
    "java ee": "Java EE",
    "j2ee": "Java EE",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "spring framework": "Spring",
    "spring mvc": "Spring MVC",
    "spring security": "Spring Security",
    "spring data": "Spring Data",
    "spring cloud": "Spring Cloud",
    "hibernate": "Hibernate",
    "jpa": "JPA",
    "hibernate/jpa": "Hibernate",
    "maven": "Maven",
    "gradle": "Gradle",
    "jvm": "JVM",
    "junit": "JUnit",
    "mockito": "Mockito",
    "tomcat": "Tomcat",
    "microservices": "Microservices",
    "microservice": "Microservices",
    "micro-services": "Microservices",
    "microservices architecture": "Microservices",

    # Python ecosystem
    "python": "Python",
    "python3": "Python",
    "python 3": "Python",
    "python programming": "Python",
    "py": "Python",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "celery": "Celery",
    "pytest": "PyTest",

    # JavaScript / TypeScript / Web
    "js": "JavaScript",
    "javascript": "JavaScript",
    "es6": "JavaScript",
    "es6+": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "react native": "React Native",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "redux": "Redux",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "sass": "Sass",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "graphql": "GraphQL",
    "websocket": "WebSockets",
    "websockets": "WebSockets",

    # C / C++ / C# / .NET
    "c": "C",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "c sharp": "C#",
    ".net": ".NET",
    ".net core": ".NET Core",
    "asp.net": "ASP.NET",

    # Other Languages
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "php": "PHP",
    "ruby": "Ruby",
    "ruby on rails": "Ruby on Rails",
    "rails": "Ruby on Rails",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "scala": "Scala",
    "r": "R",

    # Databases & Caching
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "oracle": "Oracle DB",
    "oracle database": "Oracle DB",
    "sql server": "MS SQL Server",
    "mssql": "MS SQL Server",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "sqlite": "SQLite",
    "dynamodb": "DynamoDB",
    "elasticsearch": "Elasticsearch",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "docker": "Docker",
    "containerization": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "jenkins": "Jenkins",
    "ci/cd": "CI/CD",
    "ci cd": "CI/CD",
    "continuous integration": "CI/CD",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "linux": "Linux",
    "unix": "Linux",
    "bash": "Bash/Shell",
    "shell scripting": "Bash/Shell",
    "nginx": "Nginx",
    "kafka": "Apache Kafka",
    "apache kafka": "Apache Kafka",
    "rabbitmq": "RabbitMQ",

    # Data Science & AI / ML
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "artificial intelligence": "Artificial Intelligence",
    "ai": "Artificial Intelligence",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "hadoop": "Hadoop",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "tableau": "Tableau",
    "power bi": "Power BI",

    # Core Engineering & Architecture
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "dsa": "Data Structures & Algorithms",
    "object-oriented programming": "Object-Oriented Programming",
    "object oriented programming": "Object-Oriented Programming",
    "oop": "Object-Oriented Programming",
    "oops": "Object-Oriented Programming",
    "system design": "System Design",
    "design patterns": "Design Patterns",
    "agile": "Agile/Scrum",
    "scrum": "Agile/Scrum",
}


def clean_skill_candidate(raw: str) -> Optional[str]:
    """Clean a raw candidate skill string, removing prefixes, bullets, and junk."""
    if not raw or not raw.strip():
        return None

    cleaned = raw.strip()

    # Remove leading bullets, numbers, dashes, asterisks
    cleaned = re.sub(r"^[\s•\-\*\d\.\:\;\,\(\)\[\]\/\\]+", "", cleaned)

    # Remove leading connective words and symbols like &, and, or, with, in, plus
    cleaned = re.sub(r"^(?:&|and|or|with|in|to|for|plus|as well as)\s+", "", cleaned, flags=re.I)

    # Remove common prefix phrases
    prefix_patterns = [
        r"^(?:strong\s+)?(?:hands[- ]on\s+)?experience\s+(?:with|in|of)\s*",
        r"^(?:strong\s+)?(?:working\s+)?knowledge\s+(?:with|in|of)\s*",
        r"^(?:strong\s+)?proficien(?:cy|t)\s+(?:with|in)\s*",
        r"^familiar(?:ity)?\s+(?:with|in)\s*",
        r"^understanding\s+(?:of|with)\s*",
        r"^expertise\s+(?:with|in)\s*",
        r"^strong\s+(?:skills\s+in|knowledge\s+of)\s*",
        r"^skills\s*:\s*",
        r"^required\s*:\s*",
        r"^preferred\s*:\s*",
        r"^must\s+have\s*:\s*",
        r"^nice\s+to\s+have\s*:\s*",
    ]
    for pat in prefix_patterns:
        cleaned = re.sub(pat, "", cleaned, flags=re.I)

    # Remove trailing punctuation or parenthetical details like (nice to have)
    cleaned = re.sub(r"[\s•\-\*\:\;\,\.\/\\]+$", "", cleaned)
    cleaned = re.sub(r"\s*\((?:required|preferred|bonus|plus|intermediate|advanced|beginner)\)\s*$", "", cleaned, flags=re.I)

    cleaned = cleaned.strip()

    # Reject if empty, too long (> 35 chars), or in blacklist
    if not cleaned or len(cleaned) > 35 or len(cleaned) < 2:
        return None

    lower = cleaned.lower()
    if lower in SKILL_BLACKLIST:
        return None

    # Reject if it starts with unwanted symbols or matches filler phrases
    if re.match(r"^(&|\band\b|\bor\b|degree|bachelor|master|years?|soft\s+skills)", lower):
        return None

    return cleaned


def normalize_skill_name(skill: str) -> str:
    """Normalize a skill name using the canonical alias mapping."""
    candidate = clean_skill_candidate(skill)
    if not candidate:
        return ""

    # Preserve all-caps inputs if specified (e.g. PYTHON, SQL, AWS)
    if candidate.isupper():
        return candidate.upper()

    lower = candidate.lower()
    if lower in SKILL_ALIASES:
        return SKILL_ALIASES[lower]

    return normalize_skill(candidate)


def deduplicate_skills(skills: List[str]) -> List[str]:
    """Remove duplicate skills after normalization and filtering."""
    seen: Set[str] = set()
    result = []
    for skill in skills:
        normalized = normalize_skill_name(skill)
        if not normalized:
            continue
        key = normalized.lower()
        if key not in seen and key not in SKILL_BLACKLIST:
            seen.add(key)
            result.append(normalized)
    return result


def extract_skills_from_text(text: str, known_skills: List[str] = None) -> List[str]:
    """Extract standard known skills from text using boundary-safe regex matching."""
    if not text:
        return []

    found = []
    text_lower = " " + text.lower() + " "

    # Build master candidate list from SKILL_ALIASES
    for alias, canonical in SKILL_ALIASES.items():
        # Handle special characters like C++, C#, .NET
        if alias in ("c++", "c#", ".net", ".net core"):
            pattern = re.escape(alias)
            if re.search(r"(?:\b|\s)" + pattern + r"(?:\b|\s)", text_lower):
                found.append(canonical)
        elif len(alias) <= 2:
            # Short tokens (r, c, go, ts, js, py) require strict word boundaries
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text_lower):
                found.append(canonical)
        else:
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text_lower):
                found.append(canonical)

    if known_skills:
        for ks in known_skills:
            norm = normalize_skill_name(ks)
            if norm:
                found.append(norm)

    return deduplicate_skills(found)
