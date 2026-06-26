# Oz AI

**Enterprise Incident Response Platform**

Kaggle — AI Agents Intensive Capstone (Agents for Business track)

Oz AI is an enterprise platform for structured incident response. Sprint 1 delivers the core backend API, React dashboard, log upload workflow, and Docker-based local development.

---

## Features (Sprint 1)

- **Backend API** — FastAPI with standardized `APIResponse` envelope, request logging, and centralized exception handling
- **Incident management** — Create, list, retrieve, update, and soft-delete incidents with audit logging
- **Log uploads** — Multipart file upload with validation, metadata storage, and paginated listing
- **Dashboard metrics** — Aggregate counts for incidents and uploaded logs
- **Frontend dashboard** — React 19 + TypeScript + Tailwind with routing, global loading, toasts, error boundary, and 404 page
- **API documentation** — OpenAPI/Swagger at `/docs` with summaries, descriptions, tags, and schema examples
- **Docker** — One-command startup with backend and frontend health checks

---

## Architecture overview

Oz AI follows a layered architecture documented in `docs/02_ARCHITECTURE.md`:

```text
Presentation (React Dashboard)
        │
        ▼
Backend (FastAPI · Services · Repositories)
        │
        ▼
Persistence (SQLite · SQLAlchemy ORM)
```

Sprint 1 implements the backend and presentation layers. Agent orchestration, MCP tools, and authentication are planned for later sprints.

---

## Prerequisites

- **Python 3.12+**
- **Node.js 20+** and **npm**
- **Docker** and **Docker Compose** (optional, for containerized development)

---

## Local setup

### 1. Clone the repository

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` if you need to change ports, the database path, or upload limits. Defaults work for local development.

### 3. Start the backend

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

### 4. Start the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

---

## Docker setup

From the repository root:

```bash
docker compose up --build
```

No manual configuration is required. Compose sets database, upload, and API URL defaults automatically.

| Service  | URL |
|----------|-----|
| Backend  | http://localhost:8000 |
| Frontend | http://localhost:5173 |
| API docs | http://localhost:8000/docs |

Verify the backend:

```bash
curl http://localhost:8000/api/v1/health
```

Stop services:

```bash
docker compose down
```

---

## API documentation

Interactive Swagger UI: **http://localhost:8000/docs**

All endpoints return the standard envelope:

```json
{
  "success": true,
  "message": "Human-readable status",
  "data": {}
}
```

### Endpoints (13)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Application root |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/dashboard/stats` | Dashboard metrics |
| GET | `/api/v1/system/tables` | Database table listing |
| POST | `/api/v1/incidents` | Create incident |
| GET | `/api/v1/incidents` | List incidents |
| GET | `/api/v1/incidents/{id}` | Get incident |
| PUT | `/api/v1/incidents/{id}` | Update incident |
| DELETE | `/api/v1/incidents/{id}` | Soft delete incident |
| POST | `/api/v1/logs/upload` | Upload log file |
| GET | `/api/v1/logs` | List log files |
| GET | `/api/v1/logs/{id}` | Get log metadata |
| DELETE | `/api/v1/logs/{id}` | Soft delete log file |

---

## Frontend pages (7)

| Route | Page |
|-------|------|
| `/` | Dashboard |
| `/incidents` | Incident list |
| `/incidents/:id` | Incident detail |
| `/logs` | Log upload and listing |
| `/reports` | Reports (placeholder) |
| `/settings` | Settings (placeholder) |
| `*` | 404 not found |

---

## Folder structure

```text
Kaggle/
├── backend/
│   └── app/
│       ├── api/          # HTTP route modules
│       ├── core/         # Config, logging, middleware, exceptions
│       ├── db/           # Database session and engine
│       ├── models/       # SQLAlchemy ORM models
│       ├── repositories/ # Data access layer
│       ├── schemas/      # Pydantic request/response schemas
│       ├── services/     # Business logic
│       ├── utils/        # Shared utilities
│       └── main.py       # FastAPI entry point
├── frontend/
│   └── src/
│       ├── components/   # Reusable UI (loading, toasts, tables)
│       ├── context/      # Global app state
│       ├── layouts/      # Layout wrappers
│       ├── pages/        # Route-level pages
│       ├── services/     # API client and service modules
│       └── utils/        # Formatting helpers
├── docker/               # Dockerfiles
├── storage/uploads/      # Local log file storage
├── tests/                # Backend integration tests
├── docs/                 # Project documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Screenshots

<!-- Add dashboard screenshot -->
![Dashboard](docs/screenshots/dashboard.png)

<!-- Add incidents list screenshot -->
![Incidents](docs/screenshots/incidents.png)

<!-- Add log upload screenshot -->
![Log Upload](docs/screenshots/log-upload.png)

---

## Testing

Backend tests (from `backend/`):

```bash
pip install -e ".[dev]"
python -m pytest ../tests -v
```

Frontend build:

```bash
cd frontend
npm run build
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
