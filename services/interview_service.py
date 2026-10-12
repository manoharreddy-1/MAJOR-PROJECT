"""Interview question generation service."""
import logging
from typing import Any, Dict

from ai.llm_model import LLMModel
from ai.prompts import interview_questions_prompt, sample_answer_prompt
from database.models import serialize_doc, utc_now
from database.mongodb import get_collection, COLLECTIONS

logger = logging.getLogger(__name__)


class InterviewService:
    """Generate job-specific interview questions and sample answers."""

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
        target_role = analysis.get("target_role", job.get("job_title", ""))

        prompt = interview_questions_prompt(
            resume=resume,
            job=job,
            target_role=target_role,
            missing_skills=missing,
        )

        questions = self.llm.generate_json(prompt)
        questions = self._ensure_min_questions(questions, target_role, missing)

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
        existing_str = "; ".join([q[:60] for q in (existing_questions or [])[:10]])
        prompt = f"""
Provide 5 NEW, challenging, and distinct interview questions for:
TARGET ROLE: {target_role or job.get('job_title', 'Role')}
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
            # Dynamic fallback
            more_q = [
                {"question": f"How do you approach solving edge-case architectural bottlenecks in {target_role or 'software engineering'}?", "topic": category, "difficulty": "hard"},
                {"question": f"Describe a situation where a technical design decision failed to meet SLA requirements. How did you diagnose it?", "topic": category, "difficulty": "hard"},
                {"question": f"Walk me through how you benchmark memory footprint versus runtime latency when evaluating algorithms.", "topic": category, "difficulty": "medium"},
                {"question": f"How do you structure automated regression test suites to guarantee backward compatibility in production?", "topic": category, "difficulty": "medium"},
                {"question": f"What advanced tooling or profiling instrumentation do you rely on during deep debugging sessions?", "topic": category, "difficulty": "medium"}
            ]
        return {"questions": more_q}

    def _ensure_min_questions(self, questions: Dict[str, Any], target_role: str, missing: list) -> Dict[str, Any]:
        """Ensure each of the 5 categories contains at least 10 high-quality questions."""
        if not isinstance(questions, dict):
            questions = {}

        # Default pool of questions per category
        fallback_pool = {
            "technical": [
                {"question": f"Explain a core {target_role or 'software'} engineering project from your resume and your individual contributions.", "topic": "System Design", "difficulty": "medium"},
                {"question": "How do you handle severe class imbalance or noisy outliers in datasets before training models?", "topic": "Data Preprocessing", "difficulty": "medium"},
                {"question": "Explain the practical difference between L1 and L2 regularization and how they influence feature selection.", "topic": "Model Optimization", "difficulty": "medium"},
                {"question": "What metrics do you use to evaluate performance beyond simple accuracy, and why are Precision, Recall, and F1 crucial?", "topic": "Evaluation Metrics", "difficulty": "easy"},
                {"question": "Explain the mechanics of self-attention in Transformer architectures and how multi-head attention improves representations.", "topic": "Deep Learning / NLP", "difficulty": "hard"},
                {"question": "How do you detect, monitor, and mitigate overfitting in deep neural networks during training?", "topic": "Deep Learning", "difficulty": "medium"},
                {"question": "What is the bias-variance tradeoff and how do ensemble methods like Random Forest or Gradient Boosting balance it?", "topic": "Machine Learning", "difficulty": "medium"},
                {"question": "Describe how you optimize model inference latency and throughput for deployment on resource-constrained servers.", "topic": "MLOps & Inference", "difficulty": "hard"},
                {"question": "How do gradient vanishing and exploding problems occur in deep networks, and what specific architectural remedies prevent them?", "topic": "Neural Networks", "difficulty": "hard"},
                {"question": "Explain how k-fold cross-validation works and how you prevent subtle data leakage during preprocessing and feature scaling.", "topic": "Validation", "difficulty": "medium"}
            ],
            "resume_based": [
                {"question": "Walk me through the most technically rigorous experience highlighted on your resume.", "focus": "Overall Experience"},
                {"question": "You listed several core technical skills on your resume—what is the most scalable system you built using them?", "focus": "Hands-on Implementation"},
                {"question": "How did you measure and quantify the business or user impact of the projects listed on your resume?", "focus": "Impact Measurement"},
                {"question": "What was the most challenging technical roadblock in your documented work, and how did you resolve it?", "focus": "Problem Solving"},
                {"question": "How do your academic background and foundational coursework directly prepare you for this position?", "focus": "Academic Foundation"},
                {"question": "Describe the software development methodology and lifecycle you followed for the projects on your profile.", "focus": "Development Methodology"},
                {"question": "Which programming framework listed in your skills are you most confident in, and what are its trade-offs?", "focus": "Tool Expertise"},
                {"question": "Tell me about a time you had to adapt quickly to a tool or library not originally in your comfort zone.", "focus": "Adaptability"},
                {"question": "How did you ensure test coverage, CI/CD validation, and code reproducibility in your previous work?", "focus": "Quality Assurance"},
                {"question": "Looking at your resume timeline, what is the single biggest technical capability upgrade you achieved recently?", "focus": "Continuous Learning"}
            ],
            "project_based": [
                {"question": "Describe the high-level architecture and technology stack decisions behind your primary resume project.", "project_reference": "System Architecture"},
                {"question": "How did you collect, clean, validate, and store data in the project mentioned on your resume?", "project_reference": "Data Engineering"},
                {"question": "What architectural tradeoffs did you consider when selecting the framework or model for your project?", "project_reference": "Technical Decision Making"},
                {"question": "How did you benchmark resource consumption and system performance during project execution?", "project_reference": "Benchmarking"},
                {"question": "If you had an additional engineering cycle to iterate on this project, what major feature or optimization would you implement?", "project_reference": "Future Iteration"},
                {"question": "How did you deploy, package (e.g., Docker), and host your project so external users could test it?", "project_reference": "Deployment & Delivery"},
                {"question": "Describe the most critical bug or concurrency error you encountered in your project and your debugging methodology.", "project_reference": "Debugging Methodology"},
                {"question": "How did you manage version control, Git branching strategies, and documentation during development?", "project_reference": "Version Control"},
                {"question": "How did you prevent security vulnerabilities, malicious inputs, or data leaks in your project?", "project_reference": "Security & Integrity"},
                {"question": "Did you compare your system output with an established baseline or heuristic? What were the benchmark results?", "project_reference": "Evaluation Baseline"}
            ],
            "behavioral": [
                {"question": "Tell me about a time you faced an aggressive project deadline and how you prioritized deliverables.", "competency": "Time Management"},
                {"question": "Describe a situation where team members disagreed on technical direction or architecture. How did you resolve it?", "competency": "Conflict Resolution"},
                {"question": "Give an example of a project where requirements shifted midway through development. How did you adapt?", "competency": "Adaptability"},
                {"question": "How do you effectively communicate technical architectural decisions to non-technical stakeholders or clients?", "competency": "Communication"},
                {"question": "Describe a mistake or flawed technical assumption you made in the past and what you learned from it.", "competency": "Resilience & Growth"},
                {"question": "How do you stay motivated and focused when working independently on open-ended or ambiguous tasks?", "competency": "Self-Motivation"},
                {"question": "Tell me about a time you mentored a peer or learned a valuable engineering practice from a teammate.", "competency": "Teamwork"},
                {"question": "How do you balance rapid prototyping velocity with long-term code quality, clean architecture, and technical debt?", "competency": "Engineering Standards"},
                {"question": "Describe a scenario where you took initiative to solve a problem beyond your assigned responsibilities.", "competency": "Proactivity"},
                {"question": "When facing multiple simultaneous production bugs or urgent issues, how do you decide what to triage first?", "competency": "Prioritization"}
            ],
            "skill_gap": [
                {"question": f"The target role requires skills not heavily detailed on your resume ({', '.join(missing[:3]) if missing else 'specialized skills'}). What is your ramp-up plan?", "skill": "Core Requirements", "learning_focus": "Ramp-up Strategy"},
                {"question": "Walk me through your methodical process for mastering an unfamiliar technical stack or framework under tight deadlines.", "skill": "Unfamiliar Frameworks", "learning_focus": "Learning Methodology"},
                {"question": "Have you built any personal projects or completed targeted coursework to bridge gaps for your target role?", "skill": "Bridge Projects", "learning_focus": "Self-Initiated Learning"},
                {"question": "How do you objectively verify whether you have reached production-ready competence in a newly acquired skill?", "skill": "Competence Benchmarking", "learning_focus": "Skill Verification"},
                {"question": "If assigned a task involving unfamiliar domain requirements tomorrow morning, what are your first three actionable steps?", "skill": "Domain Knowledge Gap", "learning_focus": "Execution Plan"},
                {"question": "How do you balance reading official technical documentation versus community tutorials when learning cutting-edge libraries?", "skill": "Research Capability", "learning_focus": "Resource Selection"},
                {"question": "Describe a past academic or professional experience where you successfully bridged a significant technical skill gap.", "skill": "Past Skill Gap", "learning_focus": "Track Record"},
                {"question": "What retention strategies do you use to ensure newly learned technical concepts are retained and practically applicable?", "skill": "Knowledge Retention", "learning_focus": "Active Application"},
                {"question": "How do you learn idiomatic coding conventions, design patterns, and best practices in a newly adopted programming language?", "skill": "Code Quality Standards", "learning_focus": "Software Craftsmanship"},
                {"question": "What is your continuous learning roadmap over the next 6 months to stay ahead in this domain?", "skill": "Career Growth Roadmap", "learning_focus": "Proactive Growth"}
            ]
        }

        # Ensure all 5 categories have at least 10 questions
        for cat, pool in fallback_pool.items():
            curr_list = questions.get(cat, [])
            if not isinstance(curr_list, list):
                curr_list = []
            
            # If AI returned fewer than 10 questions, append from the rich pool without duplicates
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
