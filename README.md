# 🛡️ Resilient ATS — Intelligent Resume Analyzer

An AI-powered Applicant Tracking System that goes beyond keyword matching to detect adversarial manipulation, validate authenticity, and provide smart scoring with explainable AI insights.

## ⚡ Features

- **Semantic Matching** — NLP-powered similarity using sentence-transformers
- **Adversarial Detection** — Catches hidden text, keyword stuffing, repetition, JD copy-paste
- **Multi-Factor Scoring** — Weighted scoring across 4 dimensions (0–100)
- **Trust Score** — Composite authenticity metric with visual badge
- **AI Explainability** — Human-readable explanations for every score
- **Detection Heatmap** — Color-coded visualization of suspicious content
- **Modern Dashboard** — Dark theme, glassmorphism, animated charts

## 🏗️ Architecture

```
Frontend (Next.js) ←→ Backend (FastAPI)
                         ├── Resume Parser (PDF/DOCX)
                         ├── Adversarial Detector
                         ├── Semantic Engine (sentence-transformers)
                         ├── Scoring Engine
                         └── Explainability Engine
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

The NLP model (`all-MiniLM-L6-v2`, ~80MB) will auto-download on first run.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies (already done if using npx create-next-app)
npm install

# Start dev server
npm run dev
```

### 3. Open the App

Visit **http://localhost:3000** — upload a resume and paste a job description to see the analysis!

## 📊 Scoring System

| Factor | Weight | Description |
|--------|--------|-------------|
| Skill Match | 25% | Required skills found with context |
| Semantic Similarity | 30% | Embedding-based meaning alignment |
| Experience Authenticity | 20% | Skills-to-projects consistency |
| Anti-Cheat | 25% | Penalty-based adversarial detection |

## 🛡️ Adversarial Detection

| Tactic | Detection Method |
|--------|-----------------|
| Hidden Text | Font color, size, opacity analysis |
| Keyword Stuffing | Statistical frequency analysis (TF-IDF) |
| Repeated Phrases | N-gram + sentence duplication detection |
| JD Copy-Paste | Sliding window similarity matching |

## 🧪 API Reference

### `POST /api/analyze`
Upload a resume file with a job description for full analysis.

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "resume=@resume.pdf" \
  -F "job_description=Senior React developer with 5+ years experience..."
```

### `GET /api/results/{analysis_id}`
Retrieve previously computed analysis results.

### `GET /api/health`
Health check endpoint.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React, Recharts, Framer Motion |
| Backend | FastAPI, Python 3.10+ |
| NLP | sentence-transformers (all-MiniLM-L6-v2) |
| Resume Parsing | PyMuPDF, python-docx |
| Similarity Search | FAISS (CPU) |
| Scoring | Custom multi-factor engine |

## 📁 Project Structure

```
ATS/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt     # Python dependencies
│   ├── models/
│   │   └── schemas.py       # Pydantic data models
│   ├── services/
│   │   ├── resume_parser.py          # PDF/DOCX extraction
│   │   ├── adversarial_detector.py   # Cheat detection engine
│   │   ├── semantic_engine.py        # NLP embeddings + matching
│   │   ├── scoring_engine.py         # Multi-factor scoring
│   │   └── explainability_engine.py  # AI explanation generation
│   └── routers/
│       └── analysis.py      # API route handlers
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.js       # Main dashboard
│   │   │   ├── layout.js     # Root layout
│   │   │   └── globals.css   # Design system
│   │   └── components/
│   │       ├── UploadWizard.js        # File upload + JD input
│   │       ├── ScoreCard.js           # Animated score ring
│   │       ├── ScoreBreakdown.js      # Radar chart + skills
│   │       ├── TrustScore.js          # Trust badge
│   │       ├── AdversarialHeatmap.js  # Detection heatmap
│   │       ├── AIExplanation.js       # AI insights panel
│   │       └── StrengthsWeaknesses.js # S&W display
│   └── package.json
└── README.md
```
# ATS
