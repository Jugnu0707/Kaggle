# Results

**Related:** [04 Implementation](04_implementation.md) · [07 Evaluation](07_evaluation.md) · [11 Competition Mapping](11_competition_mapping.md)

Summary of verified implementation metrics. Regenerate statistics with `python scripts/generate_repo_stats.py`.

---

## Repository statistics

| Metric | Count | Verification |
|--------|-------|--------------|
| API paths | 35 | `scripts/generate_repo_stats.py`, `tests/test_api_inventory.py` |
| API operations | 39 | Same |
| AI agents | 8 | `backend/app/ai/registry.py` |
| MCP tools | 5 | `mcp/registry.py` |
| Database tables | 16 | `backend/app/models/`, `GET /api/v1/system/tables` |
| Frontend pages | 10 | `frontend/src/pages/` |
| Automated tests | 176 | `cd backend && uv run pytest --collect-only` |
| Documentation files | 81 | `scripts/generate_repo_stats.py` |
| Lines of code (approx.) | 29,679 | `scripts/generate_repo_stats.py` |

---

## APIs

**Base URL:** `http://localhost:8000/api/v1`

| Module | Prefix | Operations |
|--------|--------|------------|
| Health | `/health` | Application health, ADK/MCP status |
| Incidents | `/incidents` | CRUD, agent output reads |
| Logs | `/logs` | Upload, list, retrieve |
| Investigations | `/investigations` | Run, replay, explain, export |
| Agents | `/agents` | Per-agent execution, orchestration, Guardian |
| Evaluation | `/evaluation` | Health scores |
| AI | `/ai` | Connectivity test, runtime status |
| System | `/system` | Tables, MCP status |
| Dashboard | `/dashboard` | Summary metrics |

OpenAPI documentation: http://localhost:8000/docs

---

## Tests

| Metric | Value |
|--------|-------|
| Tests collected | 176 |
| Test locations | `tests/`, `evaluation/tests/`, `agents/*/tests/` |

Key test files:

- `tests/test_investigation_workflow.py` — end-to-end workflow
- `tests/test_guardian_agent.py` — Guardian validation
- `tests/test_ai_test.py` — Gemini connectivity
- `tests/test_api_inventory.py` — API path/operation inventory

---

## Agents

Eight registered agents:

| Agent | API Endpoint |
|-------|--------------|
| Coordinator | `POST /api/v1/agents/orchestrate` |
| Evidence | `POST /api/v1/agents/evidence` |
| Threat Intelligence | `POST /api/v1/agents/threat-intelligence` |
| MITRE Mapping | `POST /api/v1/agents/mitre` |
| Risk Assessment | `POST /api/v1/agents/risk` |
| Response Planning | `POST /api/v1/agents/response` |
| Executive Report | `POST /api/v1/agents/executive-report` |
| Guardian | `POST /api/v1/agents/guardian/validate` |

Full pipeline: `POST /api/v1/investigations/run`

Non-agent engines: Timeline Engine, Evaluation Engine (workflow stages, not separate API agents)

---

## MCP tools

| Tool | Description |
|------|-------------|
| `health` | Application health status |
| `list_incidents` | Paginated incident list |
| `incident_details` | Single incident by ID |
| `list_logs` | Uploaded log metadata |
| `system_info` | Version, database, ADK, MCP status |

Introspection: `GET /api/v1/system/mcp`

---

## Database tables

`incidents`, `log_files`, `investigations`, `investigation_runs`, `investigation_replays`, `evidence`, `mitre_findings`, `threat_intelligence_findings`, `risk_assessments`, `response_plans`, `executive_reports`, `guardian_audits`, `timeline_events`, `agent_executions`, `audit_logs`, `evaluation_metrics`

---

## UI pages

| Page | Route |
|------|-------|
| Dashboard | `/` |
| Incidents | `/incidents` |
| Incident Detail | `/incidents/:id` |
| Investigation Runner | `/incidents/:id/investigate` |
| Investigation Replay | `/investigations/:runId/replay` |
| Log Upload | `/logs` |
| Reports | `/reports` |
| Evaluation | `/evaluation` |
| Settings | `/settings` |
| Not Found | `*` |

---

## Demo capability

`python scripts/reset_demo.py` seeds:

- 10 incidents covering common attack scenarios
- 25 log files
- Investigations on showcase incidents
- All agent output tabs populated (offline fallbacks when no API key)

---

## Performance (documented benchmarks only)

From `docs/SPRINT3_PERFORMANCE_REPORT.md` via `scripts/sprint3_performance_benchmark.py`:

| Operation | Mean (ms) |
|-----------|-----------|
| Full investigation (offline) | 36.57 |
| Dashboard load | 3.51 |
| Incident details load | 2.63 |

These are in-process benchmarks excluding network latency and Gemini API calls.

---

## Submission artifacts status

| Artifact | Status |
|----------|--------|
| Written documentation (`docs/kaggle/`) | Complete |
| Architecture diagrams (Mermaid) | Complete |
| Screenshots (12 views) | Generated renders in `docs/screenshots/` |
| Kaggle submission notebook | Not started |
| Demo video | Not started |

See [12 Submission Notes](12_submission_notes.md).
