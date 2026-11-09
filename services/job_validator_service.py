"""Job Role and Job Description Alignment Validation Service.

Validates that:
1. Target Job Title is provided.
2. The provided text is a genuine employer Job Description (and not a candidate resume/CV or random text).
3. The Job Description actually matches the Target Job Title (preventing mismatches such as 'jr otho doctor' with a Python developer JD).
"""
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from ai.llm_model import LLMModel
from utils.text_cleaner import clean_text

logger = logging.getLogger(__name__)

# Domain taxonomy for grounded verification
DOMAIN_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "medical_healthcare": {
        "title_keywords": [
            "doctor", "ortho", "orthopedic", "physician", "surgeon", "mbbs", "md", "ms",
            "clinical", "hospital", "patient", "nurse", "nursing", "dentist", "dental",
            "pediatric", "radiology", "cardiology", "pathology", "pharmacist", "pharmacy",
            "healthcare", "medical officer"
        ],
        "jd_keywords": [
            "patient", "clinical", "hospital", "surgery", "diagnosis", "treatment",
            "mbbs", "medical", "orthopedic", "physician", "healthcare", "ward",
            "opd", "pathology", "radiology", "nursing", "pharmacology", "fracture"
        ]
    },
    "tech_ai_data": {
        "title_keywords": [
            "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
            "data scientist", "data science", "data analyst", "data engineer", "nlp",
            "computer vision", "cv engineer", "mlops", "ai intern", "ml intern"
        ],
        "jd_keywords": [
            "machine learning", "deep learning", "python", "pytorch", "tensorflow",
            "scikit-learn", "nlp", "computer vision", "neural network", "data pipeline",
            "pandas", "numpy", "model training", "algorithms", "artificial intelligence", "dataset"
        ]
    },
    "tech_python": {
        "title_keywords": [
            "python developer", "python engineer", "django developer", "fastapi developer",
            "flask developer", "backend python"
        ],
        "jd_keywords": [
            "python", "django", "flask", "fastapi", "rest api", "postgresql", "mysql",
            "orm", "sql", "git", "backend", "celery", "redis"
        ]
    },
    "tech_java": {
        "title_keywords": [
            "java developer", "java engineer", "spring boot developer", "backend java",
            "j2ee developer"
        ],
        "jd_keywords": [
            "java", "spring", "spring boot", "hibernate", "microservices", "jvm",
            "maven", "gradle", "rest api", "junit", "sql"
        ]
    },
    "tech_frontend": {
        "title_keywords": [
            "frontend", "front-end", "react developer", "angular developer", "vue developer",
            "web developer", "ui/ux developer", "ui developer", "javascript developer"
        ],
        "jd_keywords": [
            "javascript", "typescript", "react", "angular", "vue", "html", "css",
            "tailwind", "bootstrap", "dom", "ui", "ux", "responsive", "webpack", "vite"
        ]
    },
    "tech_qa_testing": {
        "title_keywords": [
            "qa", "quality assurance", "test engineer", "sdet", "tester", "automation tester",
            "software test engineer", "qa engineer"
        ],
        "jd_keywords": [
            "selenium", "testing", "test cases", "automation", "junit", "testng",
            "cypress", "playwright", "bug tracking", "jira", "sdet", "regression testing"
        ]
    },
    "tech_devops_cloud": {
        "title_keywords": [
            "devops", "cloud engineer", "aws engineer", "azure engineer", "sre",
            "site reliability engineer", "infrastructure engineer", "kubernetes administrator"
        ],
        "jd_keywords": [
            "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ci/cd",
            "jenkins", "ansible", "linux", "cloud", "monitoring", "prometheus"
        ]
    },
    "finance_accounting": {
        "title_keywords": [
            "accountant", "accounting", "chartered accountant", "ca", "cpa", "auditor",
            "financial analyst", "tax consultant", "bookkeeper", "finance executive"
        ],
        "jd_keywords": [
            "accounting", "tally", "gst", "tds", "balance sheet", "audit", "taxation",
            "ledger", "financial reporting", "payroll", "invoicing", "p&l"
        ]
    },
    "civil_mechanical_core": {
        "title_keywords": [
            "civil engineer", "mechanical engineer", "structural engineer", "site engineer",
            "autocad designer", "design engineer", "electrical engineer"
        ],
        "jd_keywords": [
            "autocad", "construction", "site supervision", "solidworks", "catia", "structural",
            "concrete", "hvac", "fabrication", "surveying", "mechanical", "electrical circuit"
        ]
    },
    "sales_marketing_hr": {
        "title_keywords": [
            "sales executive", "business development", "bdr", "marketing manager",
            "digital marketer", "seo specialist", "human resources", "hr executive", "recruiter"
        ],
        "jd_keywords": [
            "sales", "lead generation", "marketing", "seo", "campaigns", "crm", "recruitment",
            "talent acquisition", "onboarding", "payroll", "client relations", "cold calling"
        ]
    },
    "logistics_transport": {
        "title_keywords": [
            "driver", "chauffeur", "delivery driver", "truck driver", "courier", "dispatch",
            "logistics", "fleet", "transport", "cab driver", "van driver"
        ],
        "jd_keywords": [
            "driving", "license", "vehicle", "delivery", "route", "transport", "shipment",
            "traffic", "cargo", "safety", "dispatch", "van", "truck", "commercial license", "dl"
        ]
    }
}



class JobValidatorService:
    """Service to validate Job Title against Job Description."""

    def __init__(self):
        self.llm = LLMModel()

    def validate_title_and_description(
        self, job_title: Optional[str], job_description: Optional[str]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates job title against job description.

        Returns:
            (is_valid, error_message, details_dict)
        """
        title = (job_title or "").strip()
        text = clean_text(job_description or "", preserve_newlines=True).strip()

        # 1. Verify Job Title exists and is a plausible occupational role
        if not title:
            return (
                False,
                "Job title / target role is required. Please enter a job title (e.g. 'Python Developer', 'Machine Learning Engineer', 'Orthopedic Doctor').",
                {"code": "MISSING_JOB_TITLE"}
            )
        is_plausible, title_err = self._is_plausible_job_title(title)
        if not is_plausible:
            return (
                False,
                f"Invalid job title: {title_err}",
                {"code": "INVALID_JOB_TITLE", "title": title}
            )

        # 2. Verify Job Description exists and meets minimal length
        if not text or len(text) < 30:
            return (
                False,
                "Job description is too short or empty. Please enter a full job description according to the role.",
                {"code": "JD_TOO_SHORT"}
            )

        # 3. Check for gibberish or nonsense keyboard mashing
        is_gibberish, gibberish_err = self._is_gibberish_or_nonsense(text)
        if is_gibberish:
            return (
                False,
                f"Invalid job description: {gibberish_err} Please enter a proper job description according to the role '{title}'.",
                {"code": "GIBBERISH_JD_TEXT"}
            )

        # 4. Check if text is a candidate resume/profile rather than a job description
        is_resume, resume_reason = self._is_resume_or_candidate_profile(text)
        if is_resume:
            return (
                False,
                f"Invalid job description: The provided text appears to be a resume or candidate profile ({resume_reason}), "
                f"not an employer job description. Please enter a proper job description according to the role '{title}'.",
                {"code": "RESUME_PASTED_AS_JD", "reason": resume_reason}
            )

        # 5. Check if text is too brief or lacks role context
        if len(text.split()) < 10 and not any(k in text.lower() for k in ["engineer", "developer", "doctor", "skills", "experience", "requirements", "driver"]):
            return (
                False,
                f"Invalid job description: The entered text is not a valid job description. "
                f"Please enter proper job requirements and responsibilities according to the role '{title}'.",
                {"code": "INVALID_JD_TEXT"}
            )

        # 6. Check Alignment between Job Title and Job Description
        # First attempt LLM validation
        llm_valid, llm_msg, llm_details = self._validate_via_llm(title, text)
        if llm_details.get("llm_verified"):
            if not llm_valid:
                return (
                    False,
                    llm_msg or f"Invalid job title and job description: The provided job description does not match the role '{title}'. Please enter a proper job description according to the role.",
                    llm_details
                )
            return (True, "", llm_details)

        # Grounded fallback verification
        grounded_valid, grounded_msg, grounded_details = self._validate_via_grounded_rules(title, text)
        if not grounded_valid:
            return (
                False,
                grounded_msg,
                grounded_details
            )

        return (True, "", grounded_details)

    def _is_plausible_job_title(self, title: str) -> Tuple[bool, str]:
        """Verify that title is an occupational job title and not a personal name or random text."""
        t_clean = title.strip().lower()

        # Direct blacklist of common personal names when entered alone without an occupational role
        personal_names = {
            "manohar", "rahul", "rohit", "priya", "anita", "john", "alex", "david", "smith",
            "kumar", "reddy", "sharma", "patel", "singh", "gupta", "suresh", "ramesh", "sneha",
            "pooja", "swathi", "dhanisetti", "durga", "rupa", "arjun", "kiran", "sai", "ravi"
        }
        if t_clean in personal_names:
            return False, f"'{title}' is a personal name, not a recognized occupational job title."

        # Recognized occupational nouns and indicators
        occupational_nouns = {
            "developer", "engineer", "doctor", "specialist", "analyst", "consultant", "manager",
            "lead", "architect", "intern", "officer", "administrator", "designer", "driver",
            "technician", "assistant", "nurse", "accountant", "pilot", "mechanic", "scientist",
            "teacher", "executive", "associate", "programmer", "operator", "clerk", "supervisor",
            "coordinator", "head", "director", "trainee", "fresher", "tester", "auditor",
            "attendant", "advisor", "practitioner", "physician", "surgeon", "sdet", "devops",
            "prof", "professor", "lecturer", "instructor", "recruiter", "marketer", "bdr",
            "chauffeur", "courier", "cashier", "chef", "cook", "writer", "editor", "artist"
        }

        # Recognized tech, domain, or industry keywords that commonly form standalone roles (e.g. "Python", "Data Science")
        domain_role_keywords = {
            "python", "java", "c++", "c#", ".net", "javascript", "typescript", "react",
            "angular", "node", "sql", "ai", "machine learning", "ml", "deep learning", "nlp",
            "devops", "cloud", "aws", "azure", "frontend", "backend", "full stack", "fullstack",
            "qa", "sdet", "ui/ux", "ui", "ux", "seo", "sales", "hr", "finance", "accounting",
            "cyber security", "data science", "data analytics", "sysadmin", "database administrator",
            "dba", "scrum master", "product owner"
        }

        has_occupational_noun = any(re.search(rf"\b{re.escape(noun)}\b", t_clean) for noun in occupational_nouns)
        has_domain_role = any(re.search(rf"\b{re.escape(dom)}\b", t_clean) for dom in domain_role_keywords)

        if has_occupational_noun or has_domain_role:
            return True, ""

        # Check in taxonomy
        in_taxonomy = any(
            any(kw in t_clean for kw in d["title_keywords"])
            for d in DOMAIN_TAXONOMY.values()
        )
        if in_taxonomy:
            return True, ""

        # Single-word without occupational noun or recognized tech skill
        words = t_clean.split()
        if len(words) == 1:
            return False, f"'{title}' is not a recognized occupational job title. Please enter a specific job title (e.g., 'Software Engineer', 'Driver', 'Java Developer')."

        return False, f"'{title}' is not recognized as a job title. Please enter a valid occupational title (e.g., 'Software Engineer', 'Driver', 'Python Developer')."

    def _is_gibberish_or_nonsense(self, text: str) -> Tuple[bool, str]:
        """Detect keyboard mashing or random gibberish strings in job description."""
        clean = re.sub(r"[^a-zA-Z\s]", " ", text)
        words = [w.lower() for w in clean.split() if len(w) >= 3]
        if not words:
            return True, "Job description contains no valid text."

        gibberish_count = 0
        vowels = set("aeiouy")
        known_tech_acronyms = {"nlp", "llm", "llms", "sql", "aws", "gcp", "css", "xml", "npm", "sdk", "api", "sde", "sdet", "devops", "ml", "ai", "rdbms", "crud", "ci/cd", "cicd", "k8s"}

        for w in words:
            if w in known_tech_acronyms:
                continue
            # Check 1: 5 or more consecutive consonants (e.g. ndjnsdc in iuendijnsdc)
            if re.search(r"[bcdfghjklmnpqrstvwxz]{5,}", w):
                gibberish_count += 1
                continue
            # Check 2: 4 or more consecutive vowels (e.g. aeiou)
            if re.search(r"[aeiou]{4,}", w):
                gibberish_count += 1
                continue
            # Check 3: Word >= 4 chars with 0 vowels (e.g. scc)
            if len(w) >= 3 and not any(c in vowels for c in w):
                gibberish_count += 1
                continue
            # Check 4: Keyboard walks / repetitive keys (asdf, jkl;, etc.)
            if any(walk in w for walk in ["asdf", "qwer", "zxcv", "hjkl", "sdfg", "fghj", "ghjk", "jkl"]):
                gibberish_count += 1
                continue
            # Check 5: High consonant ratio on words > 6 chars (e.g. aijdnia, iuendijnsdc)
            vowel_ratio = sum(1 for c in w if c in vowels) / len(w)
            if len(w) >= 6 and (vowel_ratio < 0.12 or vowel_ratio > 0.70):
                gibberish_count += 1
                continue

        # If gibberish ratio is > 25% of words, or if text is short and contains multiple gibberish words
        gibberish_ratio = gibberish_count / len(words)
        if gibberish_ratio >= 0.25 or (len(words) < 25 and gibberish_count >= 2):
            return True, "The provided job description contains nonsense or keyboard-mashed text."

        return False, ""


    def _is_resume_or_candidate_profile(self, text: str) -> Tuple[bool, str]:
        """Detect if pasted text is actually a candidate resume instead of a job description."""
        t_lower = text.lower()

        # Strong resume headers
        resume_indicators = [
            (r"\bcurriculum vitae\b", "Curriculum Vitae heading"),
            (r"\bresume\b", "Resume heading"),
            (r"\bdeclaration\b.*?(?:hereby declare|true to the best)", "Candidate declaration clause"),
            (r"\bfather'?s?\s*name\b", "Personal details / Father's name"),
            (r"\bdate of birth\b|\bd\.?o\.?b\b", "Date of birth personal field"),
            (r"\bcareer objective\b.*?(?:seeking|obtain|secure a challenging)", "Candidate career objective"),
            (r"\bmy projects\b|\bacademics?\s*projects?\b", "Candidate academic projects"),
            (r"\bcgpa\s*[:=]\s*\d+\.?\d*", "Candidate CGPA score"),
            (r"\bhall\s*ticket\b|\broll\s*no\b|\breg(?:istration)?\s*no\b", "Student roll/registration number"),
            (r"\bpassed out\b|\byear of passing\b", "Graduation passing year"),
            (r"\bhobbies\b|\bleisure\s*activities\b", "Personal hobbies section"),
        ]

        matched_indicators = []
        for pat, desc in resume_indicators:
            if re.search(pat, t_lower):
                matched_indicators.append(desc)

        # Employer/JD headers
        jd_indicators = [
            r"\bwe are looking for\b", r"\brole overview\b", r"\bjob description\b",
            r"\bkey responsibilities\b", r"\brequired qualifications\b", r"\bwhat you'?ll do\b",
            r"\bcandidate profile\b", r"\babout the role\b", r"\bjob summary\b",
            r"\bresponsibilities\s*:", r"\brequirements\s*:", r"\bqualifications\s*:"
        ]
        has_jd_indicator = any(re.search(pat, t_lower) for pat in jd_indicators)

        # If 2 or more resume indicators matched and zero JD indicators, it's definitely a resume
        if len(matched_indicators) >= 2 and not has_jd_indicator:
            return (True, ", ".join(matched_indicators[:2]))

        # Check for candidate contact block at the start without JD keywords
        first_lines = "\n".join(text.split("\n")[:8]).lower()
        has_phone = bool(re.search(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", first_lines))
        has_email = bool(re.search(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", first_lines))
        has_linkedin_github = any(k in first_lines for k in ["linkedin.com", "github.com"])

        if (has_phone or has_email) and has_linkedin_github and not has_jd_indicator:
            return (True, "contains candidate contact details and personal links at top")

        # Check for single-line person name like "Dhanisetti Rupa Durga"
        if len(text.strip().split("\n")) <= 3 and len(text.strip().split()) <= 6:
            if not any(k in t_lower for k in ["engineer", "developer", "doctor", "analyst", "intern", "manager"]):
                return (True, "contains only candidate name or single phrase")

        return (False, "")

    def _validate_via_llm(self, title: str, text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate role alignment using Gemini LLM if available."""
        if not self.llm.api_keys:
            return (True, "", {"llm_verified": False})

        snippet = text[:2000]
        prompt = (
            "You are an expert ATS recruitment validator. "
            "Verify whether the provided Job Description actually corresponds to the Target Job Title.\n\n"
            f"TARGET JOB TITLE: \"{title}\"\n\n"
            f"JOB DESCRIPTION SNIPPET:\n\"\"\"\n{snippet}\n\"\"\"\n\n"
            "TASK:\n"
            "1. Determine what profession/role the Job Title represents (e.g. Orthopedic Doctor -> Medical/Healthcare; Python Developer -> Software Engineering).\n"
            "2. Determine what profession/role the Job Description is actually describing.\n"
            "3. If they are from completely mismatched domains (for example: Target Title is 'jr otho doctor' but Job Description is for 'Python Developer' or 'Java Developer'), or if the Job Description does NOT match the Target Job Title, set matches_role to false.\n"
            "4. If the text is NOT a job description (e.g. a candidate's resume/CV), set is_valid_jd to false.\n\n"
            "Return STRICT JSON format:\n"
            "{\n"
            "  \"is_valid_jd\": true,\n"
            "  \"matches_role\": true,\n"
            "  \"expected_role\": \"...\",\n"
            "  \"detected_role\": \"...\",\n"
            "  \"reason\": \"...\"\n"
            "}"
        )

        try:
            res = self.llm.generate_json(prompt)
            if not isinstance(res, dict) or "matches_role" not in res:
                return (True, "", {"llm_verified": False})

            is_valid_jd = bool(res.get("is_valid_jd", True))
            matches_role = bool(res.get("matches_role", True))
            detected_role = res.get("detected_role") or "Unknown"
            reason = res.get("reason") or ""

            if not is_valid_jd:
                return (
                    False,
                    f"Invalid job description: {reason or 'The uploaded text is not a valid employer job description.'} Please enter a proper job description according to the role.",
                    {"llm_verified": True, "detected_role": detected_role, "reason": reason}
                )

            if not matches_role:
                msg = (
                    f"Invalid job title and job description: You entered '{title}', but this job description is for "
                    f"'{detected_role}'. {reason} Please enter a proper job description according to the role."
                )
                return (
                    False,
                    msg,
                    {"llm_verified": True, "detected_role": detected_role, "reason": reason}
                )

            return (True, "", {"llm_verified": True, "detected_role": detected_role})
        except Exception as exc:
            logger.warning("LLM role validation failed or timed out: %s", exc)
            return (True, "", {"llm_verified": False})

    def _validate_via_grounded_rules(self, title: str, text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Grounded taxonomy and keyword validator."""
        t_lower = title.lower().strip()
        jd_lower = text.lower()

        # Identify domain of Job Title
        title_domain = None
        for dom, data in DOMAIN_TAXONOMY.items():
            if any(kw in t_lower for kw in data["title_keywords"]):
                title_domain = dom
                break

        # Identify domain of Job Description
        jd_domain_scores: Dict[str, int] = {}
        for dom, data in DOMAIN_TAXONOMY.items():
            score = sum(1 for kw in data["jd_keywords"] if kw in jd_lower)
            if score > 0:
                jd_domain_scores[dom] = score

        top_jd_domain = max(jd_domain_scores.items(), key=lambda x: x[1])[0] if jd_domain_scores else None

        # Cross-Domain Conflict Detection
        # Case 1: Title is Medical / Healthcare, but JD has zero medical keywords and has tech/python/java keywords
        if title_domain == "medical_healthcare":
            medical_kw_count = jd_domain_scores.get("medical_healthcare", 0)
            tech_kw_count = sum(
                jd_domain_scores.get(d, 0)
                for d in ["tech_python", "tech_java", "tech_ai_data", "tech_frontend", "tech_devops", "tech_qa_testing"]
            )
            if medical_kw_count == 0 and tech_kw_count >= 2:
                detected = "Software Developer"
                if "python" in jd_lower:
                    detected = "Python Developer"
                elif "java" in jd_lower:
                    detected = "Java Developer"
                elif any(k in jd_lower for k in ["machine learning", "deep learning", "ai"]):
                    detected = "AI / ML Engineer"

                return (
                    False,
                    f"Invalid job title and job description: You entered '{title}' (Medical / Healthcare), "
                    f"but the job description is for a '{detected}' (Software Engineering). "
                    f"Please enter a proper job description according to the role.",
                    {"code": "ROLE_DOMAIN_MISMATCH", "entered_domain": "medical_healthcare", "detected_domain": top_jd_domain}
                )

        # Case 2: Title is Finance / Accounting, but JD is Tech / Engineering
        if title_domain == "finance_accounting":
            fin_count = jd_domain_scores.get("finance_accounting", 0)
            tech_count = sum(
                jd_domain_scores.get(d, 0)
                for d in ["tech_python", "tech_java", "tech_ai_data", "tech_frontend", "tech_devops"]
            )
            if fin_count == 0 and tech_count >= 2:
                return (
                    False,
                    f"Invalid job title and job description: You entered '{title}' (Finance / Accounting), "
                    f"but the job description is for a Software / IT position. "
                    f"Please enter a proper job description according to the role.",
                    {"code": "ROLE_DOMAIN_MISMATCH", "entered_domain": "finance_accounting", "detected_domain": top_jd_domain}
                )

        # Case 3: Title is Tech (Python, Java, AI), but JD is Medical or Civil
        if title_domain in ["tech_python", "tech_java", "tech_ai_data", "tech_frontend", "tech_devops"]:
            med_count = jd_domain_scores.get("medical_healthcare", 0)
            tech_count = jd_domain_scores.get(title_domain, 0)
            if tech_count == 0 and med_count >= 3:
                return (
                    False,
                    f"Invalid job title and job description: You entered '{title}', but the job description is for a "
                    f"Healthcare / Medical position. Please enter a proper job description according to the role.",
                    {"code": "ROLE_DOMAIN_MISMATCH", "entered_domain": title_domain, "detected_domain": "medical_healthcare"}
                )

        # Case 4: Specific tech role mismatch (e.g. entered Python Developer, but JD has ZERO Python and is purely Java/Spring)
        if title_domain == "tech_python" and "python" in t_lower:
            if "python" not in jd_lower and jd_domain_scores.get("tech_java", 0) >= 3:
                return (
                    False,
                    f"Invalid job title and job description: You entered '{title}', but the job description is for a "
                    f"Java / Spring Boot role. Please enter a proper job description according to the role.",
                    {"code": "ROLE_SPECIFIC_MISMATCH", "entered_domain": "tech_python", "detected_domain": "tech_java"}
                )

        # Case 5: Verify that at least some relevant tokens or domain relevance from the job title exist in the JD
        stop_tokens = {"junior", "senior", "intern", "lead", "fresher", "trainee", "associate", "role", "job", "title"}
        meaningful_tokens = [
            tok for tok in re.findall(r"\b[a-z]{3,}\b", t_lower)
            if tok not in stop_tokens
        ]

        if meaningful_tokens:
            token_matches = [tok for tok in meaningful_tokens if tok in jd_lower]
            if not token_matches:
                # If title domain keywords don't match JD
                if title_domain and jd_domain_scores.get(title_domain, 0) == 0:
                    return (
                        False,
                        f"Invalid job title and job description: The job description does not mention or relate to '{title}'. "
                        f"Please enter a proper job description according to the role.",
                        {"code": "ZERO_TOKEN_MATCH", "title": title}
                    )
                # If title tokens don't appear in JD and JD has domain keywords from another domain
                if len(meaningful_tokens) >= 2 or sum(jd_domain_scores.values()) >= 2:
                    return (
                        False,
                        f"Invalid job title and job description: The job description does not mention or relate to '{title}'. "
                        f"Please enter a proper job description according to the role.",
                        {"code": "ZERO_TOKEN_MATCH", "title": title}
                    )

        return (True, "", {"code": "VALID", "domain": title_domain or top_jd_domain})
