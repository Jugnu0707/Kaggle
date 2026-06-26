# Sequence Diagrams

**Project Name:** Oz AI
**Document Status:** Outline Only — Diagrams Pending Development Phase
**Date:** 2026-06-26

> This document defines the sequence diagrams needed to describe the temporal behavior of the Oz AI system. All diagrams are to be created using Mermaid syntax after implementation is complete. Section headings are the structural contract for which diagrams are required.

---

## Table of Contents

1. [Alert Ingestion Sequence](#1-alert-ingestion-sequence)
2. [Full Agent Pipeline Sequence](#2-full-agent-pipeline-sequence)
3. [Evidence Agent Sequence](#3-evidence-agent-sequence)
4. [Guardian Agent — Ingestion Phase](#4-guardian-agent--ingestion-phase)
5. [Guardian Agent — Validation Phase](#5-guardian-agent--validation-phase)
6. [Human Approval Sequence](#6-human-approval-sequence)
7. [MCP Tool Call Sequence](#7-mcp-tool-call-sequence)
8. [Error Handling Sequences](#8-error-handling-sequences)
9. [Frontend Polling Sequence](#9-frontend-polling-sequence)

---

## 1. Alert Ingestion Sequence

### 1.1 Successful Ingestion

*Pending: A Mermaid sequence diagram covering:*

Participants: `ExternalSystem`, `FastAPI`, `AuthMiddleware`, `IncidentService`, `AuditService`, `Database`, `BackgroundTask`

Sequence:
1. ExternalSystem sends `POST /api/v1/incidents` with bearer token and JSON payload.
2. AuthMiddleware validates bearer token → pass.
3. FastAPI validates payload against `IncidentCreate` Pydantic schema → valid.
4. IncidentService creates `Incident` record with status `Received`.
5. AuditService appends `IngestionReceived` audit event.
6. FastAPI adds `run_agent_pipeline(incident_id)` to BackgroundTask.
7. FastAPI returns `201 Created` with `{incident_id: "..."}`.
8. BackgroundTask invokes Coordinator Agent asynchronously.

### 1.2 Rejected Ingestion — Schema Validation Failure

*Pending: A sequence diagram showing the 422 Unprocessable Entity response path when Pydantic validation fails.*

### 1.3 Rejected Ingestion — Authentication Failure

*Pending: A sequence diagram showing the 401 Unauthorized response path.*

---

## 2. Full Agent Pipeline Sequence

### 2.1 Complete Successful Pipeline

*Pending: A Mermaid sequence diagram covering the full eight-stage agent pipeline execution.*

Participants: `BackgroundTask`, `Coordinator`, `GuardianAgent`, `EvidenceAgent`, `ThreatIntelAgent`, `MITREAgent`, `RiskAgent`, `ResponseAgent`, `ReportAgent`, `Database`

Sequence (high level):
1. BackgroundTask invokes Coordinator with `incident_id`.
2. Coordinator invokes Guardian (ingestion phase) → pass.
3. Coordinator updates status to `GatheringEvidence`.
4. Coordinator invokes Evidence Agent → writes `EvidenceBundle` and `IncidentTimeline` to DB.
5. Coordinator updates status to `EnrichingIntelligence`.
6. Coordinator invokes Threat Intel Agent → writes `ThreatIntelReport` to DB.
7. Coordinator updates status to `MappingTechniques`.
8. Coordinator invokes MITRE Mapping Agent → writes `MITREMapping` to DB.
9. Coordinator updates status to `AssessingRisk`.
10. Coordinator invokes Risk Assessment Agent → writes `RiskAssessment` to DB.
11. Coordinator updates status to `PlanningResponse`.
12. Coordinator invokes Response Planning Agent → writes `ResponsePlan` + `ResponseAction[]` to DB.
13. Coordinator updates status to `GeneratingReports`.
14. Coordinator invokes Executive Report Agent → writes `IncidentReportBundle` to DB.
15. Coordinator invokes Guardian (validation phase) → pass.
16. Coordinator updates status to `AwaitingReview`.
17. Coordinator dispatches notification (if configured).

### 2.2 Pipeline With Specialist Agent Failure

*Pending: A sequence diagram showing the pipeline continuing after the Evidence Agent returns a partial failure result.*

---

## 3. Evidence Agent Sequence

### 3.1 Evidence Collection Sequence

*Pending: A Mermaid sequence diagram covering the Evidence Agent's internal sequence.*

Participants: `Coordinator`, `EvidenceAgent`, `ADKRuntime`, `MCPPermissionRegistry`, `evidence_collector_tool`, `system_topology_query_tool`, `incident_record_write_tool`, `audit_log_write_tool`, `Database`

Sequence:
1. Coordinator invokes EvidenceAgent with session state.
2. EvidenceAgent analyzes alert payload and extracts entity list.
3. EvidenceAgent calls `evidence_collector` tool for each entity.
4. MCPPermissionRegistry validates `evidence_collector` is permitted for EvidenceAgent → pass.
5. `evidence_collector` queries `datasets/logs/` for matching events → returns event list.
6. EvidenceAgent calls `system_topology_query` for each entity.
7. `system_topology_query` returns asset records.
8. EvidenceAgent compiles `EvidenceBundle` and identifies gaps.
9. EvidenceAgent calls `incident_record_write` → writes `EvidenceBundle` to DB.
10. EvidenceAgent calls `audit_log_write` → appends evidence collection audit event.
11. EvidenceAgent returns structured `EvidenceBundle` to Coordinator.

---

## 4. Guardian Agent — Ingestion Phase

### 4.1 Clean Payload Sequence

*Pending: A sequence diagram for a payload that passes the injection scan.*

Participants: `Coordinator`, `GuardianAgent`, `prompt_injection_detector_tool`, `audit_log_write_tool`, `Database`

Sequence:
1. Coordinator invokes Guardian with raw alert payload.
2. Guardian calls `prompt_injection_detector` tool.
3. Tool evaluates payload against injection pattern library → no match.
4. Tool returns `{detected: false, patterns_checked: N}`.
5. Guardian calls `audit_log_write` with `{outcome: "injection_scan_passed"}`.
6. Guardian returns `{ingestion_valid: true}` to Coordinator.
7. Coordinator proceeds to Evidence Agent.

### 4.2 Injection Detected Sequence

*Pending: A sequence diagram for a payload that contains an injection attempt.*

Sequence:
1. Guardian calls `prompt_injection_detector` → returns `{detected: true, matched_pattern: "..."}`.
2. Guardian calls `audit_log_write` with `{outcome: "injection_detected", metadata: {pattern: redacted}}`.
3. Guardian returns `{ingestion_valid: false, reason: "injection_detected"}` to Coordinator.
4. Coordinator does NOT invoke specialist agents.
5. Coordinator updates `Incident.status` to `GuardianViolation`.
6. Coordinator writes `GuardianReport` with injection scan result.

---

## 5. Guardian Agent — Validation Phase

### 5.1 Successful Validation Sequence

*Pending: A sequence diagram for the pipeline completion validation phase.*

Participants: `Coordinator`, `GuardianAgent`, `pii_scanner_tool`, `audit_log_write_tool`, `Database`

Sequence:
1. Coordinator invokes Guardian with accumulated session outputs.
2. Guardian calls `pii_scanner` on each agent output string.
3. `pii_scanner` returns `{pii_found: false, scanned_fields: [...]}` for all fields.
4. Guardian validates approval gate: all `ResponseAction` records are in `PendingApproval` state → pass.
5. Guardian validates output safety: all outputs conform to defined schemas → pass.
6. Guardian calls `audit_log_write` with `{outcome: "validation_passed"}`.
7. Guardian writes `GuardianReport` to DB.
8. Guardian returns `{validation_passed: true}` to Coordinator.
9. Coordinator updates `Incident.status` to `AwaitingReview`.

### 5.2 PII Detected Sequence

*Pending: A sequence diagram where the PII scanner finds PII in an agent output.*

---

## 6. Human Approval Sequence

### 6.1 Approve Single Action

*Pending: A sequence diagram for approving a single `ResponseAction`.*

Participants: `Analyst`, `Frontend`, `FastAPI`, `AuthMiddleware`, `IncidentService`, `GuardianValidation`, `AuditService`, `Database`

Sequence:
1. Analyst clicks "Approve" on a `ResponseAction` in the dashboard.
2. Frontend calls `PATCH /api/v1/incidents/{id}/response/actions/{action_id}` with `{decision: "approved"}`.
3. AuthMiddleware validates bearer token → pass.
4. IncidentService retrieves `ResponseAction` → confirms status is `PendingApproval`.
5. GuardianValidation confirms the action is eligible for approval (has `requires_approval: true` and is in a valid state).
6. IncidentService updates `ResponseAction.approval_status` to `Approved`.
7. AuditService appends `{actor: "human", action: "approve_action", outcome: "success", metadata: {action_id: "..."}}`.
8. FastAPI returns `200 OK` with updated action record.
9. Frontend re-renders the action card with "Approved" status.

### 6.2 Reject Response Plan (Full)

*Pending: A sequence diagram for rejecting the full response plan with a reason.*

### 6.3 Bypass Attempt (Blocked)

*Pending: A sequence diagram showing what happens when code attempts to bypass the approval gate (e.g., directly setting `approval_status` without the Guardian validation step). This should show the ORM service layer blocking the transition.)*

---

## 7. MCP Tool Call Sequence

### 7.1 Permitted Tool Call

*Pending: A sequence diagram showing a complete permitted MCP tool call cycle.*

Participants: `Agent`, `ADKRuntime`, `MCPPermissionRegistry`, `MCPToolServer`, `DataSource`

### 7.2 Blocked Tool Call (Permission Denied)

*Pending: A sequence diagram showing an agent attempting to call a tool outside its permitted set.*

---

## 8. Error Handling Sequences

### 8.1 Specialist Agent Returns Error

*Pending: A sequence diagram showing the Coordinator's error handling when a specialist agent returns a structured error result.*

### 8.2 Database Write Failure

*Pending: A sequence diagram showing how a database write failure is handled within an MCP tool.*

### 8.3 LLM API Timeout

*Pending: A sequence diagram showing how the ADK runtime handles a Gemini API timeout, including retry behavior and ultimate failure handling.*

---

## 9. Frontend Polling Sequence

### 9.1 Incident Board Polling Loop

*Pending: A sequence diagram showing the frontend's polling mechanism for the incident list.*

Participants: `Browser`, `React Component`, `useIncidentList hook`, `API Client`, `FastAPI`, `Database`

Sequence:
1. Component mounts → `useIncidentList` hook initializes.
2. Hook calls `fetch(/api/v1/incidents)` → API returns current incident list.
3. Hook sets `setInterval(fetchIncidents, 5000)`.
4. Every 5 seconds: hook calls fetch → API queries DB → returns updated list → hook sets state → component re-renders.
5. Component unmounts → `clearInterval()` cleanup.

### 9.2 Incident Detail Polling Loop

*Pending: A sequence diagram showing the polling mechanism for a single incident's pipeline stage updates.*
