# 04 — Architecture Decision Records

**Project Name:** Oz AI
**Version:** 1.0 (MVP)
**Last Updated:** 2026-06-26

> This document contains all Architecture Decision Records (ADRs) for Oz AI. An ADR is created whenever a significant technical or architectural decision is made. ADRs are **append-only** — once recorded, they are never deleted or modified. If a decision is reversed or superseded, a new ADR is created referencing the original.

---

## ADR Template

```
### ADR-NNN — [Title]

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-NNN
**Date:** YYYY-MM-DD
**Decision Maker(s):** [Names or roles]

#### Context
[Situation that required a decision. Constraints, forces, and background.]

#### Decision
[Clear statement of what was decided.]

#### Alternatives Considered
[What else was evaluated and why it was not chosen.]

#### Pros
[Advantages of the decision.]

#### Cons
[Trade-offs and disadvantages.]

#### Consequences
[What changes downstream. What becomes easier, harder, or requires follow-on decisions.]
```

---

---

## ADR-001 — Core Technology Stack Selection (Simplified for MVP)

**Status:** Accepted
**Date:** 2026-06-26
**Decision Maker(s):** Engineering Lead

---

### Context

At project inception, the full technology stack was selected to balance competition requirements, development velocity, and engineering quality. An initial version of this decision was drafted but included components (Celery, Redis, Structlog, React Query, Zod, Zustand) that, upon architect review, introduced unnecessary complexity for the MVP scope.

The key constraints that shaped the final decision:

1. **Competition alignment:** The Kaggle AI Agents Intensive Capstone (Agents for Business track) prioritizes Google AI technologies — specifically Google ADK and Gemini. This is a hard requirement that drives the agent layer choice.

2. **MVP scope discipline:** The MVP must demonstrate a working, impressive multi-agent incident response platform. Every dependency that is not directly required by the MVP use cases is a liability — additional attack surface, additional documentation burden, additional debugging complexity, additional barrier to evaluator reproducibility.

3. **Evaluator reproducibility:** Competition evaluators run the system from scratch. A simpler dependency graph means fewer failure points and a faster evaluation setup.

4. **Python-native AI ecosystem:** Python 3.12 is the dominant language for AI/ML work. All agent libraries, Google ADK, and MCP tooling are Python-native. Keeping the backend in Python eliminates cross-language complexity.

5. **Frontend simplicity:** An enterprise dashboard for an MVP does not require additional state management or data-fetching libraries. React's built-in `useState`, `useEffect`, and the native `fetch` API are sufficient for the polling-based data model.

---

### Decision

The following **minimal** technology stack is approved for the Oz AI MVP:

**Backend:**
| Component | Technology |
|---|---|
| Language | Python 3.12 |
| API Framework | FastAPI |
| Agent Framework | Google ADK |
| Agent LLM | Google Gemini (via ADK) |
| Data Validation | Pydantic v2 |
| ORM | SQLAlchemy (async, aiosqlite) |
| Database | SQLite |
| Agent Tool Layer | MCP (Model Context Protocol) |

**Frontend:**
| Component | Technology |
|---|---|
| Framework | React 19 + TypeScript |
| Styling | Tailwind CSS |
| Build Tool | Vite |

**Infrastructure:**
| Component | Technology |
|---|---|
| Containerization | Docker |
| Orchestration | Docker Compose |

**Explicitly excluded from MVP:**
- Celery, Redis — no distributed task queue needed; FastAPI `BackgroundTasks` handles async agent dispatch
- Structlog — standard Python `logging` with JSON formatter is sufficient for MVP
- React Query, Zustand, Zod — native React hooks + fetch + Pydantic-aligned TypeScript interfaces cover the MVP data needs
- Kafka, RabbitMQ — no event streaming in MVP
- Kubernetes, Nginx, Caddy — Docker Compose is the MVP deployment target

---

### Alternatives Considered

#### Task Queue: Celery + Redis vs. FastAPI BackgroundTasks

| Option | Decision |
|---|---|
| Celery + Redis | **Rejected for MVP.** Adds two services (worker + broker), additional Docker containers, Celery configuration, and operational complexity. For the MVP's sequential, single-incident processing model, `FastAPI BackgroundTasks` is sufficient. Post-MVP, when concurrent incident processing at scale is required, Celery + Redis is the natural upgrade path. |
| FastAPI BackgroundTasks | **Selected.** In-process async task execution. Zero additional infrastructure. Sufficient for MVP workloads. |

#### Frontend Data Fetching: React Query vs. Native fetch + useEffect

| Option | Decision |
|---|---|
| React Query | **Rejected for MVP.** Excellent library, but adds dependency weight and a learning curve that is not justified when the data model is simple polling over REST. |
| Native fetch + useEffect | **Selected.** Explicit, debuggable, zero dependencies. All cache and refetch logic is visible in the component. |

#### Frontend Validation: Zod vs. TypeScript interfaces

| Option | Decision |
|---|---|
| Zod | **Rejected for MVP.** Runtime schema validation is valuable, but Pydantic on the backend + strict TypeScript on the frontend provides type safety at both ends without a third runtime validation layer. |
| TypeScript interfaces + strict mode | **Selected.** Compile-time type safety with zero runtime overhead. |

#### Logging: Structlog vs. Python standard logging

| Option | Decision |
|---|---|
| Structlog | **Rejected for MVP.** Adds a dependency. The standard `logging` module with a JSON formatter (`python-json-logger` or equivalent) is sufficient for structured log output at MVP scale. |
| Python standard logging | **Selected.** Zero additional dependency. JSON formatter produces structured output. |

#### Agent Orchestration: Google ADK vs. LangGraph vs. CrewAI

| Option | Decision |
|---|---|
| LangGraph | Strong multi-agent framework but not the competition's preferred technology. Misaligned with Kaggle evaluation criteria. |
| CrewAI | Purpose-built for multi-agent, but less mature evaluation tooling and not competition-aligned. |
| AutoGen | Excellent but tied to Azure/OpenAI ecosystem. |
| **Google ADK** | **Selected.** Competition-required. Native Gemini integration. Built-in evaluation tooling. MCP support. |

---

### Pros

- **Minimal dependency surface:** Fewer dependencies = fewer vulnerabilities, fewer version conflicts, faster installs, easier evaluator reproducibility.
- **Competition alignment:** Native Google ADK + Gemini satisfies the competition's technology evaluation criteria.
- **In-process simplicity:** No distributed systems to configure, monitor, or debug for the MVP.
- **SQLAlchemy abstraction:** The ORM fully abstracts SQLite → PostgreSQL. No code changes required for the production migration — only the connection string.
- **Single-command deployment:** `docker compose up` starts the full system. No queue workers, no separate broker service.
- **TypeScript + strict Pydantic:** Type safety at both ends of the wire without a third validation library.

---

### Cons

- **FastAPI BackgroundTasks limitation:** `BackgroundTasks` runs in the same process as the API. Under high concurrent load, long-running agent pipelines could delay API response handling. This is acceptable for MVP (single-user, sequential workload) but must be addressed before production.
- **SQLite write concurrency:** SQLite serializes writes. Running multiple incidents simultaneously will result in write contention. Acceptable for MVP; migrate to PostgreSQL for production.
- **No built-in retry for failed background tasks:** If a background agent task fails, there is no automatic retry mechanism without Celery. The Coordinator Agent's error handling must be robust. Failed pipelines are flagged in the database for human review.
- **Polling frontend:** Polling every 5 seconds is less efficient than WebSockets. For an MVP dashboard with few concurrent incidents, this is acceptable. A WebSocket upgrade path is noted for post-MVP.

---

### Consequences

1. A new ADR must be created when the decision is made to replace `FastAPI BackgroundTasks` with a distributed task queue (expected at Phase 2 post-MVP).
2. A new ADR must be created when the database is migrated from SQLite to PostgreSQL.
3. A new ADR must be created when any new library not listed in this decision is added to the stack.
4. The Gemini API key is a **required** environment variable from Day 1. Development without it requires a mock LLM layer (agent tests should be written to support both real and mock LLM backends).
5. All database access must go through SQLAlchemy async sessions. No raw SQL in application code.
6. No agent contains direct I/O. All external interactions go through registered MCP tools.

---

---

## ADR-002 — Nine-Agent Pipeline Architecture

**Status:** Superseded by ADR-003
**Date:** 2026-06-26
**Decision Maker(s):** Engineering Lead / Chief Architect

---

### Context

The initial agent design proposed five specialist agents (Parser, Triage, RCA, Remediation, Notification). Upon architect review, this design was replaced with a nine-agent architecture that better reflects the actual cognitive workflow of an expert security analyst and more thoroughly demonstrates multi-agent coordination capabilities for the competition.

The key insight is that each distinct analytical domain (evidence collection, threat intelligence, framework mapping, timeline reconstruction, risk assessment, response planning, reporting, and safety oversight) benefits from its own specialized agent with a purpose-built prompt, a specific tool set, and a defined output schema. Collapsing these into fewer agents produces agents with broader, less-focused responsibilities that are harder to test, evaluate, and improve independently.

---

### Decision

The Oz AI MVP implements nine agents in a hierarchical, sequential pipeline:

1. **Coordinator Agent** — Orchestration only
2. **Evidence Agent** — Evidence collection and normalization
3. **Threat Intelligence Agent** — IOC lookup and attribution
4. **MITRE Mapping Agent** — ATT&CK framework mapping
5. **Timeline Agent** — Incident timeline reconstruction
6. **Risk Assessment Agent** — Severity, blast radius, and risk scoring
7. **Response Planning Agent** — Actionable response plan generation
8. **Executive Report Agent** — Audience-appropriate report generation
9. **Guardian Agent** — Safety, PII, injection, and approval enforcement

---

### Alternatives Considered

| Alternative | Why Not Selected |
|---|---|
| Five-agent design (original) | Collapsing evidence + threat intel + MITRE into "RCA" produces an agent with too broad a focus. Evaluation becomes harder (what exactly is being measured?). Each concern is better served by a dedicated agent with a specific prompt and tool set. |
| Parallel agent execution (evidence + threat intel in parallel) | Would reduce wall-clock time but significantly increases Coordinator complexity, requires conflict resolution if agents produce inconsistent outputs, and is not necessary for MVP latency targets. Sequential is simpler and more predictable. |
| No dedicated Guardian Agent | Safety validation could be implemented as Pydantic validation in the service layer. Rejected because a dedicated Guardian Agent demonstrates responsible AI deployment, satisfies the competition's safety evaluation criteria, and provides a more complete and auditable safety record. |

---

### Pros

- Each agent has a single, testable responsibility.
- The pipeline maps cleanly to a real analyst's workflow, making it legible to domain experts.
- The Guardian Agent as a dedicated safety layer demonstrates responsible AI deployment and earns evaluation credit for the safety criterion.
- MITRE ATT&CK mapping as a first-class pipeline stage differentiates Oz AI from simpler classification-only systems.
- Each agent can be independently evaluated with its own precision/recall metrics.

---

### Cons

- Nine agents means nine system prompts, nine output schemas, and nine test suites. Development effort is higher than a five-agent design.
- Sequential pipeline latency is the sum of all nine agent response times. Target: <90 seconds total.
- More moving parts = more integration surface = more integration tests needed.

---

### Consequences

1. Each agent must have its own directory in `agents/` with a versioned system prompt file.
2. Agent prompts are treated as code: versioned, reviewed, and updated via PR.
3. The evaluation harness must measure output quality for each agent independently, not only end-to-end.
4. Adding or removing a pipeline stage requires a new ADR.

---

---

## ADR-003 — Eight-Agent Pipeline (Timeline Merged into Evidence Agent)

**Status:** Accepted
**Date:** 2026-06-26
**Decision Maker(s):** Engineering Lead / Chief Architect

---

### Context

Following UI/UX and architect review, the standalone Timeline Agent was identified as overlapping heavily with the Evidence Agent. Both agents consume the same log sources, operate on the same timestamped events, and produce outputs that are always consumed together in the analyst workflow (Evidence tab and Timeline tab in the UI).

Maintaining a separate Timeline Agent added pipeline latency, increased Coordinator complexity, and split logically unified work across two ADK invocations without improving evaluation clarity. The Timeline **UI tab** remains — only the agent responsible for generating timeline data changes.

---

### Decision

Remove the Timeline Agent from the pipeline. The **Evidence Agent** now produces both:

1. `EvidenceBundle` — entities, correlated events, topology, evidence gaps
2. `IncidentTimeline` — chronological event ordering, compromise timeline estimate, gap analysis

The agent count is reduced from nine to **eight**:

1. Coordinator Agent
2. Evidence Agent (evidence + timeline)
3. Threat Intelligence Agent
4. MITRE Mapping Agent
5. Risk Assessment Agent
6. Response Planning Agent
7. Executive Report Agent
8. Guardian Agent

The Timeline tab in the UI continues to display `IncidentTimeline` data. MITRE technique annotations on timeline events are merged at display time once the MITRE Mapping Agent completes (frontend or API presentation layer).

---

### Alternatives Considered

| Alternative | Why Not Selected |
|---|---|
| Keep Timeline Agent separate | Redundant log processing; adds ~10–15s pipeline latency; same MCP tools as Evidence Agent |
| Remove Timeline UI tab | Analysts require chronological view; tab stays, data source changes |
| MITRE Agent annotates timeline | Would require MITRE Agent to write back to timeline record; adds coupling. Display-time merge is simpler for MVP |

---

### Pros

- Fewer ADK invocations → faster demo and lower latency
- Evidence collection and timeline reconstruction are logically unified
- Simpler Coordinator routing and Dashboard Agent Pipeline widget (6 specialist stages + Guardian)
- Timeline tab unchanged for analysts — zero UX regression

---

### Cons

- Evidence Agent prompt and output schema are larger (more responsibilities per agent)
- Timeline evaluation metrics move under Evidence Agent (evaluation harness must update)
- ADR-002 pipeline documentation is superseded

---

### Consequences

1. Remove `agents/timeline/` from the folder structure (never create it).
2. Evidence Agent writes both `EvidenceBundle` and `IncidentTimeline` via `incident_record_write`.
3. Coordinator sequence: Guardian (ingestion) → Evidence → Threat Intel → MITRE → Risk → Response → Executive Report → Guardian (validation).
4. Pipeline stage `BuildingTimeline` is removed; timeline generation occurs during `GatheringEvidence`.
5. All documentation referencing nine agents or Timeline Agent must reference this ADR.

---

---

## Decision Log (Summary)

| ADR # | Title | Status | Date |
|---|---|---|---|
| ADR-001 | Core Technology Stack Selection (Simplified for MVP) | Accepted | 2026-06-26 |
| ADR-002 | Nine-Agent Pipeline Architecture | Superseded by ADR-003 | 2026-06-26 |
| ADR-003 | Eight-Agent Pipeline (Timeline Merged into Evidence Agent) | Accepted | 2026-06-26 |
