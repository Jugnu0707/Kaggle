# 08 — Milestones and Sprint Progress

**Project Name:** Oz AI
**Version:** 1.0 (MVP)
**Last Updated:** 2026-06-27

> This document tracks sprint and milestone progress against the engineering backlog in `03_TASKS.md`. It reflects **implemented** state, not planned architecture.

---

## Sprint summary

| Sprint | Goal | Status | Key deliverables |
|--------|------|--------|------------------|
| Sprint 1 | Foundation | **Complete** | FastAPI backend, React dashboard, incident/log CRUD, Docker Compose, 16 core endpoints |
| Sprint 2 | ADK & MCP | **Complete** | Google ADK runtime, MCP registry (5 tools), Coordinator orchestration plan, Evidence Agent |
| Sprint 3 | Agents & workflow | **Complete** | 6 specialist agents, Guardian, Timeline Engine, Evaluation framework, Investigation Runner |
| Sprint 3.5 | Competition prep | **Complete** | Doc sync (T1), ADK/MCP runtime (T2), hardening (T3), demo assets (T4) |
| Sprint 4 Task 1 | Repository quality | **Complete** | README rewrite, architecture docs, community files, readiness report |
| Sprint 4 Task 2 | Kaggle submission docs | **Complete** | `docs/kaggle/` written materials for capstone submission |
| Sprint 4 | Release hardening | **In progress** | Auth, approval workflow, datasets, submission notebook |

---

## Milestone progress

| Milestone | Name | Progress | Notes |
|-----------|------|----------|-------|
| M1 | Foundation | ~90% | Auth middleware (M1-T25) not implemented; Docker frontend uses Vite dev mode |
| M2 | Data layer | ~95% | 15 tables implemented; names differ from original spec (`Evidence` vs `EvidenceBundle`) |
| M3 | Ingestion API | ~75% | Incident CRUD and read endpoints done; no webhook, no auto-pipeline on create |
| M4 | MCP tool layer | ~35% | 5 operational tools; planned 10 domain tools not implemented |
| M5 | Agent implementation | ~85% | All 8 agents implemented; ADK session/MCP agent wiring partial |
| M6 | Approval workflow | 0% | Not started |
| M7 | Frontend dashboard | ~70% | Core pages + Investigation Runner + Evaluation; Reports/Settings stubs; no approval UI |
| M8 | Evaluation | ~50% | Offline benchmark framework; no 30-scenario library or ADK Eval |
| M9 | Polish & submission | 0% | Not started |

---

## Implementation metrics (current)

| Metric | Value |
|--------|-------|
| API paths | 35 |
| API operations | 39 |
| Database tables | 16 |
| AI agents | 8 |
| MCP tools (registered) | 5 |
| Frontend pages | 10 |
| Tests | **176** collected |

---

## Sprint 3 deliverables (completed)

### Task 1–4 — Specialist agents

- Threat Intelligence, MITRE, Risk, Response agents with API endpoints and persistence
- Frontend integration on Incident Detail tabs

### Task 5 — Evaluation framework

- `evaluation/` package: engine, metrics, scorer, benchmark, report generator
- `GET /api/v1/evaluation` endpoints
- `EvaluationPage` at `/evaluation`
- `evaluation_metrics` table

### Task 6 — Investigation workflow

- `InvestigationWorkflowService` — full Coordinator-led pipeline
- `POST /api/v1/investigations/run`, `GET /api/v1/investigations/runs/{run_id}`
- `InvestigationRunnerPage` at `/incidents/:id/investigate`
- `investigation_runs` table

---

## Sprint 4 planned scope

1. API authentication (bearer token)
2. Response plan approval workflow (M6)
3. Synthetic datasets and `simulate_alert.py`
4. Docker production profile (Nginx, non-root, `evaluation/` in image)
5. 30-scenario evaluation library
6. Kaggle submission notebook and demo artifacts
7. Complete `07_SUBMISSION_CHECKLIST.md` verification

---

## Related documents

- [`03_TASKS.md`](03_TASKS.md) — Full task backlog with checkboxes
- [`05_PROGRESS.md`](05_PROGRESS.md) — Session journal
- [`07_SUBMISSION_CHECKLIST.md`](07_SUBMISSION_CHECKLIST.md) — Pre-submission verification
