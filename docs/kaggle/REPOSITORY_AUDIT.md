# Oz AI — Repository Audit

**Audit date:** 2026-06-28  
**Repository:** https://github.com/Jugnu0707/Kaggle  
**License:** MIT (`LICENSE`)  
**Method:** Filesystem inspection, OpenAPI introspection, pytest collection, git inventory. No reused legacy doc counts.

---

## Executive summary

Oz AI is a full-stack incident response platform: FastAPI backend, React 19 frontend, eight Google ADK agents, Guardian validation, MCP tool registry, SQLite persistence, Docker Compose deployment, and 176 automated tests. The README metrics for agents, API surface, database tables, pages, MCP tools, and tests match live repository inspection.

---

## Verified statistics

| Metric | Count | Evidence |
|--------|------:|----------|
| Python files (`.py`, excl. `__pycache__`, `.venv`, `node_modules`) | **259** | `find` across repo |
| Frontend TypeScript/TSX (`frontend/src/`) | **42** | 24 `.tsx` + 18 `.ts` |
| AI specialist agents | **8** | `agents/*/agent.py` |
| API paths | **35** | `app.openapi()` via `backend/app/main.py` |
| API operations | **39** | OpenAPI operation count |
| Database tables | **16** | `backend/app/models/*` `__tablename__` |
| Frontend pages | **10** | `frontend/src/App.tsx` routes |
| Shared UI components | **11** | 10 in `components/` + 1 layout |
| Automated tests | **176** | `backend/.venv/bin/pytest --collect-only -q` |
| MCP tools | **5** | `@register_tool` in `mcp/tools/` |
| Docker Compose services | **2** | `backend`, `frontend` |
| GitHub Actions workflows | **0** | `.github/workflows/` absent |

---

## Technology stack (verified)

| Layer | Technology | Source |
|-------|------------|--------|
| Backend runtime | Python ≥3.12 | `backend/pyproject.toml` |
| API framework | FastAPI 0.138.1 | `backend/pyproject.toml` |
| ORM | SQLAlchemy 2.x | `backend/pyproject.toml` |
| Frontend | React 19, TypeScript, Vite 6, Tailwind | `frontend/package.json` |
| AI framework | Google ADK 2.3.0 | `backend/pyproject.toml`, `agents/*/agent.py` |
| LLM provider | google-genai (Gemini) | `backend/app/ai/provider.py` |
| Persistence | SQLite + file uploads | `DATABASE_URL`, `storage/uploads/` |
| Containerization | Docker Compose (2 services) | `docker-compose.yml` |
| Dependency manifest | `backend/pyproject.toml` only | No `requirements.txt` in repo |

---

## Agents (8)

| Agent | Directory | Registry name |
|-------|-----------|---------------|
| Coordinator | `agents/coordinator/` | Coordinator Agent |
| Evidence | `agents/evidence/` | Evidence Agent |
| Threat Intelligence | `agents/threat_intelligence/` | Threat Intelligence Agent |
| MITRE Mapping | `agents/mitre/` | MITRE Mapping Agent |
| Risk Assessment | `agents/risk/` | Risk Assessment Agent |
| Response Planning | `agents/response/` | Response Planning Agent |
| Executive Report | `agents/executive_report/` | Executive Report Agent |
| Guardian | `agents/guardian/` | Guardian Agent |

**Not ADK agents (separate engines):** Timeline Engine (`backend/app/services/timeline/`), Evaluation Engine (`evaluation/`).

---

## MCP tools (5)

| Tool | File |
|------|------|
| `health` | `mcp/tools/health.py` |
| `list_incidents` | `mcp/tools/incidents.py` |
| `incident_details` | `mcp/tools/incidents.py` |
| `list_logs` | `mcp/tools/logs.py` |
| `system_info` | `mcp/tools/system_info.py` |

Agents invoke backend services directly at runtime; MCP is registered and exposed via `GET /api/v1/system/mcp`.

---

## Database tables (16)

`agent_executions`, `audit_logs`, `evaluation_metrics`, `evidence`, `executive_reports`, `guardian_audits`, `incidents`, `investigations`, `investigation_replays`, `investigation_runs`, `log_files`, `mitre_findings`, `response_plans`, `risk_assessments`, `threat_intelligence_findings`, `timeline_events`.

---

## Frontend pages (10)

| Route | Page |
|-------|------|
| `/` | Dashboard |
| `/incidents` | Incidents list |
| `/incidents/:id` | Incident detail (tabbed) |
| `/incidents/:id/investigate` | Investigation runner |
| `/investigations/:runId/replay` | Investigation replay |
| `/logs` | Log upload |
| `/reports` | Reports (incident list linking to detail) |
| `/evaluation` | Evaluation dashboard |
| `/settings` | System settings |
| `*` | Not found |

---

## Scripts and demo

| Script | Purpose |
|--------|---------|
| `scripts/dev.sh` | Start backend + frontend |
| `scripts/reset_demo.py` | Wipe DB, seed 10 incidents, run showcase investigations |
| `scripts/record_demo.py` | Automated Playwright demo → `demo/output/demo.mp4` |
| `scripts/generate_assets.py` | PIL-generated screenshot assets for docs |

**Demo video (local, not git-tracked by default):** `demo/output/demo.mp4` (~167 s, 1920×1080) produced by `scripts/record_demo.py`.

---

## Documentation inventory

| Area | Location |
|------|----------|
| README | `README.md` |
| Architecture | `docs/02_ARCHITECTURE.md`, `docs/architecture/` |
| Kaggle writeup | `docs/kaggle/` (23 files) |
| Demo guides | `docs/demo/` |
| API | Swagger at `/docs` when backend running |

---

## CI / GitHub

| Item | Status |
|------|--------|
| `.github/workflows/` | **Not present** |
| `.github/SECURITY.md` | Present |
| `.github/CONTRIBUTING.md` | Present |
| Remote | `git@github.com:Jugnu0707/Kaggle.git` |

---

## README accuracy

| Claim | Verified |
|-------|----------|
| 8 agents | Yes |
| 35 paths / 39 operations | Yes |
| 16 tables | Yes |
| 10 pages | Yes |
| 5 MCP tools | Yes |
| 176 tests | Yes |
| Docker Compose | Yes |
| MIT license | Yes |
| GitHub Actions CI | **Not implemented** |
| `requirements.txt` | **Not present** (uses `pyproject.toml`) |

---

## Screenshot asset sources

| Location | Type | Resolution |
|----------|------|------------|
| `docs/screenshots/` | PIL-generated renders (`scripts/generate_assets.py`) | 1440×900 |
| `docs/demo/` | Duplicate generated renders | 1440×900 |
| `demo/output/screenshots/` | Live Playwright captures (`scripts/record_demo.py`) | 1920×1080 |

Judges should prefer `demo/output/` captures where available for authenticity; `docs/screenshots/` are stylized documentation assets.

---

## Feature verification matrix

| Feature | Status | Notes |
|---------|--------|-------|
| Multi-agent investigation pipeline | **Implemented** | `POST /api/v1/investigations/run` |
| Google ADK agent registration | **Implemented** | 8 agents, startup init |
| Gemini AI + offline fallbacks | **Implemented** | 4 AI-first agents + rule fallbacks |
| Guardian validation | **Implemented** | Between specialist stages |
| Investigation replay | **Implemented** | `/investigations/:runId/replay` |
| Evaluation dashboard | **Implemented** | API + UI + `evaluation/` engine |
| Timeline reconstruction | **Implemented** | Post-pipeline engine |
| MCP tool registry | **Partial** | 5 operational tools; agents use direct service calls |
| Docker deployment | **Implemented** | 2-service compose |
| Demo reset script | **Implemented** | Offline-capable |
| Automated demo recording | **Implemented** | `scripts/record_demo.py` |
| API authentication | **Not implemented** | Documented in limitations |
| RBAC | **Not implemented** | |
| SIEM connectors | **Not implemented** | |
| GitHub Actions CI | **Not implemented** | |
| PDF executive export | **Not implemented** | JSON + Markdown only |
| Reports dedicated view | **Partial** | Lists incidents; links to executive report tab |
| Human approval workflow | **Not implemented** | Documented only |
| WebSocket live updates | **Not implemented** | HTTP polling |

---

## Gaps for submission

1. No GitHub Actions workflow (tests not CI-gated in repo).
2. Five notebook screenshots missing from `docs/screenshots/` (incidents list, settings, log upload, reports, replay) — available in `demo/output/screenshots/` after running `record_demo.py`.
3. `docs/screenshots/` are generated renders, not live UI captures — disclose in notebook.
