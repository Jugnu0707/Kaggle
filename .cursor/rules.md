# Cursor AI Rules — Oz AI Project

**Project Name:** Oz AI
**Version:** 1.0 (MVP)
**Last Updated:** 2026-06-26
**Status:** Enforced from Day 1

> These rules govern every AI-assisted development session in this project. They are non-negotiable. If a rule conflicts with an immediate implementation goal, stop and surface the conflict explicitly rather than silently violating the rule.

---

## PRIME DIRECTIVES

Before every coding session, read the following documents in order:

1. `docs/01_PROJECT_BRIEF.md` — understand what Oz AI is and why it exists
2. `docs/02_ARCHITECTURE.md` — understand how it is structured before touching any code
3. `docs/03_TASKS.md` — identify the specific task being worked on

**Never write code for a task that does not exist in `03_TASKS.md`.**

---

## Rule 1 — Architecture Is Frozen

### 1.1 Never Change Architecture Without Approval

The architecture defined in `docs/02_ARCHITECTURE.md` is frozen prior to development. Do not:
- Change the agent pipeline sequence or add/remove agents.
- Rename top-level repository folders.
- Move responsibilities between architectural layers.
- Change the database schema design philosophy.
- Change the API contract.

If a proposed implementation path requires any of the above, **stop**. Document the proposed change and its rationale. Seek explicit team approval. Create an ADR in `docs/04_DECISIONS.md`. Only then proceed.

### 1.2 Record Every Significant Decision

Every decision that would surprise a team member who reads the code without context must be recorded as an ADR. "Significant" includes: choosing one algorithm over another, adapting a schema, deviating from a pattern in `02_ARCHITECTURE.md`, or adding any library.

---

## Rule 2 — Read Before Coding

### 2.1 Always Read PROJECT_BRIEF Before Coding

Read `docs/01_PROJECT_BRIEF.md` at the start of every session. Know the vision, the goals, the non-goals, the safety statement, and the technology stack. Code written without this context is likely to miss the mark.

### 2.2 Always Read ARCHITECTURE Before Coding

Read `docs/02_ARCHITECTURE.md` before implementing any agent, tool, service, or API endpoint. Understand which layer the code belongs to and what the layer boundaries are before writing a single line.

### 2.3 Always Read TASKS Before Coding

Read `docs/03_TASKS.md` before starting any implementation work. Identify the exact task ID being worked on. Reference the task ID in the branch name and commit message. Do not start a task that has no ID.

---

## Rule 3 — Never Introduce Dependencies Without Approval

### 3.1 The Approved Stack Is Closed

The MVP technology stack is defined in ADR-001. It is closed. No new Python packages or npm packages may be introduced without:
1. Checking whether the requirement can be met by an existing approved dependency.
2. Writing a justification explaining why a new dependency is genuinely necessary.
3. Creating an ADR in `docs/04_DECISIONS.md`.
4. Receiving explicit approval before the dependency is added.

### 3.2 Never Use Unapproved Libraries

The following are explicitly excluded from the MVP. Do not use them, do not import them, do not suggest them:
- Celery, Redis, RabbitMQ, Kafka
- React Query, Zustand, Zod
- Structlog
- Kubernetes, Nginx, Caddy (in application code)
- Any LLM orchestration library other than Google ADK (LangChain, CrewAI, AutoGen, etc.)

---

## Rule 4 — Respect Layer Boundaries

Each architectural layer has a defined responsibility. Never violate it.

| Layer | Location | Responsibility | Must NOT |
|---|---|---|---|
| API Layer | `backend/api/` | HTTP routing, request validation, response formatting | Contain business logic or database calls |
| Service Layer | `backend/services/` | Business logic, orchestration | Make direct HTTP calls or contain route logic |
| Model Layer | `backend/models/` | SQLAlchemy ORM definitions | Contain business logic |
| Schema Layer | `backend/schemas/` | Pydantic data contracts | Contain database logic |
| Agent Layer | `agents/` | ADK agent definitions and prompts | Contain direct DB access or HTTP clients |
| Tool Layer | `mcp/` | MCP tool implementations | Contain agent-specific logic |
| Frontend | `frontend/` | UI rendering and user interaction | Call databases directly or contain business rules |

**If code belongs in two layers simultaneously, it needs to be split.**

---

## Rule 5 — Prefer Modular Code

### 5.1 Single Responsibility

Every function, class, and module has exactly one reason to change. If you need to describe what a function does with the word "and," it should be two functions.

### 5.2 Keep Functions Small

Functions should fit on a screen. A function that requires scrolling to read in full is too long. Extract into smaller, named functions.

### 5.3 Keep Modules Independent

Each module must be independently testable without instantiating the full application. If a module cannot be unit-tested in isolation, it is too tightly coupled. Use dependency injection.

### 5.4 No Circular Imports

Python circular imports are a symptom of poor layering. If a circular import appears, the dependency direction needs to be reversed or the shared logic needs to be moved to a lower-level module.

---

## Rule 6 — Never Hardcode Secrets

### 6.1 Zero Tolerance for Secrets in Code

API keys, passwords, tokens, and webhook URLs must never appear in:
- Source code
- Comments
- Configuration files committed to version control
- Log output
- Test fixtures (use environment variables or mock values)

All secrets are loaded from environment variables via `backend/core/config.py`. If a secret is accidentally committed, treat it as compromised and rotate it immediately.

### 6.2 `.env` Is Never Committed

The `.env` file is in `.gitignore`. `.env.example` with all required keys (no values, descriptive comments) is always current and committed. If a new environment variable is added, `.env.example` must be updated in the same PR.

---

## Rule 7 — Never Invent APIs

### 7.1 Implement the Defined API Contract

All API endpoints are defined in `docs/02_ARCHITECTURE.md` (section 7 — Backend Architecture, API Design table). Do not invent new endpoints, rename existing endpoints, or change HTTP methods without an ADR.

### 7.2 Never Return Undocumented Schemas

Every API response must correspond to a Pydantic schema defined in `backend/schemas/`. Never return raw dictionaries, untyped JSON, or schemas not defined in the schemas module.

---

## Rule 8 — Never Rename Folders

Top-level repository folders (`backend/`, `frontend/`, `agents/`, `mcp/`, `datasets/`, `evaluation/`, `design/`, `docs/`, `scripts/`, `tests/`, `docker/`, `.github/`, `.cursor/`) may not be renamed without:
1. An ADR documenting the reason.
2. Updating all references in all documentation files.
3. Explicit team approval.

---

## Rule 9 — Follow SOLID Principles

Apply SOLID throughout:

- **Single Responsibility:** One reason to change per class and function.
- **Open/Closed:** Extend by addition (new classes, new tools) not by modification. Do not edit an existing agent to add new behavior — add a new agent or extend via inheritance.
- **Liskov Substitution:** Subtypes must be substitutable for their base types. All MCP tools must be substitutable for their base `BaseTool` class.
- **Interface Segregation:** Keep interfaces narrow. A tool that reads should not have a write method. An agent that triages should not have a notification method.
- **Dependency Inversion:** High-level modules (agents, services) depend on abstractions (base classes, interfaces), not concrete implementations. All dependencies are injected, not instantiated inline.

---

## Rule 10 — Write Production-Quality Code Only

### 10.1 No Prototype Code

There is no "I'll clean this up later." Every line of code committed to the repository must be production-quality. This means:
- Fully typed (Python type hints on all signatures, TypeScript strict mode throughout).
- Error handling for all failure paths.
- No `print()` statements as debugging — use the logging module.
- No hardcoded test data in production code paths.

### 10.2 Use Python Type Hints

Every function signature, class attribute, and non-obvious variable must have a type hint. Use `T | None` (Python 3.10+ union syntax) for optional values. Never use `Any` unless absolutely unavoidable; add a comment justifying the exception.

### 10.3 Validate All External Inputs

Every external input — API request bodies, webhook payloads, MCP tool arguments, environment variable values — must be validated before processing. Use Pydantic for Python, TypeScript strict types for the frontend.

### 10.4 Handle Errors Explicitly

No bare `except` clauses. Always catch specific exception types. Every error path must either:
- Return a structured error response to the caller, or
- Log the error with context and raise a more specific exception.

---

## Rule 11 — Explain Major Implementation Decisions

### 11.1 Comments Explain Why, Not What

Do not add comments that restate what the code does. Add comments when:
- The implementation is non-obvious and a future developer might be tempted to "fix" it incorrectly.
- A constraint is being enforced that the code alone cannot convey (e.g., "This must remain append-only — see ADR-001").
- A trade-off was made that the code does not express.

### 11.2 Major Decisions in PR Descriptions

When a PR implements a non-trivial design choice, explain the rationale in the PR description. The PR description is the first place a reviewer looks. Do not make them read the code to understand why a design was chosen.

### 11.3 Prompt Files Are Documented

Every agent system prompt file must have a header comment explaining:
- What the agent's mission is.
- What it must produce.
- What constraints govern its behavior.
- The date the prompt was last modified and the task ID that modified it.

---

## Rule 12 — Agents Use Tools, Not Direct I/O

No agent file in `agents/` may contain:
- Direct database driver calls
- Direct HTTP client calls
- File system reads/writes
- `subprocess` calls
- Any form of direct external I/O

All external interactions go through registered MCP tools in `mcp/`. This is an absolute rule. It enforces auditability: every external action an agent takes is a recorded, inspectable tool call.

---

## Rule 13 — The Guardian Agent Is Always Active

The Guardian Agent validates both the input to the pipeline (prompt injection scan) and the output of the pipeline (PII scan, approval gate, output safety). It must never be bypassed, disabled, or removed from the Coordinator's invocation sequence. Any code that attempts to skip the Guardian Agent is a critical defect.

---

## Rule 14 — Oz AI Never Acts Without Human Approval

No code in any layer may:
- Change a `ResponseAction.approval_status` from `PendingApproval` to `Approved` without a recorded human approval event in the audit trail.
- Dispatch a notification to an external channel for a `ResponseAction` that has not been approved.
- Execute any consequential action (system change, external call with side effects) without a prior human approval record.

This is the most important product constraint. Violating it is a critical defect that must be fixed before any other work continues.

---

## Rule 15 — Testing Is Not Optional

### 15.1 Write Tests for What You Write

Every new function, service method, and MCP tool implementation must be accompanied by at least:
- One happy-path unit test.
- One failure-path unit test.

### 15.2 Integration Tests for Every API Endpoint

Every new API endpoint requires an integration test using `pytest` + `httpx` or FastAPI's `TestClient`.

### 15.3 Agent Tests Use Labeled Scenarios

Every agent must be tested against a minimum of 5 labeled evaluation scenarios (from `evaluation/scenarios/`) as part of its implementation milestone. Tests must assert on specific output fields, not just "the agent returned something."

### 15.4 Never Break Existing Tests

No PR may be merged if it causes previously passing tests to fail. If a test must change because the specification changed, that specification change must be documented in `04_DECISIONS.md`.

---

## Rule 16 — Documentation Currency

- `docs/05_PROGRESS.md` is updated at the end of **every** working session. Never skip it.
- `docs/04_DECISIONS.md` is updated **immediately** when any architectural decision is made.
- `.env.example` is updated **in the same PR** as any new environment variable.
- `03_TASKS.md` is updated with new tasks **before** starting work on them, never retroactively.
- Documentation is updated **in the same PR** as the code it describes. Never in a separate "cleanup" PR.

---

## Rule 17 — Ask When Unclear

If a task description is ambiguous, if the requirements support multiple valid interpretations, or if implementation requires making an assumption not covered by the documentation:

**Stop. Ask. Do not assume silently.**

An incorrect assumption caught before implementation is free. An incorrect assumption caught in code review costs hours. An incorrect assumption that ships costs days.
