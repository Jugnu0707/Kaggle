# System Flow

**Project Name:** Oz AI
**Document Status:** Outline Only — Diagrams Pending Development Phase
**Date:** 2026-06-26

> This document describes the end-to-end system flow of the Oz AI platform. Diagrams are to be created during the development phase using actual implementation details. Section headings and content outlines are defined here as the structural contract. Do not add diagrams until the implementation is complete enough to reflect reality accurately.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Alert Ingestion Flow](#2-alert-ingestion-flow)
3. [Agent Pipeline Flow](#3-agent-pipeline-flow)
4. [Human Review Flow](#4-human-review-flow)
5. [Approval and Resolution Flow](#5-approval-and-resolution-flow)
6. [Guardian Safety Flow](#6-guardian-safety-flow)
7. [Error and Recovery Flow](#7-error-and-recovery-flow)
8. [Reporting Flow](#8-reporting-flow)

---

## 1. Overview

### 1.1 System Boundary Diagram

*Pending: A diagram showing the Oz AI system boundary with all external actors (Alert Sources, Human Analysts, CISO, External Notification Channels) and the system's primary interface points.*

### 1.2 High-Level Flow Summary

The Oz AI system flow can be summarized in five macro-steps:

1. **Ingestion** — An alert enters the system via REST API or webhook. The Guardian Agent validates the payload. The backend creates an incident record and dispatches the agent pipeline.

2. **Analysis** — The agent pipeline executes sequentially: Evidence (includes timeline) → Threat Intel → MITRE Mapping → Risk Assessment → Response Planning → Executive Report.

3. **Validation** — The Guardian Agent validates all pipeline outputs for PII, safety, and approval gate integrity.

4. **Review** — The incident is surfaced to human analysts with all agent findings. Analysts review and make approval decisions.

5. **Resolution** — Approved actions are tracked. The incident is resolved with a full audit trail and reports available for post-incident review.

---

## 2. Alert Ingestion Flow

### 2.1 REST API Ingestion Path

*Pending: A flow diagram for the path: External System → POST /api/v1/incidents → Pydantic Validation → Guardian Injection Scan → Incident Record Creation → BackgroundTask Dispatch → 201 Response.*

### 2.2 Webhook Ingestion Path

*Pending: A flow diagram for the webhook ingestion path with payload normalization.*

### 2.3 Alert Simulator Path

*Pending: A flow diagram for the `scripts/simulate_alert.py` script path used in development and evaluation.*

### 2.4 Ingestion Validation Gates

*Pending: A diagram showing the two validation gates on ingestion: (1) Pydantic schema validation at the API layer, (2) Guardian Agent injection scan.*

---

## 3. Agent Pipeline Flow

### 3.1 Full Pipeline Sequence

*Pending: A detailed sequence diagram showing the full eight-stage agent pipeline with state transitions, tool calls, and database writes at each stage.*

### 3.2 Stage Transition State Machine

*Pending: A state machine diagram showing all valid `IncidentStatus` and `PipelineStage` transitions.*

Valid stages in order:
- `Received`
- `ValidationPassed`
- `GatheringEvidence` (includes timeline generation)
- `EnrichingIntelligence`
- `MappingTechniques`
- `AssessingRisk`
- `PlanningResponse`
- `GeneratingReports`
- `GuardianValidation`
- `AwaitingReview`

### 3.3 Inter-Agent Data Flow

*Pending: A diagram showing which data structures flow between agents via ADK session state. Each edge should be labeled with the schema name.*

### 3.4 MCP Tool Call Flow

*Pending: A diagram showing how an agent makes a tool call through the MCP tool layer and receives a result. Show: Agent → ADK Runtime → MCP Tool Server → Data Source → MCP Tool Server → ADK Runtime → Agent.*

---

## 4. Human Review Flow

### 4.1 Analyst Notification Flow

*Pending: A flow diagram showing how the analyst is notified when an incident reaches `AwaitingReview` status. Show the notification dispatch path and the polling-based frontend update.*

### 4.2 Incident Review Workflow

*Pending: A flow diagram showing the analyst's review path through the incident detail tabs in the recommended review order.*

Recommended review order:
1. Overview tab (situational awareness)
2. Evidence tab (what was collected, what is missing)
3. Threat Intelligence tab (what is known about the threat)
4. MITRE ATT&CK tab (how the attack maps to known techniques)
5. Timeline tab (when things happened)
6. Risk Assessment tab (severity and blast radius)
7. Response Plan tab (what to do, in what order)
8. Reports tab (audience-ready summaries)
9. Guardian tab (safety validation confirmation)
10. Audit Trail tab (full decision record)

---

## 5. Approval and Resolution Flow

### 5.1 Response Plan Approval Flow

*Pending: A flow diagram showing the full approval workflow: analyst views response plan → approves/rejects each action → approval audit event written → Guardian validates approval gate → incident status updates.*

### 5.2 Individual Action Approval State Machine

*Pending: A state machine diagram for `ResponseAction.approval_status`: `PendingApproval` → `Approved` | `Rejected`. Show that `Approved` and `Rejected` are terminal states (no transitions out).*

### 5.3 Incident Resolution States

*Pending: A diagram showing when an incident can be marked `Resolved`, `PartiallyApproved`, and `Rejected`.*

---

## 6. Guardian Safety Flow

### 6.1 Ingestion Phase Safety Flow

*Pending: A flow diagram for the Guardian Agent's ingestion-phase responsibilities: payload received → injection scan → clean (continue) | injection detected (quarantine + audit log + GuardianViolation status).*

### 6.2 Pipeline Completion Safety Flow

*Pending: A flow diagram for the Guardian Agent's pipeline-completion responsibilities: PII scan → output safety validation → approval gate check → pass (AwaitingReview) | fail (GuardianViolation + human review required).*

### 6.3 Tool Permission Enforcement Flow

*Pending: A flow diagram showing how the MCP tool permission registry intercepts out-of-scope tool calls before they reach the tool implementation.*

---

## 7. Error and Recovery Flow

### 7.1 Specialist Agent Failure Flow

*Pending: A flow diagram showing what happens when a specialist agent returns an error: Coordinator receives error → logs to audit trail → flags PartialPipelineWarning → continues with remaining stages → surfaces warning to analyst.*

### 7.2 Pipeline Timeout Flow

*Pending: A flow diagram showing the timeout handling for the BackgroundTask: task timeout → PipelineError status → error logged → analyst notified → incident remains queryable with partial results.*

### 7.3 Database Error Recovery

*Pending: A flow diagram showing database error handling and the retry/fail-safe behavior.*

---

## 8. Reporting Flow

### 8.1 Report Generation Flow

*Pending: A flow diagram showing the Executive Report Agent's three-report generation process: Technical Report, Executive Summary, Compliance Summary.*

### 8.2 Report Retrieval Flow

*Pending: A flow diagram showing how reports are retrieved via the API and rendered in the frontend.*

### 8.3 CISO Reporting Flow

*Pending: A flow diagram showing how aggregate metrics are computed and rendered on the Reports page.*
