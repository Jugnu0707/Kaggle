# Oz AI

**Autonomous Enterprise Incident Response Platform**

Kaggle — AI Agents Intensive Capstone (Agents for Business track)

Oz AI is an enterprise platform for structured incident response. This repository contains the backend API, frontend dashboard, and project documentation.

Sprint 1 establishes the application skeleton: FastAPI backend, React frontend, and Docker-based local development.

---

## Prerequisites

- **Python 3.12+**
- **Node.js 20+** and **npm**
- **Docker** and **Docker Compose** (optional, for containerized development)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` if you need to change ports or the database path. Defaults work for local development.

---

## Run with Docker

From the repository root:

```bash
docker compose up --build
```

Services:

| Service  | URL |
|----------|-----|
| Backend  | http://localhost:8000 |
| Frontend | http://localhost:5173 |
| API docs | http://localhost:8000/docs |

Verify the backend:

```bash
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health
```

Stop services:

```bash
docker compose down
```

---

## Run locally

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The landing page displays backend health from http://localhost:8000/api/v1/health.

---

## Folder structure

```text
oz-ai/
├── backend/
│   └── app/
│       ├── api/          # HTTP route modules
│       ├── core/         # Configuration and shared core
│       ├── db/           # Database session and engine
│       ├── models/       # SQLAlchemy ORM models
│       ├── schemas/      # Pydantic schemas
│       ├── services/     # Business logic
│       ├── utils/        # Shared utilities
│       └── main.py       # FastAPI entry point
├── frontend/
│   └── src/
│       ├── components/   # Reusable UI components
│       ├── pages/        # Route-level pages
│       ├── layouts/      # Layout wrappers
│       ├── hooks/        # Custom React hooks
│       ├── services/     # API client
│       └── assets/       # Static assets
├── agents/               # Agent definitions (future)
├── mcp/                  # MCP tool servers (future)
├── datasets/             # Synthetic datasets (future)
├── evaluation/           # Evaluation harness (future)
├── docker/               # Dockerfiles
├── tests/                # Integration and E2E tests
├── scripts/              # Utility scripts
├── design/               # Architecture diagrams and wireframes
├── docs/                 # Project documentation
├── .github/              # GitHub templates and community files
├── .cursor/              # Cursor AI rules
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Documentation

Project documentation lives in `docs/`:

- `01_PROJECT_BRIEF.md` — Vision, goals, and technology stack
- `02_ARCHITECTURE.md` — System architecture
- `03_TASKS.md` — Engineering backlog
- `08_UI_UX_SPECIFICATION.md` — UI blueprint

---

## License

MIT License. See `LICENSE`.
