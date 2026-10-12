"""Google Gemini API integration for generative features."""
import json
import logging
import re
from typing import Any, Dict, Optional

import requests

from config.settings import GEMINI_API_KEY, GEMINI_API_KEY_ALT, GEMINI_MODEL

logger = logging.getLogger(__name__)


class LLMModel:
    """Google Gemini API wrapper with key rotation and JSON validation."""

    def __init__(self, model_name: str = None, api_key: str = None):
        self.model_name = model_name or GEMINI_MODEL
        self.api_keys = [
            api_key or GEMINI_API_KEY,
            GEMINI_API_KEY_ALT
        ]
        # Clean API keys list of empty values
        self.api_keys = [key for key in self.api_keys if key and key.strip()]

    def generate(self, prompt: str, max_tokens: int = 8192) -> str:
        """Generate text from prompt via Google Gemini API with key rotation."""
        if not self.api_keys:
            logger.warning("No Gemini API keys configured; using fallback response.")
            return self._fallback_response(prompt)

        # Build request body
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "maxOutputTokens": max_tokens,
                "temperature": 0.2,
            }
        }

        # Try API keys in sequence (rotation / fallback)
        for i, key in enumerate(self.api_keys):
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={key}"
            try:
                logger.info("Attempting content generation using Gemini key %s...", i + 1)
                response = requests.post(
                    api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=45
                )
                
                # Check for rate limit (429) or other API key errors (400, 403)
                if response.status_code == 429:
                    logger.warning("Gemini key %s rate-limited. Trying alternative key...", i + 1)
                    continue
                if response.status_code in [400, 403]:
                    logger.warning("Gemini key %s returned code %s. Trying alternative key...", i + 1, response.status_code)
                    continue
                
                response.raise_for_status()
                res_data = response.json()
                
                # Parse standard Gemini response structure
                candidates = res_data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        text = parts[0].get("text", "")
                        if text:
                            return text
                            
                logger.warning("Gemini key %s response missing generated text. Trying alternative key...", i + 1)
            except requests.exceptions.RequestException as exc:
                logger.warning("Gemini key %s request failed: %s. Trying alternative key...", i + 1, exc)
                continue

        # If all keys fail, use mock fallback response
        logger.error("All Gemini API keys failed or were exhausted. Using fallback response.")
        return self._fallback_response(prompt)

    def generate_json(self, prompt: str, max_tokens: int = 8192) -> Dict[str, Any]:
        """Generate and parse JSON response with validation."""
        raw = self.generate(prompt, max_tokens)
        return self._parse_json(raw)

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Extract and validate JSON from LLM output."""
        if not text:
            return {"error": "Empty response from AI model."}

        # Remove markdown code fences if present
        cleaned = re.sub(r"```json\s*", "", text)
        cleaned = re.sub(r"```\s*", "", cleaned).strip()

        # Try direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning("Failed to parse LLM JSON response.")
        return {"error": "Could not parse AI response.", "raw": text[:500]}

    def _fallback_response(self, prompt: str) -> str:
        """Provide structured fallback when API is unavailable."""
        prompt_lower = prompt.lower()
        
        # Check for sample answer prompts first
        if "sample answer" in prompt_lower or "sample_answer" in prompt_lower or "interview-friendly sample answer" in prompt_lower:
            return json.dumps({
                "answer": "To prepare for this, I focus on key concepts. For example, in my past work with Machine Learning, I built robust pipelines using Python and evaluated models using cross-validation. I apply a similar structured, metrics-driven approach to this position.",
                "tips": [
                    "Be structured: describe the Situation, Task, Action, and Result (STAR method).",
                    "Keep it concise, and align it with the skills on your resume."
                ],
                "based_on_resume": True,
                "placeholders_used": []
            })
        
        # Check for roadmap prompts next
        if "roadmap" in prompt_lower:
            return json.dumps({
                "roadmap": [
                    {"priority": "HIGH", "topic": "Core Required Skills", "reason": "Missing or critical for the target role", "learning_objective": "Build foundational knowledge and work on small projects", "estimated_week": 1, "stage": "Foundation"},
                    {"priority": "MEDIUM", "topic": "Project Portfolio Integration", "reason": "Demonstrate practical application of skills", "learning_objective": "Integrate matched skills into a portfolio project", "estimated_week": 2, "stage": "Skill Building"},
                    {"priority": "LOW", "topic": "Interview Practice & Mock Sessions", "reason": "Prepare for behavioral and technical communication", "learning_objective": "Practice answering resume and HR questions", "estimated_week": 3, "stage": "Practice"},
                ],
                "interview_practice_phase": {
                    "focus_areas": ["Core technical concepts", "Resume project walk-throughs"],
                    "recommended_activities": ["Mock interviews with peers", "Reviewing sample answers"]
                },
                "summary": "Focus on missing core skills first, then align your projects with job responsibilities and practice mock interviews."
            })

        # Check for improvements/suggestions
        if "improvement" in prompt_lower or "suggestions" in prompt_lower:
            return json.dumps({
                "general_suggestions": [
                    "Highlight your matched skills prominently in the skills section.",
                    "Quantify achievements with specific metrics where possible.",
                    "Tailor your summary to align with the target job description.",
                ],
                "section_suggestions": [
                    {"section": "summary", "suggestion": "Add a targeted professional summary mentioning key matched skills.", "priority": "high"},
                    {"section": "skills", "suggestion": "Group skills by category (Programming, ML/DL, Tools) for ATS readability.", "priority": "medium"},
                ],
                "skill_highlighting": ["Emphasize skills that matched the job requirements."],
                "achievement_wording": ["Use action verbs and measurable outcomes in experience bullets."],
                "project_improvements": ["Add technologies used and business impact to project descriptions."],
                "ats_wording": ["Use standard section headers: Experience, Education, Skills, Projects."],
                "disclaimer": "AI service unavailable. These are general suggestions based on analysis results.",
            })

        # General interview questions (10 questions per category)
        if "interview" in prompt_lower or "questions" in prompt_lower:
            return json.dumps({
                "technical": [
                    {"question": "Explain a machine learning project from your resume and your specific contributions.", "topic": "Machine Learning", "difficulty": "medium"},
                    {"question": "How do you handle severe class imbalance in datasets when training classification models?", "topic": "Data Preprocessing", "difficulty": "medium"},
                    {"question": "Explain the difference between L1 and L2 regularization and when you would prefer one over the other.", "topic": "Model Optimization", "difficulty": "medium"},
                    {"question": "What metrics do you use to evaluate models beyond simple accuracy, and why?", "topic": "Model Evaluation", "difficulty": "easy"},
                    {"question": "Explain the inner mechanics of the Transformer architecture and self-attention mechanism.", "topic": "Deep Learning / NLP", "difficulty": "hard"},
                    {"question": "How do you detect and mitigate overfitting in deep neural networks?", "topic": "Deep Learning", "difficulty": "medium"},
                    {"question": "What is the bias-variance tradeoff and how do ensemble methods like Random Forest address it?", "topic": "Core ML", "difficulty": "medium"},
                    {"question": "Describe how you optimize deep learning model inference speed for real-time production deployment.", "topic": "MLOps", "difficulty": "hard"},
                    {"question": "How do gradient vanishing and exploding problems occur, and what techniques alleviate them?", "topic": "Neural Networks", "difficulty": "hard"},
                    {"question": "Explain how cross-validation works and why data leakage occurs during feature engineering.", "topic": "Validation", "difficulty": "medium"}
                ],
                "resume_based": [
                    {"question": "Walk me through your most relevant technical experience from your resume.", "focus": "Overall Experience"},
                    {"question": "In your resume, you listed Python and data libraries—what is the most complex data pipeline you built?", "focus": "Python Experience"},
                    {"question": "How did you measure the business or technical success in the projects mentioned on your resume?", "focus": "Impact Measurement"},
                    {"question": "What was the most challenging technical roadblock in your documented work, and how did you resolve it?", "focus": "Problem Solving"},
                    {"question": "How do your academic background and coursework directly prepare you for this position?", "focus": "Academic Foundation"},
                    {"question": "Describe the development lifecycle you followed for the projects highlighted in your profile.", "focus": "Development Process"},
                    {"question": "Which framework listed in your skills are you most proficient in, and what are its notable limitations?", "focus": "Tool Expertise"},
                    {"question": "Tell me about a time you had to adapt quickly to a tool or library not originally on your resume.", "focus": "Adaptability"},
                    {"question": "How did you ensure test coverage and reproducibility in your past project implementations?", "focus": "Quality Assurance"},
                    {"question": "Looking at your resume timeline, what is the biggest technical skill upgrade you achieved recently?", "focus": "Continuous Learning"}
                ],
                "project_based": [
                    {"question": "Describe the high-level architecture and tech stack choices of your primary resume project.", "project_reference": "System Architecture"},
                    {"question": "How did you collect, clean, and validate data for your machine learning projects?", "project_reference": "Data Engineering"},
                    {"question": "What tradeoffs did you consider when choosing algorithms or frameworks for your project?", "project_reference": "Technical Decision Making"},
                    {"question": "How did you monitor performance and resource consumption during project execution?", "project_reference": "Benchmarking"},
                    {"question": "If you had an extra month to iterate on this project, what major architectural improvement would you build?", "project_reference": "Future Iteration"},
                    {"question": "How did you deploy and host your project so users or evaluators could test it?", "project_reference": "Deployment & Delivery"},
                    {"question": "Describe the most critical bug or error you encountered in your project and your debugging methodology.", "project_reference": "Debugging"},
                    {"question": "How did you manage version control, branching, and documentation during project development?", "project_reference": "Version Control"},
                    {"question": "How did you prevent security risks or data leakage in your system?", "project_reference": "Security & Integrity"},
                    {"question": "Did you compare your model or system output with a baseline? What were the benchmark results?", "project_reference": "Evaluation Baseline"}
                ],
                "behavioral": [
                    {"question": "Tell me about a time you faced a difficult deadline and how you prioritized deliverables.", "competency": "Time Management"},
                    {"question": "Describe a situation where team members disagreed on technical direction. How did you resolve it?", "competency": "Conflict Resolution"},
                    {"question": "Give an example of a project where requirements changed midway through. How did you handle it?", "competency": "Adaptability"},
                    {"question": "How do you communicate complex technical concepts to non-technical stakeholders or clients?", "competency": "Communication"},
                    {"question": "Describe a mistake or failed experiment in your development career and what lesson you learned.", "competency": "Resilience & Growth"},
                    {"question": "How do you stay motivated and focused when working independently on long-term tasks?", "competency": "Self-Motivation"},
                    {"question": "Tell me about a time you mentored a peer or learned an important skill from a teammate.", "competency": "Teamwork"},
                    {"question": "How do you balance rapid prototyping speed with code maintainability and cleanliness?", "competency": "Engineering Ethics"},
                    {"question": "Describe a scenario where you took initiative beyond your assigned responsibilities.", "competency": "Proactivity"},
                    {"question": "When overwhelmed by multiple simultaneous bugs or issues, how do you decide what to fix first?", "competency": "Prioritization"}
                ],
                "skill_gap": [
                    {"question": "The role requires specific skills not prominent on your resume. How would you rapidly ramp up on them?", "skill": "Core Requirements", "learning_focus": "Ramp-up Strategy"},
                    {"question": "Walk me through how you learn a completely unfamiliar framework or API under a tight schedule.", "skill": "Unfamiliar Frameworks", "learning_focus": "Learning Methodology"},
                    {"question": "Have you built any side projects or completed coursework to bridge gaps in your target role?", "skill": "Hands-on Bridge Projects", "learning_focus": "Self-Initiated Learning"},
                    {"question": "How do you verify whether you have achieved production-level competence in a newly acquired skill?", "skill": "Skill Mastery Verification", "learning_focus": "Competence Benchmarking"},
                    {"question": "If assigned a task involving missing domain knowledge tomorrow, what are your first three steps?", "skill": "Domain Knowledge Gap", "learning_focus": "Execution Plan"},
                    {"question": "How do you leverage official documentation vs community tutorials when learning cutting-edge libraries?", "skill": "Research Capability", "learning_focus": "Resource Selection"},
                    {"question": "Describe a previous experience where you successfully bridged a significant skill gap on the job.", "skill": "Past Skill Gap Overcoming", "learning_focus": "Track Record"},
                    {"question": "What strategies do you use to retain and practically apply new technical concepts without forgetting them?", "skill": "Knowledge Retention", "learning_focus": "Active Application"},
                    {"question": "How do you approach learning best practices, design patterns, and code conventions in a new tech stack?", "skill": "Code Quality Standards", "learning_focus": "Software Craftsmanship"},
                    {"question": "What is your current roadmap for mastering the remaining technical requirements of this position?", "skill": "Career Growth Roadmap", "learning_focus": "Proactive Goal Setting"}
                ]
            })

        return json.dumps({"message": "AI service unavailable.", "fallback": True})
