# Curato Proposal Intelligence

An AI-powered Decision Intelligence Platform that transforms marketing agency proposal PDFs into structured insights, side-by-side comparisons, risk analysis, and intelligent recommendations.

## Architecture

```
USER → React Frontend → FastAPI Backend → AI Pipeline (Claude API)
                                        → PDF Processing (PyMuPDF)
                                        → SQLite Database
```

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 19, Vite, TypeScript, Tailwind CSS v4, shadcn/ui, Framer Motion, TanStack Query, Recharts |
| Backend | Python 3.12+, FastAPI, SQLAlchemy, Pydantic |
| AI | Anthropic Claude API (Structured Outputs) |
| PDF | PyMuPDF (primary), pdfplumber (fallback) |
| Database | SQLite (MVP) → PostgreSQL (production) |

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
├── backend/
│   └── app/
│       ├── api/          # Route handlers
│       ├── services/     # Business logic
│       ├── models/       # SQLAlchemy models
│       ├── schemas/      # Pydantic schemas
│       ├── prompts/      # AI prompt templates
│       ├── utils/        # Helpers
│       ├── config.py     # Settings
│       ├── database.py   # DB setup
│       └── main.py       # App entry
├── frontend/
│   └── src/
│       ├── components/   # UI components
│       ├── pages/        # Page views
│       ├── layouts/      # App layouts
│       ├── hooks/        # Custom hooks
│       ├── services/     # API client
│       └── utils/        # Helpers
├── uploads/              # Uploaded PDFs
├── analysis/             # Analysis outputs
└── reports/              # Generated reports
```

## License

Proprietary — Curato
