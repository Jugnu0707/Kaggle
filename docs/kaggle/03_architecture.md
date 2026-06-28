# Architecture

**Related:** [02 Solution](02_solution.md) · [04 Implementation](04_implementation.md) · [Architecture docs](../architecture/README.md)

Oz AI implements a layered architecture with clear separation between presentation, API, orchestration, agents, safety validation, analytics engines, and persistence.

---

## Layer flow

```text
Frontend (React)
  ↓
FastAPI
  ↓
Coordinator
  ↓
Agents (Evidence → Threat Intel → MITRE → Risk → Response → Executive Report)
  ↓
Guardian                    ← validates after each specialist stage
  ↓
Timeline Engine
  ↓
Evaluation Engine
  ↓
SQLite
```

---

## Layer diagram

```text
┌─────────────────────────────────────────────────────────────┐
│  Frontend — React 19 · TypeScript · Tailwind · Vite         │
│  10 pages: Dashboard, Incidents, Investigation, Replay, etc.│
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
└───────┬───────┘   └────────┬────────┘   └────────┬────────┘
        │                    │                     │
        ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Specialist Agents (8)                                      │
└─────────────────────────────┬───────────────────────────────┘
                              │ validated at each stage
┌─────────────────────────────▼───────────────────────────────┐
│  Guardian Agent                                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────────┐                   ┌───────────────────┐
│ Timeline Engine   │                   │ Evaluation Engine │
└─────────┬─────────┘                   └─────────┬─────────┘
          └───────────────────┬───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SQLite — 16 tables · SQLAlchemy ORM                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Google ADK

| Role | Location |
|------|----------|
| ADK import verification at startup | `backend/app/core/adk_runtime.py` |
| Agent ADK configuration objects | `agents/*/agent.py` |
| AI runtime and agent registry | `backend/app/ai/runtime.py`, `registry.py` |
| Session tracking | `backend/app/ai/session.py` |
| Configuration | `ADK_APP_NAME`, `ADK_ENABLE_TRACING` in `.env` |

ADK configures agent identity, descriptions, prompts, and schemas. LLM inference for AI-first agents uses `google.genai.Client` via `backend/app/ai/provider.py`.

---

## Google Gemini

| Role | Location |
|------|----------|
| API key and model config | `GOOGLE_API_KEY`, `GOOGLE_MODEL` (default `gemini-2.5-pro`) |
| Centralized Gemini client | `backend/app/ai/provider.py` |
| AI-first agent services | `agents/threat_intelligence/`, `agents/risk/`, `agents/response/`, `agents/executive_report/` |
| Connectivity probe | `GET /api/v1/ai/test` |

Gemini is optional. When unavailable, agents fall back to rule engines without blocking the workflow.

---

## MCP (Model Context Protocol)

| Role | Location |
|------|----------|
| Tool registry | `mcp/registry.py` |
| Server lifecycle | `mcp/server.py` |
| Tool implementations | `mcp/tools/` |
| Runtime integration | `backend/app/core/mcp_runtime.py` |
| API introspection | `GET /api/v1/system/mcp` |

**Registered tools:** `health`, `list_incidents`, `incident_details`, `list_logs`, `system_info`

MCP provides operational data access and introspection. Agents invoke backend services directly at runtime; MCP is the foundation for future ADK-native tool calls.

---

## Investigation sequence

```text
Coordinator → Evidence → Guardian → Threat Intel → Guardian → MITRE → Guardian
  → Risk → Guardian → Response → Guardian → Executive Report → Guardian
  → Timeline → Evaluation
```

Detailed diagrams: [`docs/architecture/`](../architecture/README.md)

---

## Deployment topology

Docker Compose runs two services:

| Service | Port |
|---------|------|
| Backend (uvicorn) | 8000 |
| Frontend (Vite dev server) | 5173 |

Persistent volumes: `oz-ai-data` (SQLite), `oz-ai-uploads` (log files).

See [09 Deployment](../architecture/09_deployment.md) for full topology.
