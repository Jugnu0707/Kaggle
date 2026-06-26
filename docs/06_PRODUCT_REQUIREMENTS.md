# 06 — Product Requirements

**Project Name:** Oz AI
**Version:** 1.0 (MVP)
**Date:** 2026-06-26
**Status:** Approved — Pre-Development

> This document defines the product requirements for Oz AI. It bridges the project vision in `01_PROJECT_BRIEF.md` and the technical architecture in `02_ARCHITECTURE.md`. It is the reference for what the product must do and how users must experience it. Implementation decisions that contradict this document require an ADR.

---

## Table of Contents

1. [Product Vision](#1-product-vision)
2. [User Journey](#2-user-journey)
3. [User Stories](#3-user-stories)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [UI Pages](#6-ui-pages)
7. [Success Flow](#7-success-flow)
8. [Failure Flow](#8-failure-flow)
9. [Acceptance Criteria](#9-acceptance-criteria)

---

## 1. Product Vision

Oz AI is the intelligent first responder that every security team deserves but cannot afford to hire. It receives an alert, thinks like a senior security analyst — gathering evidence, consulting threat intelligence, mapping attack patterns to MITRE ATT&CK, reconstructing the timeline, assessing risk, and drafting a response — and presents the human analyst with a complete, structured incident brief in minutes instead of hours.

The product is not an automation that removes humans from the loop. It is a system that puts human engineers in the loop at exactly the right moment: when all the information has been gathered and organized, and a decision needs to be made.

---

## 2. User Journey

### Primary Journey: Incident Response Analyst

```
Alert Generated
      │
      │  An alert fires in the enterprise environment.
      │  It enters Oz AI through the REST API or webhook.
      ▼
Incident Created
      │
      │  The backend creates an incident record and
      │  dispatches the agent pipeline.
      ▼
Agent Pipeline Executes (autonomous)
      │
      ├── Evidence Agent gathers evidence and reconstructs timeline
      ├── Threat Intelligence Agent enriches with IOC data
      ├── MITRE Mapping Agent maps to ATT&CK framework
      ├── Risk Assessment Agent evaluates severity and blast radius
      ├── Response Planning Agent generates action plan
      ├── Executive Report Agent drafts three report variants
      └── Guardian Agent validates safety and approval gates
      │
      ▼
Incident Ready for Review
      │
      │  The analyst is notified. The incident appears
      │  in the dashboard with "Awaiting Review" status.
      ▼
Analyst Reviews the Incident
      │
      │  The analyst opens the incident in the dashboard.
      │  They review: evidence, MITRE mapping, timeline,
      │  risk assessment, and the response plan.
      ▼
Analyst Makes Decisions
      │
      ├── Approves recommended response actions
      ├── Rejects actions with documented reasons
      └── Escalates to senior engineer if needed
      │
      ▼
Incident Resolved
      │
      │  Approved actions are tracked. The incident status
      │  updates to Resolved. The full audit trail and reports
      │  are available for post-incident review.
      ▼
Post-Incident
      │
      │  The CISO reviews the executive summary report.
      │  The audit trail is available for regulatory compliance.
      │  Lessons from the incident inform future playbook updates.
```

---

## 3. User Stories

### Tier 1 Analyst Stories

**US-001** — As a Tier 1 analyst, I want to see all active incidents on a single dashboard so that I can prioritize my work without opening multiple tools.

**US-002** — As a Tier 1 analyst, I want each incident to show its severity, current status, and pipeline progress so that I know at a glance which incidents need my attention.

**US-003** — As a Tier 1 analyst, I want to open an incident and immediately see a plain-language summary of what happened so that I do not need to read raw log data to understand the situation.

**US-004** — As a Tier 1 analyst, I want to see the MITRE ATT&CK techniques identified in the incident so that I can quickly characterize the attack pattern without performing the mapping manually.

**US-005** — As a Tier 1 analyst, I want to see a chronological timeline of the incident's events so that I can understand the progression and scope of the attack.

**US-006** — As a Tier 1 analyst, I want to review a structured, prioritized response plan so that I can approve appropriate actions rather than creating a plan from scratch under pressure.

**US-007** — As a Tier 1 analyst, I want to approve or reject individual response actions with a reason for rejection so that I maintain oversight and accountability for all decisions.

**US-008** — As a Tier 1 analyst, I want to see the confidence level for each agent's finding so that I know when to apply additional scrutiny before approving a recommendation.

### Senior Security Engineer Stories

**US-009** — As a senior security engineer, I want to view the full audit trail of every agent action and tool call so that I can reconstruct the investigation during a post-incident review.

**US-010** — As a senior security engineer, I want to see the Guardian Agent's safety report for each incident so that I can verify that the pipeline operated within safe parameters.

**US-011** — As a senior security engineer, I want to submit a custom alert payload via the REST API so that I can test the system with incident scenarios from our own tooling.

**US-012** — As a senior security engineer, I want to review the evidence bundle, including identified evidence gaps, so that I can decide whether additional investigation is needed before acting on the response plan.

### CISO Stories

**US-013** — As a CISO, I want to view an executive summary for any incident that does not contain sensitive technical details so that I can communicate incident status to leadership without a security briefing.

**US-014** — As a CISO, I want to view a compliance summary that documents the incident timeline, regulatory exposure, and response actions taken so that I have the evidence needed for audit reporting.

**US-015** — As a CISO, I want to see aggregate incident metrics (volume, severity distribution, average MTTR) so that I can report on the organization's security posture.

### Platform Administrator Stories

**US-016** — As a platform administrator, I want all configuration to be environment-variable-driven so that I can deploy the system in different environments without modifying source code.

**US-017** — As a platform administrator, I want the full system to start with a single `docker compose up` command so that deployment is predictable and reproducible.

---

## 4. Functional Requirements

### FR-01 — Alert Ingestion

| ID | Requirement |
|---|---|
| FR-01.1 | The system must accept alert payloads via `POST /api/v1/incidents` as JSON. |
| FR-01.2 | The system must validate all incoming payloads against the `IncidentCreate` Pydantic schema before processing. |
| FR-01.3 | The system must reject malformed payloads with a structured `422 Unprocessable Entity` response. |
| FR-01.4 | The system must pass all incoming payloads through the Guardian Agent's prompt injection detector before agent processing begins. |
| FR-01.5 | The system must return the new incident ID to the caller immediately, before the agent pipeline completes. |

### FR-02 — Agent Pipeline

| ID | Requirement |
|---|---|
| FR-02.1 | The Coordinator Agent must invoke all specialist agents in the defined sequence for every incident. |
| FR-02.2 | Each specialist agent must write its structured output to the database via the `incident_record_write` MCP tool. |
| FR-02.3 | Each specialist agent must append at least one audit event via the `audit_log_write` MCP tool. |
| FR-02.4 | If a specialist agent returns an error result, the Coordinator must log the failure, flag the incident for human review, and continue with remaining stages where possible. |
| FR-02.5 | The incident status must update at each pipeline stage transition and be immediately queryable via the API. |
| FR-02.6 | The Guardian Agent must validate the complete set of agent outputs before the incident is marked `AwaitingReview`. |

### FR-03 — Evidence Collection

| ID | Requirement |
|---|---|
| FR-03.1 | The Evidence Agent must extract all named entities (IPs, hostnames, users, services) from the alert payload. |
| FR-03.2 | The Evidence Agent must query the log store for correlated events using each extracted entity. |
| FR-03.3 | The Evidence Agent must retrieve system topology data for all affected entities. |
| FR-03.4 | The Evidence Agent must document evidence gaps explicitly in its output. |

### FR-04 — MITRE ATT&CK Mapping

| ID | Requirement |
|---|---|
| FR-04.1 | The MITRE Mapping Agent must produce a `MITREMapping` with at least one Tactic-Technique pair per incident where sufficient evidence exists. |
| FR-04.2 | Each technique mapping must include: ATT&CK Technique ID, Technique name, Tactic, confidence score (0.0–1.0), and supporting evidence citation. |
| FR-04.3 | Technique mappings with confidence below 0.5 must be labeled as "Low Confidence" in the output and in the UI. |
| FR-04.4 | If no technique mapping can be determined with reasonable confidence, the agent must return an explicit "insufficient evidence" result rather than a low-quality guess. |

### FR-05 — Risk Assessment

| ID | Requirement |
|---|---|
| FR-05.1 | The Risk Assessment Agent must produce a severity classification: Critical, High, Medium, Low, or Informational. |
| FR-05.2 | The risk assessment must include a numerical risk score (0–100). |
| FR-05.3 | When asset criticality data is unavailable, the agent must assume maximum criticality and document this assumption. |
| FR-05.4 | The risk assessment must identify applicable regulatory frameworks (SOC 2, HIPAA, GDPR, etc.) based on the affected data types. |

### FR-06 — Response Planning

| ID | Requirement |
|---|---|
| FR-06.1 | The Response Planning Agent must produce a `ResponsePlan` with at least one action per phase (containment, remediation, recovery) for every incident. |
| FR-06.2 | Every `ResponseAction` must initialize with `approval_status: PendingApproval`. |
| FR-06.3 | Every action with risk level High or Critical must be flagged `requires_approval: true`. |
| FR-06.4 | Every action must include: description, phase, risk level, estimated effort, affected systems, prerequisites, and rollback steps. |

### FR-07 — Human-in-the-Loop Approval

| ID | Requirement |
|---|---|
| FR-07.1 | The system must provide `POST /api/v1/incidents/{id}/response/approve` and `POST /api/v1/incidents/{id}/response/reject` endpoints. |
| FR-07.2 | Approval decisions must be recorded as audit events with the approver identity and timestamp. |
| FR-07.3 | No `ResponseAction` may transition to `Approved` without a corresponding audit event. The Guardian Agent enforces this. |
| FR-07.4 | A rejection must require a reason string (minimum 10 characters). |

### FR-08 — Reporting

| ID | Requirement |
|---|---|
| FR-08.1 | The Executive Report Agent must produce three reports for every incident: Technical Report, Executive Summary, and Compliance Summary. |
| FR-08.2 | The Executive Summary must not contain: raw log data, specific vulnerability identifiers, internal IP addresses, or technical jargon beyond the minimum necessary. |
| FR-08.3 | All three reports must be retrievable via `GET /api/v1/incidents/{id}/reports`. |

### FR-09 — Guardian Safety

| ID | Requirement |
|---|---|
| FR-09.1 | The Guardian Agent must scan all incoming alert payloads for prompt injection patterns. |
| FR-09.2 | Detected injection attempts must be logged to the audit trail and the payload must be quarantined (not processed by specialist agents). |
| FR-09.3 | The Guardian Agent must scan all agent outputs for PII before they are persisted. |
| FR-09.4 | Detected PII must be flagged in the `GuardianReport` and the incident must be marked for human review. |
| FR-09.5 | The Guardian Agent must verify the human approval gate is intact before the incident is marked `ReadyForReview`. |

### FR-10 — Audit Trail

| ID | Requirement |
|---|---|
| FR-10.1 | Every agent action, tool call, and human decision must produce at least one `AuditEvent` record. |
| FR-10.2 | Audit events must be append-only. No update or delete operations are permitted. |
| FR-10.3 | The full audit trail for an incident must be retrievable via `GET /api/v1/incidents/{id}/audit`. |
| FR-10.4 | Each audit event must include: timestamp, actor (agent name or "human"), action type, outcome, and relevant metadata. |

---

## 5. Non-Functional Requirements

### NFR-01 — Performance

| ID | Requirement |
|---|---|
| NFR-01.1 | The full agent pipeline (alert submission to incident `AwaitingReview`) must complete within 90 seconds for a standard incident payload. |
| NFR-01.2 | API read endpoints (`GET /incidents`, `GET /incidents/{id}`, etc.) must respond within 500ms under normal load. |
| NFR-01.3 | The frontend incident board must refresh within 5 seconds of the backend status change. |

### NFR-02 — Reliability

| ID | Requirement |
|---|---|
| NFR-02.1 | A specialist agent failure must not crash the Coordinator Agent or the backend API. |
| NFR-02.2 | Failed pipeline stages must be surfaced to the frontend with a clear status indicator. |
| NFR-02.3 | The system must remain operational if any single specialist agent returns an error for 100% of incidents in a session. |

### NFR-03 — Security

| ID | Requirement |
|---|---|
| NFR-03.1 | All API endpoints except `/health` must require a valid bearer token. |
| NFR-03.2 | Secrets must never appear in logs, responses, or source code. |
| NFR-03.3 | The audit trail must be append-only and cannot be modified by any application code path. |
| NFR-03.4 | All external inputs must be validated with Pydantic before processing. |

### NFR-04 — Deployability

| ID | Requirement |
|---|---|
| NFR-04.1 | The full system must start from `docker compose up` in a clean environment with no external dependencies beyond Docker and the contents of `.env`. |
| NFR-04.2 | The system must initialize the database schema automatically on first startup. |
| NFR-04.3 | `.env.example` must document every required environment variable. |

### NFR-05 — Maintainability

| ID | Requirement |
|---|---|
| NFR-05.1 | All Python code must pass `black` and `ruff` checks with the project configuration. |
| NFR-05.2 | All TypeScript code must compile with `tsc --noEmit` with strict mode enabled. |
| NFR-05.3 | All new code must have a corresponding test. Test coverage must not decrease with any PR. |
| NFR-05.4 | All agent system prompts must be stored in versioned files, not inline strings. |

### NFR-06 — Usability

| ID | Requirement |
|---|---|
| NFR-06.1 | The incident severity must be visually distinct across all severity levels using consistent color coding throughout the UI. |
| NFR-06.2 | The pipeline stage must be visible on the incident list without opening the incident detail view. |
| NFR-06.3 | The response approval workflow must be completable from the incident detail view without navigating to a separate page. |
| NFR-06.4 | The UI must display a meaningful message when no incidents exist rather than an empty screen. |

---

## 6. UI Pages

### Page 1 — Incident Board (`/`)

**Purpose:** Overview of all incidents. Primary working view for Tier 1 analysts.

**Must Display:**
- List of all incidents, newest first.
- Per incident: incident ID, severity badge, status badge, pipeline stage, affected entities summary, created timestamp, MTTR (if resolved).
- Severity filter (Critical, High, Medium, Low, All).
- Status filter (Active, Awaiting Review, Resolved, Rejected, All).
- Count of incidents in each severity category.
- Auto-refresh to show pipeline progress without manual page reload.

**Empty State:** "No incidents found. The system is ready to receive alerts."

---

### Page 2 — Incident Detail (`/incidents/{id}`)

**Purpose:** Full analysis of a single incident. Primary investigation view.

**Tabs:**
1. **Overview** — Incident metadata, severity, status, pipeline stage summary, quick-action buttons.
2. **Evidence** — Entity list, correlated log events, topology context, evidence gaps.
3. **Threat Intelligence** — IOC matches, threat actor associations, novelty assessment.
4. **MITRE ATT&CK** — Tactic/technique cards with confidence scores and evidence citations.
5. **Timeline** — Chronological event list with MITRE annotations, gap markers, compromise timeline.
6. **Risk Assessment** — Severity classification, risk score, blast radius, affected assets, regulatory exposure.
7. **Response Plan** — Prioritized action list with phase, risk level, approval status, and approval controls.
8. **Reports** — Technical report, executive summary, and compliance summary with copy/export controls.
9. **Audit Trail** — Full chronological list of all audit events.
10. **Guardian** — Guardian Agent report: injection scan, PII scan, permission audit, approval gate status.

---

### Page 3 — Reports (`/reports`)

**Purpose:** Aggregate incident reporting for CISO and management.

**Must Display:**
- Total incident count for the selected time period.
- Incident count by severity.
- Average MTTR for the selected time period.
- Resolution rate (resolved / total).
- Incident list for the time period with links to individual incident details.

---

### Page 4 — System Health (`/health`)

**Purpose:** Platform operational status for administrators.

**Must Display:**
- Backend API status (online / degraded / offline).
- Database connection status.
- Active agent pipeline count.
- Total incidents processed.
- Backend version.

---

## 7. Success Flow

The following describes the ideal, uninterrupted path through the system:

1. An alert fires. The integrating system calls `POST /api/v1/incidents` with a JSON payload.
2. The backend validates the payload, creates an `Incident` record with status `Received`, and returns the incident ID.
3. The Coordinator Agent dispatches the Guardian Agent (ingestion phase). The payload passes the injection scan.
4. The Evidence Agent collects correlated log events, topology data, and reconstructs the incident timeline. Writes `EvidenceBundle` and `IncidentTimeline`. Status: `GatheringEvidence`.
5. The Threat Intelligence Agent enriches the evidence with IOC data and threat actor context. Writes `ThreatIntelReport`. Status: `EnrichingIntelligence`.
6. The MITRE Mapping Agent maps observed behaviors to ATT&CK techniques. Writes `MITREMapping`. Status: `MappingTechniques`.
7. The Risk Assessment Agent produces a severity classification and risk score. Writes `RiskAssessment`. Status: `AssessingRisk`.
8. The Response Planning Agent generates a prioritized response plan. Writes `ResponsePlan` + `ResponseAction` records (all `PendingApproval`). Status: `PlanningResponse`.
9. The Executive Report Agent generates Technical Report, Executive Summary, and Compliance Summary. Writes `IncidentReportBundle`. Status: `GeneratingReports`.
10. The Guardian Agent validates all outputs. PII scan passes. Approval gate is confirmed intact. Writes `GuardianReport`.
11. Incident status updates to `AwaitingReview`. A notification is dispatched to the configured channel (if configured).
12. The analyst opens the incident in the dashboard. Reviews all tabs.
13. The analyst approves the containment actions and rejects a remediation action with a documented reason.
14. Approval events are written to the audit trail. Status updates to `Approved`.
15. The CISO opens the Reports page, views the executive summary, and exports the compliance summary.

---

## 8. Failure Flow

The following describes the system's behavior when things go wrong:

### Failure Scenario A — Specialist Agent Error

1. The Evidence Agent fails to connect to the log data source.
2. The Evidence Agent returns a structured error result: `{success: False, error: "Log source unavailable", partial_data: {...}}`.
3. The Coordinator Agent logs the failure to the audit trail: `{actor: "evidence_agent", action: "collect_evidence", outcome: "partial_failure", error: "Log source unavailable"}`.
4. The Coordinator continues the pipeline with the partial evidence bundle.
5. The incident is flagged with a `PartialPipelineWarning` status indicator visible in the UI.
6. When the pipeline completes, the analyst sees the evidence tab with a visible warning: "Evidence collection was incomplete — log source unavailable during analysis. Manual investigation recommended."
7. The analyst reviews the partial analysis and decides whether to approve the response plan or escalate.

### Failure Scenario B — Prompt Injection Detected

1. An alert payload contains text designed to override agent instructions.
2. The Guardian Agent's injection detector identifies the pattern.
3. The payload is quarantined. Specialist agents are not invoked.
4. An `AuditEvent` is written: `{actor: "guardian_agent", action: "injection_scan", outcome: "injection_detected", metadata: {pattern: "...", payload_hash: "..."}}`.
5. The incident status is set to `GuardianViolation`.
6. The incident appears in the dashboard with a red `Guardian: Injection Detected` badge.
7. A platform administrator reviews the incident and either dismisses it (false positive) or escalates for security investigation.

### Failure Scenario C — Human Rejects Response Plan

1. The analyst reviews the response plan and determines that a recommended action poses unacceptable risk.
2. The analyst clicks "Reject" on the action and enters the reason: "Action requires production downtime during business hours — reschedule for maintenance window."
3. A rejection audit event is written.
4. The action status updates to `Rejected`. The rejection reason is displayed in the action card.
5. The analyst approves the remaining actions.
6. The incident status updates to `PartiallyApproved`. The CISO report notes that one action was rejected with the recorded reason.

### Failure Scenario D — Pipeline Does Not Complete

1. The Coordinator Agent times out or encounters an unrecoverable error mid-pipeline.
2. The incident status is set to `PipelineError`.
3. The last completed stage is recorded in the audit trail.
4. The incident appears in the dashboard with a `Pipeline Error` badge.
5. The analyst can view completed stage results and the error details.
6. The administrator reviews logs to diagnose the root cause.

---

## 9. Acceptance Criteria

The Oz AI MVP is accepted when all of the following criteria are met:

### Pipeline Acceptance

- [ ] **AC-01** — A synthetic alert payload submitted via `POST /api/v1/incidents` produces a complete incident record (all agent outputs present in the database) within 90 seconds.
- [ ] **AC-02** — The MITRE Mapping Agent correctly identifies at least one valid ATT&CK technique in 80% of evaluation scenarios.
- [ ] **AC-03** — The Risk Assessment Agent produces a severity classification matching the ground truth label in 75% of labeled evaluation scenarios.
- [ ] **AC-04** — The Guardian Agent detects prompt injection patterns in 90% of synthetic injection test cases.
- [ ] **AC-05** — The Guardian Agent produces zero false positives (injection detected on clean payloads) on the test suite.

### API Acceptance

- [ ] **AC-06** — All API endpoints defined in `02_ARCHITECTURE.md` are implemented and return correct response schemas.
- [ ] **AC-07** — All API endpoints require bearer token authentication (except `/health`).
- [ ] **AC-08** — The FastAPI OpenAPI schema (`/docs`) accurately reflects all implemented endpoints.

### UI Acceptance

- [ ] **AC-09** — The Incident Board displays all active incidents with correct severity badges and pipeline stage indicators.
- [ ] **AC-10** — The Incident Detail page renders all 10 tabs with correct data for a completed incident.
- [ ] **AC-11** — The response approval workflow allows approve/reject per action and approve/reject all.
- [ ] **AC-12** — The executive summary report is visible in the Reports tab without technical details leaking in.

### Safety Acceptance

- [ ] **AC-13** — No `ResponseAction` can be marked `Approved` without a corresponding audit event.
- [ ] **AC-14** — The Guardian Agent report is present for every completed incident.
- [ ] **AC-15** — The audit trail for a complete incident contains at least one event per agent per incident.

### Deployment Acceptance

- [ ] **AC-16** — `docker compose up` in a clean environment starts all services without errors.
- [ ] **AC-17** — All required environment variables are documented in `.env.example`.
- [ ] **AC-18** — The database schema is created automatically on first startup.

### Documentation Acceptance

- [ ] **AC-19** — All seven documentation files are complete and consistent with each other.
- [ ] **AC-20** — `README.md` includes a working quickstart guide that produces a functional system.
- [ ] **AC-21** — `07_SUBMISSION_CHECKLIST.md` is fully completed with no unchecked items.
