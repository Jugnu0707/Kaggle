# Decision Records

**Related:** [System Overview](01_system_overview.md) · [MCP Architecture](06_mcp_architecture.md) · [ADK Runtime](07_adk_runtime.md)

Summary of architectural decisions for Oz AI v0.1.0. Full ADR text with alternatives and consequences: [`docs/04_DECISIONS.md`](../04_DECISIONS.md)

---

## Decision Summary

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| ADR-001 | Core Technology Stack Selection | Accepted | 2026-06-26 |
| ADR-002 | Nine-Agent Pipeline Architecture | Superseded by ADR-003 | 2026-06-26 |
| ADR-003 | Eight-Agent Pipeline | Accepted | 2026-06-26 |
| ADR-004 | Investigation Workflow and Service-Layer Integration | Accepted | 2026-06-27 |

---

## SQLite over PostgreSQL

**Decision:** Use SQLite for the MVP database.

**Rationale:**
- Zero-configuration deployment for evaluators and judges
- Single-file persistence works with Docker volumes
- SQLAlchemy abstracts the database layer — migration to PostgreSQL requires only a connection string change

**Trade-offs:**
- Serializes writes; not suitable for concurrent production workloads
- No row-level locking or replication

**Future:** PostgreSQL migration planned for v0.2.0.

---

## FastAPI over Flask

**Decision:** Use FastAPI as the backend framework.

**Rationale:**
- Native async support and automatic OpenAPI generation
- Pydantic v2 integration for request/response validation
- Strong typing aligns with agent schema contracts
- Swagger UI at `/docs` aids evaluator exploration

**Trade-offs:**
- Synchronous agent workflow runs in the HTTP thread (acceptable for MVP)

**Alternatives rejected:** Flask (manual OpenAPI, less type safety), Django (heavier than needed for API-first MVP).

---

## React over Vue

**Decision:** Use React 19 with TypeScript for the frontend.

**Rationale:**
- Large ecosystem and familiar patterns for dashboard UIs
- TypeScript strict mode provides compile-time safety matching backend Pydantic schemas
- React 19 with native hooks avoids additional state management libraries

**Trade-offs:**
- Polling-based data fetching (no WebSockets in MVP)

**Alternatives rejected:** Vue ( viable but team familiarity favored React), Angular (heavier framework for MVP scope).

**Explicitly excluded:** React Query, Zustand, Zod — native hooks and TypeScript interfaces sufficient for MVP.

---

## MCP (Model Context Protocol)

**Decision:** Implement an in-process MCP tool registry with five operational tools.

**Rationale:**
- Competition alignment with MCP as agent tool layer standard
- Typed input/output schemas via Pydantic
- Introspectable via REST (`GET /api/v1/system/mcp`)
- Foundation for future domain tools

**Trade-offs:**
- Agents call services directly, not MCP tools at runtime (deferred)
- Only operational tools implemented; domain tools planned for v1.0.0

**Alternatives rejected:** Direct-only service calls without MCP (insufficient for competition criteria).

---

## Google ADK

**Decision:** Use Google Agent Development Kit for agent configuration and orchestration.

**Rationale:**
- Required by Kaggle AI Agents Intensive Capstone
- Native Gemini integration path
- Built-in evaluation tooling and MCP support
- Demonstrates multi-agent coordination for competition scoring

**Trade-offs:**
- Single model configuration (`GOOGLE_MODEL`); no per-agent routing
- ADK session checkpointing not implemented

**Alternatives rejected:** LangGraph, CrewAI, AutoGen — misaligned with competition technology requirements.

---

## Deterministic Fallback

**Decision:** Every AI-first agent has a rule-based fallback that executes when Gemini is unavailable or Guardian rejects output.

**Rationale:**
- Offline demos work without API keys
- Workflow never blocks on AI failure
- Evaluators can reproduce full investigations deterministically
- Replay records `ai_used` and `fallback_used` for transparency

**Trade-offs:**
- Fallback output quality is lower than Gemini-enriched output
- Free-tier Gemini quota limits AI-first enrichment

**Implementation:** Per-agent `fallback.py` modules; Guardian-triggered retry patches `_call_gemini` to return `None`.

---

## Rule-Based Guardian

**Decision:** Implement Guardian as a dedicated rule-based agent, not LLM-based validation.

**Rationale:**
- Safety validation must be deterministic and auditable
- Pattern-based injection, PII, and secret detection are fast and offline-capable
- Dedicated Guardian demonstrates responsible AI deployment for competition
- Append-only audit trail in `guardian_audits`

**Trade-offs:**
- Novel injection patterns may evade rule-based detection
- No ML-based anomaly detection

**Alternatives rejected:** Pydantic-only validation in service layer (insufficient auditability and competition visibility).

---

## Additional Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Task queue | In-process (no Celery/Redis) | MVP sequential workload; simpler deployment |
| Logging | Python standard logging | Zero additional dependencies |
| Frontend data | Native fetch + useEffect | Simple polling model; no React Query |
| Investigation trigger | Explicit API call | Operator control; no auto-dispatch on incident creation |
| Timeline | Separate Timeline Engine | Runs as workflow stage after specialist agents |
| Agent count | Eight (not nine) | Timeline Agent merged into Evidence at design level; Timeline Engine retained as service |

---

## Consequences for Documentation

1. Documentation must not claim automatic pipeline dispatch on incident creation.
2. Documentation must not claim agents invoke MCP tools at runtime.
3. Documentation must state SQLite is demo-ready, not production-ready.
4. New stack additions require a new ADR in `docs/04_DECISIONS.md`.

---

## Related Documents

| Document | Topic |
|----------|-------|
| [06_mcp_architecture.md](06_mcp_architecture.md) | MCP implementation detail |
| [07_adk_runtime.md](07_adk_runtime.md) | ADK and Gemini integration |
| [08_security_architecture.md](08_security_architecture.md) | Guardian implementation |
| [09_deployment.md](09_deployment.md) | Docker deployment |
| [`docs/04_DECISIONS.md`](../04_DECISIONS.md) | Full ADR text |
