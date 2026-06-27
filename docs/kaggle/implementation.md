# Implementation

This document describes how Oz AI is implemented across backend, frontend, database, Docker, AI runtime, and evaluation — including key engineering decisions.

---

## Backend

**Stack:** Python 3.12, FastAPI 0.138, SQLAlchemy 2.0, Pydantic v2, uvicorn

**Structure:**

| Layer | Path | Responsibility |
|-------|------|----------------|
| API routes | `backend/app/api/v1/` | 10 route modules, 39 HTTP operations |
| Services | `backend/app/services/` | Business logic, workflow orchestration |
| Repositories | `backend/app/repositories/` | Data access abstraction |
| Models | `backend/app/models/` | 16 SQLAlchemy ORM tables |
| Schemas | `backend/app/schemas/` | Request/response validation |
| Core runtimes | `backend/app/core/` | ADK, MCP, Guardian, agent runtimes |
| AI layer | `backend/app/ai/` | Gemini provider, runtime, registry |

**Key decisions:**

- **Explicit investigation trigger** — Creating an incident does not start agents; `POST /investigations/run` is the single workflow entry point.
- **Service-oriented agents** — Agent logic lives in `agents/` packages; backend services bridge API routes to agent services.
- **Guardian between stages** — `orchestration_guardian.py` validates each output before the workflow advances.
- **Replay persistence** — `investigation_replays` stores step metadata for explainability without exposing secrets.
- **Unified response envelope** — Most endpoints use `APIResponse[T]`; AI connectivity test returns flat JSON for minimal probe semantics.

**Workflow service:** `backend/app/services/investigation_workflow_service.py` coordinates the full pipeline and records replay steps.

---

## Frontend

**Stack:** React 19, TypeScript (strict), Tailwind CSS, Vite, React Router

**Pages (10):**

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

**Key decisions:**

- **Tab-based incident detail** — Each agent output maps to a dedicated tab with typed API service modules in `frontend/src/services/`.
- **Polling for run status** — Investigation Runner polls run status until completion (no WebSockets in MVP).
- **Shared layout** — `DashboardLayout` with sidebar navigation across all routes.

---

## Database

**Engine:** SQLite (MVP) via SQLAlchemy  
**URL:** `DATABASE_URL` default `sqlite:///./oz_ai.db`

**16 tables:**

`incidents`, `log_files`, `investigations`, `investigation_runs`, `investigation_replays`, `evidence`, `mitre_findings`, `threat_intelligence_findings`, `risk_assessments`, `response_plans`, `executive_reports`, `guardian_audits`, `timeline_events`, `agent_executions`, `audit_logs`, `evaluation_metrics`

**Key decisions:**

- **SQLite for MVP** — Single-file database simplifies demo deployment; PostgreSQL migration planned for production.
- **Append-only audits** — `audit_logs` and `guardian_audits` are never updated or deleted by application code.
- **Per-agent persistence** — Each specialist agent writes to its own table, enabling independent API reads and timeline reconstruction.
- **UUID primary keys** — All entity IDs use UUID strings for API consistency.

Schema introspection: `GET /api/v1/system/tables`

---

## Docker

**Files:** `docker-compose.yml`, `docker/Dockerfile.backend`, `docker/Dockerfile.frontend`

| Service | Port | Notes |
|---------|------|-------|
| `backend` | 8000 | Python 3.12-slim, copies agents/mcp/evaluation |
| `frontend` | 5173 | Node 20-alpine, Vite dev server |

**Volumes:** `backend-data` (SQLite), `upload-data` (log files)

**Key decisions:**

- **Monorepo image** — Backend image includes agent and MCP packages from repo root paths.
- **Dev-mode frontend** — Vite dev server in Docker for rapid iteration; production Nginx profile planned Sprint 4.
- **Empty default API key** — `GOOGLE_API_KEY` defaults to empty in compose for offline demo safety.

**Commands:**

```bash
docker compose up --build
python scripts/reset_demo.py
```

---

## AI

**Providers:** Google ADK (configuration), Google Gemini (`google.genai`)

| Component | Path |
|-----------|------|
| AI settings | `backend/app/core/ai_config.py` |
| Gemini provider | `backend/app/ai/provider.py` |
| ADK runtime | `backend/app/core/adk_runtime.py` |
| AI runtime/registry | `backend/app/ai/runtime.py` |
| Connectivity test | `backend/app/services/ai_test_service.py` |

**AI-first agents:** Threat Intelligence, Risk, Response, Executive Report

**Key decisions:**

- **Optional Gemini** — Empty `GOOGLE_API_KEY` triggers deterministic fallbacks across all AI-first agents.
- **JSON-only Gemini responses** — AI agents request `response_mime_type=application/json` where applicable.
- **30-second timeout** — AI requests use `ThreadPoolExecutor` with timeout; timeout triggers fallback.
- **Single-token connectivity probe** — `GET /api/v1/ai/test` sends one minimal prompt expecting `READY` to verify API key without agent orchestration.
- **Centralized client** — `GeminiProvider` is the single Gemini configuration source; agent services may also call `genai.Client` directly with shared settings.

---

## Evaluation

**Package:** `evaluation/` (engine, benchmark, metrics, scorer, report_generator)

| Component | Purpose |
|-----------|---------|
| `evaluation/engine.py` | Run evaluation scenarios |
| `evaluation/benchmark.py` | Benchmark runner |
| `evaluation/metrics.py` | Metric definitions |
| `evaluation/scorer.py` | Score agent outputs |
| `evaluation/report_generator.py` | Generate evaluation reports |

**API:** `GET /api/v1/evaluation`, `GET /api/v1/evaluation/{agent_name}`  
**UI:** `EvaluationPage` at `/evaluation`  
**Persistence:** `evaluation_metrics` table

**Key decisions:**

- **Offline benchmarks** — Evaluation runs without external API dependencies.
- **Per-agent health scores** — Dashboard surfaces agent performance for judges and operators.
- **Workflow integration** — Evaluation Engine runs at the end of every investigation workflow.

---

## Quality tooling

| Tool | Scope |
|------|-------|
| pytest | 176 automated tests |
| Ruff + Black | Python formatting and linting |
| TypeScript strict | Frontend type safety |
| OpenAPI | Auto-generated at `/docs` |

**Test locations:** `tests/`, `evaluation/tests/`, `agents/*/tests/`, `backend/app/services/timeline/tests/`
