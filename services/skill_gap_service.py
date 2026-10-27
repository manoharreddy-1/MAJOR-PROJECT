"""Skill gap analysis using SBERT semantic matching and domain knowledge."""
import logging
import re
from typing import Any, Dict, List

from ai.embeddings import best_match_similarity
from config.settings import HIGH_SKILL_THRESHOLD, MEDIUM_SKILL_THRESHOLD
from utils.skill_normalizer import (
    clean_skill_candidate,
    deduplicate_skills,
    normalize_skill_name,
    SKILL_BLACKLIST,
)
from utils.clean_skill_extractor import clean_missing_skills

logger = logging.getLogger(__name__)


# Curated learning objectives for top technical skills
CURATED_OBJECTIVES = {
    "java": "Master Core Java: OOP principles, Collections Framework, Multithreading, Exception Handling, Streams API, and JVM memory internals.",
    "spring": "Learn Spring Framework core: Dependency Injection, Inversion of Control (IoC), Aspect-Oriented Programming, and Spring Context.",
    "spring boot": "Build production-ready RESTful microservices with Spring Boot, Spring Data JPA, Spring Security, and actuator monitoring.",
    "microservices": "Study microservices architecture patterns: service discovery (Eureka), API gateways, circuit breakers (Resilience4j), and asynchronous messaging.",
    "hibernate": "Master ORM with Hibernate/JPA: entity relationships, lazy vs eager loading, JPQL/HQL queries, second-level caching, and transaction management.",
    "rest apis": "Design and build RESTful APIs adhering to HTTP standards, status codes, JSON serialization, OpenAPI/Swagger docs, and token authentication.",
    "python": "Master idiomatic Python 3, object-oriented design, comprehensions, decorators, generators, and package management with pip/virtualenv.",
    "django": "Develop robust web applications using Django: MTV architecture, ORM models, migration workflows, admin interface, and Django REST Framework.",
    "fastapi": "Build high-performance asynchronous APIs using FastAPI, Pydantic type validation, and automatic OpenAPI interactive documentation.",
    "javascript": "Master modern JavaScript (ES6+): closures, promises, async/await, event loop, DOM manipulation, and modular architecture.",
    "typescript": "Learn TypeScript static typing: interfaces, type unions, generics, enums, and compile-time type safety for full-stack apps.",
    "react": "Build dynamic user interfaces with React: functional components, Hooks (useState, useEffect, useMemo), Context API, and state management.",
    "node.js": "Build scalable server-side applications with Node.js: non-blocking event-driven I/O, Express routing, middleware, and database drivers.",
    "sql": "Develop strong relational database skills: complex JOINs, subqueries, aggregation, indexing, ACID transactions, and query optimization.",
    "mysql": "Practice MySQL database administration, schema modeling, stored procedures, indexing strategies, and query performance tuning.",
    "postgresql": "Learn PostgreSQL advanced capabilities: JSONB data types, window functions, CTEs, indexing with GiST/GIN, and ACID guarantees.",
    "mongodb": "Learn NoSQL document modeling with MongoDB: schema design, aggregation pipelines, replica sets, and Mongoose ODM integration.",
    "redis": "Master in-memory caching and message pub/sub with Redis: data structures (strings, hashes, lists, sets, sorted sets), and TTL caching patterns.",
    "aws": "Learn AWS core services: EC2 computing, S3 object storage, RDS databases, IAM security roles, and basic CloudFormation/serverless deployment.",
    "docker": "Learn containerization basics: writing multi-stage Dockerfiles, managing container networks/volumes, and running multi-container apps with Docker Compose.",
    "kubernetes": "Understand Kubernetes cluster orchestration: pods, deployments, services, configmaps, secrets, ingress controllers, and auto-scaling.",
    "ci/cd": "Build automated CI/CD deployment pipelines using GitHub Actions or Jenkins: test automation, linting, Docker packaging, and automated releases.",
    "git": "Master Git version control: branching workflows, rebase vs merge, resolving merge conflicts, git hooks, and collaborative pull request reviews.",
    "linux": "Develop Linux command-line fluency: file system navigation, permissions (chmod/chown), process management, bash scripting, and system monitoring.",
    "machine learning": "Study core ML workflows: feature engineering, train-test splits, cross-validation, regression, classification, and metrics (Precision, Recall, ROC-AUC).",
    "deep learning": "Learn deep neural networks: backpropagation, activation functions, CNNs for computer vision, RNNs/Transformers for sequence modeling.",
    "nlp": "Study Natural Language Processing: text tokenization, embeddings (Word2Vec, SBERT), sentiment classification, and LLM prompting.",
    "data structures & algorithms": "Practice core DSA: arrays, linked lists, stacks, queues, trees, graphs, sorting, dynamic programming, and Big-O complexity analysis.",
    "object-oriented programming": "Apply OOP principles in code: encapsulation, inheritance, polymorphism, abstraction, and SOLID design patterns.",
    "system design": "Study large-scale system design: load balancing, horizontal scaling, caching strategies, database sharding, CAP theorem, and rate limiting.",
}


class SkillGapService:
    """
    Semantic skill matching using SBERT embeddings and domain normalization.

    For each required skill, finds the best semantic match among candidate
    skills and classifies as MATCHED, PARTIALLY MATCHED, or MISSING.
    """

    def analyze_skills(
        self,
        resume_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str] = None,
        resume_text: str = "",
    ) -> Dict[str, Any]:
        """Perform grounded skill gap analysis."""
        preferred_skills = preferred_skills or []

        # Filter out junk tokens or blacklist entries
        all_required_raw = required_skills + preferred_skills
        valid_required = []
        for s in all_required_raw:
            cand = clean_skill_candidate(s)
            if cand:
                norm = normalize_skill_name(cand)
                if norm and norm.lower() not in SKILL_BLACKLIST and norm not in valid_required:
                    valid_required.append(norm)

        if not valid_required:
            return {
                "matched": [],
                "partial": [],
                "missing": [],
                "skill_score": 100.0,
                "total_required": 0,
            }

        # Normalize resume skills
        norm_resume_skills = deduplicate_skills(resume_skills)

        # Build candidate pool for matching
        candidate_pool = list(norm_resume_skills)
        if resume_text:
            candidate_pool.append(resume_text[:3000])

        matched, partial, missing = [], [], []

        for skill in valid_required:
            best_sim, best_match, _ = best_match_similarity(skill, candidate_pool)
            importance = "High" if (skill in required_skills or any(skill.lower() in r.lower() for r in required_skills)) else "Medium"

            # Check if candidate pool had resume text as match
            clean_match = best_match if (best_match and best_match != resume_text[:3000]) else (skill if best_sim >= 0.72 else None)

            entry = {
                "skill": skill,
                "importance": importance,
                "similarity": round(best_sim, 3),
                "best_match": clean_match,
            }

            if best_sim >= HIGH_SKILL_THRESHOLD:
                entry["status"] = "MATCHED"
                matched.append(entry)
            elif best_sim >= MEDIUM_SKILL_THRESHOLD:
                entry["status"] = "PARTIALLY MATCHED"
                entry["reason"] = f"Resume shows related knowledge ('{clean_match or skill}') but not explicit production experience for '{skill}'."
                partial.append(entry)
            else:
                entry["status"] = "MISSING"
                entry["reason"] = self._missing_reason(skill, importance)
                entry["learning_objective"] = self._learning_objective(skill)
                missing.append(entry)

        # Apply clean skill extraction pipeline: split compounds, strip prefixes, deduplicate against matched
        matched_names = [m["skill"] for m in matched] + [p["skill"] for p in partial]
        raw_missing_names = [m["skill"] for m in missing]
        cleaned_missing_names = clean_missing_skills(raw_missing_names, matched_skills=matched_names)

        clean_missing_entries = []
        for s in cleaned_missing_names:
            importance = "High" if (s in required_skills or any(s.lower() in r.lower() for r in required_skills)) else "Medium"
            clean_missing_entries.append({
                "skill": s,
                "importance": importance,
                "similarity": 0.0,
                "best_match": None,
                "status": "MISSING",
                "reason": self._missing_reason(s, importance),
                "learning_objective": self._learning_objective(s),
            })

        total_skills_count = len(matched) + len(partial) + len(clean_missing_entries)
        skill_score = self._calculate_skill_score(matched, partial, clean_missing_entries, total_skills_count)

        return {
            "matched": matched,
            "partial": partial,
            "missing": clean_missing_entries,
            "skill_score": skill_score,
            "total_required": total_skills_count,
            "thresholds": {
                "high": HIGH_SKILL_THRESHOLD,
                "medium": MEDIUM_SKILL_THRESHOLD,
            },
        }

    def _calculate_skill_score(
        self,
        matched: List,
        partial: List,
        missing: List,
        total: int,
    ) -> float:
        """Calculate skill match score on 0-100 scale."""
        if total == 0:
            return 100.0
        matched_pts = len(matched) * 1.0
        partial_pts = len(partial) * 0.5
        score = ((matched_pts + partial_pts) / total) * 100
        return round(min(100.0, score), 1)

    def _missing_reason(self, skill: str, importance: str) -> str:
        return (
            f"The target role {'strongly requires' if importance == 'High' else 'prefers'} "
            f"'{skill}', but no documented hands-on experience or project was found on your resume."
        )

    def _learning_objective(self, skill: str) -> str:
        skill_lower = skill.lower().strip()

        # Check curated knowledge base
        for key, obj in CURATED_OBJECTIVES.items():
            if key in skill_lower or skill_lower in key:
                return obj

        # Dynamic, domain-aware objective for other skills
        return (
            f"Master core concepts and industry best practices in {skill}. "
            f"Build a hands-on project demonstrating {skill} integration and highlight it in your resume's technical projects."
        )
