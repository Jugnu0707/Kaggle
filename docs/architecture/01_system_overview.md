# System Overview

**Related:** [Architecture Index](README.md) · [Component Diagram](02_component_diagram.md) · [Sequence Diagram](03_sequence_diagram.md)

---

## Purpose

Oz AI is an open-source, multi-agent incident response platform. It helps security analysts investigate security incidents by coordinating specialist agents that collect evidence, enrich indicators, map techniques, assess risk, plan response, and produce executive reports — with safety validation at every stage.

The system is built for the Kaggle AI Agents Intensive Capstone (Agents for Business track) and serves as a decision-support tool. It produces recommendations; it does not execute remediation actions.

---

## Scope

### In scope (v0.1.0)

- REST API for incident and log management
- React dashboard with ten analyst-facing pages
- Eight Google ADK specialist agents plus Timeline and Evaluation engines
- Guardian safety validation between workflow stages
- MCP tool registry with five operational tools
- SQLite persistence and file-based log storage
- Docker Compose deployment
- Offline demo mode with deterministic fallbacks

### Out of scope

- API authentication and RBAC
- SIEM or webhook integrations
- Automated remediation execution
- Live commercial threat intelligence feeds
- Multi-tenant isolation
- Production-grade horizontal scaling

Full limitations: [`docs/kaggle/limitations.md`](../kaggle/limitations.md)

---

## Major Components

| Component | Role | Location |
|-----------|------|----------|
| **React Frontend** | Analyst dashboard, investigation UI, evaluation views | `frontend/src/` |
| **FastAPI Backend** | REST API, workflow orchestration, persistence | `backend/app/` |
| **Specialist Agents** | Evidence through Executive Report pipeline | `agents/` |
| **Guardian Agent** | Output validation, PII/secret masking, injection detection | `agents/guardian/` |
| **Timeline Engine** | Chronological event reconstruction | `backend/app/services/timeline/` |
| **Evaluation Engine** | Agent health scoring and metrics persistence | `evaluation/` |
| **Google ADK Runtime** | Agent configuration and Coordinator initialization | `backend/app/core/adk_runtime.py` |
| **AI Runtime** | Agent registry, MCP discovery, Gemini provider | `backend/app/ai/` |
| **MCP Registry** | Typed operational tools for introspection and invocation | `mcp/` |
| **SQLite Database** | Sixteen tables for incidents, outputs, and audit records | `backend/app/models/` |
| **Upload Storage** | Persisted log files on disk | `storage/uploads/` |

---

## High-Level Workflow

1. **Ingest** — Analyst uploads log files and creates or selects an incident.
2. **Investigate** — Operator triggers `POST /api/v1/investigations/run` (not automatic on incident creation).
3. **Orchestrate** — Coordinator validates context and the workflow service runs specialist agents in sequence.
4. **Validate** — Guardian inspects each specialist output before the next stage proceeds.
5. **Enrich** — Threat Intelligence, MITRE, Risk, Response, and Executive Report agents produce structured outputs persisted to SQLite.
6. **Reconstruct** — Timeline Engine builds chronological events from agent outputs.
7. **Evaluate** — Evaluation Engine scores agent performance and persists metrics.
8. **Review** — Analyst inspects incident tabs, replay steps, and the evaluation dashboard.

Investigations are synchronous within the HTTP request thread. When Gemini is unavailable, AI-first agents use deterministic fallback paths without blocking the pipeline.

---

## Documentation Map

| Document | Topic |
|----------|-------|
| [02_component_diagram.md](02_component_diagram.md) | Layered system components |
| [03_sequence_diagram.md](03_sequence_diagram.md) | End-to-end request flow |
| [04_agent_workflow.md](04_agent_workflow.md) | Agent responsibilities and APIs |
| [05_database_design.md](05_database_design.md) | Entity relationships |
| [06_mcp_architecture.md](06_mcp_architecture.md) | MCP registry and tools |
| [07_adk_runtime.md](07_adk_runtime.md) | ADK initialization and Gemini |
| [08_security_architecture.md](08_security_architecture.md) | Guardian and audit trail |
| [09_deployment.md](09_deployment.md) | Docker topology and ports |
| [10_decision_records.md](10_decision_records.md) | Architectural decisions |

Authoritative reference: [`docs/02_ARCHITECTURE.md`](../02_ARCHITECTURE.md)
