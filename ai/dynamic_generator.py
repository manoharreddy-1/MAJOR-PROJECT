"""Intelligent grounded generation engine for offline/fallback AI features.

Provides dynamic, resume-grounded, and job-tailored generation for:
- Job-specific interview questions across all domains (Java, Frontend, Backend, DevOps, Data)
- Grounded resume improvement recommendations
- Week-by-week and day-by-day customized preparation roadmaps
- Grounded sample interview answers
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def detect_domain(target_role: str, skills: List[str], job_text: str = "") -> str:
    """Detect candidate's engineering domain."""
    combined = (f"{target_role} {' '.join(skills)} {job_text}").lower()

    if any(k in combined for k in ["java", "spring", "hibernate", "jvm"]):
        return "java"
    elif any(k in combined for k in ["react", "frontend", "angular", "vue", "javascript", "typescript", "ui/ux", "web developer"]):
        return "frontend"
    elif any(k in combined for k in ["devops", "cloud", "aws", "docker", "kubernetes", "sre", "infrastructure", "terraform"]):
        return "devops"
    elif any(k in combined for k in ["python", "django", "fastapi", "flask", "backend"]):
        return "python"
    elif any(k in combined for k in ["machine learning", "deep learning", "nlp", "computer vision", "data scientist", "ai engineer"]):
        return "data_ai"
    elif any(k in combined for k in ["full stack", "fullstack", "mern", "mean"]):
        return "fullstack"
    return "general"


DOMAIN_TECHNICAL_QUESTIONS = {
    "java": [
        {"question": "Explain JVM memory architecture (Heap, Stack, Metaspace) and how Garbage Collection algorithms (G1, ZGC) reclaim memory.", "topic": "JVM Internals", "difficulty": "hard"},
        {"question": "How does Java ensure memory visibility and thread safety across multi-threaded applications? Explain volatile, synchronized, and Atomic classes.", "topic": "Multithreading", "difficulty": "hard"},
        {"question": "Explain the internal hash collision resolution mechanism in Java 8+ HashMap. When does a linked list bucket convert to a Red-Black Tree?", "topic": "Collections Framework", "difficulty": "medium"},
        {"question": "How does Spring Boot implement Dependency Injection and Inversion of Control? What is the lifecycle of a Spring Bean?", "topic": "Spring Framework", "difficulty": "medium"},
        {"question": "Explain how Spring Data JPA and Hibernate manage transactions (@Transactional). What are transaction isolation levels and propagation modes?", "topic": "Hibernate & JPA", "difficulty": "hard"},
        {"question": "How do you structure microservices in Spring Boot? Explain service discovery (Eureka/Consul), API gateways, and fault tolerance with Resilience4j.", "topic": "Microservices", "difficulty": "hard"},
        {"question": "What is the difference between Comparable and Comparator interfaces in Java, and how do you implement custom sorting using lambda expressions?", "topic": "Core Java", "difficulty": "easy"},
        {"question": "Describe Java 8+ Streams API lazy evaluation. How do intermediate operations (filter, map) differ from terminal operations (collect, reduce)?", "topic": "Modern Java", "difficulty": "medium"},
        {"question": "How do you detect and resolve the N+1 query problem when loading related entities in Hibernate?", "topic": "Database Optimization", "difficulty": "medium"},
        {"question": "Explain how checked and unchecked exceptions differ in Java, and describe best practices for building enterprise exception hierarchies.", "topic": "Exception Handling", "difficulty": "easy"},
    ],
    "frontend": [
        {"question": "Explain React's Virtual DOM and Reconciliation algorithm (Fiber). How does it minimize costly direct DOM manipulations?", "topic": "React Architecture", "difficulty": "medium"},
        {"question": "How do React Hooks (useState, useEffect, useMemo, useCallback) work under the hood? How do you prevent unnecessary child re-renders?", "topic": "React Hooks", "difficulty": "medium"},
        {"question": "Compare React Context API with dedicated state management libraries (Redux, Zustand). When is Redux preferable for large enterprise apps?", "topic": "State Management", "difficulty": "medium"},
        {"question": "Explain the JavaScript Event Loop, Call Stack, Microtask Queue (Promises), and Macrotask Queue (setTimeout/setInterval).", "topic": "JavaScript Internals", "difficulty": "hard"},
        {"question": "How do you optimize Core Web Vitals (LCP, FID, CLS) in modern single-page applications? Explain code-splitting and dynamic imports.", "topic": "Web Performance", "difficulty": "hard"},
        {"question": "What are the architectural differences between Client-Side Rendering (CSR), Server-Side Rendering (SSR), and Static Site Generation (SSG) in Next.js?", "topic": "Next.js / SSR", "difficulty": "hard"},
        {"question": "How does CSS Flexbox differ from CSS Grid, and what strategy do you adopt to guarantee responsive layout consistency across devices?", "topic": "CSS & Responsive Design", "difficulty": "easy"},
        {"question": "Explain how Cross-Origin Resource Sharing (CORS) and Cross-Site Scripting (XSS) work. How do you secure frontend token storage?", "topic": "Web Security", "difficulty": "medium"},
        {"question": "How do TypeScript interfaces, type aliases, and generics provide compile-time safety and developer velocity in frontend projects?", "topic": "TypeScript", "difficulty": "medium"},
        {"question": "Describe your strategy for automated frontend testing: compare unit tests (Jest/Vitest), component tests (React Testing Library), and E2E (Playwright).", "topic": "Testing", "difficulty": "medium"},
    ],
    "devops": [
        {"question": "Explain the architectural difference between Docker containers and virtual machines. How do Linux namespaces and cgroups enforce isolation?", "topic": "Containerization", "difficulty": "medium"},
        {"question": "Describe Kubernetes core primitives: Pods, ReplicaSets, Deployments, Services (ClusterIP, NodePort, LoadBalancer), and Ingress controllers.", "topic": "Kubernetes", "difficulty": "hard"},
        {"question": "How do you design a secure, automated CI/CD pipeline using GitHub Actions or Jenkins that includes automated testing, Docker build, and blue-green deployments?", "topic": "CI/CD Pipelines", "difficulty": "hard"},
        {"question": "Explain Infrastructure as Code (IaC) principles using Terraform. How do you manage remote state locks and prevent configuration drift?", "topic": "Terraform / IaC", "difficulty": "hard"},
        {"question": "Describe how AWS Auto Scaling Groups and Kubernetes Horizontal Pod Autoscalers (HPA) scale workloads dynamically under traffic spikes.", "topic": "Cloud Scaling", "difficulty": "medium"},
        {"question": "How do you enforce security and least privilege in AWS using IAM policies, security groups, and VPC subnet routing?", "topic": "Cloud Security", "difficulty": "medium"},
        {"question": "What observability architecture (Prometheus, Grafana, ELK/OpenSearch) do you implement to monitor application uptime, latency, and error rates?", "topic": "Observability", "difficulty": "medium"},
        {"question": "Explain how Nginx functions as a reverse proxy, load balancer, and SSL termination endpoint for production services.", "topic": "Reverse Proxies", "difficulty": "medium"},
        {"question": "How do you manage secrets, API credentials, and environment configs securely across staging and production clusters?", "topic": "Secrets Management", "difficulty": "medium"},
        {"question": "Walk me through your incident triage and post-mortem workflow when a production service experiences sudden high latency and 504 errors.", "topic": "Incident Management", "difficulty": "hard"},
    ],
    "python": [
        {"question": "Explain Python's Global Interpreter Lock (GIL). How does it influence CPU-bound versus I/O-bound concurrency in multithreaded applications?", "topic": "Python Internals", "difficulty": "hard"},
        {"question": "How do Python generators, iterators, and the yield statement work? How do they optimize memory consumption when handling large datasets?", "topic": "Python Core", "difficulty": "medium"},
        {"question": "Compare synchronous frameworks (Flask/Django) with asynchronous frameworks (FastAPI). How does Python's asyncio event loop operate?", "topic": "Web Frameworks", "difficulty": "medium"},
        {"question": "Explain how database indexing operates in relational databases. How do B-tree indexes speed up queries and what are their write overheads?", "topic": "Database Architecture", "difficulty": "medium"},
        {"question": "How do you structure asynchronous background task workers using Celery with Redis or RabbitMQ as the message broker?", "topic": "Background Processing", "difficulty": "hard"},
        {"question": "Explain RESTful API best practices: idempotent HTTP methods, REST status codes, pagination, and API versioning strategies.", "topic": "API Design", "difficulty": "medium"},
        {"question": "How do you implement secure user authentication and authorization using JWT tokens, refresh tokens, and bcrypt password hashing?", "topic": "API Security", "difficulty": "medium"},
        {"question": "How do you profile, identify, and fix memory leaks or slow database query bottlenecks in production Python web services?", "topic": "Performance Profiling", "difficulty": "hard"},
        {"question": "Explain how Python decorators and context managers (with statement) operate under the hood, and describe a production use case for each.", "topic": "Python Patterns", "difficulty": "medium"},
        {"question": "How do you structure comprehensive automated unit and integration tests using PyTest fixtures and mock patches?", "topic": "Automated Testing", "difficulty": "easy"},
    ],
    "general": [
        {"question": "Explain the SOLID principles of Object-Oriented Software Design and provide an example of how each prevents architectural fragility.", "topic": "Software Architecture", "difficulty": "medium"},
        {"question": "Compare the runtime and space complexity of QuickSort, MergeSort, and HeapSort, and explain when you would select each.", "topic": "Data Structures & Algorithms", "difficulty": "medium"},
        {"question": "How do you design a database schema for high-throughput transactional systems? Explain normalization (1NF-3NF) vs selective denormalization.", "topic": "Database Design", "difficulty": "medium"},
        {"question": "Describe the architectural trade-offs between a monolithic system and a distributed microservices architecture.", "topic": "System Design", "difficulty": "medium"},
        {"question": "Explain how caching strategies (Cache-Aside, Write-Through, Write-Behind) improve throughput, and how you resolve cache invalidation.", "topic": "Caching & Scalability", "difficulty": "hard"},
        {"question": "What is the CAP theorem, and how does it govern consistency, availability, and partition tolerance in distributed databases?", "topic": "Distributed Systems", "difficulty": "hard"},
        {"question": "How do you guarantee transaction consistency and avoid concurrency race conditions using optimistic vs pessimistic locking?", "topic": "Concurrency Control", "difficulty": "medium"},
        {"question": "Walk me through your methodical process for diagnosing an intermittent, non-deterministic bug in a live production environment.", "topic": "Debugging Methodology", "difficulty": "medium"},
        {"question": "How do you write modular, self-documenting code, and what practices do you enforce in pull request reviews to maintain high quality?", "topic": "Code Quality", "difficulty": "easy"},
        {"question": "Describe your preferred Git branching strategy (e.g., Trunk-Based Development vs GitFlow) for reliable, continuous software releases.", "topic": "Version Control", "difficulty": "easy"},
    ]
}


def generate_grounded_interview_questions(prompt: str) -> Dict[str, Any]:
    """Dynamically generate interview questions grounded in job requirements and resume."""
    # Extract metadata from prompt
    target_role_match = re.search(r"TARGET ROLE:\s*([^\n]+)", prompt, re.I)
    target_role = target_role_match.group(1).strip() if target_role_match else "Software Engineer"

    skills_match = re.search(r"CANDIDATE SKILLS:\s*([^\n]+)", prompt, re.I)
    candidate_skills = [s.strip() for s in skills_match.group(1).split(",") if s.strip()] if skills_match else []

    missing_match = re.search(r"MISSING SKILLS:\s*([^\n]+)", prompt, re.I)
    missing_skills = [s.strip() for s in missing_match.group(1).split(",") if s.strip() and s.strip().lower() != "none"] if missing_match else []

    projects_match = re.search(r"PROJECTS:\s*([^\n]+)", prompt, re.I)
    projects_str = projects_match.group(1).strip() if projects_match else ""
    projects = [p.strip() for p in re.split(r"[;\n•]", projects_str) if len(p.strip()) > 5][:3]

    domain = detect_domain(target_role, candidate_skills)
    technical_pool = DOMAIN_TECHNICAL_QUESTIONS.get(domain, DOMAIN_TECHNICAL_QUESTIONS["general"])

    # Build primary skills text
    top_skill = candidate_skills[0] if candidate_skills else target_role
    second_skill = candidate_skills[1] if len(candidate_skills) > 1 else "core technical tooling"
    primary_project = projects[0] if projects else f"core {target_role} project"

    # Resume-based questions grounded in candidate's skills
    resume_based = [
        {"question": f"Walk me through your hands-on experience using {top_skill} from your resume. What was the most complex feature you built?", "focus": f"{top_skill} Hands-on"},
        {"question": f"In your resume, you highlighted proficiency with {second_skill}—describe a production challenge you resolved using it.", "focus": f"{second_skill} Experience"},
        {"question": f"How do you evaluate code quality, write unit tests, and maintain CI/CD pipelines in your projects?", "focus": "Code Quality & Testing"},
        {"question": f"Walk me through the technical decisions that led to the architecture described in your resume profile.", "focus": "Architecture Decisions"},
        {"question": f"Which programming language or framework on your resume are you most confident in, and what are its notable limitations?", "focus": "Core Proficiency"},
        {"question": f"Describe a scenario where you had to quickly learn an unfamiliar library or framework not originally on your resume.", "focus": "Technical Adaptability"},
        {"question": f"How did your academic background and foundational coursework directly prepare you for this {target_role} position?", "focus": "Academic Foundation"},
        {"question": f"Looking at your career timeline, what is the single biggest technical capability upgrade you have achieved recently?", "focus": "Continuous Learning"},
        {"question": f"How did you monitor runtime resource utilization and latency in the applications highlighted on your resume?", "focus": "Performance Benchmarking"},
        {"question": f"Describe your approach to writing documentation, API specifications, and README instructions for teammates.", "focus": "Engineering Documentation"},
    ]

    # Project-based questions
    project_based = [
        {"question": f"Describe the high-level architecture, database schema, and tech stack choices behind '{primary_project}'.", "project_reference": primary_project},
        {"question": f"What was the most challenging technical roadblock or concurrency issue in '{primary_project}', and how did you diagnose it?", "project_reference": "Problem Solving"},
        {"question": f"How did you validate data inputs, handle error states, and prevent security vulnerabilities in '{primary_project}'?", "project_reference": "Security & Validation"},
        {"question": f"If you had another development sprint to iterate on '{primary_project}', what major architectural optimization would you implement?", "project_reference": "Scalability Iteration"},
        {"question": f"How did you deploy, package, and host '{primary_project}' so users or evaluators could interact with it?", "project_reference": "Deployment & Delivery"},
        {"question": f"What specific metrics (latency, throughput, user count, test coverage) did you achieve in your primary project?", "project_reference": "Impact Measurement"},
        {"question": f"What architectural tradeoffs did you consider when selecting the framework or database for '{primary_project}'?", "project_reference": "Technical Decision Making"},
        {"question": f"Describe how you structured version control, Git commits, and pull requests while developing your projects.", "project_reference": "Version Control"},
        {"question": f"Did you compare your project implementation with an existing industry benchmark or baseline? What were the results?", "project_reference": "Benchmarking"},
        {"question": f"How would you refactor '{primary_project}' to handle a 10x surge in concurrent users without degrading response times?", "project_reference": "High-load Scaling"},
    ]

    # Behavioral questions
    behavioral = [
        {"question": f"Tell me about a time you faced an aggressive project deadline for a {target_role} deliverable. How did you prioritize tasks?", "competency": "Time Management"},
        {"question": "Describe a situation where team members disagreed on technical direction or architecture. How did you resolve the disagreement?", "competency": "Conflict Resolution"},
        {"question": "Give an example of a project where requirements shifted midway through development. How did you adapt your implementation?", "competency": "Adaptability"},
        {"question": "How do you effectively communicate technical architectural decisions and tradeoffs to non-technical stakeholders?", "competency": "Communication"},
        {"question": "Describe a mistake or failed technical experiment in your development career and what valuable lesson you learned from it.", "competency": "Resilience & Growth"},
        {"question": "How do you stay motivated, structured, and focused when working independently on ambiguous, open-ended tasks?", "competency": "Self-Motivation"},
        {"question": "Tell me about a time you collaborated with a peer, conducted a code review, or learned an important engineering technique from a teammate.", "competency": "Teamwork"},
        {"question": "How do you balance rapid prototyping velocity with code maintainability, clean design, and minimizing technical debt?", "competency": "Engineering Ethics"},
        {"question": "Describe a scenario where you took initiative to solve a critical issue beyond your assigned responsibilities.", "competency": "Proactivity"},
        {"question": "When facing multiple simultaneous production bugs or urgent support tickets, how do you decide what to triage first?", "competency": "Prioritization"},
    ]

    # Skill gap questions
    missing_str = ", ".join(missing_skills[:3]) if missing_skills else f"specialized requirements for {target_role}"
    skill_gap = [
        {"question": f"The job description explicitly values {missing_str}. What is your structured ramp-up strategy to master this rapidly?", "skill": missing_skills[0] if missing_skills else "Target Requirements", "learning_focus": "Ramp-up Strategy"},
        {"question": f"Walk me through how you learn an unfamiliar framework or tool under tight project deadlines.", "skill": "Unfamiliar Tech", "learning_focus": "Learning Methodology"},
        {"question": f"Have you built any personal side projects or completed coursework to bridge knowledge gaps for {target_role}?", "skill": "Bridge Projects", "learning_focus": "Self-Initiated Learning"},
        {"question": "How do you objectively verify whether you have reached production-ready competence in a newly acquired technical skill?", "skill": "Competence Benchmarking", "learning_focus": "Skill Verification"},
        {"question": "If assigned a project involving an unfamiliar library tomorrow morning, what are your first three actionable steps?", "skill": "Domain Knowledge Gap", "learning_focus": "Execution Plan"},
        {"question": "How do you balance official technical documentation versus community tutorials when learning cutting-edge libraries?", "skill": "Research Capability", "learning_focus": "Resource Selection"},
        {"question": "Describe a past academic or professional experience where you successfully bridged a significant technical skill gap on the fly.", "skill": "Past Skill Gap", "learning_focus": "Track Record"},
        {"question": "What active recall and hands-on coding techniques do you use to retain newly learned engineering concepts?", "skill": "Knowledge Retention", "learning_focus": "Active Application"},
        {"question": f"How do you learn idiomatic design patterns, coding conventions, and best practices in {target_role}?", "skill": "Code Standards", "learning_focus": "Software Craftsmanship"},
        {"question": f"What is your continuous learning roadmap over the next 6 months to stay ahead as a top-tier {target_role}?", "skill": "Career Growth", "learning_focus": "Proactive Growth"},
    ]

    return {
        "technical": technical_pool[:10],
        "resume_based": resume_based[:10],
        "project_based": project_based[:10],
        "behavioral": behavioral[:10],
        "skill_gap": skill_gap[:10],
    }


def generate_grounded_resume_improvement(prompt: str) -> Dict[str, Any]:
    """Generate dynamic resume improvements tailored to candidate's gaps and target role."""
    role_match = re.search(r"JOB TITLE:\s*([^\n]+)", prompt, re.I)
    target_role = role_match.group(1).strip() if role_match else "Target Role"

    matched_match = re.search(r"MATCHED SKILLS:\s*([^\n]+)", prompt, re.I)
    matched_skills = [s.strip() for s in matched_match.group(1).split(",") if s.strip() and s.strip().lower() != "none"] if matched_match else []

    missing_match = re.search(r"MISSING SKILLS:\s*([^\n]+)", prompt, re.I)
    missing_skills = [s.strip() for s in missing_match.group(1).split(",") if s.strip() and s.strip().lower() != "none"] if missing_match else []

    weak_match = re.search(r"WEAK SECTIONS:\s*([^\n]+)", prompt, re.I)
    weak_sections = [s.strip() for s in weak_match.group(1).split(",") if s.strip() and s.strip().lower() != "none"] if weak_match else []

    top_matched = ", ".join(matched_skills[:4]) if matched_skills else "your core technical skills"
    top_missing = ", ".join(missing_skills[:3]) if missing_skills else "specialized requirements"

    general_suggestions = [
        f"Tailor your resume headline specifically for '{target_role}' to immediately capture recruiter and ATS attention.",
        f"Prominently highlight your confirmed matching skills ({top_matched}) at the very top of your Skills section.",
        f"Bridge the primary skill gaps ({top_missing}) by completing focused mini-projects and adding them to your Projects section.",
        "Quantify project outcomes with measurable business metrics (e.g., 'reduced API latency by 35%', 'optimized query execution from 2.1s to 400ms').",
    ]

    section_suggestions = []
    if "skills" in weak_sections or not weak_sections:
        section_suggestions.append({
            "section": "Skills Section",
            "suggestion": f"Reorganize your skills into ATS-friendly categories: Languages, Frameworks, Databases, and Developer Tools. Emphasize {top_matched}.",
            "priority": "high"
        })
    if "summary" in weak_sections or not weak_sections:
        section_suggestions.append({
            "section": "Professional Summary",
            "suggestion": f"Add a concise 3-line professional summary highlighting your proficiency in {top_matched} and your target focus on {target_role} roles.",
            "priority": "high"
        })
    if "projects" in weak_sections or not weak_sections:
        section_suggestions.append({
            "section": "Projects Section",
            "suggestion": f"Structure project bullet points using the STAR method: Situation, Task, Action, and measurable Result. Explicitly mention tech stacks used.",
            "priority": "medium"
        })
    if "experience" in weak_sections:
        section_suggestions.append({
            "section": "Experience Section",
            "suggestion": "Begin every bullet point with a strong action verb (Architected, Engineered, Implemented, Optimized) and include technical impact metrics.",
            "priority": "medium"
        })

    return {
        "general_suggestions": general_suggestions,
        "section_suggestions": section_suggestions,
        "skill_highlighting": [
            f"Feature {m} prominently under core competencies as it directly aligns with the {target_role} job description."
            for m in (matched_skills[:4] or ["Core Programming"])
        ],
        "achievement_wording": [
            f"Instead of 'Worked on {top_matched} application', write: 'Architected and deployed a modular application using {top_matched}, supporting 500+ daily requests with 99.8% uptime.'",
            "Instead of 'Fixed bugs and improved performance', write: 'Identified and eliminated database bottlenecks, reducing query response times by 40% across high-traffic endpoints.'",
        ],
        "project_improvements": [
            f"Include GitHub repository links and live deployment URLs for your key projects.",
            f"Add a dedicated 'Key Technologies' sub-line beneath each project title listing {top_matched}.",
        ],
        "ats_wording": [
            "Use standard, single-column ATS section headers: 'Work Experience', 'Technical Skills', 'Projects', 'Education'.",
            f"Ensure exact keyword matches for {target_role} requirements appear naturally within bullet points.",
        ],
        "disclaimer": "All recommendations are grounded in your actual uploaded resume and job description. Only add skills you have hands-on experience with.",
    }


def generate_grounded_roadmap(
    prompt: str = "",
    target_role: str = "Software Engineer",
    matched_skills: List[str] = None,
    missing_skills: List[str] = None,
    weeks: int = 4,
    hours_per_week: int = 15,
) -> Dict[str, Any]:
    """Generate dynamic, customized preparation roadmap with day-by-day learning activities."""
    # Parse from prompt if parameters are empty
    if not missing_skills:
        role_match = re.search(r"TARGET ROLE:\s*([^\n]+)", prompt, re.I)
        if role_match:
            target_role = role_match.group(1).strip()

        missing_match = re.search(r"MISSING SKILLS:\s*([^\n]+)", prompt, re.I)
        if missing_match:
            missing_skills = [s.strip() for s in missing_match.group(1).split(",") if s.strip() and s.strip().lower() != "none"]

    missing_skills = missing_skills or ["Core Role Fundamentals", "Framework Architecture", "System Design & Integration"]
    matched_skills = matched_skills or []

    # Safe boundaries for weeks and hours
    weeks = max(1, min(12, int(weeks)))
    hours_per_week = max(5, min(40, int(hours_per_week)))
    total_hours = weeks * hours_per_week

    # Build weekly schedule
    weekly_plan = []
    roadmap_items = []

    # Distribute missing skills across available weeks
    num_missing = len(missing_skills)
    days_per_week = 6  # 6 study days per week, 1 rest/review day
    daily_hours = round(hours_per_week / days_per_week, 1)

    for w in range(1, weeks + 1):
        # Determine focus skill for this week
        if w <= num_missing:
            focus_skill = missing_skills[w - 1]
            priority = "HIGH"
            stage = "Foundation" if w == 1 else "Skill Building"
        elif w == weeks:
            focus_skill = f"{target_role} Mock Interviews & Portfolio Polish"
            priority = "MEDIUM"
            stage = "Review & Practice"
        else:
            skill_idx = (w - 1) % max(1, num_missing)
            focus_skill = f"{missing_skills[skill_idx]} Advanced Patterns & Integration"
            priority = "MEDIUM"
            stage = "Advanced Integration"

        # Generate day-wise activities for this week
        daily_activities = [
            {
                "day": "Day 1",
                "hours": daily_hours,
                "topic": f"{focus_skill} Fundamentals & Architecture",
                "learning_goal": f"Understand core theory, setup local environment, and study {focus_skill} syntax and primitives.",
                "practical_task": f"Create a new sandbox repo, configure dependencies, and verify basic '{focus_skill}' execution.",
                "checkpoint": "Can explain the core mental model and write foundational syntax without documentation."
            },
            {
                "day": "Day 2",
                "hours": daily_hours,
                "topic": f"Core Workflows & Common Idioms in {focus_skill}",
                "learning_goal": f"Master standard library components, essential patterns, and idiomatic conventions in {focus_skill}.",
                "practical_task": f"Build 2-3 targeted functional exercises demonstrating core {focus_skill} features.",
                "checkpoint": "Completed functional exercises and verified correct test outputs."
            },
            {
                "day": "Day 3",
                "hours": daily_hours,
                "topic": f"Hands-on Implementation & API Integration",
                "learning_goal": f"Connect {focus_skill} to external data, databases, or client interfaces.",
                "practical_task": f"Implement CRUD operations or data transformations utilizing {focus_skill}.",
                "checkpoint": "Working prototype demonstrating error handling and data validation."
            },
            {
                "day": "Day 4",
                "hours": daily_hours,
                "topic": f"Edge Cases, Performance Tuning & Best Practices",
                "learning_goal": f"Diagnose bottlenecks, handle memory or concurrency constraints, and study clean architecture in {focus_skill}.",
                "practical_task": f"Refactor your codebase, add logging, and optimize query or computation times.",
                "checkpoint": "Benchmarked performance and verified robust error handling."
            },
            {
                "day": "Day 5",
                "hours": daily_hours,
                "topic": f"Mini-Project Development & Testing",
                "learning_goal": f"Consolidate learning by building a standalone, resume-worthy feature using {focus_skill}.",
                "practical_task": f"Write automated unit tests and integration tests covering your mini-project functionality.",
                "checkpoint": "Mini-project runs cleanly with automated test coverage."
            },
            {
                "day": "Day 6",
                "hours": daily_hours,
                "topic": f"{focus_skill} Interview Questions & Q&A Drill",
                "learning_goal": f"Practice verbal technical explanations and solve live coding challenge questions on {focus_skill}.",
                "practical_task": f"Answer 5 technical interview questions out loud using the STAR method.",
                "checkpoint": "Confident verbal articulation of technical tradeoffs and architecture."
            },
            {
                "day": "Day 7",
                "hours": round(daily_hours * 0.5, 1),
                "topic": "Weekly Retrospective & Milestone Review",
                "learning_goal": "Consolidate weekly knowledge, push Git code commits, and update resume bullet points.",
                "practical_task": f"Commit your week's project to GitHub with a polished README and update your resume skills.",
                "checkpoint": f"Milestone for Week {w} marked complete."
            }
        ]

        week_obj = {
            "week_number": w,
            "estimated_week": w,
            "topic": focus_skill,
            "priority": priority,
            "stage": stage,
            "weekly_hours": hours_per_week,
            "reason": f"Targets critical candidate skill gap identified for {target_role} readiness.",
            "learning_objective": f"Achieve verified production-level competence in {focus_skill} across {hours_per_week} allocated study hours.",
            "daily_activities": daily_activities,
        }
        weekly_plan.append(week_obj)
        roadmap_items.append(week_obj)

    return {
        "target_role": target_role,
        "total_weeks": weeks,
        "hours_per_week": hours_per_week,
        "total_hours": total_hours,
        "daily_hours": daily_hours,
        "summary": (
            f"Personalized {weeks}-week preparation plan ({hours_per_week} hrs/week, {total_hours} total hours) "
            f"designed to systematically close skill gaps in {', '.join(missing_skills[:3])} for your target {target_role} role."
        ),
        "weekly_plan": weekly_plan,
        "roadmap": roadmap_items,
        "interview_practice_phase": {
            "focus_areas": [
                f"{target_role} core technical questions",
                f"Defending resume projects using the STAR method",
                f"Articulating tradeoffs for {', '.join(missing_skills[:2])}"
            ],
            "recommended_activities": [
                f"Solve 2 coding challenges per week matching {target_role} requirements",
                "Conduct recorded mock interview sessions practicing technical communication",
                "Review sample answers and refine verbal walkthroughs"
            ]
        }
    }


def generate_grounded_sample_answer(prompt: str) -> Dict[str, Any]:
    """Generate structured sample answer using STAR method."""
    q_match = re.search(r"QUESTION:\s*([^\n]+)", prompt, re.I)
    question = q_match.group(1).strip() if q_match else "Explain your technical experience."

    skills_match = re.search(r"RESUME SKILLS:\s*([^\n]+)", prompt, re.I)
    skills = [s.strip() for s in skills_match.group(1).split(",") if s.strip()] if skills_match else ["software development"]

    top_skill = skills[0] if skills else "engineering"

    answer = (
        f"In my past work utilizing {top_skill}, I approach technical problems methodically. "
        f"For example, when architecting system components, I first define the data contracts and constraints, "
        f"implement modular logic with automated unit tests, and continuously monitor performance metrics. "
        f"This structured, quality-driven approach directly prepares me to deliver reliable results in this role."
    )

    return {
        "answer": answer,
        "tips": [
            "Structure your answer using the STAR method: Situation, Task, Action, and measurable Result.",
            f"Anchor your answer to concrete tools from your resume like {top_skill} rather than speaking purely theoretically.",
            "Conclude by connecting your technical decision directly to business impact or user reliability."
        ],
        "based_on_resume": True,
        "placeholders_used": []
    }
