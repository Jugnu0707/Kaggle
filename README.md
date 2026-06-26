# Oz AI

**Enterprise Incident Response Platform** · **v0.1.0** · **Sprint 1 Complete**

Kaggle — AI Agents Intensive Capstone (Agents for Business track)

Oz AI is an enterprise platform for structured incident response. Sprint 1 delivers the core backend API, React dashboard, log upload workflow, Docker-based local development, and production-ready engineering foundations.

---

## Project status

| Milestone | Status |
|-----------|--------|
| Sprint 1 — Foundation | **Complete** |
| Sprint 2 — ADK framework setup | **Complete** |
| Sprint 2 — MCP infrastructure | **Complete** |
| Sprint 2 — Coordinator orchestration | **Complete** |
| Sprint 2 — Evidence Agent | **Complete** |
| Sprint 3 — Ingestion & API expansion | Planned |
| Sprint 4 — Evaluation & release hardening | Planned |

---

## Features (Sprint 1)

- **Backend API** — FastAPI with standardized `APIResponse` envelope, request logging, and centralized exception handling
- **Incident management** — Create, list, retrieve, update, and soft-delete incidents with audit logging
- **Log uploads** — Multipart file upload with validation, metadata storage, and paginated listing
- **Dashboard metrics** — Aggregate counts for incidents and uploaded logs
- **Frontend dashboard** — React 19 + TypeScript + Tailwind with routing, global loading, toasts, error boundary, and 404 page
- **API documentation** — OpenAPI/Swagger at `/docs` with summaries, descriptions, tags, and schema examples
- **Docker** — One-command startup with backend and frontend health checks and persistent volumes
- **Code quality** — Ruff, Black, and isort configured for the backend

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

Sprint 1 implements the backend and presentation layers. Advanced orchestration capabilities described in the architecture document are planned for later sprints.

---

## Prerequisites

- **Python 3.12+**
- **Node.js 20+** and **npm**
- **Docker** and **Docker Compose** (optional, for containerized development)

---

## Environment variables

Copy `.env.example` to `.env` for local development. Docker Compose supplies defaults automatically.

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application display name | `Oz AI` |
| `APP_VERSION` | Semantic version string | `0.1.0` |
| `HOST` | Backend bind address | `0.0.0.0` |
| `PORT` | Backend port | `8000` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./oz_ai.db` |
| `UPLOAD_DIR` | Log file storage directory | `storage/uploads` |
| `MAX_UPLOAD_SIZE_BYTES` | Maximum upload size in bytes | `52428800` (50 MB) |
| `VITE_API_URL` | Frontend API base URL | `http://localhost:8000` |
| `GOOGLE_API_KEY` | Google Gemini API key (required for LLM execution in later sprints) | *(empty)* |
| `GOOGLE_MODEL` | Gemini model name for ADK agents | `gemini-2.5-pro` |
| `ADK_APP_NAME` | ADK application identifier | `oz_ai` |
| `ADK_ENABLE_TRACING` | Enable ADK OpenTelemetry tracing | `false` |

Never commit `.env` files or secrets to the repository.

---

## Google ADK setup (Sprint 2 Task 1)

Oz AI uses the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) for agent orchestration. Sprint 2 Task 1 adds framework setup only — no LLM calls or business logic.

### Installation

ADK is included in backend dependencies. From `backend/`:

```bash
pip install -e ".[dev]"
```

This installs `google-adk==2.3.0` along with the FastAPI backend.

**Note:** `google-adk` requires FastAPI `>=0.133`, Pydantic `>=2.12`, and Uvicorn `>=0.34`. These versions are pinned in `backend/pyproject.toml` to satisfy ADK compatibility.

### Required environment variables

Add to your `.env` (see `.env.example`):

| Variable | Required now | Description |
|----------|--------------|-------------|
| `GOOGLE_API_KEY` | No (Sprint 2 Task 1) | Gemini API key — needed when LLM agents are enabled |
| `GOOGLE_MODEL` | No | Default model name (`gemini-2.5-pro`) |
| `ADK_APP_NAME` | No | ADK application identifier |
| `ADK_ENABLE_TRACING` | No | Enable ADK tracing (`false` by default) |

### Verify ADK setup

1. Start the backend:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Check startup logs for:

```text
Google ADK import verified successfully
Coordinator Agent initialized: loaded=True
```

3. Call the health endpoint:

```bash
curl http://localhost:8000/api/v1/health
```

Expected fields in `data`:

```json
{
  "status": "healthy",
  "adk": true,
  "coordinator": true,
  "mcp": true
}
```

4. Run ADK tests:

```bash
python -m pytest ../tests/test_coordinator.py ../tests/test_adk_startup.py ../tests/test_health.py -v
```

---

## Google AI configuration (Sprint 2 — API verification)

Oz AI reads Google AI Studio credentials from `.env` via `backend/app/core/ai_config.py`. Sprint 2 adds a **connectivity check only** — no agent reasoning or LLM pipelines are invoked.

### Required environment variables

Add to your `.env` (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI Studio / Gemini API key | *(empty)* |
| `GOOGLE_MODEL` | Gemini model ID for verification | `gemini-2.5-pro` |

Obtain an API key from [Google AI Studio](https://aistudio.google.com/apikey).

### Verify Google AI connectivity

1. Ensure `GOOGLE_API_KEY` and `GOOGLE_MODEL` are set in `.env`.

2. Start the backend:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Call the AI health endpoint:

```bash
curl http://localhost:8000/api/v1/ai/health
```

**Success** — API key and model are working:

```json
{
  "success": true,
  "message": "Google AI connectivity verified",
  "data": {
    "connected": true,
    "model": "gemini-2.5-pro",
    "response": "Oz AI Ready"
  }
}
```

**Failure** — missing or invalid configuration:

```json
{
  "success": false,
  "message": "Google AI connectivity check failed",
  "data": {
    "connected": false,
    "error": "GOOGLE_API_KEY is not configured"
  }
}
```

4. Run AI verification tests:

```bash
python -m pytest ../tests/test_ai_health.py -v
```

The check sends the prompt `Reply with exactly: Oz AI Ready` to the configured model using the official `google-genai` SDK (installed with `google-adk`).

---

## MCP tool layer (Sprint 2 Task 2)

Oz AI mediates all agent-to-system interactions through **MCP (Model Context Protocol)** tools in `mcp/`. Sprint 2 Task 2 adds infrastructure only — no AI execution, LLM calls, or business logic.

### Purpose

The MCP layer provides a standardized, auditable interface between future ADK agents and backend services. Tools return structured `{success, data, error}` responses and are registered automatically at startup.

### Registered tools (5)

| Tool | Description |
|------|-------------|
| `health` | Application health status |
| `list_incidents` | Paginated incident list (via `IncidentService`) |
| `incident_details` | Single incident by ID (via `IncidentService`) |
| `list_logs` | Uploaded log file metadata (via `LogService`) |
| `system_info` | Version, database, ADK status, and MCP status |

### Verify MCP setup

1. Check startup logs for:

```text
Registered MCP tool: health — Return application health status.
...
MCP server started with 5 registered tools
```

2. Call the MCP status endpoint:

```bash
curl http://localhost:8000/api/v1/system/mcp
```

Expected response in `data`:

```json
{
  "mcp": true,
  "tool_count": 5,
  "tools": [
    "health",
    "incident_details",
    "list_incidents",
    "list_logs",
    "system_info"
  ]
}
```

3. Run MCP tests:

```bash
python -m pytest ../tests/test_mcp_registry.py ../tests/test_mcp_server.py ../tests/test_mcp_api.py -v
```

### Adding a new MCP tool

1. Create a module under `mcp/tools/` (for example `mcp/tools/my_tool.py`).
2. Define Pydantic **input** and **output** schemas.
3. Decorate the handler with `@register_tool(name=..., description=..., input_model=..., output_model=...)`.
4. Import the module in `mcp/tools/__init__.py` so it registers at startup.
5. Add tests under `tests/` and update this README tool table.

---

## Coordinator orchestration (Sprint 2 Task 3)

The Coordinator Agent uses Google ADK configuration (name, description, prompt, input/output schemas) to generate orchestration plans without executing specialist agents or LLM calls.

### Orchestrate an incident

```bash
curl -X POST http://localhost:8000/api/v1/agents/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"incident_id": "<incident-uuid>"}'
```

Example `data` response:

```json
{
  "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "workflow_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "accepted",
  "workflow": [
    "Evidence Agent",
    "Threat Intelligence Agent",
    "MITRE Mapping Agent",
    "Risk Assessment Agent",
    "Response Planning Agent",
    "Executive Report Agent",
    "Guardian Agent"
  ]
}
```

Each orchestration request creates an `agent_executions` record for the Coordinator Agent.

---

## Evidence Agent (Sprint 2 Task 4)

The Evidence Agent collects, validates, normalizes, and summarizes uploaded log evidence. No LLM calls, MCP tools, or threat analysis are performed.

### Collect evidence

```bash
curl -X POST http://localhost:8000/api/v1/agents/evidence \
  -H "Content-Type: application/json" \
  -d '{"incident_id": "<incident-uuid>", "log_file_id": "<log-uuid>"}'
```

Supported readable formats: `.log`, `.txt`, `.json`, `.csv`. EVTX files return a Sprint 2 parse note without failing.

When orchestrating with both `incident_id` and `log_id`, the Coordinator invokes the Evidence Agent first and includes `evidence_result` in the orchestration response.

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

The SQLite database and upload directory are created automatically on startup.

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

Verify health:

```bash
curl http://localhost:8000/api/v1/health
docker compose ps
```

Both services include health checks. SQLite is stored in the `oz-ai-data` volume and survives container restarts. Services use `restart: unless-stopped`.

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

### Endpoints (16)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Application root |
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/agents/orchestrate` | Generate Coordinator orchestration plan |
| POST | `/api/v1/agents/evidence` | Collect and summarize log evidence |
| GET | `/api/v1/dashboard/stats` | Dashboard metrics |
| GET | `/api/v1/system/tables` | Database table listing |
| GET | `/api/v1/system/mcp` | MCP server status and registered tools |
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
├── agents/                 # Google ADK agent definitions
│   ├── coordinator/        # Coordinator Agent (Sprint 2 Task 3)
│   └── evidence/           # Evidence Agent (Sprint 2 Task 4)
├── mcp/                    # MCP tool server and registry (Sprint 2 Task 2)
│   ├── server.py           # MCP server lifecycle
│   ├── registry.py         # Tool registration and invocation
│   └── tools/              # Registered MCP tool implementations
├── backend/
│   ├── app/
│   │   ├── api/            # HTTP route modules
│   │   ├── core/           # Config, logging, middleware, exceptions
│   │   ├── db/             # Database session and engine
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── repositories/   # Data access layer
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Shared utilities
│   │   └── main.py         # FastAPI entry point
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── components/     # Reusable UI (loading, toasts, tables)
│       ├── context/        # Global app state
│       ├── layouts/        # Layout wrappers
│       ├── pages/          # Route-level pages
│       ├── services/       # API client and service modules
│       └── utils/          # Formatting helpers
├── docker/                 # Dockerfiles
├── docs/                   # Project documentation
│   └── screenshots/        # UI screenshot placeholders
├── storage/uploads/        # Local log file storage
├── tests/                  # Backend integration tests
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

Backend formatting and linting:

```bash
cd backend
python -m ruff check ../backend/app ../tests
python -m isort --check-only ../backend/app ../tests
python -m black --check ../backend/app ../tests
```

---

## Roadmap

### Sprint 2 — ADK framework setup

- Google ADK integration and configuration
- Minimal Coordinator Agent placeholder
- Health endpoint ADK status reporting
- Startup validation for ADK and Coordinator

### Sprint 2 — MCP infrastructure

- MCP server, registry, and five initial tools
- `GET /api/v1/system/mcp` status endpoint
- Health endpoint MCP status reporting
- Tool registration tests (no duplicate registrations)

### Sprint 3 — Ingestion and API expansion

- Webhook ingestion endpoint for external alert sources
- Alert simulator scripts for development and demos
- Extended REST endpoints for evidence and investigation data
- API rate limiting and request validation hardening

### Sprint 4 — Evaluation and release hardening

- End-to-end test suite and CI pipeline
- Synthetic dataset packaging for demos
- Production Docker profile (multi-stage frontend build)
- Submission documentation and demo scenarios

See `docs/03_TASKS.md` for the full engineering backlog.

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
