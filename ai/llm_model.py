"""Google Gemini API integration with dynamic grounded fallback."""
import json
import logging
import re
from typing import Any, Dict, Optional

import requests

from config.settings import GEMINI_API_KEY, GEMINI_API_KEY_ALT, GEMINI_MODEL

logger = logging.getLogger(__name__)


class LLMModel:
    """Google Gemini API wrapper with key rotation, JSON validation, and dynamic offline generation."""

    def __init__(self, model_name: str = None, api_key: str = None):
        self.model_name = model_name or GEMINI_MODEL
        if api_key is not None:
            self.api_keys = [api_key] if api_key.strip() else []
        else:
            self.api_keys = [GEMINI_API_KEY, GEMINI_API_KEY_ALT]
        # Clean API keys list of empty values
        self.api_keys = [key for key in self.api_keys if key and key.strip()]

    def generate(self, prompt: str, max_tokens: int = 8192) -> str:
        """Generate text from prompt via Google Gemini API with key rotation."""
        if not self.api_keys:
            logger.warning("No Gemini API keys configured; using dynamic grounded fallback.")
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
                    timeout=2.5
                )

                if response.status_code == 429:
                    logger.warning("Gemini key %s rate-limited. Trying alternative key...", i + 1)
                    continue
                if response.status_code in [400, 403]:
                    logger.warning("Gemini key %s returned code %s (%s). Trying alternative key...", i + 1, response.status_code, response.text[:150])
                    continue

                response.raise_for_status()
                res_data = response.json()

                candidates = res_data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        text = parts[0].get("text", "")
                        if text:
                            return text

                logger.warning("Gemini key %s response missing generated text. Trying alternative key...", i + 1)
            except requests.exceptions.ConnectionError as exc:
                logger.warning("Gemini connection error: %s. Network unavailable, breaking to fallback.", exc)
                break
            except requests.exceptions.Timeout as exc:
                logger.warning("Gemini key %s timed out: %s.", i + 1, exc)
                continue
            except requests.exceptions.RequestException as exc:
                logger.warning("Gemini key %s request failed: %s. Trying alternative key...", i + 1, exc)
                continue

        logger.info("Gemini API unavailable or keys exhausted. Using dynamic grounded fallback generator.")
        return self._fallback_response(prompt)

    def generate_json(self, prompt: str, max_tokens: int = 8192) -> Dict[str, Any]:
        """Generate and parse JSON response with validation."""
        raw = self.generate(prompt, max_tokens)
        return self._parse_json(raw)

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Extract and validate JSON from LLM output."""
        if not text:
            return {"error": "Empty response from AI model."}

        cleaned = re.sub(r"```json\s*", "", text)
        cleaned = re.sub(r"```\s*", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning("Failed to parse LLM JSON response.")
        return {"error": "Could not parse AI response.", "raw": text[:500]}

    def _fallback_response(self, prompt: str) -> str:
        """Provide structured dynamic fallback when Gemini API is unavailable or rate limited."""
        prompt_lower = prompt.lower()

        try:
            from ai.dynamic_generator import (
                generate_grounded_interview_questions,
                generate_grounded_resume_improvement,
                generate_grounded_roadmap,
                generate_grounded_sample_answer,
            )

            # Check for sample answer prompts first
            if "sample answer" in prompt_lower or "sample_answer" in prompt_lower or "interview-friendly sample answer" in prompt_lower:
                return json.dumps(generate_grounded_sample_answer(prompt))

            # Check for roadmap prompts next
            if "roadmap" in prompt_lower:
                return json.dumps(generate_grounded_roadmap(prompt=prompt))

            # Check for improvements/suggestions
            if "improvement" in prompt_lower or "suggestions" in prompt_lower or "resume improvement" in prompt_lower:
                return json.dumps(generate_grounded_resume_improvement(prompt))

            # General interview questions
            if "interview" in prompt_lower or "questions" in prompt_lower:
                return json.dumps(generate_grounded_interview_questions(prompt))
        except Exception as exc:
            logger.exception("Dynamic fallback generation failed: %s", exc)

        return json.dumps({"message": "AI service offline. Using heuristic fallback.", "fallback": True})
