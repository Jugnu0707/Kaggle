# Repository Inventory

Generated: 2026-06-27 · Oz AI v0.1.0

---

# Repository Statistics

| Metric | Count |
|--------|-------|
| Total folders | 66 |
| Total files | 679 |
| Python files | 256 |
| TypeScript files (.ts + .tsx) | 43 |
| TypeScript files (.ts only) | 19 |
| TypeScript React files (.tsx) | 24 |
| Markdown files | 191 |
| Pytest tests (collected) | 176 |
| Test files | 50 |
| Database models (SQLAlchemy) | 16 |
| Database tables | 16 |
| API paths | 35 |
| API operations | 39 |
| AI agents | 8 |
| MCP tools | 5 |
| Frontend pages | 10 |
| React components | 10 |
| Layout components | 1 |
| Frontend services | 15 |
| Documentation files (.md) | 191 |
| Lines of code (approx.) | 29,333 |

Exclusions for counts: `node_modules`, `.git`, `__pycache__`, `.venv`, `dist`, `build`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `*.egg-info`.

---

# Folder Tree

```
.cursor/
    └── rules.md
.github/
    ├── ISSUE_TEMPLATE/
    │   ├── BUG_REPORT.md
    │   └── FEATURE_REQUEST.md
    ├── CODE_OF_CONDUCT.md
    ├── CODEOWNERS
    ├── CONTRIBUTING.md
    ├── PULL_REQUEST_TEMPLATE.md
    └── SECURITY.md
agents/
    ├── coordinator/
    │   ├── tests/
    │   │   ├── conftest.py
    │   │   └── test_orchestrator.py
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── models.py
    │   ├── orchestrator.py
    │   ├── prompt.md
    │   └── README.md
    ├── evidence/
    │   ├── tests/
    │   │   ├── conftest.py
    │   │   └── test_service.py
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── models.py
    │   ├── prompt.md
    │   ├── README.md
    │   └── service.py
    ├── executive_report/
    │   ├── tests/
    │   │   ├── conftest.py
    │   │   ├── test_executive_report_service.py
    │   │   ├── test_fallback.py
    │   │   └── test_markdown_generator.py
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── fallback.py
    │   ├── markdown_generator.py
    │   ├── models.py
    │   ├── prompt.md
    │   ├── README.md
    │   ├── schemas.py
    │   └── service.py
    ├── guardian/
    │   ├── tests/
    │   │   ├── conftest.py
    │   │   ├── test_pii_detector.py
    │   │   ├── test_prompt_injection.py
    │   │   ├── test_secret_detector.py
    │   │   └── test_validator.py
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── confidence.py
    │   ├── pii_detector.py
    │   ├── prompt_injection.py
    │   ├── README.md
    │   ├── schemas.py
    │   ├── secret_detector.py
    │   ├── service.py
    │   └── validator.py
    ├── mitre/
    │   ├── tests/
    │   │   └── test_mappings.py
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── mappings.py
    │   ├── models.py
    │   ├── prompt.md
    │   ├── README.md
    │   └── service.py
    ├── response/
    │   ├── tests/
    │   │   ├── conftest.py
    │   │   ├── test_response_fallback.py
    │   │   └── test_response_service.py
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── fallback.py
    │   ├── models.py
    │   ├── prompt.md
    │   ├── README.md
    │   ├── schemas.py
    │   └── service.py
    ├── risk/
    │   ├── tests/
    │   │   ├── conftest.py
    │   │   ├── test_fallback.py
    │   │   └── test_risk_service.py
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── fallback.py
    │   ├── models.py
    │   ├── prompt.md
    │   ├── README.md
    │   ├── schemas.py
    │   └── service.py
    ├── threat_intelligence/
    │   ├── tests/
    │   │   ├── conftest.py
    │   │   ├── test_extractor.py
    │   │   ├── test_reputation_engine.py
    │   │   ├── test_threat_intelligence_service.py
    │   │   └── test_ti_fallback.py
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── extractor.py
    │   ├── fallback.py
    │   ├── ioc_extractor.py
    │   ├── models.py
    │   ├── prompt.md
    │   ├── README.md
    │   ├── reputation_engine.py
    │   ├── schemas.py
    │   └── service.py
    ├── __init__.py
    └── conftest.py
backend/
    ├── app/
    │   ├── ai/
    │   │   ├── __init__.py
    │   │   ├── metrics.py
    │   │   ├── provider.py
    │   │   ├── registry.py
    │   │   ├── runtime.py
    │   │   └── session.py
    │   ├── api/
    │   │   ├── v1/
    │   │   └── __init__.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── adk_runtime.py
    │   │   ├── ai_config.py
    │   │   ├── config.py
    │   │   ├── evidence_runtime.py
    │   │   ├── exceptions.py
    │   │   ├── executive_report_runtime.py
    │   │   ├── guardian_config.py
    │   │   ├── guardian_runtime.py
    │   │   ├── logging.py
    │   │   ├── mcp_runtime.py
    │   │   ├── middleware.py
    │   │   ├── mitre_runtime.py
    │   │   ├── openapi.py
    │   │   ├── response_runtime.py
    │   │   ├── risk_runtime.py
    │   │   ├── state.py
    │   │   └── threat_intelligence_runtime.py
    │   ├── db/
    │   │   ├── __init__.py
    │   │   └── database.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── agent_execution.py
    │   │   ├── audit_log.py
    │   │   ├── base.py
    │   │   ├── enums.py
    │   │   ├── evaluation_metric.py
    │   │   ├── evidence.py
    │   │   ├── executive_report.py
    │   │   ├── guardian_audit.py
    │   │   ├── incident.py
    │   │   ├── investigation.py
    │   │   ├── investigation_replay.py
    │   │   ├── investigation_run.py
    │   │   ├── log_file.py
    │   │   ├── mitre_finding.py
    │   │   ├── response_plan.py
    │   │   ├── risk_assessment.py
    │   │   ├── threat_intelligence_finding.py
    │   │   └── timeline_event.py
    │   ├── repositories/
    │   │   ├── __init__.py
    │   │   ├── agent_execution_repository.py
    │   │   ├── audit_log_repository.py
    │   │   ├── evaluation_metric_repository.py
    │   │   ├── executive_report_repository.py
    │   │   ├── guardian_audit_repository.py
    │   │   ├── incident_repository.py
    │   │   ├── investigation_replay_repository.py
    │   │   ├── investigation_run_repository.py
    │   │   ├── log_repository.py
    │   │   ├── mitre_finding_repository.py
    │   │   ├── response_plan_repository.py
    │   │   ├── risk_assessment_repository.py
    │   │   ├── threat_intelligence_finding_repository.py
    │   │   └── timeline_event_repository.py
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   ├── ai_health.py
    │   │   ├── ai_test.py
    │   │   ├── audit_log.py
    │   │   ├── dashboard.py
    │   │   ├── enums.py
    │   │   ├── evaluation.py
    │   │   ├── evidence.py
    │   │   ├── evidence_agent.py
    │   │   ├── executive_report_agent.py
    │   │   ├── guardian_agent.py
    │   │   ├── incident.py
    │   │   ├── investigation.py
    │   │   ├── investigation_replay.py
    │   │   ├── log_file.py
    │   │   ├── mitre_agent.py
    │   │   ├── orchestration.py
    │   │   ├── response.py
    │   │   ├── response_agent.py
    │   │   ├── risk_agent.py
    │   │   └── threat_intelligence_agent.py
    │   ├── services/
    │   │   ├── timeline/
    │   │   ├── __init__.py
    │   │   ├── ai_test_service.py
    │   │   ├── dashboard_service.py
    │   │   ├── evaluation_service.py
    │   │   ├── evidence_agent_service.py
    │   │   ├── executive_report_agent_service.py
    │   │   ├── gemini_service.py
    │   │   ├── guardian_agent_service.py
    │   │   ├── incident_service.py
    │   │   ├── investigation_replay_service.py
    │   │   ├── investigation_workflow_service.py
    │   │   ├── log_service.py
    │   │   ├── mitre_agent_service.py
    │   │   ├── orchestration_guardian.py
    │   │   ├── orchestration_service.py
    │   │   ├── replay_builder.py
    │   │   ├── response_agent_service.py
    │   │   ├── risk_agent_service.py
    │   │   ├── threat_intelligence_agent_service.py
    │   │   └── timeline_service.py
    │   ├── utils/
    │   │   ├── __init__.py
    │   │   ├── file_validation.py
    │   │   └── sanitize.py
    │   ├── __init__.py
    │   └── main.py
    ├── scripts/
    │   ├── demo_agent_outputs.py
    │   ├── demo_catalog.py
    │   └── seed_demo_data.py
    ├── oz_ai.db
    ├── pyproject.toml
    └── uv.lock
CHANGELOG.md
CODE_OF_CONDUCT.md
CONTRIBUTING.md
datasets/
design/
    ├── DATA_FLOW.md
    ├── SEQUENCE_DIAGRAM.md
    ├── SYSTEM_FLOW.md
    ├── THREAT_MODEL.md
    └── UI_WIREFRAMES.md
docker/
    ├── Dockerfile.backend
    └── Dockerfile.frontend
docker-compose.yml
docs/
    ├── architecture/
    │   ├── agent-workflow.md
    │   ├── architecture.png
    │   ├── database-er.md
    │   ├── investigation-sequence.md
    │   ├── mcp-interaction.md
    │   ├── README.md
    │   └── system-architecture.md
    ├── demo/
    │   ├── dashboard.png
    │   ├── demo_flow.md
    │   ├── demo_script.md
    │   ├── evaluation-dashboard.png
    │   ├── evidence.png
    │   ├── executive-report.png
    │   ├── faq.md
    │   ├── guardian.png
    │   ├── incident-details.png
    │   ├── investigation-runner.png
    │   ├── mitre.png
    │   ├── narration.md
    │   ├── README.md
    │   ├── recording_checklist.md
    │   ├── response-plan.png
    │   ├── risk-assessment.png
    │   ├── storyboard.md
    │   ├── threat-intelligence.png
    │   └── timeline.png
    ├── diagrams/
    │   ├── agent_sequence.md
    │   ├── database_er.md
    │   ├── investigation_flow.md
    │   ├── mcp_flow.md
    │   ├── README.md
    │   └── system_architecture.md
    ├── kaggle/
    │   ├── ai_agents.md
    │   ├── architecture.md
    │   ├── evaluation.md
    │   ├── final_checklist.md
    │   ├── future_work.md
    │   ├── implementation.md
    │   ├── limitations.md
    │   ├── problem_statement.md
    │   ├── solution.md
    │   └── submission_notes.md
    ├── screenshots/
    │   ├── dashboard.png
    │   ├── evaluation-dashboard.png
    │   ├── evidence.png
    │   ├── executive-report.png
    │   ├── guardian.png
    │   ├── incident-details.png
    │   ├── investigation-runner.png
    │   ├── mitre.png
    │   ├── response-plan.png
    │   ├── risk-assessment.png
    │   ├── threat-intelligence.png
    │   └── timeline.png
    ├── submission/
    │   ├── ARCHITECTURE.md
    │   ├── DEMO_GUIDE.md
    │   ├── FINAL_WRITEUP.md
    │   ├── JUDGE_NOTES.md
    │   ├── README.md
    │   ├── REPOSITORY_GUIDE.md
    │   └── VIDEO_GUIDE.md
    ├── 01_PROJECT_BRIEF.md
    ├── 02_ARCHITECTURE.md
    ├── 03_TASKS.md
    ├── 04_DECISIONS.md
    ├── 05_PROGRESS.md
    ├── 06_PRODUCT_REQUIREMENTS.md
    ├── 07_SUBMISSION_CHECKLIST.md
    ├── 08_MILESTONES.md
    ├── 08_UI_UX_SPECIFICATION.md
    ├── architecture.png
    ├── COMPETITION_ALIGNMENT.md
    ├── COMPETITION_SCORECARD.md
    ├── FINAL_ACCEPTANCE_CHECKLIST.md
    ├── FINAL_READINESS_REPORT.md
    ├── repository_inventory.md
    ├── REPOSITORY_READINESS_REPORT.md
    ├── SPRINT3_COMPLETION_REPORT.md
    ├── SPRINT3_PERFORMANCE_REPORT.md
    └── SUBMISSION_VERIFICATION_REPORT.md
evaluation/
    ├── results/
    │   └── (204 evaluation report artifacts (*.json, *.md))
    ├── tests/
    │   ├── __init__.py
    │   ├── test_metrics.py
    │   └── test_report_generator.py
    ├── __init__.py
    ├── benchmark.py
    ├── datasets.py
    ├── engine.py
    ├── metrics.py
    ├── README.md
    ├── report_generator.py
    └── scorer.py
frontend/
    ├── src/
    │   ├── assets/
    │   ├── components/
    │   │   ├── BackendUnavailableBanner.tsx
    │   │   ├── DataTable.tsx
    │   │   ├── ErrorBoundary.tsx
    │   │   ├── FileUpload.tsx
    │   │   ├── GlobalLoadingIndicator.tsx
    │   │   ├── Navbar.tsx
    │   │   ├── Sidebar.tsx
    │   │   ├── TimelineTab.tsx
    │   │   ├── ToastContainer.tsx
    │   │   └── ui.tsx
    │   ├── context/
    │   │   └── AppContext.tsx
    │   ├── hooks/
    │   ├── layouts/
    │   │   └── DashboardLayout.tsx
    │   ├── pages/
    │   │   ├── DashboardPage.tsx
    │   │   ├── EvaluationPage.tsx
    │   │   ├── IncidentDetailPage.tsx
    │   │   ├── IncidentsPage.tsx
    │   │   ├── InvestigationReplayPage.tsx
    │   │   ├── InvestigationRunnerPage.tsx
    │   │   ├── LogUploadPage.tsx
    │   │   ├── NotFoundPage.tsx
    │   │   ├── ReportsPage.tsx
    │   │   └── SettingsPage.tsx
    │   ├── services/
    │   │   ├── apiClient.ts
    │   │   ├── dashboardService.ts
    │   │   ├── evaluationService.ts
    │   │   ├── executiveReportService.ts
    │   │   ├── guardianService.ts
    │   │   ├── incidentService.ts
    │   │   ├── investigationReplayService.ts
    │   │   ├── investigationService.ts
    │   │   ├── logService.ts
    │   │   ├── mitreService.ts
    │   │   ├── responseService.ts
    │   │   ├── riskService.ts
    │   │   ├── systemService.ts
    │   │   ├── threatIntelligenceService.ts
    │   │   └── timelineService.ts
    │   ├── types/
    │   │   └── api.ts
    │   ├── utils/
    │   │   └── format.ts
    │   ├── App.tsx
    │   ├── index.css
    │   ├── main.tsx
    │   └── vite-env.d.ts
    ├── index.html
    ├── package-lock.json
    ├── package.json
    ├── postcss.config.js
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── tsconfig.node.json
    └── vite.config.ts
LICENSE
mcp/
    ├── tools/
    │   ├── __init__.py
    │   ├── health.py
    │   ├── incidents.py
    │   ├── logs.py
    │   └── system.py
    ├── __init__.py
    ├── registry.py
    └── server.py
pytest.ini
README.md
ROADMAP.md
scripts/
    ├── dev-backend.sh
    ├── dev-frontend.sh
    ├── dev.sh
    ├── generate_assets.py
    ├── generate_repo_stats.py
    ├── reset_demo.py
    └── sprint3_performance_benchmark.py
SECURITY.md
storage/
    └── uploads/
        └── (30 uploaded log files (*.log))
tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_adk_startup.py
    ├── test_ai_health.py
    ├── test_ai_runtime.py
    ├── test_ai_test.py
    ├── test_api_inventory.py
    ├── test_coordinator.py
    ├── test_dashboard.py
    ├── test_database.py
    ├── test_evaluation.py
    ├── test_evidence_agent.py
    ├── test_executive_report_agent.py
    ├── test_guardian_agent.py
    ├── test_health.py
    ├── test_incidents.py
    ├── test_investigation_replay.py
    ├── test_investigation_workflow.py
    ├── test_logs.py
    ├── test_mcp_api.py
    ├── test_mcp_registry.py
    ├── test_mcp_server.py
    ├── test_mitre_agent.py
    ├── test_orchestration.py
    ├── test_reliability.py
    ├── test_response_agent.py
    ├── test_risk_agent.py
    ├── test_sprint3_e2e_integration.py
    ├── test_threat_intelligence_agent.py
    └── test_timeline.py
```

---

# Architecture Mapping

## `agents/`

- **Purpose:** Google ADK specialist agent implementations (coordinator, evidence, threat intel, MITRE, risk, response, executive report, guardian).
- **Owner:** AI / agent layer
- **Dependencies:** FastAPI services, investigation workflow, ADK runtime
- **Used by:** Backend services, MCP runtime, evaluation engine

## `backend/`

- **Purpose:** FastAPI application: API routes, SQLAlchemy models, services, repositories, AI/MCP runtimes.
- **Owner:** Application core
- **Dependencies:** agents/, mcp/, SQLite
- **Used by:** frontend/, tests/, scripts/, docker/

## `frontend/`

- **Purpose:** React + Vite dashboard for incidents, investigations, logs, reports, evaluation.
- **Owner:** UI layer
- **Dependencies:** backend API (REST)
- **Used by:** End users, demo video

## `mcp/`

- **Purpose:** Model Context Protocol server and operational tools (health, incidents, logs, system).
- **Owner:** MCP integration layer
- **Dependencies:** backend DB session, app settings
- **Used by:** Coordinator, Evidence Agent, AI runtime

## `evaluation/`

- **Purpose:** Agent benchmark datasets, metrics, scoring, and report generation.
- **Owner:** Quality / benchmarking
- **Dependencies:** agents/, backend services
- **Used by:** Evaluation API, Sprint 3 reports

## `docs/`

- **Purpose:** Project documentation, architecture diagrams, Kaggle writeup, submission package.
- **Owner:** Documentation
- **Dependencies:** Repository contents
- **Used by:** Judges, contributors, README

## `docker/`

- **Purpose:** Container build definitions for backend and frontend.
- **Owner:** Deployment
- **Dependencies:** docker-compose.yml
- **Used by:** CI, local Docker runs

## `tests/`

- **Purpose:** Integration and API test suite (pytest).
- **Owner:** Quality assurance
- **Dependencies:** backend app, agents
- **Used by:** CI, local dev

## `scripts/`

- **Purpose:** Dev orchestration, demo reset, asset generation, benchmarks.
- **Owner:** Tooling
- **Dependencies:** backend, frontend
- **Used by:** Developers, demo setup

## `design/`

- **Purpose:** Early-stage system flow, threat model, wireframes.
- **Owner:** Design artifacts
- **Dependencies:** Product requirements
- **Used by:** Architecture docs

## `datasets/`

- **Purpose:** Placeholder for external datasets.
- **Owner:** Data (placeholder)
- **Dependencies:** —
- **Used by:** Evaluation (future)

## `storage/`

- **Purpose:** Uploaded log file storage (`storage/uploads/`).
- **Owner:** Runtime data
- **Dependencies:** Log upload API
- **Used by:** Evidence Agent, timeline parser

## `.github/`

- **Purpose:** GitHub community templates (issues, PR, security).
- **Owner:** Community / OSS
- **Dependencies:** —
- **Used by:** Contributors

---

# Backend Inventory

## Models (`backend/app/models/`)

- `agent_execution.py`
- `audit_log.py`
- `base.py`
- `enums.py`
- `evaluation_metric.py`
- `evidence.py`
- `executive_report.py`
- `guardian_audit.py`
- `incident.py`
- `investigation.py`
- `investigation_replay.py`
- `investigation_run.py`
- `log_file.py`
- `mitre_finding.py`
- `response_plan.py`
- `risk_assessment.py`
- `threat_intelligence_finding.py`
- `timeline_event.py`

## Schemas (`backend/app/schemas/`)

- `ai_health.py`
- `ai_test.py`
- `audit_log.py`
- `dashboard.py`
- `enums.py`
- `evaluation.py`
- `evidence.py`
- `evidence_agent.py`
- `executive_report_agent.py`
- `guardian_agent.py`
- `incident.py`
- `investigation.py`
- `investigation_replay.py`
- `log_file.py`
- `mitre_agent.py`
- `orchestration.py`
- `response.py`
- `response_agent.py`
- `risk_agent.py`
- `threat_intelligence_agent.py`

## Services (`backend/app/services/`)

- `ai_test_service.py`
- `dashboard_service.py`
- `evaluation_service.py`
- `evidence_agent_service.py`
- `executive_report_agent_service.py`
- `gemini_service.py`
- `guardian_agent_service.py`
- `incident_service.py`
- `investigation_replay_service.py`
- `investigation_workflow_service.py`
- `log_service.py`
- `mitre_agent_service.py`
- `orchestration_guardian.py`
- `orchestration_service.py`
- `replay_builder.py`
- `response_agent_service.py`
- `risk_agent_service.py`
- `threat_intelligence_agent_service.py`
- `timeline_service.py`

### Timeline submodule (`backend/app/services/timeline/`)

- `engine.py`
- `models.py`
- `parser.py`
- `schemas.py`

## Repositories (`backend/app/repositories/`)

- `agent_execution_repository.py`
- `audit_log_repository.py`
- `evaluation_metric_repository.py`
- `executive_report_repository.py`
- `guardian_audit_repository.py`
- `incident_repository.py`
- `investigation_replay_repository.py`
- `investigation_run_repository.py`
- `log_repository.py`
- `mitre_finding_repository.py`
- `response_plan_repository.py`
- `risk_assessment_repository.py`
- `threat_intelligence_finding_repository.py`
- `timeline_event_repository.py`

## Routers (`backend/app/api/v1/`)

- `agents.py`
- `ai.py`
- `dashboard.py`
- `evaluation.py`
- `health.py`
- `incidents.py`
- `investigations.py`
- `logs.py`
- `system.py`

---

# Frontend Inventory

## Pages (`frontend/src/pages/`)

- `DashboardPage.tsx`
- `EvaluationPage.tsx`
- `IncidentDetailPage.tsx`
- `IncidentsPage.tsx`
- `InvestigationReplayPage.tsx`
- `InvestigationRunnerPage.tsx`
- `LogUploadPage.tsx`
- `NotFoundPage.tsx`
- `ReportsPage.tsx`
- `SettingsPage.tsx`

## Components (`frontend/src/components/`)

- `BackendUnavailableBanner.tsx`
- `DataTable.tsx`
- `ErrorBoundary.tsx`
- `FileUpload.tsx`
- `GlobalLoadingIndicator.tsx`
- `Navbar.tsx`
- `Sidebar.tsx`
- `TimelineTab.tsx`
- `ToastContainer.tsx`
- `ui.tsx`

## Layouts (`frontend/src/layouts/`)

- `DashboardLayout.tsx`

## Hooks (`frontend/src/hooks/`)

- None (directory exists; no custom hooks defined)

## Contexts (`frontend/src/context/`)

- `AppContext.tsx`

## Services (`frontend/src/services/`)

- `apiClient.ts`
- `dashboardService.ts`
- `evaluationService.ts`
- `executiveReportService.ts`
- `guardianService.ts`
- `incidentService.ts`
- `investigationReplayService.ts`
- `investigationService.ts`
- `logService.ts`
- `mitreService.ts`
- `responseService.ts`
- `riskService.ts`
- `systemService.ts`
- `threatIntelligenceService.ts`
- `timelineService.ts`

---

# AI Inventory

| Agent | Input | Output | Engine | Fallback | API Endpoint |
|-------|-------|--------|--------|----------|--------------|
| Coordinator Agent | OrchestrateRequest (`incident_id`, `log_file_id`) | OrchestrationPlan (workflow stages, validation status) | Rule engine (deterministic orchestrator; no LLM invocation) | None | POST `/api/v1/agents/orchestrate` |
| Evidence Agent | EvidenceCollectRequest (`incident_id`, `log_file_id`) | Evidence package + summary (file type, entries, quality notes) | Rule engine (file parsing and normalization) | None | POST `/api/v1/agents/evidence` |
| Threat Intelligence Agent | ThreatIntelligenceRequest (`incident_id`) | IOC findings with reputation, descriptions, analyst notes | AI-first (Gemini 2.5 Pro JSON) | `fallback.py` offline reputation engine | POST `/api/v1/agents/threat-intelligence` |
| MITRE Mapping Agent | MitreMappingRequest (`incident_id`) | Mapped ATT&CK techniques with confidence and evidence refs | Rule engine (`mappings.py` local rules) | None | POST `/api/v1/agents/mitre` |
| Risk Assessment Agent | RiskAssessmentRequest (`incident_id`) | Structured risk assessment (overall level, factors, rationale) | AI-first (Gemini JSON) | `fallback.py` severity/MITRE rule engine | POST `/api/v1/agents/risk` |
| Response Planning Agent | ResponsePlanRequest (`incident_id`) | Response plan (priority, actions, containment, recovery) | AI-first (Gemini JSON) | `fallback.py` scenario playbooks | POST `/api/v1/agents/response` |
| Executive Report Agent | ExecutiveReportRequest (`incident_id`) | Executive report JSON + Markdown sections | AI-first (Gemini JSON) | `fallback.py` template engine | POST `/api/v1/agents/executive-report` |
| Guardian Agent | GuardianValidateRequest (agent output payload) | Validation status (approved / warning / rejected), masked output | Rule engine (schema, PII, secrets, injection, confidence) | Retry signal to originating agent on rejection | POST `/api/v1/agents/guardian/validate` |

### MCP Tools (`mcp/tools/`)

| Tool | Input | Output | Used by |
|------|-------|--------|---------|
| `health` | None | Application health status | GET-equivalent tool handler |
| `list_incidents` | Pagination + filters | Paginated incident list | Incident repository |
| `incident_details` | incident_id | Single incident record | Incident repository |
| `list_logs` | Pagination | Uploaded log metadata | Log repository |
| `system_info` | None | Version, DB, ADK, MCP status | App settings + runtime state |

---

# API Inventory

### Root

- GET `/` — API metadata

### agents.py

- POST `/api/v1/agents/evidence` — Evidence Agent
- POST `/api/v1/agents/threat-intelligence` — Threat Intelligence Agent
- POST `/api/v1/agents/mitre` — MITRE Mapping Agent
- POST `/api/v1/agents/risk` — Risk Assessment Agent
- POST `/api/v1/agents/response` — Response Planning Agent
- POST `/api/v1/agents/executive-report` — Executive Report Agent
- POST `/api/v1/agents/guardian/validate` — Guardian validation
- POST `/api/v1/agents/orchestrate` — Coordinator orchestration

### ai.py

- GET `/api/v1/ai/health` — AI runtime health
- GET `/api/v1/ai/test` — Gemini connectivity probe

### dashboard.py

- GET `/api/v1/dashboard/stats` — Dashboard aggregate stats

### evaluation.py

- GET `/api/v1/evaluation` — Evaluation overview
- GET `/api/v1/evaluation/{agent_name}` — Per-agent evaluation metrics

### health.py

- GET `/api/v1/health` — Application health check

### incidents.py

- POST `/api/v1/incidents` — Create incident
- GET `/api/v1/incidents` — List incidents
- GET `/api/v1/incidents/{incident_id}` — Get incident
- PUT `/api/v1/incidents/{incident_id}` — Update incident
- DELETE `/api/v1/incidents/{incident_id}` — Delete incident
- GET `/api/v1/incidents/{incident_id}/executive-report` — Get executive report
- GET `/api/v1/incidents/{incident_id}/guardian-audits` — List guardian audits
- GET `/api/v1/incidents/{incident_id}/mitre` — Get MITRE mappings
- GET `/api/v1/incidents/{incident_id}/response` — Get response plan
- GET `/api/v1/incidents/{incident_id}/risk` — Get risk assessment
- GET `/api/v1/incidents/{incident_id}/threat-intelligence` — Get threat intel findings
- GET `/api/v1/incidents/{incident_id}/timeline` — Get incident timeline
- GET `/api/v1/incidents/{incident_id}/timeline/export` — Export timeline

### investigations.py

- POST `/api/v1/investigations/run` — Run full investigation workflow
- GET `/api/v1/investigations/runs/{run_id}` — Get investigation run status
- GET `/api/v1/investigations/{run_id}/explain` — Investigation explainability
- GET `/api/v1/investigations/{run_id}/replay` — Investigation replay data
- GET `/api/v1/investigations/{run_id}/replay/export` — Export investigation replay

### logs.py

- POST `/api/v1/logs/upload` — Upload log file
- GET `/api/v1/logs` — List log files
- GET `/api/v1/logs/{log_id}` — Get log file metadata
- DELETE `/api/v1/logs/{log_id}` — Delete log file

### system.py

- GET `/api/v1/system/mcp` — MCP server status
- GET `/api/v1/system/tables` — List database tables

---

# Database Inventory

| Table | Model | Description |
|-------|-------|-------------|
| `incidents` | `Incident` | Core incident records |
| `investigations` | `Investigation` | Investigation lifecycle per incident |
| `investigation_runs` | `InvestigationRun` | Workflow execution runs |
| `investigation_replays` | `InvestigationReplay` | Replay snapshots for explainability |
| `log_files` | `LogFile` | Uploaded evidence log metadata |
| `evidence` | `Evidence` | Normalized evidence packages |
| `agent_executions` | `AgentExecution` | Per-agent workflow execution records |
| `audit_logs` | `AuditLog` | Entity audit trail |
| `mitre_findings` | `MitreFinding` | MITRE ATT&CK technique mappings |
| `threat_intelligence_findings` | `ThreatIntelligenceFinding` | IOC enrichment results |
| `risk_assessments` | `RiskAssessment` | Risk assessment outputs |
| `response_plans` | `ResponsePlan` | Incident response plans |
| `executive_reports` | `ExecutiveReport` | Executive report JSON + Markdown |
| `guardian_audits` | `GuardianAudit` | Guardian validation audit records |
| `timeline_events` | `TimelineEvent` | Parsed timeline events |
| `evaluation_metrics` | `EvaluationMetric` | Agent evaluation benchmark metrics |

---

# Test Inventory

Total test files: 50

- `agents/coordinator/tests/test_orchestrator.py`
- `agents/evidence/tests/test_service.py`
- `agents/executive_report/tests/test_executive_report_service.py`
- `agents/executive_report/tests/test_fallback.py`
- `agents/executive_report/tests/test_markdown_generator.py`
- `agents/guardian/tests/test_pii_detector.py`
- `agents/guardian/tests/test_prompt_injection.py`
- `agents/guardian/tests/test_secret_detector.py`
- `agents/guardian/tests/test_validator.py`
- `agents/mitre/tests/test_mappings.py`
- `agents/response/tests/test_response_fallback.py`
- `agents/response/tests/test_response_service.py`
- `agents/risk/tests/test_fallback.py`
- `agents/risk/tests/test_risk_service.py`
- `agents/threat_intelligence/tests/test_extractor.py`
- `agents/threat_intelligence/tests/test_reputation_engine.py`
- `agents/threat_intelligence/tests/test_threat_intelligence_service.py`
- `agents/threat_intelligence/tests/test_ti_fallback.py`
- `backend/app/services/timeline/tests/test_engine.py`
- `backend/app/services/timeline/tests/test_parser.py`
- `evaluation/tests/test_metrics.py`
- `evaluation/tests/test_report_generator.py`
- `tests/test_adk_startup.py`
- `tests/test_ai_health.py`
- `tests/test_ai_runtime.py`
- `tests/test_ai_test.py`
- `tests/test_api_inventory.py`
- `tests/test_coordinator.py`
- `tests/test_dashboard.py`
- `tests/test_database.py`
- `tests/test_evaluation.py`
- `tests/test_evidence_agent.py`
- `tests/test_executive_report_agent.py`
- `tests/test_guardian_agent.py`
- `tests/test_health.py`
- `tests/test_incidents.py`
- `tests/test_investigation_replay.py`
- `tests/test_investigation_workflow.py`
- `tests/test_logs.py`
- `tests/test_mcp_api.py`
- `tests/test_mcp_registry.py`
- `tests/test_mcp_server.py`
- `tests/test_mitre_agent.py`
- `tests/test_orchestration.py`
- `tests/test_reliability.py`
- `tests/test_response_agent.py`
- `tests/test_risk_agent.py`
- `tests/test_sprint3_e2e_integration.py`
- `tests/test_threat_intelligence_agent.py`
- `tests/test_timeline.py`

---

# Documentation Inventory

Total markdown documents: 191

## `.cursor/`

- `.cursor/rules.md`

## `.github/CODE_OF_CONDUCT.md/`

- `.github/CODE_OF_CONDUCT.md`

## `.github/CONTRIBUTING.md/`

- `.github/CONTRIBUTING.md`

## `.github/ISSUE_TEMPLATE/`

- `.github/ISSUE_TEMPLATE/BUG_REPORT.md`
- `.github/ISSUE_TEMPLATE/FEATURE_REQUEST.md`

## `.github/PULL_REQUEST_TEMPLATE.md/`

- `.github/PULL_REQUEST_TEMPLATE.md`

## `.github/SECURITY.md/`

- `.github/SECURITY.md`

## `CHANGELOG.md/`

- `CHANGELOG.md`

## `CODE_OF_CONDUCT.md/`

- `CODE_OF_CONDUCT.md`

## `CONTRIBUTING.md/`

- `CONTRIBUTING.md`

## `README.md/`

- `README.md`

## `ROADMAP.md/`

- `ROADMAP.md`

## `SECURITY.md/`

- `SECURITY.md`

## `agents/coordinator/`

- `agents/coordinator/README.md`
- `agents/coordinator/prompt.md`

## `agents/evidence/`

- `agents/evidence/README.md`
- `agents/evidence/prompt.md`

## `agents/executive_report/`

- `agents/executive_report/README.md`
- `agents/executive_report/prompt.md`

## `agents/guardian/`

- `agents/guardian/README.md`

## `agents/mitre/`

- `agents/mitre/README.md`
- `agents/mitre/prompt.md`

## `agents/response/`

- `agents/response/README.md`
- `agents/response/prompt.md`

## `agents/risk/`

- `agents/risk/README.md`
- `agents/risk/prompt.md`

## `agents/threat_intelligence/`

- `agents/threat_intelligence/README.md`
- `agents/threat_intelligence/prompt.md`

## `backend/`

- `backend/app/services/timeline/README.md`

## `design/DATA_FLOW.md/`

- `design/DATA_FLOW.md`

## `design/SEQUENCE_DIAGRAM.md/`

- `design/SEQUENCE_DIAGRAM.md`

## `design/SYSTEM_FLOW.md/`

- `design/SYSTEM_FLOW.md`

## `design/THREAT_MODEL.md/`

- `design/THREAT_MODEL.md`

## `design/UI_WIREFRAMES.md/`

- `design/UI_WIREFRAMES.md`

## `docs/01_PROJECT_BRIEF.md/`

- `docs/01_PROJECT_BRIEF.md`

## `docs/02_ARCHITECTURE.md/`

- `docs/02_ARCHITECTURE.md`

## `docs/03_TASKS.md/`

- `docs/03_TASKS.md`

## `docs/04_DECISIONS.md/`

- `docs/04_DECISIONS.md`

## `docs/05_PROGRESS.md/`

- `docs/05_PROGRESS.md`

## `docs/06_PRODUCT_REQUIREMENTS.md/`

- `docs/06_PRODUCT_REQUIREMENTS.md`

## `docs/07_SUBMISSION_CHECKLIST.md/`

- `docs/07_SUBMISSION_CHECKLIST.md`

## `docs/08_MILESTONES.md/`

- `docs/08_MILESTONES.md`

## `docs/08_UI_UX_SPECIFICATION.md/`

- `docs/08_UI_UX_SPECIFICATION.md`

## `docs/COMPETITION_ALIGNMENT.md/`

- `docs/COMPETITION_ALIGNMENT.md`

## `docs/COMPETITION_SCORECARD.md/`

- `docs/COMPETITION_SCORECARD.md`

## `docs/FINAL_ACCEPTANCE_CHECKLIST.md/`

- `docs/FINAL_ACCEPTANCE_CHECKLIST.md`

## `docs/FINAL_READINESS_REPORT.md/`

- `docs/FINAL_READINESS_REPORT.md`

## `docs/REPOSITORY_READINESS_REPORT.md/`

- `docs/REPOSITORY_READINESS_REPORT.md`

## `docs/SPRINT3_COMPLETION_REPORT.md/`

- `docs/SPRINT3_COMPLETION_REPORT.md`

## `docs/SPRINT3_PERFORMANCE_REPORT.md/`

- `docs/SPRINT3_PERFORMANCE_REPORT.md`

## `docs/SUBMISSION_VERIFICATION_REPORT.md/`

- `docs/SUBMISSION_VERIFICATION_REPORT.md`

## `docs/architecture/`

- `docs/architecture/README.md`
- `docs/architecture/agent-workflow.md`
- `docs/architecture/database-er.md`
- `docs/architecture/investigation-sequence.md`
- `docs/architecture/mcp-interaction.md`
- `docs/architecture/system-architecture.md`

## `docs/demo/`

- `docs/demo/README.md`
- `docs/demo/demo_flow.md`
- `docs/demo/demo_script.md`
- `docs/demo/faq.md`
- `docs/demo/narration.md`
- `docs/demo/recording_checklist.md`
- `docs/demo/storyboard.md`

## `docs/diagrams/`

- `docs/diagrams/README.md`
- `docs/diagrams/agent_sequence.md`
- `docs/diagrams/database_er.md`
- `docs/diagrams/investigation_flow.md`
- `docs/diagrams/mcp_flow.md`
- `docs/diagrams/system_architecture.md`

## `docs/kaggle/`

- `docs/kaggle/ai_agents.md`
- `docs/kaggle/architecture.md`
- `docs/kaggle/evaluation.md`
- `docs/kaggle/final_checklist.md`
- `docs/kaggle/future_work.md`
- `docs/kaggle/implementation.md`
- `docs/kaggle/limitations.md`
- `docs/kaggle/problem_statement.md`
- `docs/kaggle/solution.md`
- `docs/kaggle/submission_notes.md`

## `docs/repository_inventory.md/`

- `docs/repository_inventory.md`

## `docs/submission/`

- `docs/submission/ARCHITECTURE.md`
- `docs/submission/DEMO_GUIDE.md`
- `docs/submission/FINAL_WRITEUP.md`
- `docs/submission/JUDGE_NOTES.md`
- `docs/submission/README.md`
- `docs/submission/REPOSITORY_GUIDE.md`
- `docs/submission/VIDEO_GUIDE.md`

## `evaluation/README.md/`

- `evaluation/README.md`

## `evaluation/results/`

- `evaluation/results/evaluation_report_20260627_022951.md`
- `evaluation/results/evaluation_report_20260627_023031.md`
- `evaluation/results/evaluation_report_20260627_023218.md`
- `evaluation/results/evaluation_report_20260627_023923.md`
- `evaluation/results/evaluation_report_20260627_025100.md`
- `evaluation/results/evaluation_report_20260627_025101.md`
- `evaluation/results/evaluation_report_20260627_025106.md`
- `evaluation/results/evaluation_report_20260627_025113.md`
- `evaluation/results/evaluation_report_20260627_025144.md`
- `evaluation/results/evaluation_report_20260627_025148.md`
- `evaluation/results/evaluation_report_20260627_025149.md`
- `evaluation/results/evaluation_report_20260627_030616.md`
- `evaluation/results/evaluation_report_20260627_031124.md`
- `evaluation/results/evaluation_report_20260627_031752.md`
- `evaluation/results/evaluation_report_20260627_031753.md`
- `evaluation/results/evaluation_report_20260627_031802.md`
- `evaluation/results/evaluation_report_20260627_031803.md`
- `evaluation/results/evaluation_report_20260627_031835.md`
- `evaluation/results/evaluation_report_20260627_031836.md`
- `evaluation/results/evaluation_report_20260627_031840.md`
- `evaluation/results/evaluation_report_20260627_031906.md`
- `evaluation/results/evaluation_report_20260627_031907.md`
- `evaluation/results/evaluation_report_20260627_031954.md`
- `evaluation/results/evaluation_report_20260627_031955.md`
- `evaluation/results/evaluation_report_20260627_032015.md`
- `evaluation/results/evaluation_report_20260627_032016.md`
- `evaluation/results/evaluation_report_20260627_032109.md`
- `evaluation/results/evaluation_report_20260627_032121.md`
- `evaluation/results/evaluation_report_20260627_032122.md`
- `evaluation/results/evaluation_report_20260627_032154.md`
- `evaluation/results/evaluation_report_20260627_032155.md`
- `evaluation/results/evaluation_report_20260627_032253.md`
- `evaluation/results/evaluation_report_20260627_032254.md`
- `evaluation/results/evaluation_report_20260627_032305.md`
- `evaluation/results/evaluation_report_20260627_032641.md`
- `evaluation/results/evaluation_report_20260627_032850.md`
- `evaluation/results/evaluation_report_20260627_032857.md`
- `evaluation/results/evaluation_report_20260627_032858.md`
- `evaluation/results/evaluation_report_20260627_032859.md`
- `evaluation/results/evaluation_report_20260627_033413.md`
- `evaluation/results/evaluation_report_20260627_033414.md`
- `evaluation/results/evaluation_report_20260627_033417.md`
- `evaluation/results/evaluation_report_20260627_033418.md`
- `evaluation/results/evaluation_report_20260627_033419.md`
- `evaluation/results/evaluation_report_20260627_034222.md`
- `evaluation/results/evaluation_report_20260627_034223.md`
- `evaluation/results/evaluation_report_20260627_034224.md`
- `evaluation/results/evaluation_report_20260627_034259.md`
- `evaluation/results/evaluation_report_20260627_034321.md`
- `evaluation/results/evaluation_report_20260627_034322.md`
- `evaluation/results/evaluation_report_20260627_034323.md`
- `evaluation/results/evaluation_report_20260627_034326.md`
- `evaluation/results/evaluation_report_20260627_034343.md`
- `evaluation/results/evaluation_report_20260627_034344.md`
- `evaluation/results/evaluation_report_20260627_034345.md`
- `evaluation/results/evaluation_report_20260627_034349.md`
- `evaluation/results/evaluation_report_20260627_034400.md`
- `evaluation/results/evaluation_report_20260627_034401.md`
- `evaluation/results/evaluation_report_20260627_034402.md`
- `evaluation/results/evaluation_report_20260627_034411.md`
- `evaluation/results/evaluation_report_20260627_034412.md`
- `evaluation/results/evaluation_report_20260627_034413.md`
- `evaluation/results/evaluation_report_20260627_034432.md`
- `evaluation/results/evaluation_report_20260627_034433.md`
- `evaluation/results/evaluation_report_20260627_034434.md`
- `evaluation/results/evaluation_report_20260627_040339.md`
- `evaluation/results/evaluation_report_20260627_041255.md`
- `evaluation/results/evaluation_report_20260627_041313.md`
- `evaluation/results/evaluation_report_20260627_041822.md`
- `evaluation/results/evaluation_report_20260627_041843.md`
- `evaluation/results/evaluation_report_20260627_042257.md`
- `evaluation/results/evaluation_report_20260627_042448.md`
- `evaluation/results/evaluation_report_20260627_042655.md`
- `evaluation/results/evaluation_report_20260627_042804.md`
- `evaluation/results/evaluation_report_20260627_042824.md`
- `evaluation/results/evaluation_report_20260627_042841.md`
- `evaluation/results/evaluation_report_20260627_042858.md`
- `evaluation/results/evaluation_report_20260627_043047.md`
- `evaluation/results/evaluation_report_20260627_043113.md`
- `evaluation/results/evaluation_report_20260627_043206.md`
- `evaluation/results/evaluation_report_20260627_043254.md`
- `evaluation/results/evaluation_report_20260627_043428.md`
- `evaluation/results/evaluation_report_20260627_043514.md`
- `evaluation/results/evaluation_report_20260627_043533.md`
- `evaluation/results/evaluation_report_20260627_043618.md`
- `evaluation/results/evaluation_report_20260627_043752.md`
- `evaluation/results/evaluation_report_20260627_043755.md`
- `evaluation/results/evaluation_report_20260627_043805.md`
- `evaluation/results/evaluation_report_20260627_043834.md`
- `evaluation/results/evaluation_report_20260627_043837.md`
- `evaluation/results/evaluation_report_20260627_043845.md`
- `evaluation/results/evaluation_report_20260627_044008.md`
- `evaluation/results/evaluation_report_20260627_044040.md`
- `evaluation/results/evaluation_report_20260627_044041.md`
- `evaluation/results/evaluation_report_20260627_044328.md`
- `evaluation/results/evaluation_report_20260627_044345.md`
- `evaluation/results/evaluation_report_20260627_045204.md`
- `evaluation/results/evaluation_report_20260627_045319.md`
- `evaluation/results/evaluation_report_20260627_045518.md`
- `evaluation/results/evaluation_report_20260627_045717.md`
- `evaluation/results/evaluation_report_20260627_045923.md`
- `evaluation/results/evaluation_report_20260627_050143.md`

