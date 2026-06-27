# Submission Notes

This document maps Oz AI's implementation to Kaggle AI Agents Intensive Capstone judging criteria. It is written for Google engineers and Kaggle judges evaluating the Agents for Business track submission.

**Competition:** Kaggle AI Agents Intensive Capstone  
**Track:** Agents for Business  
**Project:** Oz AI — Enterprise Incident Response Platform  
**Repository:** https://github.com/Jugnu0707/Kaggle

---

## Judging criteria mapping

### Innovation

**Criterion:** Novel application of AI agents to a real business problem.

**Oz AI evidence:**

- Eight specialist agents in a directed investigation pipeline — not a single general-purpose chatbot
- Guardian safety layer between every specialist stage (uncommon in capstone projects)
- Investigation replay with explainability (`ai_used`, `fallback_used`, step latency)
- Offline-first design: full demo without API keys via deterministic fallbacks
- Executive report generation that excludes raw logs from leadership output

**Where to look:** `POST /api/v1/investigations/run`, `docs/kaggle/ai_agents.md`, Investigation Replay page

---

### Architecture

**Criterion:** Clear system design with appropriate separation of concerns.

**Oz AI evidence:**

- Layered architecture: React → FastAPI → Services → Agents → Guardian → Engines → SQLite
- 16 normalized database tables with per-agent persistence
- Repository pattern for data access; service layer for business logic
- ADK runtime, MCP runtime, and Gemini provider as distinct integration layers
- Mermaid diagrams in `docs/architecture/`

**Repository statistics:** 35 API paths, 39 operations, 8 agents, 16 tables, 5 MCP tools, 10 frontend pages, 176 tests

**Where to look:** `docs/kaggle/architecture.md`, `docs/architecture/`, `docs/02_ARCHITECTURE.md`

---

### Google ADK

**Criterion:** Meaningful use of Google Agent Development Kit.

**Oz AI evidence:**

- ADK verified at startup (`backend/app/core/adk_runtime.py`)
- Eight agents with ADK configuration objects (`agents/*/agent.py`)
- Agent registry with versioned metadata (`backend/app/ai/registry.py`)
- ADK app name and tracing configuration (`ADK_APP_NAME`, `ADK_ENABLE_TRACING`)
- Prompt files versioned per agent (`agents/*/prompt.md`)

**Gap:** ADK session checkpointing and `adk eval` not yet implemented.

**Where to look:** `agents/coordinator/agent.py`, Settings page (ADK status), `GET /api/v1/system/mcp`

---

### MCP (Model Context Protocol)

**Criterion:** MCP tool registry and operational tool exposure.

**Oz AI evidence:**

- Custom MCP registry with typed input/output schemas (`mcp/registry.py`)
- Five registered tools with startup logging (`mcp/server.py`)
- MCP runtime integrated into AI runtime (`backend/app/core/mcp_runtime.py`)
- API introspection: `GET /api/v1/system/mcp`
- MCP interaction diagram: `docs/architecture/mcp-interaction.md`

**Gap:** Domain MCP tools not implemented; agents call services directly today.

**Where to look:** `mcp/tools/`, Settings page (MCP tool list)

---

### Security

**Criterion:** Responsible AI, output validation, and safety guardrails.

**Oz AI evidence:**

- Guardian Agent: prompt injection detection, PII masking, secret detection, schema validation, confidence thresholds
- Guardian invoked between every workflow stage (`orchestration_guardian.py`)
- Append-only `guardian_audits` and `audit_logs` tables
- Sanitized replay export (`backend/app/utils/sanitize.py`)
- Secrets in environment variables only; `.env` gitignored
- Response plans are recommendations only — no automatic remediation
- Human approval gate architecturally documented

**Gap:** API authentication and approval workflow enforcement not yet implemented.

**Where to look:** `agents/guardian/`, Guardian tab in Incident Detail, `docs/kaggle/limitations.md`

---

### Deployability

**Criterion:** Runnable by judges with minimal setup.

**Oz AI evidence:**

- `docker compose up --build` — two-service stack
- `python scripts/reset_demo.py` — one-click demo (10 incidents, 25 logs)
- Offline demo mode without `GOOGLE_API_KEY`
- `GET /api/v1/ai/test` — verify Gemini connectivity with minimal token usage
- `GET /api/v1/health` — health check
- Environment template: `.env.example`

**Commands for judges:**

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
cp .env.example .env
docker compose up --build
python scripts/reset_demo.py
open http://localhost:5173
open http://localhost:8000/docs
```

**Where to look:** `README.md`, `docker-compose.yml`, `scripts/reset_demo.py`

---

### Documentation

**Criterion:** Professional, complete, accurate documentation.

**Oz AI evidence:**

- Complete README with badges, statistics, architecture, demo workflow
- `docs/kaggle/` — submission write-up (this directory)
- `docs/architecture/` — Mermaid diagrams and high-resolution architecture PNG
- `docs/COMPETITION_ALIGNMENT.md` — requirement-to-code mapping
- `docs/REPOSITORY_READINESS_REPORT.md` — audit report (82/100)
- Root community files: LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, ROADMAP
- Per-agent README files in `agents/*/README.md`
- OpenAPI documentation at `/docs`

**Where to look:** `README.md`, `docs/kaggle/`, `docs/architecture/`

---

### User Experience

**Criterion:** Intuitive dashboard for security analysts and judges.

**Oz AI evidence:**

- 10-page React dashboard with consistent dark-theme layout
- Tabbed Incident Detail for every agent output
- Investigation Runner with live status polling
- Investigation Replay with step navigation, AI/Fallback badges, JSON/Markdown export
- Evaluation dashboard with per-agent health scores
- Settings page showing health, ADK, and MCP status
- Demo screenshots in `docs/demo/`

**Demo path (10 minutes):**

1. Dashboard → incident overview
2. Incidents → Suspicious PowerShell Execution
3. Review all agent tabs
4. Run new investigation
5. View replay and export
6. Evaluation dashboard
7. Settings → verify ADK and MCP

**Where to look:** `frontend/src/pages/`, `docs/demo/`

---

## Repository statistics (verified)

| Metric | Count |
|--------|-------|
| API paths | 35 |
| API operations | 39 |
| AI agents | 8 |
| Database tables | 16 |
| Frontend pages | 10 |
| MCP tools | 5 |
| Automated tests | 176 |
| Documentation files | 46 |
| Lines of code (approx.) | 29,333 |

Regenerate: `python scripts/generate_repo_stats.py`

---

## Submission artifacts status

| Artifact | Status | Location |
|----------|--------|----------|
| Problem statement | Complete | `docs/kaggle/problem_statement.md` |
| Solution description | Complete | `docs/kaggle/solution.md` |
| Architecture documentation | Complete | `docs/kaggle/architecture.md` |
| Agent documentation | Complete | `docs/kaggle/ai_agents.md` |
| Implementation notes | Complete | `docs/kaggle/implementation.md` |
| Evaluation report | Complete | `docs/kaggle/evaluation.md` |
| Limitations | Complete | `docs/kaggle/limitations.md` |
| Future work | Complete | `docs/kaggle/future_work.md` |
| Demo video script | Complete | `docs/demo/demo_script.md` |
| Final checklist | Complete | `docs/kaggle/final_checklist.md` |
| Mermaid diagrams | Complete | `docs/diagrams/` |
| Screenshots (12 views) | Complete | `docs/screenshots/` |
| Kaggle notebook | **Pending** | Sprint 4 |
| Demo video recording | **Pending** | Sprint 4 |

---

## Recommended judge review order

1. `README.md` — overview and quickstart
2. `docker compose up --build` + `python scripts/reset_demo.py`
3. Dashboard → Incident Detail tabs → Investigation Runner
4. `GET /api/v1/ai/test` in Swagger (if API key configured)
5. Investigation Replay and export
6. Evaluation dashboard and Settings (ADK/MCP status)
7. `docs/kaggle/` written materials
8. `docs/diagrams/` and `docs/architecture/` diagrams
9. `docs/kaggle/final_checklist.md` — submission verification
10. `cd backend && uv run pytest` — test verification

---

## Contact and license

- **License:** MIT ([LICENSE](../../LICENSE))
- **Contributing:** [CONTRIBUTING.md](../../CONTRIBUTING.md)
- **Security:** [SECURITY.md](../../SECURITY.md)
