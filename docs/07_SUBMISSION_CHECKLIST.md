# 07 — Submission Checklist

**Project Name:** Oz AI
**Competition:** Kaggle — AI Agents Intensive Capstone
**Track:** Agents for Business
**Target Submission Date:** TBD
**Version:** 1.0 (MVP)

> This document is the authoritative pre-submission checklist for the Oz AI competition entry. Every item must be verified and checked before submission. No item is optional. This checklist is reviewed during Milestone 9 (Polish and Submission).

---

## How to Use This Checklist

Work through each section from top to bottom. Check each item only when it has been **verified**, not when it is believed to be complete. For each checked item, add the verification date in the format `[x] — YYYY-MM-DD`.

---

## Section 1 — Repository

- [ ] The repository is public (or accessible to evaluators).
- [ ] The repository follows the folder structure defined in `02_ARCHITECTURE.md` exactly.
- [ ] No top-level folders have been renamed or added without an ADR.
- [ ] `.gitignore` covers: Python artifacts, Node artifacts, Docker artifacts, OS artifacts, and `.env` files.
- [ ] `.env` is not present in the repository (confirmed: `git ls-files | grep "^\.env$"` returns nothing).
- [ ] `.env.example` is present, current, and documents every required environment variable with descriptions.
- [ ] `LICENSE` (MIT) is present in the root.
- [ ] `pyproject.toml` is present with all Python dependencies pinned to specific versions.
- [ ] `package.json` is present in `frontend/` with all Node dependencies pinned to specific versions.
- [ ] `docker-compose.yml` is present in the root.

---

## Section 2 — README

- [ ] `README.md` is present in the root.
- [ ] README includes: project name, subtitle, competition context, and track name.
- [ ] README includes a one-paragraph project description that clearly explains what Oz AI does.
- [ ] README includes the full quickstart guide: prerequisites, clone, `.env` setup, `docker compose up`.
- [ ] README includes an architecture summary (can reference `02_ARCHITECTURE.md`).
- [ ] README includes a description of all eight agents with a one-line mission for each.
- [ ] README includes the evaluation results summary (key metrics from Milestone 8).
- [ ] README includes screenshots or a link to the demonstration video.
- [ ] README includes a link to the Kaggle submission notebook.
- [ ] README includes a "Competition Context" section explaining alignment with Kaggle requirements.
- [ ] README compiles with no broken links (verify all internal links point to existing files).

---

## Section 3 — Architecture Documentation

- [ ] `docs/01_PROJECT_BRIEF.md` is complete and current.
- [ ] `docs/02_ARCHITECTURE.md` is complete, consistent with the implemented system, and current.
- [ ] `docs/03_TASKS.md` reflects all completed tasks with checkboxes marked.
- [ ] `docs/04_DECISIONS.md` includes ADRs for all significant architectural decisions made during development.
- [ ] `docs/05_PROGRESS.md` has a journal entry for every working session.
- [ ] `docs/06_PRODUCT_REQUIREMENTS.md` is complete and all acceptance criteria are checked.
- [ ] `docs/07_SUBMISSION_CHECKLIST.md` is complete (this document).
- [ ] `docs/08_UI_UX_SPECIFICATION.md` is complete and reflects the eight-agent pipeline and Dashboard Agent Pipeline widget.
- [ ] All documentation files are internally consistent (agent names, tool names, endpoint paths, folder names match across documents).
- [ ] `design/SYSTEM_FLOW.md` is complete with actual system flow diagrams.
- [ ] `design/DATA_FLOW.md` is complete with actual data flow diagrams.
- [ ] `design/SEQUENCE_DIAGRAM.md` is complete with agent pipeline sequence diagrams.
- [ ] `design/THREAT_MODEL.md` is complete with the platform threat model.
- [ ] `design/UI_WIREFRAMES.md` is complete with UI wireframes or screenshots.

---

## Section 4 — Google ADK Integration

- [ ] Google ADK is installed as a pinned dependency in `pyproject.toml`.
- [ ] All eight agents are implemented as ADK agents in `agents/`.
- [ ] The Coordinator Agent uses ADK's session management for inter-agent state.
- [ ] ADK session state is checkpointed to the database at each pipeline stage.
- [ ] The ADK agent runtime is initialized correctly from environment configuration.
- [ ] The `adk eval` tooling is configured and used in the evaluation harness.
- [ ] ADK version is documented in `04_DECISIONS.md` (ADR-001).
- [ ] The Kaggle submission notebook demonstrates ADK agent invocation with visible output.

---

## Section 5 — MCP Tool Implementation

- [ ] All ten MCP tools listed in `02_ARCHITECTURE.md` are implemented in `mcp/`.
- [ ] Each tool has a dedicated directory under `mcp/`.
- [ ] Every tool follows the standard `ToolResult[T]` response contract.
- [ ] Tool permissions are enforced: each agent can only call its permitted tool set.
- [ ] Every tool has unit tests that run without an ADK runtime.
- [ ] The tool permission registry rejects out-of-scope calls with structured errors.
- [ ] All tools are registered with the ADK agent runtime and callable from agent prompts.

---

## Section 6 — Multi-Agent System

- [ ] All eight agents are implemented and independently tested:
  - [ ] Coordinator Agent
  - [ ] Evidence Agent (includes timeline generation)
  - [ ] Threat Intelligence Agent
  - [ ] MITRE Mapping Agent
  - [ ] Risk Assessment Agent
  - [ ] Response Planning Agent
  - [ ] Executive Report Agent
  - [ ] Guardian Agent
- [ ] Each agent has a versioned system prompt file in its agent directory.
- [ ] Each agent has a unit test suite with at minimum 5 labeled test scenarios.
- [ ] The full agent pipeline completes end-to-end for at least 10 different synthetic incidents.
- [ ] The Coordinator Agent correctly handles specialist agent failure without crashing.
- [ ] The Guardian Agent correctly detects prompt injection on synthetic test cases.
- [ ] The Guardian Agent correctly scans for and flags PII in synthetic output test cases.
- [ ] The human approval gate is enforced: no action can bypass approval.
- [ ] The audit trail captures all agent actions and tool calls.

---

## Section 7 — Evaluation

- [ ] The evaluation scenario library contains at least 30 labeled scenarios in `evaluation/scenarios/`.
- [ ] Scenarios cover all 6 incident categories.
- [ ] Scenarios cover all severity levels (Critical, High, Medium, Low).
- [ ] The evaluation harness runner (`evaluation/harness/run_eval.py`) executes successfully against all 30 scenarios.
- [ ] MITRE technique mapping precision and recall are calculated and documented.
- [ ] Risk severity classification accuracy is calculated and documented.
- [ ] Guardian injection detection precision and recall are calculated and documented.
- [ ] End-to-end pipeline latency is measured and documented (mean, p90).
- [ ] Evaluation results are recorded in `05_PROGRESS.md`.
- [ ] Evaluation results are summarized in `README.md`.
- [ ] Evaluation results are presented in the Kaggle submission notebook.
- [ ] ADK Eval is configured and produces a structured evaluation report.

---

## Section 8 — Security and Safety

- [ ] The Guardian Agent is active for every incident (no bypass code paths exist).
- [ ] Prompt injection detection is applied to every incoming alert payload.
- [ ] PII scanning is applied to every agent output before persistence.
- [ ] The human approval gate is enforced at both the API layer and the Guardian Agent layer.
- [ ] No `ResponseAction` can be marked `Approved` without a recorded audit event.
- [ ] No secrets appear anywhere in the source code (verify with: `git log --all --full-diff -p | grep -i "api_key\|password\|secret\|token"`).
- [ ] `.env` is confirmed absent from the repository (see Section 1).
- [ ] All API endpoints require authentication (bearer token).
- [ ] The audit trail is append-only (no update/delete code paths exist for `AuditEvent`).
- [ ] PII detected by the Guardian Agent is flagged, not silently discarded.
- [ ] The `GuardianReport` is present in the incident record for every completed incident.

---

## Section 9 — Demonstration Video

- [ ] A demonstration video exists (screen recording or presentation).
- [ ] The video demonstrates: submitting an alert, watching the agent pipeline run, reviewing the incident in the dashboard, and approving the response plan.
- [ ] The video demonstrates the MITRE ATT&CK mapping tab with technique cards.
- [ ] The video demonstrates the incident timeline view.
- [ ] The video demonstrates the Guardian Agent report.
- [ ] The video demonstrates at least one rejection of a response action with a reason.
- [ ] The video demonstrates the executive summary report.
- [ ] The video is publicly accessible (YouTube, Google Drive, or Kaggle attachment).
- [ ] The video URL is included in `README.md` and the Kaggle submission notebook.
- [ ] The video is under 10 minutes (respect evaluator time).

---

## Section 10 — Kaggle Submission Notebook (Writeup)

- [ ] The Kaggle submission notebook is created and publicly accessible.
- [ ] The notebook includes: project introduction, business problem statement, and competition alignment.
- [ ] The notebook includes a system architecture overview with the component diagram from `02_ARCHITECTURE.md`.
- [ ] The notebook includes a description of each of the eight agents with their mission.
- [ ] The notebook includes a description of the Guardian Agent's safety mechanisms.
- [ ] The notebook includes the MCP tool layer description.
- [ ] The notebook demonstrates a live or pre-recorded agent pipeline run with visible output.
- [ ] The notebook includes the evaluation methodology and results.
- [ ] The notebook includes a section on lessons learned and engineering decisions.
- [ ] The notebook includes the future roadmap section from `01_PROJECT_BRIEF.md`.
- [ ] The notebook includes a conclusion that connects the solution back to the competition's Agents for Business goals.
- [ ] All code cells in the notebook execute without errors.
- [ ] The notebook is formatted professionally (headings, explanatory prose between cells, consistent style).

---

## Section 11 — Screenshots

- [ ] Screenshot: Incident Board — multiple incidents with different severity levels visible.
- [ ] Screenshot: Incident Detail — Overview tab.
- [ ] Screenshot: Incident Detail — MITRE ATT&CK tab with technique cards.
- [ ] Screenshot: Incident Detail — Timeline tab with annotated events.
- [ ] Screenshot: Incident Detail — Risk Assessment tab.
- [ ] Screenshot: Incident Detail — Response Plan tab with approval controls.
- [ ] Screenshot: Incident Detail — Audit Trail tab.
- [ ] Screenshot: Incident Detail — Guardian report tab.
- [ ] Screenshot: Executive Summary report.
- [ ] All screenshots are high-resolution and legible.
- [ ] Screenshots are included in `README.md` or linked from it.

---

## Section 12 — Deployment Verification

- [ ] `docker compose up` in a completely clean environment (fresh clone, `.env` populated from `.env.example`) produces a running system with zero errors.
- [ ] The backend API is accessible at `http://localhost:8000`.
- [ ] The frontend dashboard is accessible at `http://localhost:5173`.
- [ ] `GET http://localhost:8000/api/v1/health` returns `200 OK`.
- [ ] A synthetic alert submitted via `POST /api/v1/incidents` results in a complete incident record.
- [ ] The full pipeline completes within 90 seconds on the evaluation machine.
- [ ] The database is initialized automatically without manual intervention.

---

## Section 13 — Docker

- [ ] `docker/Dockerfile.backend` builds successfully: `docker build -f docker/Dockerfile.backend .`
- [ ] `docker/Dockerfile.frontend` builds successfully: `docker build -f docker/Dockerfile.frontend .`
- [ ] `docker-compose.yml` is valid: `docker compose config` produces no errors.
- [ ] Both services restart cleanly after `docker compose down && docker compose up`.
- [ ] No hardcoded credentials appear in any Dockerfile or `docker-compose.yml`.
- [ ] Dockerfiles use specific base image tags (not `:latest`).

---

## Section 14 — Demo Dataset

- [ ] `datasets/alerts/` contains at minimum 10 realistic synthetic alert templates.
- [ ] `datasets/logs/` contains at minimum 500 synthetic log entries.
- [ ] `datasets/threat_intel/` contains at minimum 100 IOC records.
- [ ] `datasets/mitre/` contains the local ATT&CK knowledge base subset.
- [ ] `datasets/topology/` contains the simulated enterprise topology.
- [ ] `scripts/seed_datasets.py` runs successfully and populates the knowledge bases.
- [ ] `scripts/simulate_alert.py` runs successfully and creates a new incident.

---

## Section 15 — License

- [ ] `LICENSE` is present in the repository root.
- [ ] The license is MIT.
- [ ] The copyright year and holder name are correct.
- [ ] The license is compatible with all third-party dependencies used.

---

## Section 16 — Environment Example

- [ ] `.env.example` is present in the repository root.
- [ ] Every environment variable used anywhere in the codebase is documented in `.env.example`.
- [ ] Each variable has a descriptive comment explaining its purpose and acceptable values.
- [ ] No actual values (keys, passwords, tokens) appear in `.env.example`.
- [ ] The `.env.example` has been tested: populating it and running `docker compose up` produces a working system.

---

## Section 17 — Testing

- [ ] All unit tests pass: `pytest backend/ agents/ mcp/ tests/ -v`.
- [ ] All TypeScript files compile: `tsc --noEmit` in `frontend/`.
- [ ] All Python files pass formatting: `black --check .`.
- [ ] All Python files pass linting: `ruff check .`.
- [ ] Test coverage is documented (minimum acceptable: 60% on backend services).
- [ ] Integration tests pass for all API endpoints.
- [ ] End-to-end pipeline test passes (alert submission → complete incident record).

---

## Section 18 — GitHub Repository

- [ ] `.github/ISSUE_TEMPLATE/BUG_REPORT.md` is present.
- [ ] `.github/ISSUE_TEMPLATE/FEATURE_REQUEST.md` is present.
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` is present.
- [ ] `.github/CODEOWNERS` is present.
- [ ] `.github/CODE_OF_CONDUCT.md` is present.
- [ ] `.github/CONTRIBUTING.md` is present.
- [ ] `.github/SECURITY.md` is present.
- [ ] `.cursor/rules.md` is present and complete.
- [ ] The repository has a meaningful description and relevant topics set on GitHub.

---

## Section 19 — Future Work

- [ ] The `README.md` includes a "Future Roadmap" section referencing the phases in `01_PROJECT_BRIEF.md`.
- [ ] The Kaggle submission notebook includes a "What's Next" section with at least 3 concrete post-MVP improvements.
- [ ] `04_DECISIONS.md` documents any known technical debt with a recommended resolution path.
- [ ] Known limitations of the MVP are documented honestly in the README and the submission notebook.

---

## Section 20 — Final Review

- [ ] All documentation files have been read in full by at least one person other than the author.
- [ ] All acceptance criteria in `06_PRODUCT_REQUIREMENTS.md` (Section 9) are checked.
- [ ] The system has been demonstrated end-to-end with at least 5 different synthetic incidents immediately prior to submission.
- [ ] No `TODO`, `FIXME`, or `HACK` comments remain in any committed file.
- [ ] No test data, debug prints, or development-only code remains in the production code paths.
- [ ] The Kaggle submission form has been completed with all required metadata.
- [ ] The competition submission deadline has been verified and submission is completed before it.

---

## Submission Sign-Off

| Item | Name | Date |
|---|---|---|
| Technical review completed | | |
| Documentation review completed | | |
| Evaluation results verified | | |
| Demo video approved | | |
| Final submission submitted | | |
