# Oz AI — Judge FAQ

Concise answers for Kaggle judges and Google engineers. All responses reflect the **implemented system** as of v0.1.0.

**Repository:** https://github.com/Jugnu0707/Kaggle

---

## Why Google ADK?

Google ADK is the competition's required agent framework. Oz AI uses it to configure all eight agents — name, description, prompts, schemas — with runtime initialization at startup (`backend/app/core/adk_runtime.py`). Eight agents register in `backend/app/ai/registry.py`. This demonstrates native ADK integration, not a generic LLM wrapper.

**Gap:** ADK session checkpointing and `adk eval` are not implemented. Workflow state persists in SQLite via services.

---

## Why MCP?

MCP provides a typed, discoverable tool layer with Pydantic input/output schemas (`mcp/registry.py`). Oz AI registers five operational tools introspectable via `GET /api/v1/system/mcp` and visible on the Settings page. MCP matches the competition requirement for tool protocol integration and provides a foundation for future ADK-native agent tool calls.

**Gap:** Domain tools (`evidence_collector`, `threat_intel_lookup`) are not implemented. Agents call backend services directly at runtime.

---

## Why multiple agents?

Incident response decomposes into distinct stages — evidence collection, IOC enrichment, ATT&CK mapping, risk scoring, response planning, executive reporting — each with different schemas and test criteria. One monolithic model produces broad, hard-to-evaluate outputs. Eight specialists with a Coordinator and Guardian enable per-agent testing, replay transparency, and a workflow that maps to real SOC analyst practice.

---

## Why SQLite?

SQLite enables single-command demo deployment: one file, no external database server, Docker volume at `/app/data/oz_ai.db`. Judges run `docker compose up --build` without provisioning PostgreSQL. SQLAlchemy abstracts the layer — production migration requires only a connection string change.

**Trade-off:** SQLite serializes writes; not suitable for concurrent multi-user production workloads.

---

## How would this scale?

| Layer | Scale path |
|-------|------------|
| Database | PostgreSQL with connection pooling |
| Agent execution | Worker processes or queue (Celery/Redis) instead of in-process HTTP thread |
| API | Horizontal scaling behind a load balancer |
| Frontend | Static Nginx build with CDN (Docker currently runs Vite dev server) |
| AI | Per-agent model routing, response caching, batch enrichment |

Current MVP runs synchronously in the FastAPI request thread — acceptable for single-analyst demos.

---

## Why deterministic fallback?

Enterprise systems cannot depend solely on cloud AI. Gemini quota limits, network failures, and air-gapped environments are normal. Four AI-first agents — Threat Intelligence, Risk, Response, Executive Report — invoke rule engines, playbooks, or templates when Gemini is unavailable. The workflow never blocks. `python scripts/reset_demo.py` completes full investigations without `GOOGLE_API_KEY`. Investigation Replay records `ai_used` and `fallback_used` per step.

Verified by: `tests/test_reliability.py`, per-agent service tests, offline demo reset.

---

## How would you integrate with SIEMs?

Oz AI complements SIEM and EDR — it does not replace them. Planned integration path:

1. **Webhook receiver** — ingest alerts from Splunk, Microsoft Sentinel, or Elastic; normalize to Oz AI incident schema
2. **Log pull connector** — scheduled queries export results to `POST /api/v1/logs/upload`
3. **Case sync** — push investigation status and executive report summaries back to SIEM ticketing

MITRE technique IDs and IOC fields already align with common SIEM export formats. See `docs/kaggle/10_future_work.md`.

**Current state:** Manual log upload via dashboard or API only. No Splunk, Sentinel, or CrowdStrike connectors.

---

## Additional likely questions

### Why Guardian as a separate agent?

Safety validation requires deterministic, auditable rules — not LLM self-policing. Guardian runs between every workflow stage: prompt injection detection, PII masking, secret masking, schema validation, confidence thresholds. Records persist to `guardian_audits`.

### Does Oz AI execute remediation?

No. Response plans are recommendations only. No host isolation, IP blocking, or playbook execution. Human approval workflow is documented but not enforced in API or UI.

### Why explicit `POST /investigations/run`?

Incidents are records; investigations are deliberate analyst actions. Auto-running agents on incident creation would misrepresent SOC workflows and consume resources on false positives.

### How is agent quality measured?

- 176 automated tests
- Evaluation Engine with health scores (availability 30%, reliability 30%, performance 20%, accuracy 20%)
- Evaluation dashboard at `/evaluation`
- Offline benchmark: full investigation ~36.57 ms mean in-process (`docs/SPRINT3_PERFORMANCE_REPORT.md`)

### How does a judge run the demo?

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle && cp .env.example .env
docker compose up --build
python scripts/reset_demo.py
open http://localhost:5173
```

Works fully offline without `GOOGLE_API_KEY`.

### What does `GET /api/v1/ai/test` do?

Minimal Gemini connectivity probe — one small prompt expecting `READY`. Verifies API key and model without running the full agent pipeline.

---

## Quick reference

| Question | One-line answer |
|----------|-----------------|
| Why ADK? | Competition stack; eight configured agents with registry |
| Why MCP? | Five typed operational tools; introspection API |
| Why multiple agents? | Distinct schemas and testability per investigation stage |
| Why SQLite? | One-file demo deploy; PostgreSQL for production |
| How scale? | Postgres, worker queue, horizontal API, static frontend |
| Why fallback? | Reliability without Gemini; offline judging |
| How SIEM? | Webhook + log connectors planned; manual upload today |
| Auto-remediation? | Never — recommendations only |

---

## Related documents

- [FINAL_DEMO_SCRIPT.md](FINAL_DEMO_SCRIPT.md)
- [docs/kaggle/FINAL_WRITEUP.md](../kaggle/FINAL_WRITEUP.md)
- [docs/kaggle/11_competition_mapping.md](../kaggle/11_competition_mapping.md)
- [docs/kaggle/09_limitations.md](../kaggle/09_limitations.md)
