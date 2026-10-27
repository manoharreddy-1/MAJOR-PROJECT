# AI Resume Analyzer

**Deep Learning-Based ATS, Skill Gap Analysis & AI Resume Optimizer System**

A CSE(AI) major project that uses Sentence-BERT (SBERT) semantic embeddings and cosine similarity for transparent resume-job matching, extended with clean canonical skill gap extraction, interactive ATS resume creation, interview preparation, and dynamic roadmaps.

---

## 🌟 Key Features

### 1. Transparent SBERT Semantic ATS Scoring
- Calculates an objective, multi-factor ATS match score:
  - **45% Semantic Alignment** (Overall Resume Context ↔ Job Description)
  - **30% Technical Skills Alignment** (SBERT semantic skill matching with thresholds)
  - **15% Experience Alignment** (Work History ↔ Job Responsibilities)
  - **10% Education Match** (Academic Qualifications ↔ Degree Requirements)
- Transparent mathematical breakdown showing weighted scores and radar charts.

### 2. Clean, Canonical Skill Gap Extraction Pipeline (Part 1)
- Eliminates sentence fragments and grammatical noise from job descriptions.
- **Compound Phrase Splitting**: e.g., `"Pandas and Scikit"` → `["Pandas", "scikit-learn"]`; `"Ai/Ml Or Data Science."` → `["AI/ML", "Data Science"]`.
- **Filler Word & Punctuation Stripping**: e.g., `"Exposure To Numpy"` → `"NumPy"`, `"Exposure To Llms"` → `"LLMs"`.
- **Broken Fragment Repair**: Repairs cut-off text such as `"Oriented Programming."` → `"Object-Oriented Programming"`, and stitches multi-line fragments like `"Strong Problem"` + `"Solving And Analytical Skills."` → `["Problem Solving", "Analytical Skills"]`.
- **Non-Skill Blacklisting**: Filters out noise tokens like `"IT"`, `"Good To Have"`, `"Learn"`, `"Paced Environment"`.
- **Taxonomy Normalization**: Standardizes casing and aliases (`NLP`, `LLMs`, `NumPy`, `scikit-learn`, `PyTorch`, `Generative AI`).
- **Matched Skill Deduplication**: Automatically prevents any skill already present on the resume from showing up as missing.

### 3. ✨ Create Resume with AI (Part 2)
- One-click ATS resume enhancement accessible right under the Matched, Partial, and Missing skills columns.
- **Strict Anti-Hallucination Guardrails**:
  - Historical facts (name, contact info, employers, education, dates) are 100% preserved.
  - Skills are woven into Summary and Project bullets **only** when verified context exists (e.g. adding NumPy/Pandas to an existing Python ML project).
  - Skills lacking prior project evidence are placed in a **Skills Requiring Confirmation** checklist for user review before inclusion.
- **Genuine ATS Score Recalculation**:
  - Re-runs the exact underlying `ATSService.analyze()` SBERT scoring engine on the newly generated resume.
  - Displays real **Old Score → New Score** and score improvement delta badge (`+XX% ATS Boost`).
- **Interactive Side-by-Side Review**:
  - Displays **Original Resume** (read-only) side-by-side with **AI-Optimized Resume** (editable inline).
  - Newly added skills and sections are clearly highlighted in green badges.
- **ATS-Compliant Single-Column Export**:
  - **Download DOCX**: Generates a standard single-column Word document via `python-docx`.
  - **Download PDF**: Generates clean vector PDF via `PyMuPDF` (`fitz`).
  - **Copy Text**: One-click clipboard copy for application portals.

### 4. Strict Authentication & Role Management
- Enforces strict credential authentication via SHA-256 with salt.
- Invalid or unregistered credentials return `401 Unauthorized` errors.
- Pre-seeded evaluation accounts for demonstrations:
  - Username: `student` | Password: `student123`
  - Username: `demo` | Password: `demo123`

---

## Architecture

```
Frontend (HTML5 / CSS3 / Vanilla JS)
    ↓
Flask REST API (Blueprints: /api/resume, /api/job, /api, /api/course, /api/auth)
    ↓
Clean Skill Extractor & Normalizer
    ↓
SBERT Semantic Embeddings (all-MiniLM-L6-v2) + Cosine Similarity
    ↓
Transparent ATS Scoring Engine (45% Sem + 30% Skill + 15% Exp + 10% Edu)
    ↓
AI Resume Optimizer Service (Gemini API + Grounded Fallback Engine)
    ↓
ATS Re-Scoring Engine (Old Score → New Recalculated Score)
    ↓
Export Subsystem (python-docx for DOCX, PyMuPDF for PDF)
    ↓
MongoDB Atlas / In-Memory MockCollection (Local Fallback)
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user account |
| POST | `/api/auth/login` | Authenticate with registered credentials |
| POST | `/api/resume/upload` | Upload PDF/DOCX resume file |
| POST | `/api/job/analyze` | Parse and structure job description |
| POST | `/api/analyze` | Run full SBERT ATS analysis & skill gap |
| GET | `/api/analysis/<id>` | Retrieve stored ATS analysis |
| GET | `/api/history` | User analysis history |
| POST | `/api/optimize-resume` | ✨ AI Resume Optimizer & ATS Re-scoring |
| POST | `/api/optimize-resume/export/docx` | Export optimized resume to Word (.docx) |
| POST | `/api/optimize-resume/export/pdf` | Export optimized resume to PDF (.pdf) |
| POST | `/api/interview/generate` | Domain-tailored interview preparation |
| POST | `/api/roadmap/generate` | Day-by-day lagging skill preparation roadmap |
| GET | `/api/health` | Service health status |

---

## Setup & Running Locally

### Prerequisites
- Python 3.10 or 3.11
- Virtual environment (`venv`)

### Installation
```bash
# 1. Activate your virtual environment
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env

# 4. Start Flask server
python app.py
```
Open **http://localhost:5000** in your browser.

---

## Running Automated Tests

The test suite covers clean extraction, dirty fragments, 0 missing skills, 5 missing skills, auth security, and export endpoints:

```bash
pytest tests/ -v
```

All 33 test cases pass across the entire suite:
- `tests/test_skill_cleaning.py`: Validates compound phrase splitting, filler stripping, fragment repair, and matched skill deduplication.
- `tests/test_resume_optimizer.py`: Tests 5 missing skills, 0 missing skills, invalid inputs, and score recalculation.
- `tests/test_api.py`: Tests authentication rules, optimizer endpoint, and DOCX/PDF export streaming.
- `tests/test_scoring.py`: Validates ATS weighted scoring mathematics.
- `tests/test_job_parser.py`: Tests requirements parsing.
- `tests/test_mongodb_mock.py`: Tests data persistence.
- `tests/test_skill_normalizer.py`: Tests skill taxonomy mappings.

---

## Disclaimer
This is an AI-generated, project-specific match score based on research-grounded semantic embeddings and is not an official score used by any commercial ATS. The system enforces strict anti-hallucination policies and never fabricates candidate degrees, companies, or experience dates.
