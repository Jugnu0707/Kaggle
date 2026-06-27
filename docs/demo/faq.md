# Oz AI Demo Video — Judge FAQ

Prepared answers for Kaggle judges and Google engineers. Responses reflect the **actual implementation** as of Sprint 4 Task 3.

---

## Competition & project scope

### Why did you choose enterprise incident response?

Enterprise SOC teams face documented MTTR challenges and alert fatigue. Incident response is a high-value **Agents for Business** use case: multi-step workflows, structured outputs, executive stakeholders, and measurable business impact. Oz AI demonstrates agents coordinating on a real operational problem—not a toy chatbot.

### How does Oz AI align with the Agents for Business track?

Oz AI targets measurable business outcomes (faster structured investigations, executive-ready reporting), deploys eight coordinated business-logic agents, and includes evaluation metrics tied to agent quality. See `docs/COMPETITION_ALIGNMENT.md` and `docs/kaggle/submission_notes.md`.

### What is intentionally out of scope?

Automatic remediation, SIEM connectors, API authentication (Sprint 4 in progress), and human approval enforcement in the UI. Oz AI is decision-support, not autonomous response execution.

---

## Google ADK

### Why Google ADK?

ADK provides a standardized agent configuration model—name, description, prompts, schemas—that maps cleanly to production agent fleets. Oz AI uses ADK for all eight agents (`agents/*/agent.py`) with runtime initialization at startup (`backend/app/core/adk_runtime.py`). This demonstrates native ADK integration rather than wrapping a generic LLM script.

### How deeply is ADK integrated?

- ADK import verified at application startup
- Eight agents registered in `backend/app/ai/registry.py`
- Configurable `ADK_APP_NAME` and `ADK_ENABLE_TRACING`
- LLM calls via `google.genai.Client` aligned with ADK stack

**Gap:** ADK session checkpointing and `adk eval` are planned—not yet implemented.

### Do agents use ADK to call tools at runtime?

Agents currently invoke backend **services** directly. ADK configures identity and schemas; MCP tools are registered separately. Domain MCP tool wiring is on the roadmap.

---

## MCP (Model Context Protocol)

### Why MCP?

MCP provides a discoverable, typed tool layer that agents and external systems can invoke consistently. Oz AI implements a custom registry (`mcp/registry.py`) with input/output Pydantic schemas—matching MCP's contract philosophy.

### What MCP tools are implemented?

Five operational tools:

| Tool | Purpose |
|------|---------|
| `health` | Application health |
| `list_incidents` | Paginated incident list |
| `incident_details` | Single incident by ID |
| `list_logs` | Log file metadata |
| `system_info` | Version, database, ADK, MCP status |

Exposed via `GET /api/v1/system/mcp` and visible on the Settings page.

### Why aren't agents calling MCP tools during investigations?

Operational MCP tools support introspection and future ADK tool binding. Domain agents use service layers for lower latency and simpler MVP scope. Domain tools (`evidence_collector`, `threat_intel_lookup`) are documented in `docs/03_TASKS.md` for Sprint 4+.

---

## AI & fallback

### Why Gemini?

Gemini integrates with Google ADK and the competition stack. Four agents use Gemini JSON generation: Threat Intelligence, Risk, Response, and Executive Report.

### Why fallback engines?

Enterprise platforms cannot depend solely on cloud AI availability. Quota limits, network failures, and air-gapped environments are normal. Oz AI's AI-first agents catch errors and invoke rule engines (`fallback.py` in each package) so investigations **always complete** with structured output.

### How do you prove fallback works?

1. Run `python scripts/reset_demo.py` without `GOOGLE_API_KEY`
2. All incident tabs populate with rule-engine data
3. Investigation Replay shows `fallback_used: true` on AI-first steps
4. Tests: `tests/test_reliability.py`, per-agent quota tests

### What does `GET /api/v1/ai/test` do?

A minimal connectivity probe—one Gemini call, one-word `READY` response—to verify API key and model without running the full agent pipeline.

---

## Guardian & security

### Why Guardian?

A single LLM cannot be the only safety layer in a security product. Guardian is a **dedicated rule-based validator** between every workflow stage: prompt injection patterns, PII detection, secret masking, JSON schema compliance, and confidence thresholds.

### Does Guardian block the workflow?

Guardian records `approved`, `warning`, or `rejected` in `guardian_audits`. Rejected outputs can trigger fallback paths; the workflow is designed to continue with safe structured data rather than crash or expose unsafe content.

### Why isn't human approval implemented yet?

The architecture documents human-in-the-loop for response actions. API and UI enforcement is Sprint 4 scope (`docs/03_TASKS.md` M6). Oz AI never executes remediation automatically today—plans are recommendations only.

### How are secrets handled?

API keys live in `.env` only. `.env` is gitignored. Replay export uses `sanitize.py`. Guardian masks detected secrets in outputs when `MASK_SECRETS=true`.

---

## Architecture & data

### Why SQLite?

SQLite enables single-command demo deployment—one file, no external database server. Ideal for Kaggle judging, local demos, and `docker compose up`. The architecture document (`docs/02_ARCHITECTURE.md`) identifies PostgreSQL as the production migration path.

### How would this scale?

| Layer | Scale path |
|-------|------------|
| Database | PostgreSQL with connection pooling |
| Agents | Worker processes or queue (Celery/Redis) instead of in-process execution |
| API | Horizontal scaling behind load balancer |
| Frontend | Static Nginx build, CDN |
| AI | Per-agent model routing, caching, batch enrichment |

### Why sixteen database tables?

Per-agent persistence enables independent API reads, timeline reconstruction, and audit trails. Tables map 1:1 to agent outputs plus workflow metadata (`investigation_runs`, `investigation_replays`).

### Why explicit `POST /investigations/run`?

Incidents are records; investigations are deliberate analyst actions. Auto-running agents on incident creation would misrepresent SOC workflows and consume resources on false positives.

---

## SIEM & integrations

### How would Oz AI integrate with Splunk / Sentinel / Elastic?

Planned ingestion layer:

1. **Webhook receiver** — normalize alerts to Oz AI incident schema
2. **Log pull connector** — scheduled queries export logs to `POST /api/v1/logs/upload`
3. **Bidirectional sync** — push investigation status back to SIEM case management

MITRE and IOC fields already align with common SIEM export formats. See `docs/kaggle/future_work.md`.

### Why no VirusTotal / AbuseIPDB today?

Threat Intelligence uses a local reputation engine for offline demos. External API adapters are planned behind `reputation_engine.py` without changing the agent API surface.

### Would Oz AI replace a SIEM?

No. Oz AI structures investigation **after** detection. It complements SIEM, EDR, and ticketing—not replaces them.

---

## Evaluation & testing

### How is agent quality measured?

- **176 automated tests** across API, agents, workflow, reliability
- **Evaluation Engine** — offline benchmarks, persisted `evaluation_metrics`
- **Evaluation Dashboard** — `/evaluation` UI
- **Investigation Replay** — per-step AI/fallback and latency metadata

Performance benchmark (in-process, offline): full investigation ~37 ms mean (`docs/SPRINT3_PERFORMANCE_REPORT.md`).

### What is the 30-scenario library gap?

The evaluation framework exists; a comprehensive labeled scenario library for regression gates is Sprint 4 work (`docs/03_TASKS.md` M8).

---

## Deployment & demo

### How does a judge run Oz AI?

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
cp .env.example .env
docker compose up --build
python scripts/reset_demo.py
open http://localhost:5173
```

Works fully offline without `GOOGLE_API_KEY`.

### Is the demo data realistic?

Ten incidents with twenty-five logs cover PowerShell, brute force, ransomware, credential dumping, lateral movement, and exfiltration. Logs are synthetic but structurally representative of EDR, auth, and firewall formats.

---

## User experience

### Why tab-based incident detail?

SOC analysts navigate by investigation phase. Each tab maps to one agent output and one API endpoint—clear mental model for demos and production.

### Why polling instead of WebSockets?

MVP simplicity. Investigation runs complete in seconds with offline fallbacks. WebSockets are on the UX roadmap.

---

## Quick reference — one-line answers

| Question | Answer |
|----------|--------|
| Why ADK? | Standardized agent config aligned with Google stack and competition |
| Why MCP? | Typed tool registry; five operational tools; foundation for agent tool calls |
| Why fallback? | Reliability when Gemini unavailable; offline demos; quota safety |
| Why Guardian? | Dedicated safety layer between stages—not trusting LLM self-policing |
| Why SQLite? | One-file demo deploy; PostgreSQL for production |
| How scale? | Postgres, worker queue, horizontal API, static frontend |
| How SIEM? | Webhook ingestion + log connectors (planned) |
| Auto-remediation? | Never—recommendations only; human approval planned |

---

## Related documents

- [Demo script](demo_script.md)
- [Submission notes](../kaggle/submission_notes.md)
- [Competition alignment](../COMPETITION_ALIGNMENT.md)
- [Limitations](../kaggle/limitations.md)
- [Future work](../kaggle/future_work.md)
