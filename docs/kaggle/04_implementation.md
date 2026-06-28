# Implementation

**Related:** [03 Architecture](03_architecture.md) · [05 AI Agents](05_ai_agents.md) · [07 Evaluation](07_evaluation.md)

This document describes how Oz AI is implemented across backend, frontend, database, AI runtime, Docker, and testing.

---

## Backend

**Stack:** Python 3.12, FastAPI 0.138, SQLAlchemy 2.0, Pydantic v2, uvicorn

| Layer | Path | Responsibility |
|-------|------|----------------|
| API routes | `backend/app/api/v1/` | 10 route modules, 39 HTTP operations, 35 paths |
| Services | `backend/app/services/` | Business logic, workflow orchestration |
| Repositories | `backend/app/repositories/` | Data access abstraction |
| Models | `backend/app/models/` | 16 SQLAlchemy ORM tables |
| Schemas | `backend/app/schemas/` | Request/response validation |
| Core runtimes | `backend/app/core/` | ADK, MCP, Guardian, agent runtimes |
| AI layer | `backend/app/ai/` | Gemini provider, runtime, registry |

**Key behaviors:**

- Investigations triggered explicitly via `POST /api/v1/investigations/run`
- Agent logic in `agents/` packages; backend services bridge API routes to agent services
- Guardian validates each stage via `orchestration_guardian.py`
- Replay steps persisted to `investigation_replays` with sanitized summaries
- Most endpoints use `APIResponse[T]` response envelope

**Workflow service:** `backend/app/services/investigation_workflow_service.py`

---

## Frontend

**Stack:** React 19, TypeScript (strict), Tailwind CSS, Vite 6, React Router 7

| Page | Route | Purpose |
|------|-------|---------|
| Dashboard | `/` | Incident counts, recent activity |
| Incidents | `/incidents` | Incident list and creation |
| Incident Detail | `/incidents/:id` | Tabbed agent outputs |
| Investigation Runner | `/incidents/:id/investigate` | Start and monitor runs |
| Investigation Replay | `/investigations/:runId/replay` | Step replay and export |
| Log Upload | `/logs` | Upload and manage log files |
| Reports | `/reports` | Executive report access |
| Evaluation | `/evaluation` | Agent health dashboard |
| Settings | `/settings` | Health, ADK, MCP status |
| Not Found | `*` | 404 handler |

**Key behaviors:**

- Tab-based incident detail with typed API service modules in `frontend/src/services/`
- Investigation Runner polls run status until completion (no WebSockets)
- Shared `DashboardLayout` with sidebar navigation

---

## Database

**Engine:** SQLite via SQLAlchemy  
**Default URL:** `sqlite:///./oz_ai.db` (Docker: `sqlite:////app/data/oz_ai.db`)

**16 tables:**

`incidents`, `log_files`, `investigations`, `investigation_runs`, `investigation_replays`, `evidence`, `mitre_findings`, `threat_intelligence_findings`, `risk_assessments`, `response_plans`, `executive_reports`, `guardian_audits`, `timeline_events`, `agent_executions`, `audit_logs`, `evaluation_metrics`

**Key behaviors:**

- UUID primary keys on all entities
- Per-agent persistence in dedicated tables
- Append-only `audit_logs` and `guardian_audits`
- Schema introspection: `GET /api/v1/system/tables`

---

## AI

**Providers:** Google ADK (configuration), Google Gemini (`google-genai`)

| Component | Path |
|-----------|------|
| AI settings | `backend/app/core/ai_config.py` |
| Gemini provider | `backend/app/ai/provider.py` |
| ADK runtime | `backend/app/core/adk_runtime.py` |
| AI runtime/registry | `backend/app/ai/runtime.py` |
| Connectivity test | `backend/app/services/ai_test_service.py` |

**AI-first agents:** Threat Intelligence, Risk, Response, Executive Report

**Key behaviors:**

- Empty `GOOGLE_API_KEY` triggers deterministic fallbacks
- JSON-mode Gemini responses where applicable
- AI requests use timeout with fallback on failure
- `GET /api/v1/ai/test` sends minimal probe expecting `READY`

---

## Docker

**Files:** `docker-compose.yml`, `docker/Dockerfile.backend`, `docker/Dockerfile.frontend`

| Service | Port | Notes |
|---------|------|-------|
| `oz-ai-backend` | 8000 | Includes `agents/`, `mcp/`, `evaluation/` |
| `oz-ai-frontend` | 5173 | Vite dev server |

**Volumes:** `oz-ai-data` (SQLite), `oz-ai-uploads` (log files)

```bash
docker compose up --build
python scripts/reset_demo.py
```

---

## Testing

| Tool | Scope |
|------|-------|
| pytest | 176 automated tests |
| Ruff + Black | Python formatting and linting |
| TypeScript strict | Frontend type safety |
| OpenAPI | Auto-generated at `/docs` |

**Test locations:** `tests/`, `evaluation/tests/`, `agents/*/tests/`, `backend/app/services/timeline/tests/`

**Categories:** API endpoints, Guardian validation, investigation workflow, MCP registry, AI connectivity, database initialization, agent service unit tests

```bash
cd backend && uv run pytest
```

Quality tooling configuration: `backend/pyproject.toml`, `frontend/tsconfig.json`
