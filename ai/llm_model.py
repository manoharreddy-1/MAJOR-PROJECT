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

        # General interview questions
        if "interview" in prompt_lower or "questions" in prompt_lower:
            return json.dumps({
                "technical": [{"question": "Explain a machine learning project from your resume.", "topic": "ML", "difficulty": "medium"}],
                "resume_based": [{"question": "Walk me through your most relevant experience.", "focus": "experience"}],
                "project_based": [{"question": "Describe the architecture of a project you built.", "project_reference": "Resume project"}],
                "behavioral": [{"question": "Tell me about a challenging problem you solved.", "competency": "problem-solving"}],
                "skill_gap": [{"question": "How would you approach learning a missing required skill?", "skill": "Missing skill", "learning_focus": "self-learning"}],
            })

        return json.dumps({"message": "AI service unavailable.", "fallback": True})
