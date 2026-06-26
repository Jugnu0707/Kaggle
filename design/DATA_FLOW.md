# Data Flow

**Project Name:** Oz AI
**Document Status:** Outline Only — Diagrams Pending Development Phase
**Date:** 2026-06-26

> This document describes how data flows through the Oz AI platform from ingestion to persistence to presentation. Diagrams are to be completed during the development phase using actual schema names and field names. Section headings are the structural contract.

---

## Table of Contents

1. [Data Architecture Overview](#1-data-architecture-overview)
2. [Ingestion Data Flow](#2-ingestion-data-flow)
3. [Agent Layer Data Flow](#3-agent-layer-data-flow)
4. [Persistence Data Flow](#4-persistence-data-flow)
5. [API Data Flow](#5-api-data-flow)
6. [Frontend Data Flow](#6-frontend-data-flow)
7. [Audit Data Flow](#7-audit-data-flow)
8. [MCP Tool Data Flow](#8-mcp-tool-data-flow)

---

## 1. Data Architecture Overview

### 1.1 Data Domain Map

*Pending: A diagram showing the major data domains in Oz AI and their relationships:*

- **Incident Domain** — `Incident`, `EvidenceBundle`, `ThreatIntelReport`, `MITREMapping`, `IncidentTimeline`, `RiskAssessment`, `ResponsePlan`, `ResponseAction`, `IncidentReportBundle`, `GuardianReport`
- **Audit Domain** — `AuditEvent` (append-only, cross-cutting)
- **Knowledge Domain** — `datasets/` contents (threat intel, MITRE ATT&CK, topology, logs) — read-only reference data
- **Configuration Domain** — Environment variables and settings (no persistence in database)

### 1.2 Data Lifecycle

*Pending: A lifecycle diagram showing how an `Incident` record is born (on alert ingestion), grows (as agents append their outputs), reviewed (by human analysts), and archived (upon resolution).*

### 1.3 Data Immutability Boundaries

*Pending: A diagram highlighting which data is mutable vs. immutable:*

- **Immutable:** `AuditEvent` records — append only, no modifications ever
- **Immutable after write:** Agent output records (`EvidenceBundle`, `ThreatIntelReport`, etc.) — written once by the agent, never updated
- **Mutable:** `Incident.status`, `Incident.pipeline_stage`, `ResponseAction.approval_status`

---

## 2. Ingestion Data Flow

### 2.1 API Payload Schema

*Pending: A data flow diagram showing the transformation of the raw JSON alert payload through the ingestion pipeline:*

```
Raw JSON Payload
      ↓
IncidentCreate (Pydantic schema validation)
      ↓
Guardian Agent Injection Scan
      ↓
Incident ORM model (SQLite write)
      ↓
BackgroundTask Dispatch (payload + incident_id)
```

### 2.2 Alert Payload Structure

*Pending: A schema diagram for the `IncidentCreate` Pydantic model with all required and optional fields.*

Required fields (tentative):
- `source` — Alert system identifier
- `alert_type` — Category of alert
- `severity_hint` — Caller's severity assessment (may be overridden by Triage Agent)
- `payload` — Raw alert body (any structured format)
- `timestamp` — Alert generation timestamp
- `entities` — Optional pre-extracted entities (IPs, users, hostnames)

---

## 3. Agent Layer Data Flow

### 3.1 ADK Session State Schema

*Pending: A diagram showing the ADK session state object as it evolves through each pipeline stage. Show the fields added by each agent.*

### 3.2 Agent-to-Agent Data Contract

*Pending: A table showing exactly which session state fields each agent reads and which fields it writes.*

| Agent | Reads From Session | Writes To Session |
|---|---|---|
| Evidence Agent | `raw_alert`, `incident_id` | `evidence_bundle`, `incident_timeline` |
| Threat Intel Agent | `evidence_bundle` | `threat_intel_report` |
| MITRE Mapping Agent | `evidence_bundle`, `threat_intel_report` | `mitre_mapping` |
| Risk Assessment Agent | `evidence_bundle`, `threat_intel_report`, `mitre_mapping`, `incident_timeline` | `risk_assessment` |
| Response Planning Agent | All prior outputs | `response_plan` |
| Executive Report Agent | All prior outputs | `report_bundle` |
| Guardian Agent | `raw_alert` (ingestion), all outputs (validation) | `guardian_report` |

### 3.3 Output Schema Definitions

*Pending: Schema diagrams for each agent output type. To be completed when Pydantic schemas are finalized during Milestone 2.*

---

## 4. Persistence Data Flow

### 4.1 Database Entity Relationship Diagram

*Pending: A full Entity Relationship Diagram (ERD) for the SQLite database. To be created after SQLAlchemy models are finalized in Milestone 2.*

Entities and their primary relationships:
- `Incident` → `EvidenceBundle` (1:1)
- `Incident` → `ThreatIntelReport` (1:1)
- `Incident` → `MITREMapping` (1:1)
- `Incident` → `IncidentTimeline` (1:1)
- `Incident` → `RiskAssessment` (1:1)
- `Incident` → `ResponsePlan` (1:1)
- `ResponsePlan` → `ResponseAction` (1:many)
- `Incident` → `IncidentReportBundle` (1:1)
- `Incident` → `GuardianReport` (1:1)
- `Incident` → `AuditEvent` (1:many)

### 4.2 Write Path Flow

*Pending: A flow diagram showing how an agent result travels from the ADK session through the `incident_record_write` MCP tool to the SQLAlchemy service to the SQLite database.*

### 4.3 Read Path Flow

*Pending: A flow diagram showing how the API retrieves incident data: HTTP request → FastAPI router → Service layer → SQLAlchemy query → Database → Pydantic serialization → HTTP response.*

---

## 5. API Data Flow

### 5.1 Request/Response Schema Map

*Pending: A table mapping each API endpoint to its request schema (Pydantic model) and response schema.*

### 5.2 Authentication Data Flow

*Pending: A flow diagram showing how the bearer token is validated: HTTP request → Auth middleware → Token comparison → Proceed | 401 Unauthorized.*

### 5.3 Pagination Data Flow

*Pending: A flow diagram showing how the `GET /api/v1/incidents` pagination parameters flow through the service layer to a paginated SQLAlchemy query.*

---

## 6. Frontend Data Flow

### 6.1 Component Data Flow

*Pending: A diagram showing how data flows from the API to the React component tree. Show: API client → custom hook (useIncident, useAuditTrail, etc.) → page component → child components.*

### 6.2 Polling Mechanism

*Pending: A sequence diagram showing the frontend polling mechanism: useEffect with setInterval → API fetch → state update → component re-render.*

### 6.3 Approval Workflow Data Flow

*Pending: A flow diagram showing the data path for an analyst's approval action: Button click → API call (POST /response/approve) → Backend service → Guardian validation → Database write → Audit event → API response → UI state update.*

---

## 7. Audit Data Flow

### 7.1 Audit Event Write Path

*Pending: A flow diagram showing how an `AuditEvent` is created: Agent or service calls `audit_log_write` MCP tool → AuditService.append() → INSERT INTO audit_events (no UPDATE, no DELETE paths).*

### 7.2 Audit Event Schema

*Pending: A schema diagram for the `AuditEvent` entity with all fields and their types.*

Fields:
- `id` — UUID primary key
- `incident_id` — Foreign key to `Incident`
- `event_type` — Enumerated type (AgentAction, ToolCall, HumanDecision, GuardianEvent, StatusChange)
- `actor` — Agent name or "human:{user_id}"
- `action` — Description of the action taken
- `outcome` — Success, Failure, PartialSuccess
- `metadata` — JSON blob of context-specific details
- `timestamp` — UTC timestamp, set at write time, never modifiable

### 7.3 Audit Retrieval Path

*Pending: A flow diagram showing how the audit trail is retrieved and rendered in the frontend audit trail tab.*

---

## 8. MCP Tool Data Flow

### 8.1 Tool Call Request/Response Flow

*Pending: A sequence diagram showing a complete MCP tool call cycle: Agent requests tool → ADK validates permission → MCP server executes → ToolResult returned to ADK → Result added to session state.*

### 8.2 Tool Result Schema

*Pending: A schema diagram for the generic `ToolResult[T]` response contract used by all MCP tools.*

```
ToolResult[T]:
  success: bool
  data: T | None
  error: str | None
  metadata: dict | None   # execution time, source, etc.
```

### 8.3 Permission Enforcement Data Flow

*Pending: A flow diagram showing how the MCP tool permission registry intercepts and validates tool calls before they reach the tool implementation.*
