# AI Resume Analyzer

**Deep Learning-Based ATS & Personalized Interview Preparation System**

A CSE(AI) major project that uses Sentence-BERT (SBERT) semantic embeddings and cosine similarity for resume-job matching, extended with skill gap analysis, resume improvement, interview preparation, and personalized roadmaps.

## Core AI Component

| Component | Technology |
|-----------|-----------|
| Semantic Matching | `sentence-transformers/all-MiniLM-L6-v2` |
| Similarity Metric | Cosine Similarity (scikit-learn) |
| Entity Extraction | `dslim/bert-base-NER` (Hugging Face) |
| Generative AI | Hugging Face Inference API |
| Baseline Comparison | TF-IDF + Cosine Similarity |

> **Important:** SBERT is the MAIN deep learning model. This is NOT a keyword-based ATS.

## Architecture

```
Frontend (HTML/CSS/JS)
    ↓
Flask REST API
    ↓
SBERT Embeddings + Cosine Similarity
    ↓
ATS Scoring + Skill Gap Analysis
    ↓
Generative AI (Improvement, Interview, Roadmap)
    ↓
MongoDB Atlas (Persistent Storage)
```

## Project Structure

```
ai-resume-analyzer/
├── app.py                  # Flask application entry point
├── api/                    # REST API routes
├── ai/                     # SBERT, NER, LLM models
├── services/               # Business logic
├── parsers/                # PDF, OCR, resume, job parsers
├── database/               # MongoDB connection
├── utils/                  # Scoring, validation, normalization
├── frontend/               # HTML templates + static assets
├── config/                 # Settings and weights
├── evaluation/             # SBERT vs TF-IDF evaluation
├── tests/                  # Unit tests
├── requirements.txt
├── vercel.json
└── .env.example
```

## Setup

### Prerequisites

- Python 3.10+
- MongoDB Atlas account (or local MongoDB)
- Hugging Face API key (for generative features)
- Tesseract OCR (optional, for scanned PDFs)

### Installation

```bash
# Clone and enter project
cd "major project"

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your MongoDB URI and Hugging Face API key
```

### Run Locally

```bash
python app.py
```

Open http://localhost:5000

### Run Tests

```bash
pytest tests/ -v
```

### Run Evaluation

```bash
python evaluation/evaluate_models.py
```

## ATS Scoring Formula

| Component | Weight | Method |
|-----------|--------|--------|
| Semantic Match | 45% | SBERT cosine similarity (resume ↔ job) |
| Skill Match | 30% | Per-skill SBERT matching with thresholds |
| Experience Match | 15% | SBERT (experience ↔ responsibilities) |
| Education Match | 10% | SBERT (education ↔ requirements) |

Weights configurable in `config/settings.py`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/resume/upload` | Upload PDF resume |
| GET | `/api/resume/extract/<id>` | Get extracted resume |
| PUT | `/api/resume/extract/<id>` | Update extracted data |
| POST | `/api/job/analyze` | Analyze job description |
| POST | `/api/analyze` | Run SBERT ATS analysis |
| GET | `/api/analysis/<id>` | Get analysis results |
| GET | `/api/history` | Analysis history |
| POST | `/api/resume/improve` | Resume improvement suggestions |
| POST | `/api/interview/generate` | Interview questions |
| POST | `/api/roadmap/generate` | Preparation roadmap |
| GET | `/api/health` | Health check |

## Deployment (Vercel)

1. Push to GitHub
2. Connect to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy

> **Note:** SBERT model loading on Vercel serverless may require a dedicated inference service (Hugging Face Spaces/Inference Endpoint) for production. The AI module is designed to be separable.

## Research Foundation

Inspired by **CareerBERT**: "Matching Resumes to ESCO Jobs in a Shared Embedding Space for Generic Job Recommendations."

Our extension:
- Resume information extraction
- Section-aware SBERT matching
- Transparent weighted ATS scoring
- Skill gap analysis with learning objectives
- Generative AI career preparation features

## Disclaimer

This is an AI-generated project-specific match score and is not an official score used by any particular company's ATS. The system never fabricates candidate information.
