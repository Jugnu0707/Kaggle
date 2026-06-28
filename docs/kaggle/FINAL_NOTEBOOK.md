# Oz AI — Multi-Agent Incident Response for Enterprise Security Operations

**Kaggle AI Agents Intensive Capstone · Agents for Business Track**  
**Repository:** https://github.com/Jugnu0707/Kaggle · **License:** MIT

---

## 1. Problem Statement

Enterprise security operations centers process thousands of alerts daily. Each incident may require log correlation, indicator enrichment, MITRE ATT&CK mapping, risk scoring, response planning, and executive reporting — often under time pressure.

Three recurring problems drive this project:

1. **Alert fatigue** — low-confidence signals hide true incidents.
2. **Investigation delays** — analysts repeat manual steps across consoles.
3. **Inconsistent output** — quality depends on individual experience rather than repeatable process.

Existing tools address parts of the lifecycle (SIEM detection, threat feeds, ticketing) but rarely produce a single structured investigation artifact from log upload to leadership-ready output.

---

## 2. Business Motivation

Mean time to respond (MTTR) and analyst burnout directly affect breach containment cost. Oz AI targets the **analysis and communication gap** between raw logs and actionable decisions — not autonomous remediation.

The platform is a **decision-support system**: it accelerates structured investigation and produces auditable artifacts. Human analysts remain accountable for containment and remediation actions.

---

## 3. Solution Overview

Oz AI coordinates eight Google ADK specialist agents through one investigation pipeline. Analysts upload logs, create incidents, and explicitly trigger investigations via the UI or `POST /api/v1/investigations/run`.

Each specialist output passes through the **Guardian Agent** before the pipeline continues. A **Timeline Engine** reconstructs events; an **Evaluation Engine** scores agent health after runs.

Four agents call Google Gemini when `GOOGLE_API_KEY` is set (Threat Intelligence, Risk, Response, Executive Report). When Gemini is unavailable, deterministic fallbacks ensure the workflow completes offline.

**Quick start:**

```bash
git clone https://github.com/Jugnu0707/Kaggle.git && cd Kaggle
cp .env.example .env
docker compose up --build
backend/.venv/bin/python scripts/reset_demo.py
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:5173 |
| API / Swagger | http://localhost:8000/docs |

---

## 4. Architecture

```text
React Frontend (10 pages)
  → FastAPI Backend (35 paths, 39 operations)
  → Coordinator → Evidence → Threat Intel → MITRE → Risk → Response → Executive Report
  → Guardian (validates after each specialist stage)
  → Timeline Engine → Evaluation Engine
  → SQLite (16 tables) + file storage
```

**Backend** (`backend/app/`): routes, services, repositories, workflow orchestration.  
**Agents** (`agents/`): eight ADK-configured specialists plus Guardian.  
**Frontend** (`frontend/src/`): React 19, TypeScript, Tailwind, Vite.  
**MCP** (`mcp/`): five operational tools exposed via `GET /api/v1/system/mcp`.

---

## 5. Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+, TypeScript |
| Backend | FastAPI 0.138, SQLAlchemy, Uvicorn |
| Frontend | React 19, Vite 6, Tailwind CSS |
| AI | Google ADK 2.3, google-genai (Gemini) |
| Persistence | SQLite, on-disk log uploads |
| Deployment | Docker Compose (backend + frontend) |
| Tests | pytest — **176 collected** |

Dependencies are managed in `backend/pyproject.toml` (no root `requirements.txt`).

---

## 6. AI Agent Architecture

| Agent | Role | AI / Rules |
|-------|------|------------|
| Coordinator | Sequences pipeline | Rule-based |
| Evidence | Parses uploaded logs | Rule-based |
| Threat Intelligence | IOC enrichment | Gemini → offline reputation |
| MITRE Mapping | ATT&CK techniques | Local rules |
| Risk Assessment | Severity scoring | Gemini → rule scoring |
| Response Planning | Playbooks | Gemini → templates |
| Executive Report | Leadership summary | Gemini → templates |
| Guardian | Validates every stage | Rule-based (injection, PII, secrets) |

ADK initializes at startup (`backend/app/core/adk_runtime.py`). All eight agents import `google.adk.agents.Agent`.

---

## 7. Workflow

1. Analyst creates incident and uploads logs (`.log`, `.txt`, `.json`, `.csv`; `.evtx` metadata).
2. Analyst triggers investigation explicitly — creation alone does not run agents.
3. Coordinator executes specialists in order; Guardian gates each stage.
4. Timeline and evaluation engines run after the agent chain.
5. Results appear in incident detail tabs, replay view, and evaluation dashboard.

Investigations are **not** auto-triggered on incident creation.

---

## 8. Investigation Pipeline

```text
Coordinator → Evidence → Guardian → Threat Intelligence → Guardian → MITRE → Guardian
  → Risk → Guardian → Response → Guardian → Executive Report → Guardian
  → Timeline → Evaluation
```

Showcase demo incident: **Suspicious PowerShell Execution** (seeded by `scripts/reset_demo.py`).

Replay exposes per-step `ai_used` and `fallback_used` flags at `/investigations/{runId}/replay`.

---

## 9. Screenshots

![Dashboard](images/dashboard.png)

![Incident List](images/incidents.png)

![Incident Detail](images/incident-detail.png)

![Threat Intelligence](images/threat-intelligence.png)

![MITRE ATT&CK](images/mitre.png)

![Risk Assessment](images/risk-assessment.png)

![Response Plan](images/response-plan.png)

![Executive Report](images/executive-report.png)

![Guardian Audit](images/guardian.png)

![Timeline](images/timeline.png)

![Investigation Replay](images/replay.png)

![Evaluation Dashboard](images/evaluation.png)

![Reports](images/reports.png)

![Settings](images/settings.png)

![Log Upload](images/log-upload.png)

*Image file mapping: see `NOTEBOOK_IMAGES.md` in the repository.*

---

## 10. Results

After a completed investigation on the showcase incident, the platform produces:

- Structured evidence records from uploaded logs
- Threat intelligence findings with IOC reputation data
- MITRE technique mappings (e.g. T1059.001 PowerShell)
- Risk assessment with confidence scoring
- Response plan (containment, eradication, recovery)
- Executive report in JSON and Markdown
- Guardian audit trail per agent stage
- Chronological timeline events
- Evaluation metrics persisted to `evaluation_metrics`

All outputs are stored in SQLite and visible in the React dashboard without external SIEM integration.

---

## 11. Evaluation

The `evaluation/` module scores agent health using weighted metrics: availability (30%), reliability (30%), performance (20%), accuracy (20%).

- Offline benchmarks in `evaluation/benchmark.py`
- API: `GET /api/v1/evaluation`, `GET /api/v1/evaluation/{agent_name}`
- UI: `/evaluation` page with per-agent charts

Evaluation runs after investigations complete; results feed the Evaluation Dashboard screenshot above.

---

## 12. Testing

**176 automated tests** collected via pytest (`backend/.venv/bin/pytest --collect-only -q`).

Coverage includes:

- API endpoints (`tests/test_incidents.py`, `test_investigation_workflow.py`, etc.)
- Individual agents (`tests/test_threat_intelligence_agent.py`, `test_guardian_agent.py`, etc.)
- Investigation replay and evaluation
- MCP registry and health checks

**Note:** No GitHub Actions workflow is configured; tests run locally or in CI you configure externally.

---

## 13. Limitations

Documented honestly in `docs/kaggle/limitations.md`:

- No API authentication or RBAC (all endpoints open on the network)
- SQLite single-file database (demo-scale, not production HA)
- MCP provides five operational tools; agents call services directly
- No live SIEM connectors or automatic remediation
- Vite dev server in Docker (not production Nginx build)
- `docs/screenshots/` assets are PIL-generated renders; live captures are in `demo/output/screenshots/`

---

## 14. Future Work

- Bearer-token authentication and RBAC
- PostgreSQL and horizontal scaling
- Domain MCP tools wired into ADK runtime
- SIEM/webhook ingestion
- GitHub Actions CI pipeline
- PDF export for executive reports
- ADK session checkpointing and `adk eval` integration

---

## 15. Repository

| Item | Location |
|------|----------|
| Source | https://github.com/Jugnu0707/Kaggle |
| Backend | `backend/app/` |
| Agents | `agents/` |
| Frontend | `frontend/src/` |
| Tests | `tests/` |
| Demo reset | `scripts/reset_demo.py` |
| Demo recording | `scripts/record_demo.py` → `demo/output/demo.mp4` |
| Documentation | `docs/`, `docs/kaggle/` |

**Verified counts:** 259 Python files · 42 frontend TS/TSX files · 8 agents · 35 API paths · 39 operations · 16 database tables · 10 pages · 5 MCP tools · 176 tests.

---

## 16. Demo Video

Automated demo recording:

```bash
./scripts/dev.sh
backend/.venv/bin/python scripts/record_demo.py
```

**Output:** `demo/output/demo.mp4` (1920×1080 H.264, ~167 seconds, verified locally)

**Kaggle upload placeholder:** `[Upload demo/output/demo.mp4 to Kaggle Datasets or Media and link here]`

Video URL for judges: _add after upload_

---

## 17. Conclusion

Oz AI demonstrates a production-shaped multi-agent incident response workflow using Google ADK, Guardian safety gates, MCP operational tooling, and a full React analyst dashboard. The implementation is verifiable: 176 tests, 35 API paths, eight specialist agents, and an offline-capable demo path.

The system accelerates investigation structure and executive communication without replacing human judgment — aligned with enterprise security operations requirements for the Agents for Business track.

---

*Submission artifacts: `REPOSITORY_AUDIT.md`, `SECURITY_AUDIT.md`, `SCREENSHOT_CHECKLIST.md`, `SUBMISSION_CHECKLIST.md`, `NOTEBOOK_IMAGES.md`*
