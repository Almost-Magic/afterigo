# Ripple CRM v3 — Relationship Intelligence Engine

> Made with love by Mani Padisetti @ Almost Magic Tech Lab

## Overview

Ripple is an Agentic Relationship Operating System (ROS) built for Australian SMBs. It tracks contacts, companies, deals, interactions, commitments, and relationship health — all powered by local AI via Ollama (no cloud API keys, ever).

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL (pgvector) running on port 5433
- Redis running on port 6379

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Update DATABASE_URL password
python -m alembic upgrade head
python -m uvicorn app.main:app --host 0.0.0.0 --port 8100
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3100](http://localhost:3100) in your browser.

## Ports

| Component | Port |
|-----------|------|
| Backend (FastAPI) | 8100 |
| Frontend (React/Vite) | 3100 |
| PostgreSQL (pgvector) | 5433 |
| Redis | 6379 |
| Ollama | 11434 |

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy (async), Alembic, PostgreSQL + pgvector
- **Frontend:** React, Vite, Tailwind CSS v4
- **Design:** AMTL Design System (Sora/Inter/JetBrains Mono, Midnight #0A0E14 + Gold #C9944A)
- **AI:** Ollama (local only, routed via Supervisor)

## Licence

MIT

---

*"The market doesn't reward impressive specs. It rewards daily behaviour change."*
