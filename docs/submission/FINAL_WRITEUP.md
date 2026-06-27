# Oz AI — Final Competition Writeup

**Competition:** Kaggle AI Agents: Intensive Vibe Coding Capstone  
**Track:** Agents for Business  
**Repository:** https://github.com/Jugnu0707/Kaggle  
**Version:** 0.1.0 · Submission Ready

---

## 1. Problem

Enterprise security operations centers (SOCs) process thousands of alerts daily from endpoint detection, identity systems, network monitoring, and cloud workloads. Each potential incident demands triage, log correlation, threat framework mapping, risk narrative, response planning, and executive communication—often while an active breach unfolds.

Manual incident response introduces delays at every stage. Analysts navigate multiple consoles for log collection. Threat intelligence lookups happen indicator by indicator. MITRE ATT&CK mapping depends on individual experience. Risk assessments and executive summaries are written from scratch. These sequential manual steps compound into hours of mean time to respond (MTTR), during which adversaries may deploy ransomware, exfiltrate credentials, or establish persistence.

Alert fatigue amplifies the crisis. When analysts face hundreds of low-confidence alerts per shift, true incidents are missed or deprioritized. Investigation quality varies by analyst skill and shift. Institutional knowledge is not captured in repeatable workflows. Security teams spend disproportionate effort on documentation rather than decisive containment.

The business impact is direct: breach costs scale with response delay, audit readiness suffers from inconsistent analysis, and leadership lacks timely plain-language briefings. Oz AI addresses this domain—enterprise incident response—where multi-agent AI can accelerate structured analysis without replacing human judgment on consequential decisions.

---

## 2. Solution

Oz AI is an open-source **enterprise incident response platform** built for the Kaggle capstone. It combines a React 19 operations dashboard, FastAPI backend, eight Google ADK specialist agents, a Guardian safety layer, MCP operational tools, Timeline and Evaluation engines, and SQLite persistence in a single deployable system.

The platform is a **decision-support system**. Investigations are triggered explicitly via `POST /api/v1/investigations/run`. Creating an incident does not automatically start the agent pipeline. Response plans contain containment, eradication, and recovery **recommendations only**—Oz AI never isolates hosts, blocks IPs, or executes remediation autonomously.

A showcase investigation on **Suspicious PowerShell Execution** demonstrates the full pipeline: WINWORD.EXE spawns PowerShell with an encoded command on a finance workstation. Three log files feed the Evidence Agent. Threat Intelligence extracts IOCs including external IP `185.234.72.19`. MITRE maps T1059.001 PowerShell. Risk and Response agents produce scored assessments and playbooks. Executive Report generates leadership-ready JSON and Markdown without raw logs. Guardian validates every stage. Timeline reconstructs the attack sequence. Evaluation records agent health metrics.

**One-command demo:** `python scripts/reset_demo.py` seeds ten incidents with twenty-five logs across attack types (PowerShell, brute force, ransomware, credential dumping, lateral movement, exfiltration) and runs investigations on showcase cases. **Docker:** `docker compose up --build` starts backend (port 8000) and frontend (port 5173). The platform operates fully offline without `GOOGLE_API_KEY`; Gemini enriches AI-first agents when configured.

---

## 3. Architecture

Oz AI follows a layered architecture documented in `docs/02_ARCHITECTURE.md` and `docs/diagrams/`.

```text
Presentation:  React Dashboard (10 pages)
       ↓
API Layer:     FastAPI — 35 paths, 39 HTTP operations
       ↓
Application:   Services, Repositories, Investigation Workflow
       ↓
Intelligence:  Coordinator + 7 Specialist Agents + Guardian
       ↓
Engines:       Timeline Engine, Evaluation Engine
       ↓
Tools:         Google ADK Runtime, MCP Registry (5 tools), Gemini API
       ↓
Persistence:   SQLite — 16 ORM tables, append-only audits
```

**Frontend routes:** Dashboard, Incidents, Incident Detail (tabbed agent outputs), Investigation Runner, Investigation Replay, Logs, Reports, Evaluation, Settings.

**Backend structure:** `backend/app/api/v1/` (REST), `backend/app/services/` (workflow orchestration), `backend/app/repositories/` (data access), `agents/` (specialist logic), `mcp/` (tool registry), `evaluation/` (benchmarks).

**Design principles:** explicit orchestration, Guardian between stages, AI-first with deterministic fallbacks, append-only audit trails, sanitized replay export.

High-resolution diagram: `docs/architecture/architecture.png`. Mermaid diagrams render on GitHub in `docs/diagrams/`.

---

## 4. AI Workflow

The **Coordinator Agent** validates incident and log context, builds an orchestration plan, and persists execution metadata. It uses rule-based logic without LLM invocation.

The **Investigation Workflow Service** executes agents in order with Guardian validation between each stage:

```text
Coordinator → Evidence → Guardian → Threat Intelligence → Guardian
→ MITRE → Guardian → Risk → Guardian → Response → Guardian
→ Executive Report → Guardian → Timeline → Evaluation
```

| Agent | Responsibility | AI | Fallback |
|-------|----------------|-----|----------|
| Evidence | Log normalization | Rules | Empty package |
| Threat Intelligence | IOC extraction + enrichment | Gemini | Offline reputation engine |
| MITRE | ATT&CK mapping | Local rules | Empty techniques |
| Risk | Enterprise risk scoring | Gemini | Severity/technique rules |
| Response | Containment/recovery plan | Gemini | Scenario playbooks |
| Executive Report | Leadership summary | Gemini | Template engine |
| Guardian | Safety validation | Rules | Bypass if disabled |

**Explainability:** `investigation_replays` stores per-step metadata. APIs: `GET /investigations/{run_id}/replay`, `/explain`, `/replay/export` (JSON/Markdown). Each step records `ai_used`, `fallback_used`, and `duration_ms`.

**Connectivity test:** `GET /api/v1/ai/test` sends one minimal Gemini prompt expecting `READY`—verifies API key without running the full pipeline.

---

## 5. Google ADK

Google Agent Development Kit integration is foundational to Oz AI:

- ADK import verified at application startup (`adk_runtime.py`)
- Eight agents define ADK configuration: name, description, prompt, schemas (`agents/*/agent.py`)
- Central agent registry with version metadata (`backend/app/ai/registry.py`)
- Environment: `ADK_APP_NAME`, `ADK_ENABLE_TRACING`
- Settings page displays ADK loaded status for judges

LLM inference uses `google.genai.Client` through `backend/app/ai/provider.py`. ADK configures agent identity; services orchestrate execution. Planned post-capstone: ADK session checkpointing and `adk eval` integration.

---

## 6. MCP (Model Context Protocol)

Oz AI implements an in-process MCP tool registry with typed Pydantic input/output schemas (`mcp/registry.py`). Five tools register at startup:

| Tool | Description |
|------|-------------|
| `health` | Application health status |
| `list_incidents` | Paginated incident list |
| `incident_details` | Single incident by ID |
| `list_logs` | Uploaded log metadata |
| `system_info` | Version, database, ADK, MCP status |

The MCP server lifecycle is managed in `mcp/server.py`. Runtime integration: `backend/app/core/mcp_runtime.py`. Judges verify via `GET /api/v1/system/mcp` and the Settings page.

Domain agents currently invoke backend services directly for lower MVP latency. MCP provides operational introspection and a foundation for ADK-native tool calls. Domain tools (`evidence_collector`, `threat_intel_lookup`) are documented for future sprints.

---

## 7. Security

Security is enforced by architecture, not prompt instructions alone.

The **Guardian Agent** runs between every workflow stage, detecting prompt injection, scanning for PII and secrets, validating JSON schemas, and checking confidence thresholds (`MIN_AI_CONFIDENCE`, default 70). Outcomes: `approved`, `warning`, or `rejected`—all persisted to append-only `guardian_audits`.

Additional controls: secrets in environment variables only (`.env` gitignored); `sanitize.py` on replay export; no raw logs in executive reports; audit logs never modified after creation. Response actions require human approval in the architecture; API/UI enforcement is planned.

Oz AI **never performs automatic remediation**. The Response Planning Agent drafts recommendations; execution remains a human responsibility.

Configuration: `GUARDIAN_ENABLED`, `MASK_SECRETS`, `MASK_PII`.

---

## 8. Evaluation

Oz AI demonstrates quality through automated testing, benchmarks, and a live evaluation dashboard.

| Metric | Value |
|--------|-------|
| Automated tests | 176 collected |
| API inventory test | 35 paths verified |
| E2E integration test | Full analyst workflow through replay |
| Reliability tests | Quota errors, missing API key, AI unavailable |
| Offline investigation benchmark | ~37 ms mean (in-process) |
| Documentation files | 47 |

**Evaluation framework:** `evaluation/engine.py`, `evaluation/benchmark.py`, persisted `evaluation_metrics` table, `/evaluation` UI with per-agent health scores.

**AI fallback verification:** Without `GOOGLE_API_KEY`, `reset_demo.py` completes investigations with rule-engine outputs on all tabs. Replay flags show `fallback_used: true` on AI-first stages.

Judges can run: `cd backend && uv run pytest`

---

## 9. Limitations

Honest scope boundaries:

- **SQLite** for single-file demo deployment; production needs PostgreSQL
- **No API authentication** or RBAC in v0.1.0
- **No SIEM connectors** — logs uploaded manually or via REST
- **Operational MCP only** — five tools, not full domain tool layer
- **No automatic remediation** or approval workflow UI
- **Offline threat intel** — local reputation rules, not live VirusTotal/AbuseIPDB
- **In-process agent execution** — worker isolation planned for production
- **Docker frontend** uses Vite dev server; production Nginx profile planned
- **Submission notebook and demo video** — packaging step remaining

These reflect MVP scope for capstone demonstration, not missing vision.

---

## 10. Future Work

Post-capstone roadmap (`ROADMAP.md`):

- **Integrations:** VirusTotal, AbuseIPDB, Splunk, Sentinel, Elastic, CrowdStrike
- **Security:** API bearer tokens, RBAC, response approval workflow
- **MCP:** Domain tools, ADK-native agent tool calls
- **Infrastructure:** PostgreSQL, production Docker, worker queues, rate limiting
- **Evaluation:** 30-scenario labeled library, CI regression gates
- **UX:** WebSocket live updates, `/about` page, PDF export

---

## Repository Statistics

| Metric | Count |
|--------|-------|
| API paths | 35 |
| API operations | 39 |
| AI agents | 8 |
| MCP tools | 5 |
| Database tables | 16 |
| Frontend pages | 10 |
| Tests | 176 |
| Documentation files | 47 |
| Lines of code (approx.) | 29,333 |

---

## Judge Quickstart

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle && cp .env.example .env
docker compose up --build
python scripts/reset_demo.py
```

Open http://localhost:5173 → Incidents → **Suspicious PowerShell Execution** → review all tabs → Evaluation → Settings (ADK + MCP).

**License:** MIT · **Docs:** `docs/kaggle/`, `docs/submission/`, `docs/demo/`

---

*Consolidated writeup for Kaggle submission. Detailed sections: `docs/kaggle/*.md`. Estimated word count: ~1,450 core narrative; paste with `docs/kaggle/` sections for full ~2,400 words.*
