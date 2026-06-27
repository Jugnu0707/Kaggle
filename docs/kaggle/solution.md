# Solution

## Oz AI

Oz AI is an open-source enterprise incident response platform built for the Kaggle AI Agents Intensive Capstone (Agents for Business track). It combines a React operations dashboard, a FastAPI backend, eight Google ADK specialist agents, a Guardian safety layer, MCP operational tools, and SQLite persistence into a single deployable system. Oz AI is a decision-support platform: it structures investigations, surfaces risk, and drafts response recommendations — it does not execute remediation autonomously.

## Architecture

Oz AI follows a layered architecture documented in `docs/02_ARCHITECTURE.md` and `docs/architecture/`:

```text
React Dashboard → FastAPI API → Services & Workflow → Specialist Agents
  → Guardian Validation → Timeline Engine → Evaluation Engine → SQLite
```

The **Coordinator Agent** validates incident context and defines the execution plan. The **Investigation Workflow Service** (`InvestigationWorkflowService`) runs the full pipeline when an analyst triggers `POST /api/v1/investigations/run`. Each specialist agent persists structured output to dedicated database tables. The **Guardian Agent** validates every stage before the workflow advances. After agent execution, the **Timeline Engine** reconstructs a chronological event sequence and the **Evaluation Engine** scores agent outputs against benchmark criteria.

Google ADK provides agent configuration and runtime initialization (`backend/app/core/adk_runtime.py`). Google Gemini (`google.genai`) enriches Threat Intelligence, Risk, Response, and Executive Report agents when `GOOGLE_API_KEY` is configured. An MCP registry exposes five operational tools (`health`, `list_incidents`, `incident_details`, `list_logs`, `system_info`) for introspection and future ADK tool wiring. Rule-based engines and deterministic fallbacks ensure the platform operates fully offline for demos and judging environments without API keys.

## Workflow

A typical investigation proceeds as follows:

1. Analyst creates an incident and uploads log files via the dashboard or API.
2. Analyst opens the Investigation Runner and starts a new run.
3. Coordinator validates context and builds the execution plan.
4. Evidence Agent normalizes uploaded logs into a structured evidence package.
5. Guardian validates evidence output.
6. Threat Intelligence Agent extracts IOCs and enriches reputation (Gemini or offline engine).
7. Guardian validates threat intelligence output.
8. MITRE Mapping Agent maps evidence to ATT&CK techniques via local rules.
9. Guardian validates MITRE output.
10. Risk Assessment Agent scores enterprise risk (Gemini or rule engine).
11. Guardian validates risk output.
12. Response Planning Agent drafts containment and recovery steps (Gemini or playbooks).
13. Guardian validates response output.
14. Executive Report Agent produces JSON and Markdown leadership summaries (Gemini or templates).
15. Guardian validates executive report output.
16. Timeline Engine builds the incident timeline from persisted agent outputs.
17. Evaluation Engine records performance metrics.
18. Analyst reviews results in Incident Detail tabs, Timeline, Evaluation dashboard, and Investigation Replay.

Replay and explainability APIs (`/investigations/{run_id}/replay`, `/explain`, `/replay/export`) expose step-level metadata including AI vs. fallback usage, latency, and sanitized input/output summaries.

## Benefits

| Benefit | How Oz AI delivers |
|---------|-------------------|
| Faster triage | Automated evidence normalization and IOC extraction |
| Consistent analysis | Repeatable multi-agent pipeline with Guardian gates |
| Framework alignment | MITRE ATT&CK mapping on every investigation |
| Executive readiness | Structured reports without raw log exposure |
| Offline capability | Deterministic fallbacks when Gemini is unavailable |
| Auditability | Append-only guardian audits, replay export, evaluation metrics |
| Deployability | `docker compose up --build` and `python scripts/reset_demo.py` |
| Transparency | Investigation replay shows which agent ran, with what outcome |

Oz AI demonstrates that multi-agent coordination, Google ADK integration, MCP tooling, and responsible AI guardrails can be composed into a production-shaped incident response workflow suitable for enterprise security operations — while keeping humans accountable for approval and execution of consequential actions (approval workflow enforcement planned for Sprint 4).
