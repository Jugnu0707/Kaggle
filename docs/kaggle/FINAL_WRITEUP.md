# Oz AI

## Multi-Agent Incident Response for Enterprise Security Operations

**Kaggle AI Agents Intensive Capstone · Agents for Business Track**  
**Repository:** https://github.com/Jugnu0707/Kaggle · **License:** MIT

---

## Problem Statement

Enterprise security operations centers (SOCs) face sustained operational pressure. Endpoint detection, network monitoring, identity systems, and cloud workloads generate thousands of alerts daily. Each signal may require log correlation, indicator enrichment, MITRE ATT&CK mapping, risk assessment, response planning, and executive communication — often during an active incident.

Three structural problems dominate daily work. **Alert fatigue** causes analysts to deprioritize or miss true incidents when reviewing hundreds of low-confidence alerts. **Investigation delays** arise from sequential manual steps: log collection across consoles, indicator-by-indicator threat lookups, framework mapping from memory, and ad hoc playbooks. These compound into extended mean time to respond. **Analyst workload** concentrates on senior staff who become bottlenecks, while junior analysts may skip enrichment steps. Post-incident reporting for compliance and leadership adds demand on the same teams containing active threats.

Existing tooling addresses parts of this lifecycle. SIEM platforms detect anomalies but rarely produce structured investigation artifacts. Threat feeds provide data without investigation context. Ticketing systems track tasks without analyzing evidence. No single tool covers the path from log upload to leadership-ready output. Security teams therefore repeat the same analytical steps for every incident, with quality dependent on individual analyst experience rather than repeatable process.

---

## Why AI Agents?

Incident response decomposes into specialist tasks with distinct schemas, test criteria, and failure modes. A single monolithic model cannot maintain focused outputs and auditable behavior across all stages.

Multi-agent systems assign each stage to a specialist agent with defined inputs and outputs. A coordinator ensures sequencing. A safety layer validates outputs before analysts consume them. Deterministic fallbacks allow offline operation when cloud AI is unavailable. Human analysts remain accountable for consequential decisions; agents accelerate structured analysis and produce consistent artifacts.

Oz AI applies this model to enterprise incident response — a domain where coordinated specialist agents deliver workflow structure without replacing human judgment. Each agent maintains a single responsibility, typed input/output schema, and independent test suite, making the system evaluable stage by stage rather than only end-to-end.

---

## Solution Overview

Oz AI is an open-source incident response platform combining a React dashboard, FastAPI backend, eight Google ADK specialist agents, Guardian safety validation, MCP operational tools, and SQLite persistence. It is a **decision-support system**: it structures investigations, surfaces risk, and drafts response recommendations. It does not execute remediation autonomously.

An analyst creates an incident, uploads log files (`.log`, `.txt`, `.json`, `.csv`; `.evtx` metadata only), and explicitly triggers an investigation via `POST /api/v1/investigations/run` or the Investigation Runner UI. Creating an incident does not start the agent pipeline automatically.

Four AI-first agents — Threat Intelligence, Risk Assessment, Response Planning, and Executive Report — call Google Gemini when `GOOGLE_API_KEY` is configured. When Gemini is unavailable (missing key, quota exceeded, timeout, invalid JSON, or Guardian rejection), each falls back to rule engines, playbooks, or templates. The workflow never blocks on AI failure. Replay steps record `ai_used` and `fallback_used` for transparency.

Deployment requires one command:

```bash
git clone https://github.com/Jugnu0707/Kaggle.git && cd Kaggle
cp .env.example .env && docker compose up --build
python scripts/reset_demo.py   # optional: 10 incidents, 25 logs, offline
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:5173 |
| API / Swagger | http://localhost:8000 / http://localhost:8000/docs |

---

## Architecture

Oz AI uses a layered architecture with clear separation of concerns:

```text
React Frontend (10 pages)
  → FastAPI Backend (35 paths, 39 operations)
  → Coordinator Agent
  → Specialist Agents (Evidence → Threat Intel → MITRE → Risk → Response → Executive Report)
  → Guardian Agent (validates after each specialist stage)
  → Timeline Engine
  → Evaluation Engine
  → SQLite (16 tables) + file storage (uploaded logs)
```

**Backend** (`backend/app/`): API routes, services, repositories, ORM models, and workflow orchestration via `InvestigationWorkflowService`. Agent logic lives in `agents/`; backend services bridge routes to agent services.

**Frontend** (`frontend/src/`): React 19, TypeScript, Tailwind CSS, Vite. Ten pages: Dashboard (incident overview), Incidents (list and creation), Incident Detail (tabbed views for evidence, threat intel, MITRE, risk, response, executive report, Guardian, timeline), Investigation Runner (start and poll run status), Investigation Replay (step navigation with AI/Fallback badges), Log Upload, Reports, Evaluation (agent health scores), and Settings (health, ADK, MCP status). Data fetching uses native `fetch` with polling — no WebSockets in v0.1.0.

**Persistence**: Sixteen SQLAlchemy tables with per-agent output storage. Log binaries stored on disk at `storage/uploads/`. Docker volumes: `oz-ai-data` (database), `oz-ai-uploads` (files).

**Google ADK** initializes at startup (`backend/app/core/adk_runtime.py`), configures eight agents, and registers them in the AI runtime. LLM inference uses `google-genai` via `backend/app/ai/provider.py`.

**MCP** provides an in-process tool registry (`mcp/`) with five operational tools. Agents invoke backend services directly at runtime; MCP supports introspection and future ADK tool wiring.

---

## Investigation Workflow

Pipeline order when `POST /api/v1/investigations/run` is called:

```text
Coordinator → Evidence → Guardian → Threat Intelligence → Guardian → MITRE → Guardian
  → Risk → Guardian → Response → Guardian → Executive Report → Guardian
  → Timeline Engine → Evaluation Engine
```

| Agent | Engine | Persists to |
|-------|--------|-------------|
| Coordinator | Rule-based | `agent_executions` |
| Evidence | Rule-based log parsing | `evidence` |
| Threat Intelligence | Gemini → offline reputation | `threat_intelligence_findings` |
| MITRE Mapping | Local ATT&CK rules | `mitre_findings` |
| Risk Assessment | Gemini → rule scoring | `risk_assessments` |
| Response Planning | Gemini → playbooks | `response_plans` |
| Executive Report | Gemini → templates | `executive_reports` |
| Guardian | Rule-based validation | `guardian_audits` |

Each specialist agent also exposes an isolated API endpoint under `/api/v1/agents/`. Investigation runs are tracked in `investigation_runs`; step records in `investigation_replays` support replay, explain, and sanitized export APIs.

The Coordinator validates that incident and log references exist before the pipeline proceeds. The Evidence Agent parses uploaded content without performing threat analysis — keeping collection separate from enrichment. MITRE mapping uses local rules in `agents/mitre/mappings.py` (e.g., PowerShell → T1059.001, ransomware → T1486) with no external MITRE API dependency. The Timeline Engine reconstructs chronological events from persisted agent outputs as a post-pipeline stage, distinct from the ADK agent layer.

---

## Technical Implementation

**Stack:** Python 3.12, FastAPI 0.138, SQLAlchemy 2.0, Pydantic v2, React 19, TypeScript, Tailwind CSS, Vite 6, Docker Compose.

**Backend structure:** Ten API route modules covering health, incidents, logs, investigations, agents, evaluation, AI connectivity, system introspection, and dashboard metrics. Guardian integration via `orchestration_guardian.run_stage_with_guardian` validates each stage before advancing.

**Database tables (16):** `incidents`, `log_files`, `investigations`, `investigation_runs`, `investigation_replays`, `evidence`, `mitre_findings`, `threat_intelligence_findings`, `risk_assessments`, `response_plans`, `executive_reports`, `guardian_audits`, `timeline_events`, `agent_executions`, `audit_logs`, `evaluation_metrics`.

**Docker:** Two services — `oz-ai-backend` on port 8000, `oz-ai-frontend` on port 5173. Backend image includes `agents/`, `mcp/`, and `evaluation/` packages.

**Testing:** 176 automated tests across `tests/`, `evaluation/tests/`, and `agents/*/tests/`. Categories include API endpoints, Guardian validation (prompt injection, PII, schema), investigation workflow and replay, MCP registry lifecycle, AI connectivity (`test_ai_test.py`), reliability scenarios (quota errors, missing key), and per-agent service tests. An API inventory test validates all 35 paths and 39 operations. End-to-end integration tests cover the full analyst workflow through replay export. Run: `cd backend && uv run pytest`.

---

## Security & Guardian

The Guardian Agent (`agents/guardian/validator.py`) is rule-based — no LLM. It runs automatically after every specialist stage and via `POST /api/v1/agents/guardian/validate`.

Validation pipeline: empty response check, prompt injection scan (`prompt_injection.py`), PII detection and masking (`pii_detector.py`, `MASK_PII=true`), secret detection and masking (`secret_detector.py`, `MASK_SECRETS=true`), JSON schema validation per agent type, mandatory field checks, and confidence threshold enforcement (`MIN_AI_CONFIDENCE=70`).

Statuses: `approved` (continue), `warning` (continue with logged issues), `rejected` (retry without Gemini or accept agent fallback). Every validation persists to `guardian_audits`. Replay export sanitizes sensitive values via `backend/app/utils/sanitize.py`.

Response plans are recommendations only. Oz AI does not isolate hosts, block IPs, or execute playbooks. API authentication and human approval workflows are not implemented in v0.1.0.

---

## Google ADK Integration

At application startup, FastAPI lifespan initializes ADK (`initialize_adk_runtime`), verifies `google.adk` imports, loads the Coordinator Agent, initializes specialist agent runtimes, starts MCP, and builds the AI runtime registry with eight agents.

Configuration: `GOOGLE_API_KEY` (optional), `GOOGLE_MODEL` (default `gemini-2.5-pro`), `ADK_APP_NAME`, `ADK_ENABLE_TRACING`.

`GeminiProvider` centralizes the Gemini client. AI-first agents request JSON-mode responses. `GET /api/v1/ai/test` sends a minimal probe to verify connectivity without running the full pipeline.

ADK session tracking exists in-memory (`backend/app/ai/session.py`) but ADK native session checkpointing is not implemented. Workflow state persists in SQLite via services.

---

## MCP Integration

Oz AI registers five operational MCP tools through an in-process registry (`mcp/registry.py`):

| Tool | Purpose |
|------|---------|
| `health` | Application health status |
| `list_incidents` | Paginated incident list |
| `incident_details` | Single incident by ID |
| `list_logs` | Uploaded log metadata |
| `system_info` | Version, database, ADK, MCP status |

Tools use Pydantic input/output schemas and delegate to existing service layers. Discovery occurs at AI runtime initialization. Introspection: `GET /api/v1/system/mcp`. Invocation: `AIRuntime.invoke_tool()`.

Domain tools (e.g., `evidence_collector`, `threat_intel_lookup`) are planned but not implemented. Agents call backend services directly rather than MCP tools at runtime.

---

## Evaluation & Results

**Repository statistics** (verified via `python scripts/generate_repo_stats.py`):

| Metric | Count |
|--------|-------|
| API paths / operations | 35 / 39 |
| AI agents | 8 |
| MCP tools | 5 |
| Database tables | 16 |
| Frontend pages | 10 |
| Automated tests | 176 |
| Lines of code (approx.) | 29,679 |

**Evaluation Engine** (`evaluation/engine.py`) runs at the end of each investigation. **Health scores** (`evaluation/scorer.py`) combine availability (30%), reliability (30%), performance (20%), and accuracy (20%) into a 0–100 composite per agent.

**Replay** persists step number, agent name, duration, `ai_used`, `fallback_used`, and sanitized summaries to `investigation_replays`. APIs: `/investigations/{run_id}/replay`, `/explain`, `/replay/export`.

**Performance benchmarks** from `scripts/sprint3_performance_benchmark.py` (in-process TestClient, offline fallbacks; source: `docs/SPRINT3_PERFORMANCE_REPORT.md`):

| Operation | Mean (ms) |
|-----------|-----------|
| Full investigation | 36.57 |
| Dashboard load | 3.51 |
| Evaluation dashboard load | 2.08 |

These exclude network latency and Gemini API calls. Production Gemini enrichment adds seconds per AI-first agent depending on model and quota. Offline demo (`scripts/reset_demo.py`) seeds ten incidents with twenty-five logs covering scenarios including PowerShell execution, brute force, ransomware, credential dumping, and lateral movement — all agent output tabs populate via fallbacks when no API key is configured.

**AI fallback verification** is tested across missing API key, quota exceeded (429), timeout, invalid key, and Guardian rejection scenarios. Each replay step exposes whether Gemini or a rule engine produced the output, supporting judge verification without requiring live API access.

Prior sprint hardening reported ~93% line coverage across `app`, `agents`, `mcp`, and `evaluation` packages. Regenerate with `pytest --cov` before citing in submission materials.

---

## Known Limitations

Oz AI is an MVP for demonstration and capstone evaluation. Current constraints:

- **SQLite** — single-file database; suitable for demos, not concurrent production workloads.
- **No API authentication or RBAC** — all endpoints are open.
- **Offline threat intelligence** — local reputation rules only; no VirusTotal or commercial feeds.
- **No SIEM integration** — manual log upload; no Splunk, Sentinel, or webhook ingestion.
- **No automated remediation** — response plans are recommendations only.
- **Operational MCP only** — five tools; agents do not call MCP at runtime.
- **Demo deployment** — Docker runs Vite dev server, not a production Nginx build.
- **Human approval** — architecturally documented but not enforced in API or UI.
- **Submission artifacts** — Kaggle notebook and demo video not yet produced.

Screenshots in `docs/screenshots/` are programmatic renders, not live browser captures.

---

## Future Work

Planned extensions include PostgreSQL migration, bearer-token authentication and RBAC, SIEM connectors (Splunk, Microsoft Sentinel, Elastic), live threat feeds (VirusTotal, AbuseIPDB), human approval workflow for response plans, multi-tenant isolation, domain MCP tools with ADK-native invocation, ADK session checkpointing, a 30-scenario labeled evaluation library, and production Docker images with Nginx static frontend.

See `ROADMAP.md` for sprint-level tracking.

---

## Conclusion

Oz AI demonstrates a deployable multi-agent incident response workflow for the Kaggle AI Agents Intensive Capstone. Eight Google ADK specialist agents coordinate through an explicit investigation pipeline with Guardian validation at every stage. Deterministic fallbacks enable fully offline demos. MCP tools provide operational introspection. One hundred seventy-six tests, investigation replay with AI/fallback transparency, and an evaluation dashboard provide evidence of system quality.

The platform structures analyst work from log upload to executive report without claiming autonomous remediation or production enterprise readiness. Human analysts remain responsible for approving and executing response actions — a boundary Oz AI respects by design.

For competition evaluators, the repository maps to core capstone criteria: multi-agent coordination (eight specialists), Google ADK (runtime and agent registry), MCP (five registered tools), security (Guardian between stages), deployability (`docker compose up --build`), and evaluation (176 tests plus health-score dashboard). Detailed requirement mapping is in `docs/kaggle/11_competition_mapping.md`.

**Quick start for judges:**

```bash
git clone https://github.com/Jugnu0707/Kaggle.git && cd Kaggle
cp .env.example .env && docker compose up --build
python scripts/reset_demo.py && open http://localhost:5173
```

---

## Validation Checklist

| Check | Status |
|-------|--------|
| Word count within 2,500 maximum | Yes — 2,276 words (full document) |
| Target range 2,200–2,400 words | Yes |
| All 15 required sections present | Yes |
| No duplicate sections | Yes |
| No contradictory statements (MCP vs direct service calls, approval workflow, remediation) | Yes — limitations stated explicitly |
| Statistics match `generate_repo_stats.py` | Yes — 35/39/8/5/16/10/176/29679 |
| Benchmark numbers sourced from SPRINT3 report only | Yes — 36.57 ms full investigation |
| No placeholder text | Yes |
| No unimplemented features claimed as complete | Yes — auth, approval, SIEM, domain MCP marked as gaps |
| No Mermaid diagrams (Kaggle compatibility) | Yes — text architecture only |
| Human-in-the-loop paired with not-implemented disclosure | Yes |

---

*Generated for RC2 Task 4. Do not submit directly — adapt for Kaggle notebook format.*
