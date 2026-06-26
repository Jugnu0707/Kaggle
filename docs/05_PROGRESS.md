# 05 — Project Journal

**Project Name:** Oz AI
**Version:** 1.0 (MVP)

> This document is a running journal of the project's progress. It is updated at the end of every working session. New entries are added at the top (most recent first). Old entries are never edited.

---

## Journal Entry Format

```
---

## YYYY-MM-DD — Day N

**Session Duration:** X hours
**Milestone Focus:** Milestone N — [Name]

### Completed

- Task completed with brief description of outcome.

### In Progress

- Task currently in progress with current state and next action.

### Blocked

- Blocker description, cause, and what is needed to unblock.

### Next Steps

- What will be worked on in the next session.

### Notes

- Decisions made informally during the session.
- Open questions to resolve.
- Observations about the codebase or architecture.

---
```

---

## YYYY-MM-DD — Day 1

**Session Duration:** 4 hours
**Milestone Focus:** Milestone 1 — Foundation (Documentation Phase)

---

### Completed

- **Project scoping complete.** Defined the full project vision, mission, problem statement, user personas, business value, success criteria, and technology stack in `01_PROJECT_BRIEF.md`. The document establishes the single source of truth for what Oz AI is and why it is being built.

- **High-level architecture defined.** Produced `02_ARCHITECTURE.md` covering the five-layer system architecture, full component diagram, all six proposed agents with their responsibilities and data contracts, the MCP tool layer, ADK integration pattern, backend and frontend layer designs, database entity overview, security model, deployment strategy, and evaluation approach. No implementation code was written; the document intentionally defers implementation details to the development phase.

- **Engineering backlog created.** Produced `03_TASKS.md` with a fully organized engineering backlog across 9 milestones and approximately 90 discrete tasks. Each task has a unique ID (`M<n>-T<nn>`) for reference in pull requests and progress tracking.

- **ADR process established.** Produced `04_DECISIONS.md` with a reusable ADR template and the first decision record (ADR-001) documenting the rationale for the full technology stack selection, including alternatives considered, pros, cons, and consequences.

- **Project journal initialized.** Created `05_PROGRESS.md` (this document) to serve as the running project log.

- **Cursor rules defined.** Created `.cursor/rules.md` establishing the AI coding guidelines, engineering principles, and process rules that govern all agent-assisted development in this project.

---

### In Progress

- **Milestone 1 task review (M1-T07 through M1-T12):** All five documentation files and the Cursor rules file have been created. A final review pass is needed to verify cross-document consistency (e.g., technology names, agent names, and task IDs are consistent between `01_PROJECT_BRIEF.md`, `02_ARCHITECTURE.md`, and `03_TASKS.md`).

---

### Blocked

- None. No blockers exist at the end of Day 1. The documentation phase is complete and development can begin.

---

### Next Steps

- **Session 2 (Milestone 1 — Repository):**
  - Initialize the monorepo folder structure as defined in `02_ARCHITECTURE.md` (task M1-T01).
  - Create `.gitignore`, `.env.example`, `pyproject.toml`, and `package.json` (tasks M1-T02 through M1-T05).
  - Create the `README.md` with project overview and quickstart (task M1-T06).
  - Build the FastAPI application skeleton (tasks M1-T18 through M1-T25).
  - Build the Docker Compose configuration (tasks M1-T13 through M1-T17).

- **Priority question for Session 2:** Confirm the Gemini API key is available in the local `.env` before beginning any ADK or agent work. This is a hard dependency for Milestone 5.

---

### Notes

- The agent pipeline is designed as a sequential, synchronous pipeline within an asynchronous Celery task. This simplifies the MVP considerably compared to a fully parallel agent graph. If evaluation reveals that the sequential pipeline is a performance bottleneck (unlikely for the MVP scale), parallelizing Parser + Triage as independent tracks is a logical first optimization.

- The knowledge base used by the `knowledge_base_search` MCP tool must be populated with synthetic runbook content before agent testing can begin (Milestone 4). Plan to create this content in the `evaluation/scenarios/` directory and seed it during tool implementation.

- The decision to use SQLite for the MVP (ADR-001) creates a natural constraint: the system should not be benchmarked for concurrent write throughput. For the competition evaluation, all scenarios will be run sequentially, so this is not a concern. If the evaluator runs parallel scenarios, Redis can be used as an optimistic lock to serialize incident writes.

- The "human-in-the-loop" approval gate in Milestone 6 is a key differentiator from naive agent automation. The documentation and architecture must clearly communicate this design decision in the competition submission — it demonstrates responsible AI deployment practice.

- Open question: Should the `05_PROGRESS.md` journal be auto-committed at the end of each session, or manually committed? Recommend: manually committed with the daily work in the same commit to ensure the journal accurately reflects the day's actual work.

---
