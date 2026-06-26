# 03 — Engineering Backlog

**Project Name:** Oz AI
**Version:** 1.0 (MVP)
**Last Updated:** 2026-06-26

> This document is the authoritative engineering backlog for the Oz AI MVP. All work must be tracked here. Pull requests must reference a task ID. Mark tasks complete with `[x]` when merged to `main`. Add new tasks as they are discovered — never remove tasks.

---

## Task ID Convention

`M<milestone>-T<number>` — e.g., `M1-T03` = Milestone 1, Task 3.

---

## Milestone 1 — Foundation

*Goal: Establish the project skeleton with a working repository, documentation, and local infrastructure. Nothing is built until this milestone is complete and reviewed.*

### 1.1 Repository

- [ ] **M1-T01** — Initialize the repository with the complete folder structure defined in `02_ARCHITECTURE.md` (all top-level directories and `__init__.py` / `index.ts` placeholders where needed)
- [ ] **M1-T02** — Create `.gitignore` covering Python artifacts (`__pycache__`, `.venv`, `*.pyc`, `*.db`), Node artifacts (`node_modules`, `dist`), Docker artifacts, OS artifacts (`.DS_Store`, `Thumbs.db`), and environment files (`.env`)
- [ ] **M1-T03** — Create `.env.example` with all required environment variable keys documented with descriptions (no values)
- [ ] **M1-T04** — Initialize `pyproject.toml` with Python project metadata, pinned dependencies (FastAPI, SQLAlchemy, Pydantic, aiosqlite, httpx, pytest, black, ruff), and tool configuration sections
- [ ] **M1-T05** — Initialize `package.json` for the frontend with pinned dependencies: React 19, TypeScript, Tailwind CSS, Vite
- [ ] **M1-T06** — Create `LICENSE` (MIT License)
- [ ] **M1-T07** — Create `README.md` with: project overview, competition context, architecture summary, quickstart guide, environment variable reference, and links to all documentation

### 1.2 Documentation Review

- [ ] **M1-T08** — Final review pass on `01_PROJECT_BRIEF.md` for cross-document consistency
- [ ] **M1-T09** — Final review pass on `02_ARCHITECTURE.md` — verify all agent names, tool names, and endpoint paths are consistent
- [ ] **M1-T10** — Final review pass on `03_TASKS.md` (this document)
- [ ] **M1-T11** — Final review pass on `04_DECISIONS.md`
- [ ] **M1-T12** — Final review pass on `05_PROGRESS.md`
- [ ] **M1-T13** — Final review pass on `06_PRODUCT_REQUIREMENTS.md`
- [ ] **M1-T14** — Final review pass on `07_SUBMISSION_CHECKLIST.md`
- [ ] **M1-T15** — Final review pass on `08_UI_UX_SPECIFICATION.md`
- [ ] **M1-T15a** — Final review pass on `.cursor/rules.md`

### 1.3 Docker

- [ ] **M1-T16** — Create `docker/Dockerfile.backend` for the FastAPI application (Python 3.12 slim base, `pyproject.toml` install, non-root user)
- [ ] **M1-T17** — Create `docker/Dockerfile.frontend` for the React application (Node LTS base, multi-stage: build + Nginx static serve)
- [ ] **M1-T18** — Create `docker-compose.yml` orchestrating: `backend` (port 8000) and `frontend` (port 5173 dev / 80 prod)
- [ ] **M1-T19** — Verify `docker compose up` starts both services with no errors in a clean environment
- [ ] **M1-T20** — Verify the frontend can reach the backend `/api/v1/health` endpoint within the Docker network

### 1.4 Backend Skeleton

- [ ] **M1-T21** — Create `backend/core/config.py` using Pydantic Settings to load all configuration from environment variables
- [ ] **M1-T22** — Create `backend/core/database.py` with async SQLAlchemy engine, session factory, and `get_db` dependency
- [ ] **M1-T23** — Create `backend/main.py` — FastAPI application with lifespan (DB initialization on startup), CORS middleware, and API router registration
- [ ] **M1-T24** — Implement `GET /api/v1/health` returning service name, version, and status
- [ ] **M1-T25** — Implement API key bearer token authentication middleware applied to all `/api/v1/` routes except `/health`

### 1.5 Frontend Skeleton

- [ ] **M1-T26** — Bootstrap the Vite + React + TypeScript project with strict TypeScript configuration
- [ ] **M1-T27** — Configure Tailwind CSS with a design token system (project color palette for severity levels: Critical=red, High=orange, Medium=yellow, Low=blue, Info=gray)
- [ ] **M1-T28** — Set up React Router with placeholder routes for all planned pages
- [ ] **M1-T29** — Create a base `Layout` component with a navigation sidebar and top header
- [ ] **M1-T30** — Create the API client service (`frontend/src/services/api.ts`) as a typed `fetch` wrapper pointing to the backend base URL from environment
- [ ] **M1-T31** — Verify the frontend renders with no TypeScript or Tailwind errors

---

## Milestone 2 — Data Layer

*Goal: Define all database entities and establish the full persistence layer before any business logic is written.*

### 2.1 SQLAlchemy ORM Models

- [ ] **M2-T01** — Define `Incident` model: id, status (enum), severity (enum), raw\_payload (JSON), created\_at, updated\_at, pipeline\_stage
- [ ] **M2-T02** — Define `EvidenceBundle` model: incident\_id (FK), events (JSON), entities (JSON), topology\_context (JSON), evidence\_gaps (JSON), collected\_at
- [ ] **M2-T03** — Define `ThreatIntelReport` model: incident\_id (FK), ioc\_matches (JSON), threat\_actor\_associations (JSON), novelty\_assessment, confidence\_score, created\_at
- [ ] **M2-T04** — Define `MITREMapping` model: incident\_id (FK), technique\_mappings (JSON), kill\_chain\_stage, coverage\_assessment, created\_at
- [ ] **M2-T05** — Define `IncidentTimeline` model: incident\_id (FK), events (JSON), compromise\_timeline (JSON), gap\_analysis (JSON), created\_at
- [ ] **M2-T06** — Define `RiskAssessment` model: incident\_id (FK), severity\_level, blast\_radius (JSON), affected\_assets (JSON), regulatory\_exposure (JSON), risk\_score (int), confidence\_level, created\_at
- [ ] **M2-T07** — Define `ResponsePlan` model: incident\_id (FK), phase\_summary (JSON), created\_at, approval\_status
- [ ] **M2-T08** — Define `ResponseAction` model: plan\_id (FK), action\_description, phase (enum: containment/remediation/recovery), risk\_level (enum), requires\_approval (bool), approval\_status (enum), approved\_by, approved\_at
- [ ] **M2-T09** — Define `IncidentReportBundle` model: incident\_id (FK), technical\_report (text), executive\_summary (text), compliance\_summary (text), created\_at
- [ ] **M2-T10** — Define `GuardianReport` model: incident\_id (FK), injection\_scan\_result (JSON), pii\_scan\_result (JSON), permission\_audit (JSON), approval\_gate\_result (JSON), output\_safety\_result (JSON), created\_at
- [ ] **M2-T11** — Define `AuditEvent` model: id, incident\_id (FK), event\_type, actor (agent name or "human"), action, outcome, metadata (JSON), timestamp — no update/delete permitted

### 2.2 Pydantic Schemas

- [ ] **M2-T12** — Define shared enums: `IncidentStatus`, `Severity`, `IncidentCategory`, `PipelineStage`, `ActionPhase`, `RiskLevel`, `ApprovalStatus`
- [ ] **M2-T13** — Define API schemas for `Incident`: `IncidentCreate`, `IncidentRead`, `IncidentListItem`
- [ ] **M2-T14** — Define internal agent data schemas matching each ORM model: `EvidenceBundleSchema`, `ThreatIntelReportSchema`, `MITREMappingSchema`, `IncidentTimelineSchema`, `RiskAssessmentSchema`, `ResponsePlanSchema`, `ResponseActionSchema`
- [ ] **M2-T15** — Define `AuditEventSchema` for read and write operations
- [ ] **M2-T16** — Define `GuardianReportSchema`

### 2.3 Service Layer

- [ ] **M2-T17** — Implement `IncidentService`: create, get by ID, list with filters, update status/pipeline\_stage
- [ ] **M2-T18** — Implement `AuditService`: append-only write; no update or delete methods defined
- [ ] **M2-T19** — Implement `ReportService`: write and retrieve `IncidentReportBundle`
- [ ] **M2-T20** — Write unit tests for all service methods (mock DB session)

### 2.4 Database Initialization

- [ ] **M2-T21** — Implement database table creation on FastAPI application startup (SQLAlchemy `create_all` for MVP)
- [ ] **M2-T22** — Create `scripts/seed_datasets.py`: seed the local knowledge base (`datasets/threat_intel/`, `datasets/mitre/`) with static reference data required by MCP tools
- [ ] **M2-T23** — Create `scripts/reset_db.py`: drops and recreates all tables for clean development state

---

## Milestone 3 — Ingestion API

*Goal: Build the API layer for receiving alert payloads and exposing incident data.*

### 3.1 Incident API

- [ ] **M3-T01** — Implement `POST /api/v1/incidents`: validate payload, create Incident record, dispatch agent pipeline as BackgroundTask, return incident ID
- [ ] **M3-T02** — Implement `GET /api/v1/incidents`: paginated list with severity and status filters
- [ ] **M3-T03** — Implement `GET /api/v1/incidents/{id}`: full incident record including all agent results
- [ ] **M3-T04** — Implement `GET /api/v1/incidents/{id}/evidence`: evidence bundle
- [ ] **M3-T05** — Implement `GET /api/v1/incidents/{id}/mitre`: MITRE ATT&CK mapping
- [ ] **M3-T06** — Implement `GET /api/v1/incidents/{id}/timeline`: incident timeline
- [ ] **M3-T07** — Implement `GET /api/v1/incidents/{id}/risk`: risk assessment
- [ ] **M3-T08** — Implement `GET /api/v1/incidents/{id}/response`: response plan with all actions
- [ ] **M3-T09** — Implement `GET /api/v1/incidents/{id}/reports`: incident report bundle
- [ ] **M3-T10** — Implement `GET /api/v1/incidents/{id}/audit`: audit trail (ordered by timestamp)
- [ ] **M3-T11** — Implement `GET /api/v1/incidents/{id}/guardian`: Guardian Agent report
- [ ] **M3-T12** — Write pytest integration tests for all incident read endpoints
- [ ] **M3-T13** — Verify FastAPI OpenAPI schema (`/docs`) accurately reflects all endpoint contracts

### 3.2 Alert Simulator

- [ ] **M3-T14** — Create `scripts/simulate_alert.py`: generates a realistic synthetic alert payload and submits it to `POST /api/v1/incidents`
- [ ] **M3-T15** — Build alert template library in `datasets/alerts/`: minimum 10 templates covering all 6 evaluation scenario categories
- [ ] **M3-T16** — Verify submitted alerts appear in the incident list and trigger the agent pipeline (BackgroundTask dispatched, status transitions visible)

---

## Milestone 4 — MCP Tool Layer

*Goal: Implement all MCP tool servers. Every tool must be independently testable before agents are implemented.*

### 4.1 MCP Infrastructure

- [ ] **M4-T01** — Set up the MCP server framework in `mcp/` (server base class, response contract definition, tool registration pattern)
- [ ] **M4-T02** — Define the standard tool response contract: `ToolResult[T]` with `success: bool`, `data: T`, `error: str | None`
- [ ] **M4-T03** — Implement tool permission registry: maps each agent to its allowed tool set; rejects out-of-scope calls

### 4.2 Tool Implementations

- [ ] **M4-T04** — Implement `evidence_collector`: queries `datasets/logs/` for events matching entity, time range, or keyword; returns structured event list
- [ ] **M4-T05** — Implement `knowledge_base_search`: keyword/semantic search over runbook and past incident documents in `datasets/`; returns ranked document excerpts
- [ ] **M4-T06** — Implement `threat_intel_lookup`: looks up IPs, domains, and hashes against `datasets/threat_intel/` IOC database; returns match records with confidence scores
- [ ] **M4-T07** — Implement `mitre_attack_search`: searches the local MITRE ATT&CK knowledge base in `datasets/mitre/` by keyword or technique ID; returns technique records
- [ ] **M4-T08** — Implement `system_topology_query`: returns asset records from `datasets/topology/` for given entity names or IPs
- [ ] **M4-T09** — Implement `incident_record_write`: writes a structured agent result to the appropriate ORM model via the service layer
- [ ] **M4-T10** — Implement `audit_log_write`: appends an `AuditEvent` record via `AuditService`
- [ ] **M4-T11** — Implement `pii_scanner`: scans text for PII patterns using regex rules (email, phone, SSN, IP-as-PII, named entity heuristics); returns matched spans and redacted text
- [ ] **M4-T12** — Implement `prompt_injection_detector`: evaluates text against a pattern library of known prompt injection signatures; returns detection result and matched patterns
- [ ] **M4-T13** — Implement `notification_dispatch`: sends a message to configured channel (Slack webhook if configured, console log as fallback); records delivery attempt

### 4.3 Datasets

- [ ] **M4-T14** — Build `datasets/logs/`: minimum 500 synthetic log entries across 6 incident categories, realistic timestamps, multiple source systems
- [ ] **M4-T15** — Build `datasets/threat_intel/`: minimum 100 IOC records (IPs, domains, hashes) with threat actor labels and confidence scores
- [ ] **M4-T16** — Build `datasets/mitre/`: local knowledge base subset covering the 15 ATT&CK techniques most relevant to the evaluation scenario categories
- [ ] **M4-T17** — Build `datasets/topology/`: system topology map for the simulated enterprise environment (minimum 20 assets with relationships and criticality labels)

### 4.4 Tool Testing

- [ ] **M4-T18** — Write unit tests for every MCP tool (test against datasets directly, no ADK runtime required)
- [ ] **M4-T19** — Verify tool permission enforcement: assert that out-of-scope tool calls are rejected with a structured error

---

## Milestone 5 — Agent Implementation

*Goal: Implement all eight ADK agents and the full orchestration pipeline.*

### 5.1 ADK Setup

- [ ] **M5-T01** — Install and configure Google ADK in the Python environment (pin version in `pyproject.toml`)
- [ ] **M5-T02** — Configure ADK to use Gemini as the LLM backend (model name and API key from environment)
- [ ] **M5-T03** — Implement the ADK session factory and define the session state schema for the incident pipeline
- [ ] **M5-T04** — Verify ADK can initialize a minimal `LlmAgent`, call a registered MCP tool, and return a structured result end-to-end

### 5.2 Guardian Agent (implement first — validates all others)

- [ ] **M5-T05** — Implement the Guardian Agent system prompt with explicit instructions for injection detection, PII scanning, permission validation, and approval gate enforcement
- [ ] **M5-T06** — Register `prompt_injection_detector`, `pii_scanner`, and `audit_log_write` as permitted tools
- [ ] **M5-T07** — Implement the ingestion-phase Guardian invocation: validate raw alert payload before Evidence Agent processing
- [ ] **M5-T08** — Implement the pipeline-completion Guardian invocation: validate all accumulated agent outputs
- [ ] **M5-T09** — Implement the `GuardianReport` output parser and database write
- [ ] **M5-T10** — Write unit tests for the Guardian Agent against: 5 clean payloads, 5 injection attempts, 5 PII-containing outputs

### 5.3 Evidence Agent

- [ ] **M5-T11** — Implement the Evidence Agent system prompt with entity extraction, log correlation, gap documentation, and **timeline generation** requirements
- [ ] **M5-T12** — Register `evidence_collector`, `system_topology_query`, `incident_record_write`, `audit_log_write` as permitted tools
- [ ] **M5-T13** — Implement output parsing for `EvidenceBundle` and `IncidentTimeline`; write both records to the database
- [ ] **M5-T14** — Write unit tests against 5 synthetic alert payloads (verify entity extraction, evidence gaps, and timeline ordering)

### 5.4 Threat Intelligence Agent

- [ ] **M5-T15** — Implement the Threat Intelligence Agent system prompt with IOC lookup, attribution, and confidence scoring requirements
- [ ] **M5-T16** — Register `threat_intel_lookup`, `knowledge_base_search`, `incident_record_write`, `audit_log_write` as permitted tools
- [ ] **M5-T17** — Implement the `ThreatIntelReport` output parser and database write
- [ ] **M5-T18** — Write unit tests against 5 evidence bundles (2 with known IOC matches, 3 with no matches — verify correct "no attribution" handling)

### 5.5 MITRE Mapping Agent

- [ ] **M5-T19** — Implement the MITRE Mapping Agent system prompt with explicit ATT&CK technique mapping, evidence citation, and confidence scoring requirements
- [ ] **M5-T20** — Register `mitre_attack_search`, `knowledge_base_search`, `incident_record_write`, `audit_log_write` as permitted tools
- [ ] **M5-T21** — Implement the `MITREMapping` output parser and database write
- [ ] **M5-T22** — Write unit tests against 5 evidence + threat intel input combinations; verify technique IDs are valid ATT&CK entries

### 5.5 Risk Assessment Agent

- [ ] **M5-T27** — Implement the Risk Assessment Agent system prompt with severity classification, blast radius analysis, regulatory exposure assessment, and risk scoring requirements
- [ ] **M5-T28** — Register `system_topology_query`, `knowledge_base_search`, `incident_record_write`, `audit_log_write` as permitted tools
- [ ] **M5-T29** — Implement the `RiskAssessment` output parser and database write
- [ ] **M5-T30** — Write unit tests against 5 labeled scenarios (verify severity classification matches ground truth)

### 5.6 Response Planning Agent

- [ ] **M5-T31** — Implement the Response Planning Agent system prompt with playbook search, action prioritization, risk annotation, and human approval flag requirements
- [ ] **M5-T32** — Register `knowledge_base_search`, `incident_record_write`, `audit_log_write` as permitted tools
- [ ] **M5-T33** — Implement the `ResponsePlan` and `ResponseAction` output parser and database write (all actions initialize with `ApprovalStatus.PendingApproval`)
- [ ] **M5-T34** — Write unit tests against 5 incident scenarios; verify all high-risk actions are flagged as requiring approval

### 5.7 Executive Report Agent

- [ ] **M5-T35** — Implement the Executive Report Agent system prompt with separate generation requirements for technical, executive, and compliance report variants
- [ ] **M5-T36** — Register `incident_record_write`, `audit_log_write` as permitted tools
- [ ] **M5-T37** — Implement the `IncidentReportBundle` output parser and database write
- [ ] **M5-T38** — Write unit tests against 3 full incident records; verify technical details do not leak into the executive summary

### 5.8 Coordinator Agent

- [ ] **M5-T39** — Implement the Coordinator Agent that invokes each specialist agent in the defined sequence: Guardian (ingestion) → Evidence → Threat Intel → MITRE → Risk → Response → Executive Report → Guardian (validation)
- [ ] **M5-T40** — Implement `IncidentStatus` and `PipelineStage` update logic at each stage transition
- [ ] **M5-T41** — Implement error routing: on specialist agent failure, log, flag for human review, continue remaining stages where possible
- [ ] **M5-T42** — Wire the Coordinator Agent to the FastAPI `BackgroundTask` dispatcher
- [ ] **M5-T43** — Write an end-to-end integration test: submit a synthetic alert → verify a complete incident record is produced with all agent outputs

---

## Milestone 6 — Approval Workflow

*Goal: Implement the human-in-the-loop approval gate for response plans.*

- [ ] **M6-T01** — Implement `POST /api/v1/incidents/{id}/response/approve`: approve the full response plan; write approval audit event
- [ ] **M6-T02** — Implement `POST /api/v1/incidents/{id}/response/reject`: reject the plan with a required reason; write rejection audit event
- [ ] **M6-T03** — Implement `PATCH /api/v1/incidents/{id}/response/actions/{action_id}`: approve or reject an individual action
- [ ] **M6-T04** — Ensure the Guardian Agent's approval gate validation runs before any `ResponseAction` can transition to `Approved`
- [ ] **M6-T05** — Update `Incident.status` to `AwaitingApproval` when the pipeline completes and `Approved` or `Rejected` based on human decision
- [ ] **M6-T06** — Write integration tests for all approval workflow endpoints

---

## Milestone 7 — Frontend Dashboard

*Goal: Build the full React dashboard.*

### 7.1 Incident Board

- [ ] **M7-T01** — Build `Dashboard` page: metric cards, severity distribution, **Agent Pipeline widget** (Evidence / Threat Intel / MITRE / Risk / Response / Guardian with ✔ ⏳ ○ ✖ states), recent incidents, latest reports
- [ ] **M7-T02** — Implement severity filter and status filter
- [ ] **M7-T03** — Implement periodic polling (every 5 seconds) to reflect agent pipeline progress
- [ ] **M7-T04** — Make incident rows clickable; navigate to Incident Detail

### 7.2 Incident Detail

- [ ] **M7-T05** — Build `IncidentDetail` page with tabs per `08_UI_UX_SPECIFICATION.md`: Overview, Evidence, Timeline, MITRE ATT&CK, Threat Intelligence, Risk Assessment, Response Plan, Guardian Report, Audit Trail
- [ ] **M7-T05a** — Overview tab: AI Confidence, Investigation Duration, Processing Status, Reports quick access, Agent Pipeline mini-widget
- [ ] **M7-T06** — Render evidence bundle: entity list, event count, topology summary, evidence gaps
- [ ] **M7-T07** — Render MITRE mapping: tactic/technique cards with confidence badges and evidence citations
- [ ] **M7-T08** — Render timeline: chronological event list with MITRE technique annotations and gap markers
- [ ] **M7-T09** — Render risk assessment: severity badge, blast radius, affected asset list, risk score, regulatory flags
- [ ] **M7-T10** — Render response plan: prioritized action list with phase, risk level, and approval status per action

### 7.3 Response Approval

- [ ] **M7-T11** — Build the response approval workflow within the Incident Detail page
- [ ] **M7-T12** — Implement "Approve All" and "Reject All" with confirmation modal
- [ ] **M7-T13** — Implement per-action approve/reject with reason input for rejections
- [ ] **M7-T14** — Show approval status and timestamp for each action post-decision

### 7.4 Reports

- [ ] **M7-T15** — Build `Reports` tab: render technical report, executive summary, and compliance summary with separate display areas
- [ ] **M7-T16** — Add export controls: Download PDF, Download Markdown, Copy to Clipboard; include disabled **Share Link** button (future feature) per UI spec

### 7.5 Audit Trail

- [ ] **M7-T17** — Build `AuditTrail` tab: chronological list of all audit events with actor, action, outcome, and timestamp

### 7.6 System Health

- [ ] **M7-T18** — Implement `GET /api/v1/system/status` backend endpoint
- [ ] **M7-T19** — Build `SystemHealth` page showing backend API status and current active incident count

---

## Milestone 8 — Evaluation

*Goal: Build the evaluation harness and run a baseline evaluation pass.*

- [ ] **M8-T01** — Define the evaluation scenario schema: `EvalScenario` with input alert, expected MITRE techniques, expected severity, expected risk score range
- [ ] **M8-T02** — Build the labeled evaluation scenario library: minimum 30 scenarios in `evaluation/scenarios/` across all 6 categories
- [ ] **M8-T03** — Implement the evaluation harness runner (`evaluation/harness/run_eval.py`): submits each scenario, waits for pipeline completion, collects all agent outputs
- [ ] **M8-T04** — Implement MITRE technique mapping precision/recall calculation
- [ ] **M8-T05** — Implement risk severity classification accuracy calculation
- [ ] **M8-T06** — Implement Guardian injection detection precision/recall calculation against synthetic injection test suite
- [ ] **M8-T07** — Implement end-to-end latency measurement (alert submission to pipeline complete)
- [ ] **M8-T08** — Configure ADK Eval for scenario-based pipeline validation
- [ ] **M8-T09** — Run baseline evaluation pass; record results in `05_PROGRESS.md`
- [ ] **M8-T10** — Iterate on agent prompts based on evaluation findings; document changes in `04_DECISIONS.md`

---

## Milestone 9 — Polish and Submission

*Goal: Final quality pass, documentation, and Kaggle submission preparation.*

- [ ] **M9-T01** — Full end-to-end walkthrough: run 5 synthetic incidents through the complete pipeline and verify all UI pages render correctly
- [ ] **M9-T02** — Fix all bugs identified during walkthrough
- [ ] **M9-T03** — Verify `docker compose up` from a clean environment produces a fully functional system
- [ ] **M9-T04** — Complete final `README.md` with: evaluation results, competition context, demo instructions
- [ ] **M9-T05** — Complete all items in `07_SUBMISSION_CHECKLIST.md`
- [ ] **M9-T06** — Prepare the Kaggle submission notebook with: problem statement, architecture walkthrough, agent demonstrations, evaluation results, and conclusion
- [ ] **M9-T07** — Record demonstration screenshots or video for submission
- [ ] **M9-T08** — Final review of all documentation files for accuracy and completeness
- [ ] **M9-T09** — Tag release `v1.0.0` on `main`
- [ ] **M9-T10** — Submit to Kaggle competition
