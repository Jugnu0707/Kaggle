# Pull Request

## Task Reference

<!-- Every PR must reference a task from 03_TASKS.md. No exceptions. -->

**Task ID:** <!-- e.g., M5-T05 -->
**Task Title:** <!-- e.g., Implement Evidence Agent -->

## PR Type

<!-- Select one -->

- [ ] `feat:` — New feature or agent capability
- [ ] `fix:` — Bug fix
- [ ] `docs:` — Documentation only
- [ ] `refactor:` — Code restructuring (no behavior change)
- [ ] `test:` — Adding or updating tests
- [ ] `style:` — Formatting / linting (no logic change)
- [ ] `chore:` — Build scripts, dependencies, CI config

## Description

<!-- What does this PR do? Explain the "what" and "why" in 2–5 sentences. -->
<!-- If this is a non-obvious implementation choice, explain the rationale here. -->

## Changes Made

<!-- List the specific changes in this PR. -->

- 
- 
- 

## Architecture Compliance

<!-- Verify that this PR complies with the architecture defined in 02_ARCHITECTURE.md. -->

- [ ] The change does not violate any layer boundary (`api/` contains no business logic, agents contain no direct I/O, etc.)
- [ ] The change does not add or remove a pipeline stage without an ADR in `04_DECISIONS.md`
- [ ] No new library has been introduced without an ADR
- [ ] No top-level folder has been renamed
- [ ] All agent-to-external-system interactions go through MCP tools

## Safety and Security

- [ ] No secrets, API keys, or credentials appear anywhere in the changed files
- [ ] All external inputs are validated with Pydantic (backend) or TypeScript strict types (frontend)
- [ ] If this touches the approval workflow: the human approval gate remains intact and cannot be bypassed
- [ ] If this touches agent outputs: the Guardian Agent can still validate the output
- [ ] The audit trail records all relevant actions in this change

## Documentation

- [ ] `docs/03_TASKS.md` is updated — this task's checkbox is marked complete
- [ ] `docs/05_PROGRESS.md` has been updated for this session
- [ ] If a new environment variable was added: `.env.example` has been updated with a description
- [ ] If an ADR was required: it has been added to `docs/04_DECISIONS.md`
- [ ] If this changes API contracts: `docs/02_ARCHITECTURE.md` has been updated

## Testing

- [ ] Unit tests have been written or updated for all new/changed logic
- [ ] All existing tests pass (`pytest` passes locally)
- [ ] If this is an API change: integration tests have been added
- [ ] If this is an agent change: tests cover at minimum 5 labeled evaluation scenarios
- [ ] TypeScript compiles with no errors (`tsc --noEmit`)
- [ ] Python passes formatting and linting (`black --check .` and `ruff check .`)

## Deployment Verification

- [ ] `docker compose up` succeeds after this change
- [ ] No hard-coded environment-specific values have been introduced
- [ ] If a new service dependency was introduced: it is present in `docker-compose.yml`

## Screenshots (if UI change)

<!-- Add screenshots showing the before and after for any UI changes. -->

## Reviewer Notes

<!-- Anything you want to flag for the reviewer: tricky decisions, areas needing extra scrutiny, known edge cases. -->
