"""AI Course Generator Service with Gemini AI & YouTube API Integration.

Based on the 'AI Course Generator' specification:
- Generates structured course outlines & chapter layouts
- Generates detailed chapter-wise explanations and practical code examples
- Fetches relevant YouTube tutorial videos for each chapter
- Stores and retrieves courses in MongoDB / in-memory DB
"""
import logging
import os
import uuid
from typing import Any, Dict, List, Optional
import requests

from ai.llm_model import LLMModel
from database.models import utc_now, serialize_doc, to_object_id
from database.mongodb import get_collection, COLLECTIONS
from config.settings import YOUTUBE_API_KEY
from services.course_content_catalog import get_curated_course

logger = logging.getLogger(__name__)


class CourseService:
    """Handles AI Course creation, chapter generation, and YouTube video integration."""

    def __init__(self):
        self.llm = LLMModel()
        self.courses_col = get_collection(COLLECTIONS["courses"])
        self.chapters_col = get_collection(COLLECTIONS["chapters"])

    def fetch_youtube_video(self, query: str) -> Optional[Dict[str, str]]:
        """Fetch the most relevant educational YouTube video for a topic/chapter."""
        api_key = YOUTUBE_API_KEY
        if not api_key:
            return None

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": f"{query} programming tutorial",
            "maxResults": 1,
            "type": "video",
            "order": "relevance",
            "relevanceLanguage": "en",
            "videoCategoryId": "27",  # Education category
            "safeSearch": "strict",
            "videoDuration": "medium",
            "key": api_key,
        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    item = items[0]
                    video_id = item.get("id", {}).get("videoId")
                    snippet = item.get("snippet", {})
                    if video_id:
                        return {
                            "video_id": video_id,
                            "title": snippet.get("title", ""),
                            "description": snippet.get("description", ""),
                            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                            "channel": snippet.get("channelTitle", ""),
                        }
            else:
                logger.warning("YouTube API error (status %s): %s", resp.status_code, resp.text[:200])
        except Exception as e:
            logger.warning("Failed to fetch YouTube video for '%s': %s", query, e)

        # Direct mapping for top programming topics so video embed & thumbnail always work
        query_lower = query.lower()
        topic_video_map = {
            "java basics": {"id": "eIrMbAQSU34", "title": "Java Tutorial for Beginners - Programming with Mosh", "channel": "Programming with Mosh"},
            "control flow": {"id": "A74TOX803D0", "title": "Java Control Flow, Loops and Conditionals", "channel": "freeCodeCamp.org"},
            "oop": {"id": "xk4_1vDrzzo", "title": "Java Object Oriented Programming (OOP) - Full Course", "channel": "freeCodeCamp.org"},
            "collections": {"id": "9kgt37Xp71k", "title": "Java Collections Framework Full Tutorial", "channel": "Amigoscode"},
            "exception": {"id": "1XAfapoKshY", "title": "Java Exception Handling Tutorial", "channel": "Telusko"},
            "java": {"id": "eIrMbAQSU34", "title": "Java Tutorial for Beginners", "channel": "Programming with Mosh"},
            "python": {"id": "_uQrJ0TkZlc", "title": "Python Tutorial for Beginners - Full Course", "channel": "Programming with Mosh"},
            "data structures": {"id": "RBSGKlAvoiM", "title": "Data Structures and Algorithms in Java", "channel": "freeCodeCamp.org"},
            "spring boot": {"id": "9SGDpanrc8U", "title": "Spring Boot Tutorial for Beginners", "channel": "Amigoscode"}
        }

        for k, v in topic_video_map.items():
            if k in query_lower:
                return {
                    "video_id": v["id"],
                    "title": v["title"],
                    "description": f"Curated high-definition tutorial for {query}.",
                    "thumbnail": f"https://img.youtube.com/vi/{v['id']}/hqdefault.jpg",
                    "channel": v["channel"]
                }

        # Fallback search video ID if network fails or quota is exhausted
        default_id = "eIrMbAQSU34" if "java" in query_lower else "_uQrJ0TkZlc" if "python" in query_lower else "kqtD5dpn9C8"
        return {
            "video_id": default_id,
            "title": f"Educational Tutorial: {query}",
            "thumbnail": f"https://img.youtube.com/vi/{default_id}/hqdefault.jpg",
            "channel": "YouTube Education",
            "search_query": f"{query} tutorial",
            "youtube_search_url": f"https://www.youtube.com/results?search_query={requests.utils.quote(query + ' tutorial')}"
        }

    def generate_course_layout(
        self,
        topic: str,
        category: str = "Technology & Science",
        level: str = "Beginner",
        duration: str = "1 Hour",
        num_chapters: int = 5,
        include_video: str = "Yes",
        description: str = "",
        user_name: str = "User",
        user_id: str = None
    ) -> Dict[str, Any]:
        """Generate course layout/outline using Gemini AI."""
        prompt = f"""
You are an expert curriculum designer and educator.
Create a structured course layout for:
- Course Topic: {topic}
- Category: {category}
- Difficulty Level: {level}
- Target Duration: {duration}
- Number of Chapters: {num_chapters}
- Additional Description/Focus: {description}

Return ONLY valid JSON in the exact following schema:
{{
  "name": "{topic}",
  "category": "{category}",
  "level": "{level}",
  "duration": "{duration}",
  "summary": "2-3 sentences overview of the course and what the student will achieve.",
  "courseBanner": "/placeholder.svg",
  "chapters": [
    {{
      "chapter_id": 1,
      "name": "Chapter Title",
      "about": "Clear 1-2 sentence description of what this chapter covers.",
      "duration": "15 mins"
    }}
  ]
}}
"""
        curated = get_curated_course(topic)
        if curated:
            response = {
                "name": curated.get("name", topic),
                "category": curated.get("category", category),
                "level": level,
                "duration": duration,
                "summary": curated.get("summary", ""),
                "courseBanner": "/placeholder.svg",
                "chapters": [
                    {
                        "chapter_id": ch["chapter_id"],
                        "name": ch["name"],
                        "about": ch["about"],
                        "duration": ch.get("duration", "15 mins"),
                        "coding_challenge": ch.get("coding_challenge")
                    }
                    for ch in curated["chapters"][:num_chapters]
                ]
            }
        else:
            response = self.llm.generate_json(prompt)
            
            # Validate or fallback
            if "chapters" not in response or not isinstance(response.get("chapters"), list):
                # Construct standard chapters
                chapters = []
                for i in range(1, num_chapters + 1):
                    chapters.append({
                        "chapter_id": i,
                        "name": f"Module {i}: Fundamental Principles of {topic}",
                        "about": f"Comprehensive guide to core concepts and practical workflows in {topic}.",
                        "duration": f"{max(10, 60 // num_chapters)} mins",
                    })
                response = {
                    "name": topic,
                    "category": category,
                    "level": level,
                    "duration": duration,
                    "summary": f"A comprehensive {level}-level course covering fundamental and advanced concepts in {topic}.",
                    "courseBanner": "/placeholder.svg",
                    "chapters": chapters,
                }

        course_id = str(uuid.uuid4())[:12]
        doc = {
            "course_id": course_id,
            "name": response.get("name", topic),
            "category": category,
            "level": level,
            "duration": duration,
            "include_video": include_video,
            "summary": response.get("summary", ""),
            "courseBanner": response.get("courseBanner", "/placeholder.svg"),
            "chapters_outline": response.get("chapters", []),
            "created_by": user_id or "anonymous",
            "user_name": user_name or "Learner",
            "publish": False,
            "created_at": utc_now(),
        }

        self.courses_col.insert_one(doc)
        return {"course_id": course_id, "course": serialize_doc(doc)}

    def generate_chapter_content(
        self,
        course_id: str,
        chapter_id: int,
        chapter_name: str,
        course_name: str
    ) -> Dict[str, Any]:
        """Generate in-depth chapter content (explanations + code examples) and attach video."""
        prompt = f"""
You are an expert tutor creating lecture content for:
Course: {course_name}
Chapter {chapter_id}: {chapter_name}

Provide detailed educational content with practical code examples.
Return ONLY valid JSON matching this structure:
{{
  "title": "{chapter_name}",
  "explanation": "Detailed, thorough step-by-step explanation of the concepts in this chapter.",
  "key_takeaways": [
    "Takeaway 1",
    "Takeaway 2",
    "Takeaway 3"
  ],
  "code_examples": [
    {{
      "title": "Example Title",
      "language": "python",
      "code": "# Code demonstrating the concept\\nprint('Hello world')",
      "explanation": "Brief breakdown of how this code works."
    }}
  ]
}}
"""
        # Check curated knowledge base first
        curated = get_curated_course(course_name)
        curated_ch = None
        if curated:
            for c in curated["chapters"]:
                if c["chapter_id"] == chapter_id or c["name"].lower() == chapter_name.lower():
                    curated_ch = c
                    break

        if curated_ch:
            content_res = {
                "title": curated_ch["name"],
                "explanation": curated_ch["explanation"],
                "key_takeaways": curated_ch["key_takeaways"],
                "code_examples": curated_ch["code_examples"],
                "coding_challenge": curated_ch.get("coding_challenge"),
                "quiz": curated_ch.get("quiz", [])
            }
        else:
            content_res = self.llm.generate_json(prompt)
            if not content_res or "explanation" not in content_res:
                content_res = {
                    "title": chapter_name,
                    "explanation": f"In this chapter, we explore {chapter_name} in detail. Understanding these fundamental principles is key to mastering {course_name}.",
                    "key_takeaways": [
                        f"Core principles behind {chapter_name}",
                        "Implementation techniques and best practices",
                        "Practical application in real-world scenarios"
                    ],
                    "code_examples": [
                        {
                            "title": f"Implementing {chapter_name}",
                            "language": "python",
                            "code": f"# Implementation for {chapter_name}\ndef execute_task():\n    print('Executing: {chapter_name}')\n\nexecute_task()",
                            "explanation": f"Basic code example demonstrating {chapter_name}."
                        }
                    ],
                    "coding_challenge": {
                        "title": f"{chapter_name} Challenge",
                        "description": f"Write a solution to demonstrate mastery of {chapter_name}.",
                        "starter_code": "def solution():\n    # Implement solution\n    return 'Success'\n\nprint(solution())",
                        "language": "python",
                        "test_cases": [
                            {"input": "default", "expected_output": "Success"}
                        ]
                    },
                    "quiz": [
                        {
                            "question": f"What is the primary role of {chapter_name} in software engineering?",
                            "options": [
                                f"To provide foundational structure and logic for {chapter_name}",
                                "To manage direct memory allocation in the hardware",
                                "To replace operating system drivers",
                                "None of the above"
                            ],
                            "correct_answer": 0,
                            "explanation": f"{chapter_name} forms an integral conceptual and practical pillar in modern engineering."
                        },
                        {
                            "question": "Which principle ensures robust software architecture?",
                            "options": [
                                "Writing modular, testable, and well-structured code",
                                "Hardcoding parameters in all functions",
                                "Avoiding error handling and logs",
                                "Ignoring unit test validations"
                            ],
                            "correct_answer": 0,
                            "explanation": "Modularity and testing ensure maintainability and high code quality."
                        }
                    ]
                }
            elif not content_res.get("quiz"):
                content_res["quiz"] = [
                    {
                        "question": f"Which best describes the primary focus of {chapter_name}?",
                        "options": [
                            f"Core concepts and practical application of {chapter_name}",
                            "Low-level kernel device management",
                            "Database indexing only",
                            "None of the above"
                        ],
                        "correct_answer": 0,
                        "explanation": f"This chapter emphasizes the core paradigms of {chapter_name}."
                    }
                ]

        # Fetch YouTube video
        video_info = self.fetch_youtube_video(f"{course_name} {chapter_name}")

        chapter_doc = {
            "course_id": course_id,
            "chapter_id": chapter_id,
            "name": chapter_name,
            "content": content_res,
            "video": video_info,
            "created_at": utc_now()
        }

        # Upsert in chapters collection
        self.chapters_col.update_one(
            {"course_id": course_id, "chapter_id": chapter_id},
            {"$set": chapter_doc},
            upsert=True
        )

        return serialize_doc(chapter_doc)

    def generate_full_course_content(self, course_id: str) -> Dict[str, Any]:
        """Generate content for all chapters in a course outline and mark published."""
        course = self.courses_col.find_one({"course_id": course_id})
        if not course:
            raise ValueError(f"Course {course_id} not found")

        chapters_outline = course.get("chapters_outline", [])
        course_name = course.get("name", "Course")
        generated_chapters = []

        for ch in chapters_outline:
            ch_id = ch.get("chapter_id", 1)
            ch_name = ch.get("name", f"Chapter {ch_id}")
            ch_data = self.generate_chapter_content(
                course_id=course_id,
                chapter_id=ch_id,
                chapter_name=ch_name,
                course_name=course_name
            )
            generated_chapters.append(ch_data)

        # Mark course as published
        self.courses_col.update_one(
            {"course_id": course_id},
            {"$set": {"publish": True, "updated_at": utc_now()}}
        )

        return {
            "course_id": course_id,
            "published": True,
            "chapters_count": len(generated_chapters)
        }

    def get_course_details(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full course details along with generated chapters."""
        course = self.courses_col.find_one({"course_id": course_id})
        if not course:
            return None

        chapters = list(self.chapters_col.find({"course_id": course_id}))
        if not chapters and course.get("chapters_outline"):
            # Auto-populate chapters so user never encounters an uninitialized course
            for ch in course["chapters_outline"]:
                ch_id = ch.get("chapter_id", 1)
                ch_name = ch.get("name", f"Chapter {ch_id}")
                self.generate_chapter_content(
                    course_id=course_id,
                    chapter_id=ch_id,
                    chapter_name=ch_name,
                    course_name=course.get("name", "Course")
                )
            chapters = list(self.chapters_col.find({"course_id": course_id}))

        chapters.sort(key=lambda c: c.get("chapter_id", 0))

        result = serialize_doc(course)
        result["chapters"] = [serialize_doc(ch) for ch in chapters]
        return result

    def list_courses(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve list of courses for dashboard and explore views."""
        courses = list(self.courses_col.find().sort("created_at", -1).limit(limit))
        return [serialize_doc(c) for c in courses]
