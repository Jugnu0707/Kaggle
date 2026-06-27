# Sprint 3 Completion Report

**Project:** Oz AI  
**Sprint:** 3 — Agents & Workflow  
**Task:** 8 — Integration, performance, and acceptance validation  
**Date:** 2026-06-27  
**Status:** **Complete**

---

## Executive summary

Sprint 3 delivers a full multi-agent incident investigation platform: eight specialist agents, Coordinator orchestration, Guardian validation, Timeline and Evaluation engines, end-to-end investigation workflow, investigation replay with explainability, and a React operations dashboard. All **171 automated tests pass**. Performance benchmarks show sub-40 ms full investigation execution in-process with offline fallbacks.

---

## Features completed (Sprint 3)

| Area | Deliverable |
|------|-------------|
| Specialist agents | Evidence, Threat Intelligence, MITRE, Risk, Response, Executive Report, Guardian |
| Orchestration | Coordinator Agent + `InvestigationWorkflowService` |
| Workflow API | `POST /api/v1/investigations/run` |
| Timeline Engine | Event collection, normalization, deduplication |
| Evaluation framework | Offline benchmarks, health scores, persisted metrics |
| Investigation replay | Step-by-step replay, explainability, JSON/Markdown export |
| Frontend | Dashboard, incidents, logs, investigation runner, replay, evaluation |
| Demo readiness | `scripts/reset_demo.py` (Sprint 3.5) |

---

## API inventory (39 endpoints)

| # | Method | Path | Tag |
|---|--------|------|-----|
| 1 | GET | `/` | root |
| 2 | GET | `/api/v1/health` | health |
| 3 | GET | `/api/v1/ai/health` | ai |
| 4 | GET | `/api/v1/dashboard/stats` | dashboard |
| 5 | GET | `/api/v1/evaluation` | evaluation |
| 6 | GET | `/api/v1/evaluation/{agent_name}` | evaluation |
| 7 | GET | `/api/v1/system/tables` | system |
| 8 | GET | `/api/v1/system/mcp` | system |
| 9 | POST | `/api/v1/incidents` | incidents |
| 10 | GET | `/api/v1/incidents` | incidents |
| 11 | GET | `/api/v1/incidents/{id}` | incidents |
| 12 | GET | `/api/v1/incidents/{id}/mitre` | incidents |
| 13 | GET | `/api/v1/incidents/{id}/threat-intelligence` | incidents |
| 14 | GET | `/api/v1/incidents/{id}/risk` | incidents |
| 15 | GET | `/api/v1/incidents/{id}/response` | incidents |
| 16 | GET | `/api/v1/incidents/{id}/executive-report` | incidents |
| 17 | GET | `/api/v1/incidents/{id}/timeline` | incidents |
| 18 | GET | `/api/v1/incidents/{id}/timeline/export` | incidents |
| 19 | GET | `/api/v1/incidents/{id}/guardian-audits` | incidents |
| 20 | PUT | `/api/v1/incidents/{id}` | incidents |
| 21 | DELETE | `/api/v1/incidents/{id}` | incidents |
| 22 | POST | `/api/v1/logs/upload` | logs |
| 23 | GET | `/api/v1/logs` | logs |
| 24 | GET | `/api/v1/logs/{log_id}` | logs |
| 25 | DELETE | `/api/v1/logs/{log_id}` | logs |
| 26 | POST | `/api/v1/investigations/run` | investigations |
| 27 | GET | `/api/v1/investigations/runs/{run_id}` | investigations |
| 28 | GET | `/api/v1/investigations/{run_id}/replay` | investigations |
| 29 | GET | `/api/v1/investigations/{run_id}/explain` | investigations |
| 30 | GET | `/api/v1/investigations/{run_id}/replay/export` | investigations |
| 31 | POST | `/api/v1/agents/evidence` | agents |
| 32 | POST | `/api/v1/agents/threat-intelligence` | agents |
| 33 | POST | `/api/v1/agents/mitre` | agents |
| 34 | POST | `/api/v1/agents/risk` | agents |
| 35 | POST | `/api/v1/agents/response` | agents |
| 36 | POST | `/api/v1/agents/executive-report` | agents |
| 37 | POST | `/api/v1/agents/guardian/validate` | agents |
| 38 | POST | `/api/v1/agents/orchestrate` | agents |

OpenAPI documentation available at `/docs` with request/response schemas and error codes.

---

## Database tables (16)

`incidents`, `investigations`, `investigation_runs`, `investigation_replays`, `log_files`, `evidence`, `threat_intelligence_findings`, `mitre_findings`, `risk_assessments`, `response_plans`, `executive_reports`, `timeline_events`, `guardian_audits`, `agent_executions`, `audit_logs`, `evaluation_metrics`

---

## AI agents (8)

Coordinator, Evidence, Threat Intelligence, MITRE Mapping, Risk Assessment, Response Planning, Executive Report, Guardian

Additional workflow stages: Timeline Engine, Evaluation Engine

---

## MCP tools (5)

`health`, `list_incidents`, `incident_details`, `list_logs`, `system_info`

---

## Frontend pages (10)

Dashboard, Incidents, Incident Detail, Investigation Runner, Investigation Replay, Log Uploads, Reports, Evaluation, Settings, Not Found

---

## Integration test summary

| Test suite | Tests | Result |
|------------|-------|--------|
| Full suite | 171 | **Pass** |
| Sprint 3 E2E (`test_sprint3_e2e_integration.py`) | 1 | Pass |
| API inventory (`test_api_inventory.py`) | 6 | Pass |
| Reliability (`test_reliability.py`) | 7 | Pass |
| Investigation workflow | 5 | Pass |
| Investigation replay | 5 | Pass |

E2E workflow validated: Dashboard → Incident → Log upload → Investigation → all agent stages → Evaluation → Replay → Export.

---

## Performance summary

See [`SPRINT3_PERFORMANCE_REPORT.md`](SPRINT3_PERFORMANCE_REPORT.md).

| Operation | Mean (ms) |
|-----------|-----------|
| Dashboard load | 3.5 |
| Incident details load | 2.6 |
| Full investigation | 36.6 |
| Replay generation | 2.1 |
| Timeline API | 5.5 |
| Evaluation dashboard | 2.1 |

Regenerate: `python scripts/sprint3_performance_benchmark.py`

---

## Reliability validation

| Scenario | Result |
|----------|--------|
| AI unavailable (no API key) | Investigation completes with fallbacks |
| Gemini quota error | Workflow continues with fallback |
| Invalid AI JSON response | Fallback engines used |
| Investigation without log | Evidence stages skipped; pipeline continues |
| Invalid file extension | 400 with error envelope |
| Large file (> limit) | 400 rejected |
| Missing incident | 404 on all read endpoints |
| Database re-init | Health reports `database_connected: true` |

---

## Docker validation

| Check | Status |
|-------|--------|
| `docker-compose.yml` syntax | Valid |
| Backend healthcheck | Configured (`/api/v1/health`) |
| Frontend healthcheck | Configured (port 5173) |
| SQLite volume | `oz-ai-data` |
| Upload volume | `oz-ai-uploads` |
| ADK/MCP env vars | Present |
| **Runtime `docker compose up`** | **Not executed** (Docker CLI unavailable in validation environment) |

Recommended manual verification: `docker compose up --build` from a fresh clone.

---

## Repository quality

| Tool | Status |
|------|--------|
| pytest | 171 passed |
| Ruff | Run with auto-fix on `app/`; minor style items remain in agents package |
| Black | Applied to `backend/app` |
| Secrets in repo | None committed |
| `.gitignore` | Covers `.env`, `*.db`, uploads, caches |

---

## Known limitations

1. No API authentication (planned Sprint 4)
2. Human approval workflow not enforced in UI/API
3. Frontend Docker uses Vite dev server, not production Nginx build
4. Live Gemini required for AI (non-fallback) agent paths
5. Docker not verified in CI/sandbox environment
6. Kaggle submission notebook and demo video not created

---

## Technical debt

1. Consolidate duplicate agent runtime initialization paths
2. Persist investigation `stages` JSON on `investigation_runs` for `get_run` replay without `investigation_replays`
3. Add incident-scoped log list filter on API
4. Production Docker profile (Nginx, non-root backend)
5. Expand evaluation to 30-scenario labeled library
6. Address remaining Ruff warnings in `agents/` package

---

## Definition of done — Sprint 3

| Criterion | Met |
|-----------|-----|
| All implemented agents execute correctly | Yes |
| Full investigation workflow works | Yes |
| Replay works | Yes |
| Evaluation works | Yes |
| No critical bugs in test suite | Yes |
| Tests pass | 171/171 |
| Docker compose file valid | Yes |
| Documentation reflects Sprint 3 | Yes |

---

## Recommendations before Sprint 3.5 / 4

1. Run `docker compose up --build` on a clean machine and document results
2. Record demo video walking Investigation Runner → Replay
3. Complete Kaggle submission notebook
4. Implement API authentication and response approval gates
5. Add frontend production Docker profile
6. Expand performance benchmarks with live Gemini latency samples

---

*Sprint 3 Task 8 validation complete.*
