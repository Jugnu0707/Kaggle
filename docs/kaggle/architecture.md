# Architecture

Oz AI implements a layered architecture where the presentation tier, API gateway, orchestration layer, intelligence agents, safety validation, analytics engines, and persistence store are clearly separated.

## Layer diagram

```text
┌─────────────────────────────────────────────────────────────┐
│  Frontend — React 19 · TypeScript · Tailwind · Vite         │
│  Routes: Dashboard, Incidents, Logs, Investigation, Replay  │
└─────────────────────────────┬───────────────────────────────┘
                              │ REST (39 operations · 35 paths)
┌─────────────────────────────▼───────────────────────────────┐
│  FastAPI Backend                                            │
│  API v1 · Services · Repositories · Investigation Workflow  │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ Coordinator   │   │ Google ADK      │   │ MCP Runtime     │
│ Agent         │   │ Runtime         │   │ 5 tools         │
│ (plan only)   │   │ agent registry  │   │ registry/server │
└───────┬───────┘   └────────┬────────┘   └────────┬────────┘
        │                    │                     │
        ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Specialist Agents (8)                                      │
│  Evidence · Threat Intel · MITRE · Risk · Response ·        │
│  Executive Report · Guardian                                  │
└─────────────────────────────┬───────────────────────────────┘
                              │ validated at each stage
┌─────────────────────────────▼───────────────────────────────┐
│  Guardian Agent — injection · PII · schema · confidence     │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────────┐                   ┌───────────────────┐
│ Timeline Engine   │                   │ Evaluation Engine │
│ event collection  │                   │ benchmarks/metrics│
└─────────┬─────────┘                   └─────────┬─────────┘
          │                                       │
          └───────────────────┬───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SQLite — 16 tables · SQLAlchemy ORM · append-only audits   │
└─────────────────────────────────────────────────────────────┘
```

## Component placement

### Google ADK

| Role | Location |
|------|----------|
| ADK import verification at startup | `backend/app/core/adk_runtime.py` |
| Agent ADK configuration objects | `agents/*/agent.py` |
| AI runtime and agent registry | `backend/app/ai/runtime.py`, `registry.py` |
| Session and tracing settings | `backend/app/core/ai_config.py` (`ADK_APP_NAME`, `ADK_ENABLE_TRACING`) |

ADK configures agent identity, descriptions, prompts, and schemas. LLM inference for AI-first agents uses `google.genai.Client` via `backend/app/ai/provider.py`.

### Google Gemini

| Role | Location |
|------|----------|
| API key and model config | `GOOGLE_API_KEY`, `GOOGLE_MODEL` in `.env` |
| Centralized Gemini client | `backend/app/ai/provider.py` |
| AI-first agent services | `agents/threat_intelligence/service.py`, `agents/risk/service.py`, `agents/response/service.py`, `agents/executive_report/service.py` |
| Connectivity probe | `GET /api/v1/ai/test` (`backend/app/services/ai_test_service.py`) |

Gemini is optional. When unavailable or misconfigured, agents fall back to rule engines without blocking the workflow.

### MCP (Model Context Protocol)

| Role | Location |
|------|----------|
| Tool registry | `mcp/registry.py` |
| Server lifecycle | `mcp/server.py` |
| Tool implementations | `mcp/tools/` (`health`, `incidents`, `logs`, `system`) |
| Runtime integration | `backend/app/core/mcp_runtime.py` |
| API introspection | `GET /api/v1/system/mcp` |

MCP tools provide operational data access. Domain agents currently invoke backend services directly; MCP is the foundation for ADK-native tool calls in future sprints.

### Rule Engine (deterministic fallbacks)

| Agent | Rule engine location |
|-------|---------------------|
| Coordinator | `agents/coordinator/orchestrator.py` — validation and plan building |
| Evidence | `agents/evidence/service.py` — log parsing and normalization |
| Threat Intelligence | `agents/threat_intelligence/ioc_extractor.py`, `reputation_engine.py`, `fallback.py` |
| MITRE | `agents/mitre/mappings.py` — local ATT&CK rule matching |
| Risk | `agents/risk/fallback.py` — severity and technique-based scoring |
| Response | `agents/response/fallback.py` — scenario playbooks |
| Executive Report | `agents/executive_report/fallback.py`, `markdown_generator.py` |
| Guardian | `agents/guardian/validator.py`, `prompt_injection.py`, `pii_detector.py` |
| Timeline | `backend/app/services/timeline/` — event collection and deduplication |
| Evaluation | `evaluation/engine.py`, `scorer.py`, `metrics.py` |

## Investigation sequence

```text
Coordinator → Evidence → Guardian → Threat Intel → Guardian → MITRE → Guardian
  → Risk → Guardian → Response → Guardian → Executive Report → Guardian
  → Timeline → Evaluation
```

Detailed sequence diagram: `docs/architecture/investigation-sequence.md`

## Data model

Sixteen ORM tables model incidents, investigations, agent outputs, audit trails, replay steps, and evaluation metrics. ER diagram: `docs/architecture/database-er.md`.

## Deployment topology

Docker Compose runs two services: backend (uvicorn on port 8000) and frontend (Vite dev server on port 5173). The backend image copies `backend/app`, `agents`, `mcp`, and `evaluation` packages. Persistent volumes hold SQLite database and uploaded logs.
