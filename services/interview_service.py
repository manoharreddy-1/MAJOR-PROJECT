"""Interview question generation service grounded in target role and resume."""
import logging
from typing import Any, Dict, List

from ai.llm_model import LLMModel
from ai.prompts import interview_questions_prompt, sample_answer_prompt
from ai.dynamic_generator import (
    DOMAIN_TECHNICAL_QUESTIONS,
    detect_domain,
    generate_grounded_interview_questions,
)
from database.models import serialize_doc, utc_now
from database.mongodb import get_collection, COLLECTIONS

logger = logging.getLogger(__name__)


class InterviewService:
    """Generate job-specific interview questions and grounded sample answers."""

    def __init__(self):
        self.llm = LLMModel()
        self.collection = get_collection(COLLECTIONS["interview_preparations"])

    def generate(
        self,
        resume: Dict,
        job: Dict,
        analysis: Dict,
        user_id: str = None,
        analysis_id: str = None,
    ) -> Dict[str, Any]:
        missing = [s["skill"] for s in analysis.get("skill_analysis", {}).get("missing", [])]
        target_role = analysis.get("target_role") or job.get("job_title", "Software Engineer")

        prompt = interview_questions_prompt(
            resume=resume,
            job=job,
            target_role=target_role,
            missing_skills=missing,
        )

        questions = self.llm.generate_json(prompt)
        questions = self._ensure_min_questions(questions, target_role, missing, resume)

        doc = {
            "user_id": user_id,
            "analysis_id": analysis_id,
            "target_role": target_role,
            "questions": questions,
            "created_at": utc_now(),
        }
        result = self.collection.insert_one(doc)

        return {
            "interview_id": str(result.inserted_id),
            "questions": questions,
        }

    def generate_more_questions(
        self,
        resume: Dict,
        job: Dict,
        category: str,
        existing_questions: list = None,
        target_role: str = ""
    ) -> Dict[str, Any]:
        """Generate 5 additional fresh questions for a specific category."""
        target_role = target_role or job.get("job_title", "Software Engineer")
        domain = detect_domain(target_role, resume.get("skills", []))
        existing_str = "; ".join([q[:60] for q in (existing_questions or [])[:10]])

        prompt = f"""
Provide 5 NEW, challenging, and distinct interview questions for:
TARGET ROLE: {target_role}
CATEGORY: {category}
AVOID EXISTING QUESTIONS: {existing_str}
RESUME SKILLS: {', '.join(resume.get('skills', [])[:10])}

Return ONLY valid JSON in format:
{{
    "questions": [
        {{"question": "New in-depth question...", "topic": "{category}", "difficulty": "medium", "competency": "analytical thinking"}}
    ]
}}
"""
        res = self.llm.generate_json(prompt)
        more_q = res.get("questions", [])

        if not more_q or not isinstance(more_q, list):
            # Dynamic domain-aware fallback questions
            if domain == "java":
                fallback_pool = [
                    {"question": f"How do you design a high-throughput, low-latency microservice in {target_role} using Spring Boot and asynchronous messaging?", "topic": category, "difficulty": "hard"},
                    {"question": "Explain how you handle distributed transactions and eventual consistency across multiple microservices (e.g. Saga Pattern).", "topic": category, "difficulty": "hard"},
                    {"question": "What profiling tools (VisualVM, JProfiler, Async-Profiler) do you use to diagnose Java thread contention or memory leaks?", "topic": category, "difficulty": "hard"},
                    {"question": "How do you implement resilient database connection pooling (HikariCP) and optimize prepared statements in high-load services?", "topic": category, "difficulty": "medium"},
                    {"question": "Describe your strategy for contract-testing RESTful APIs to prevent breaking changes for downstream consumers.", "topic": category, "difficulty": "medium"},
                ]
            elif domain == "frontend":
                fallback_pool = [
                    {"question": f"How do you optimize initial page bundle size and tree-shaking in modern {target_role} web applications?", "topic": category, "difficulty": "hard"},
                    {"question": "Explain how Web Workers can offload heavy computational tasks from the main UI thread to prevent interface freezing.", "topic": category, "difficulty": "medium"},
                    {"question": "Describe how you implement accessible (WCAG AA compliant) component libraries from scratch.", "topic": category, "difficulty": "medium"},
                    {"question": "How do you structure client-side caching and stale-while-revalidate data fetching with libraries like React Query or SWR?", "topic": category, "difficulty": "medium"},
                    {"question": "What is your strategy for monitoring client-side runtime errors and performance anomalies in production?", "topic": category, "difficulty": "medium"},
                ]
            else:
                fallback_pool = [
                    {"question": f"How do you approach solving edge-case architectural bottlenecks in {target_role}?", "topic": category, "difficulty": "hard"},
                    {"question": "Describe a situation where a technical design decision failed to meet SLA requirements. How did you diagnose it?", "topic": category, "difficulty": "hard"},
                    {"question": "Walk me through how you benchmark memory footprint versus runtime latency when evaluating algorithms.", "topic": category, "difficulty": "medium"},
                    {"question": "How do you structure automated regression test suites to guarantee backward compatibility in production?", "topic": category, "difficulty": "medium"},
                    {"question": "What advanced tooling or profiling instrumentation do you rely on during deep debugging sessions?", "topic": category, "difficulty": "medium"},
                ]
            more_q = fallback_pool

        return {"questions": more_q}

    def _ensure_min_questions(
        self,
        questions: Dict[str, Any],
        target_role: str,
        missing: list,
        resume: Dict = None,
    ) -> Dict[str, Any]:
        """Ensure each of the 5 categories contains at least 10 high-quality questions for target role."""
        if not isinstance(questions, dict):
            questions = {}

        resume = resume or {}
        candidate_skills = resume.get("skills", [])
        domain = detect_domain(target_role, candidate_skills)
        grounded_pool = DOMAIN_TECHNICAL_QUESTIONS.get(domain, DOMAIN_TECHNICAL_QUESTIONS["general"])

        top_skill = candidate_skills[0] if candidate_skills else target_role
        projects = resume.get("projects", [])
        primary_project = projects[0] if projects else f"core {target_role} project"

        fallback_pool = {
            "technical": grounded_pool,
            "resume_based": [
                {"question": f"Walk me through your hands-on experience using {top_skill} from your resume.", "focus": f"{top_skill} Experience"},
                {"question": f"You listed core technical skills on your resume—what is the most scalable system you built using them?", "focus": "Hands-on Implementation"},
                {"question": "How did you measure and quantify the business or user impact of the projects listed on your resume?", "focus": "Impact Measurement"},
                {"question": "What was the most challenging technical roadblock in your documented work, and how did you resolve it?", "focus": "Problem Solving"},
                {"question": f"How do your academic background and foundational coursework directly prepare you for this {target_role} position?", "focus": "Academic Foundation"},
                {"question": "Describe the software development methodology and lifecycle you followed for the projects on your profile.", "focus": "Development Methodology"},
                {"question": "Which programming framework listed in your skills are you most confident in, and what are its trade-offs?", "focus": "Tool Expertise"},
                {"question": "Tell me about a time you had to adapt quickly to a tool or library not originally in your comfort zone.", "focus": "Adaptability"},
                {"question": "How did you ensure test coverage, CI/CD validation, and code reproducibility in your previous work?", "focus": "Quality Assurance"},
                {"question": "Looking at your resume timeline, what is the single biggest technical capability upgrade you achieved recently?", "focus": "Continuous Learning"},
            ],
            "project_based": [
                {"question": f"Describe the high-level architecture and technology stack decisions behind '{primary_project}'.", "project_reference": "System Architecture"},
                {"question": f"How did you validate data inputs, handle error states, and prevent security vulnerabilities in '{primary_project}'?", "project_reference": "Security & Validation"},
                {"question": f"What architectural tradeoffs did you consider when selecting the framework or model for '{primary_project}'?", "project_reference": "Technical Decision Making"},
                {"question": f"How did you benchmark resource consumption and system performance during execution of '{primary_project}'?", "project_reference": "Benchmarking"},
                {"question": f"If you had an additional engineering cycle to iterate on '{primary_project}', what major feature or optimization would you implement?", "project_reference": "Future Iteration"},
                {"question": f"How did you deploy, package (e.g., Docker), and host '{primary_project}' so external users could test it?", "project_reference": "Deployment & Delivery"},
                {"question": f"Describe the most critical bug or concurrency error you encountered in '{primary_project}' and your debugging methodology.", "project_reference": "Debugging Methodology"},
                {"question": "How did you manage version control, Git branching strategies, and documentation during development?", "project_reference": "Version Control"},
                {"question": "How did you prevent security vulnerabilities, malicious inputs, or data leaks in your project?", "project_reference": "Security & Integrity"},
                {"question": "Did you compare your system output with an established baseline or heuristic? What were the benchmark results?", "project_reference": "Evaluation Baseline"},
            ],
            "behavioral": [
                {"question": f"Tell me about a time you faced an aggressive project deadline for a {target_role} deliverable and how you prioritized tasks.", "competency": "Time Management"},
                {"question": "Describe a situation where team members disagreed on technical direction or architecture. How did you resolve it?", "competency": "Conflict Resolution"},
                {"question": "Give an example of a project where requirements shifted midway through development. How did you adapt?", "competency": "Adaptability"},
                {"question": "How do you effectively communicate technical architectural decisions to non-technical stakeholders or clients?", "competency": "Communication"},
                {"question": "Describe a mistake or flawed technical assumption you made in the past and what you learned from it.", "competency": "Resilience & Growth"},
                {"question": "How do you stay motivated and focused when working independently on open-ended or ambiguous tasks?", "competency": "Self-Motivation"},
                {"question": "Tell me about a time you mentored a peer or learned a valuable engineering practice from a teammate.", "competency": "Teamwork"},
                {"question": "How do you balance rapid prototyping velocity with long-term code quality, clean architecture, and technical debt?", "competency": "Engineering Standards"},
                {"question": "Describe a scenario where you took initiative to solve a problem beyond your assigned responsibilities.", "competency": "Proactivity"},
                {"question": "When facing multiple simultaneous production bugs or urgent issues, how do you decide what to triage first?", "competency": "Prioritization"},
            ],
            "skill_gap": [
                {"question": f"The target role requires skills not heavily detailed on your resume ({', '.join(missing[:3]) if missing else 'specialized skills'}). What is your ramp-up plan?", "skill": missing[0] if missing else "Core Requirements", "learning_focus": "Ramp-up Strategy"},
                {"question": "Walk me through your methodical process for mastering an unfamiliar technical stack or framework under tight deadlines.", "skill": "Unfamiliar Frameworks", "learning_focus": "Learning Methodology"},
                {"question": f"Have you built any personal projects or completed targeted coursework to bridge gaps for {target_role}?", "skill": "Bridge Projects", "learning_focus": "Self-Initiated Learning"},
                {"question": "How do you objectively verify whether you have reached production-ready competence in a newly acquired skill?", "skill": "Competence Benchmarking", "learning_focus": "Skill Verification"},
                {"question": "If assigned a task involving unfamiliar domain requirements tomorrow morning, what are your first three actionable steps?", "skill": "Domain Knowledge Gap", "learning_focus": "Execution Plan"},
                {"question": "How do you balance reading official technical documentation versus community tutorials when learning cutting-edge libraries?", "skill": "Research Capability", "learning_focus": "Resource Selection"},
                {"question": "Describe a past academic or professional experience where you successfully bridged a significant technical skill gap.", "skill": "Past Skill Gap", "learning_focus": "Track Record"},
                {"question": "What retention strategies do you use to ensure newly learned technical concepts are retained and practically applicable?", "skill": "Knowledge Retention", "learning_focus": "Active Application"},
                {"question": f"How do you learn idiomatic coding conventions, design patterns, and best practices in {target_role}?", "skill": "Code Quality Standards", "learning_focus": "Software Craftsmanship"},
                {"question": "What is your continuous learning roadmap over the next 6 months to stay ahead in this domain?", "skill": "Career Growth Roadmap", "learning_focus": "Proactive Growth"},
            ]
        }

        # Ensure all 5 categories have at least 10 questions
        for cat, pool in fallback_pool.items():
            curr_list = questions.get(cat, [])
            if not isinstance(curr_list, list):
                curr_list = []

            # If fewer than 10 questions, fill from role-specific pool
            if len(curr_list) < 10:
                existing_texts = {q.get("question", "").lower() for q in curr_list if isinstance(q, dict)}
                for fallback_q in pool:
                    if fallback_q["question"].lower() not in existing_texts:
                        curr_list.append(fallback_q)
                    if len(curr_list) >= 10:
                        break
            questions[cat] = curr_list

        return questions

    def generate_sample_answer(
        self, question: str, resume: Dict, category: str
    ) -> Dict[str, Any]:
        prompt = sample_answer_prompt(question, resume, category)
        return self.llm.generate_json(prompt)
