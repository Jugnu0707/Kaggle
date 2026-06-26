# Contributing to Oz AI

Thank you for your interest in contributing to Oz AI. This document explains the engineering process, standards, and expectations for all contributions.

**Before contributing anything**, read the following documents in full:

1. `docs/01_PROJECT_BRIEF.md` — Project vision, goals, non-goals, and technology stack
2. `docs/02_ARCHITECTURE.md` — System architecture and layer boundaries
3. `docs/03_TASKS.md` — Current engineering backlog
4. `.cursor/rules.md` — Coding rules and engineering standards

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Development Environment](#2-development-environment)
3. [Branch Strategy](#3-branch-strategy)
4. [Commit Convention](#4-commit-convention)
5. [Pull Request Process](#5-pull-request-process)
6. [Code Standards](#6-code-standards)
7. [Testing Requirements](#7-testing-requirements)
8. [Documentation Requirements](#8-documentation-requirements)
9. [Agent and Prompt Development](#9-agent-and-prompt-development)
10. [Questions and Clarifications](#10-questions-and-clarifications)

---

## 1. Getting Started

All contributions must correspond to a task in `docs/03_TASKS.md`. If the work you want to do does not have a task, create one in `03_TASKS.md` first (via PR or direct edit on a task branch) and get it confirmed before starting implementation.

**Never start implementing without a task ID.**

---

## 2. Development Environment

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop
- Git

### Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd oz-ai

# 2. Copy and populate environment variables
cp .env.example .env
# Fill in the required values — especially GEMINI_API_KEY

# 3. Start the full development environment
docker compose up

# 4. In a separate terminal, install Python dev dependencies locally
# (for linting, testing, and IDE support)
pip install -e ".[dev]"

# 5. Install frontend dependencies
cd frontend && npm install
```

### Running Tests

```bash
# Backend unit and integration tests
pytest backend/ agents/ mcp/ tests/ -v

# Frontend TypeScript check
cd frontend && npx tsc --noEmit

# Python formatting check
black --check .

# Python linting
ruff check .
```

---

## 3. Branch Strategy

| Branch Type | Pattern | Base Branch | Merges Into |
|---|---|---|---|
| Feature | `feature/<task-id>-short-description` | `develop` | `develop` |
| Bug fix | `bugfix/<issue-id>-short-description` | `develop` | `develop` |
| Release | `release/<version>` | `develop` | `main` + `develop` |

**Examples:**
- `feature/M5-T11-evidence-agent`
- `bugfix/42-guardian-pii-false-positive`
- `release/1.0.0`

**Rules:**
- `main` is always deployable. Direct commits to `main` are blocked.
- `develop` is the integration branch. All feature and bugfix branches merge here.
- Never commit directly to `main` or `develop` — always go through a PR.
- Keep feature branches short-lived. One branch per task.

---

## 4. Commit Convention

All commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).

**Format:** `<type>(<scope>): <description>`

| Type | When to Use |
|---|---|
| `feat` | New feature, new agent, new API endpoint |
| `fix` | Bug fix |
| `docs` | Documentation-only changes |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `style` | Formatting, linting (no logic changes) |
| `chore` | Build scripts, dependency updates, CI config |

**Examples:**
```
feat(M5-T11): implement evidence agent with log query and topology tools
fix(M4-T11): correct pii scanner regex for SSN pattern
docs(M1-T07): update project brief with revised technology stack
test(M5-T10): add guardian agent unit tests for injection scenarios
```

The commit body should reference the task ID:

```
feat(M5-T11): implement evidence agent with log query and topology tools

Implements the Evidence Agent per the architecture defined in 02_ARCHITECTURE.md.
The agent extracts entities from the alert payload, queries the log store, and
retrieves system topology data for all affected entities.

Resolves M5-T11
```

---

## 5. Pull Request Process

1. **Create a branch** from `develop` using the naming convention above.
2. **Implement the task** following all rules in `.cursor/rules.md`.
3. **Write tests** before considering the task complete.
4. **Update documentation** in the same PR as the code (not separately).
5. **Fill out the PR template** in full. Do not skip sections.
6. **Self-review your PR** before requesting review. Read through every changed file with fresh eyes.
7. **Request review** from the CODEOWNERS for the changed paths.
8. **Address all review comments** before merging.
9. **Merge via squash-merge** into `develop`. No merge commits.
10. **Delete the feature branch** after merging.

### PR Checklist Summary

Before marking a PR "Ready for Review":

- [ ] All task items are implemented
- [ ] Tests are written and passing
- [ ] `black --check .` passes
- [ ] `ruff check .` passes
- [ ] `tsc --noEmit` passes (if frontend changes)
- [ ] `docker compose up` succeeds
- [ ] `03_TASKS.md` is updated
- [ ] `05_PROGRESS.md` is updated
- [ ] `.env.example` is updated (if new env vars were added)
- [ ] PR template is filled out completely

---

## 6. Code Standards

### Python

- Python 3.12+ with strict type hints on all signatures.
- `black` for formatting (line length: 100).
- `ruff` for linting.
- Pydantic v2 for all data models.
- `async/await` throughout — no blocking I/O in async context.
- Google-style docstrings on all public functions and classes.
- No bare `except` clauses.
- No `Any` without an explanatory comment.
- No commented-out code.

### TypeScript / React

- Strict TypeScript mode enabled (`"strict": true`).
- Functional components only.
- Explicit prop interfaces.
- No `any`.

### All Code

- Functions do one thing.
- Meaningful names — never single-letter variables outside mathematical expressions.
- Comments explain **why**, not **what**.
- No debug `print()` or `console.log()` statements in committed code.

---

## 7. Testing Requirements

| Code Type | Minimum Test Requirement |
|---|---|
| Business logic function | 1 happy-path test + 1 failure-path test |
| API endpoint | Integration test with request/response verification |
| MCP tool | Unit test against dataset fixtures |
| Agent | 5 labeled evaluation scenario tests |
| Database model | Unit test for any custom validation or constraint |

**Tests live adjacent to the code they test** (within the same module's `tests/` subdirectory) except for integration and end-to-end tests which live in `tests/`.

---

## 8. Documentation Requirements

Documentation is not optional and is not deferred. The following rules apply:

- Every new API endpoint must be reflected in `02_ARCHITECTURE.md` (API table).
- Every new MCP tool must be reflected in `02_ARCHITECTURE.md` (tool inventory table).
- Every new or changed task must be reflected in `03_TASKS.md`.
- Every significant technical decision must be recorded in `04_DECISIONS.md`.
- Every new environment variable must be added to `.env.example` with a description.
- `05_PROGRESS.md` must be updated at the end of every working session.

**Documentation changes belong in the same PR as the code they describe.**

---

## 9. Agent and Prompt Development

Agents are implemented in `agents/`. Each agent directory contains:

- `agent.py` — ADK agent definition, tool registration, output parsing
- `prompt.txt` (or `prompt.md`) — Versioned system prompt
- `schemas.py` — Pydantic output schemas for this agent
- `tests/` — Agent unit tests with labeled scenarios

**System prompts are code.** They must be:
- Stored in versioned files (not inline strings).
- Reviewed in PRs like any other code change.
- Updated via the same PR process as implementation changes.
- Documented with a header comment explaining mission, output contract, and constraints.

**Adding a new pipeline stage** (a new agent between existing agents, or replacing an existing agent) requires an ADR in `04_DECISIONS.md` before any implementation begins.

---

## 10. Questions and Clarifications

If a task is ambiguous, requirements support multiple valid interpretations, or implementation requires an assumption not covered by the documentation:

**Do not assume. Ask.**

Open an issue with the label `question` and describe the ambiguity clearly. Tag the relevant CODEOWNER. Wait for a response before implementing.

An incorrect assumption caught before implementation is free. One caught in code review costs hours. One that ships costs days.
