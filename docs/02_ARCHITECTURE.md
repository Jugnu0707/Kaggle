# 02 — Architecture

**Project Name:** Oz AI
**Version:** 1.0 (MVP)
**Status:** Sprint 3 Complete — reflects implemented system
**Date:** 2026-06-27

> This document is the authoritative architecture reference for Oz AI. Sections marked **(implemented)** describe the running system. Sections marked **(planned)** describe Sprint 4 or post-MVP work. Deviations from original pre-development design are recorded in `04_DECISIONS.md`.

---

## Implementation status (2026-06-27)

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI backend (35 endpoints) | Implemented | No API authentication |
| 15 database tables | Implemented | Schema differs from original entity names |
| 8 AI agents | Implemented | LLM via `google-genai`; fallbacks when no API key |
| MCP registry (5 tools) | Implemented | Agents do not call MCP tools at runtime |
| Investigation workflow | Implemented | `POST /api/v1/investigations/run` |
| Timeline Engine | Implemented | Separate `TimelineService` stage in workflow |
| Evaluation framework | Implemented | Offline benchmarks + API dashboard |
| Guardian validation | Implemented | Between specialist stages in workflow |
| Human approval workflow | Planned | M6 not started |
| Webhook ingestion | Planned | M3-T14–T16 not done |
| 10 domain MCP tools | Planned | Only 5 operational tools exist |
| ADK session checkpointing | Planned | State in DB via services, not ADK sessions |
| API authentication | Planned | M1-T25 not done |

---

## Table of Contents

1. [Overall Architecture](#1-overall-architecture)
2. [Component Diagram](#2-component-diagram)
3. [Agent Architecture](#3-agent-architecture)
4. [Proposed Agents](#4-proposed-agents)
5. [MCP Tool Layer](#5-mcp-tool-layer)
6. [ADK Overview](#6-adk-overview)
7. [Backend Architecture](#7-backend-architecture)
8. [Frontend Architecture](#8-frontend-architecture)
9. [Folder Structure](#9-folder-structure)
10. [Database Overview](#10-database-overview)
11. [Security Overview](#11-security-overview)
12. [Deployment Overview](#12-deployment-overview)
13. [Evaluation Strategy](#13-evaluation-strategy)

---

## 1. Overall Architecture

Oz AI is organized into five logical layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INGESTION LAYER (partial)                    │
│   REST API (incidents, logs)  ·  Alert Simulator — planned         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  Incident / log payloads
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          BACKEND LAYER (implemented)                 │
│   FastAPI  ·  Services  ·  Repositories  ·  Investigation Workflow   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  Explicit investigation trigger
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          AGENT LAYER (implemented)                   │
│   8 agents  ·  Guardian between stages  ·  Timeline + Evaluation     │
│   MCP registry (5 tools) — agents call services directly today       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  Structured results  ·  Audit events
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PERSISTENCE LAYER (implemented)                │
│   SQLite  ·  15 tables  ·  Audit logs  ·  Evaluation metrics         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  REST queries
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER (partial)                    │
│   React dashboard  ·  Investigation Runner  ·  Evaluation page      │
│   Approval workflows — planned                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**End-to-end data flow (implemented):**
1. An operator creates an incident and uploads logs via the REST API or UI.
2. The operator triggers an investigation via `POST /api/v1/investigations/run` or the Investigation Runner UI.
3. `InvestigationWorkflowService` runs the Coordinator-led pipeline with Guardian validation between specialist stages.
4. Timeline Engine and Evaluation Engine run at the end of the workflow.
5. Results are persisted to incident-related tables and surfaced in Incident Detail tabs.
6. Human approval of response actions is **not yet** enforced in the UI or API.

---

## 2. Component Diagram

```
                    ┌──────────────────────────────────────┐
                    │           External Sources            │
                    │   Alert Webhooks  ·  API Clients     │
                    │   Alert Simulator (scripts/)         │
                    └─────────────────┬────────────────────┘
                                      │ HTTPS
                    ┌─────────────────▼────────────────────┐
                    │           FastAPI Backend             │
                    │                                       │
                    │  ┌────────────────────────────────┐  │
                    │  │  Ingestion Router               │  │
                    │  │  Incident Service               │  │
                    │  │  Audit Service                  │  │
                    │  │  Report Service                 │  │
                    │  │  REST API  /api/v1/             │  │
                    │  └──────────┬──────────────────────┘  │
                    │             │ Async Agent Dispatch     │
                    └─────────────│──────────┬──────────────┘
                                  │          │
                    Agent Task    │          │  Read/Write
                                  │          │
          ┌───────────────────────▼──┐  ┌───▼───────────────┐
          │   FastAPI BackgroundTask  │  │    SQLite DB       │
          │   (asyncio, in-process)   │  │  (SQLAlchemy)      │
          └───────────────┬──────────┘  └───────────────────┘
                          │ Agent Invocation
    ┌─────────────────────▼────────────────────────────────────────┐
    │                   Google ADK Runtime                          │
    │                                                               │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │                  Coordinator Agent                        │ │
    │  │         (Orchestrates the full agent pipeline)           │ │
    │  └──────────┬──────────────────────────────────────────────┘ │
    │             │                                                  │
    │    ┌────────▼──────────────────────────────────────────────┐ │
    │    │              Specialist Agent Pipeline                  │ │
    │    │                                                         │ │
    │    │  [1] Evidence Agent                                     │ │
    │    │       ↓                                                  │ │
    │    │  [2] Threat Intelligence Agent                          │ │
    │    │       ↓                                                  │ │
    │    │  [3] MITRE Mapping Agent                                │ │
    │    │       ↓                                                  │ │
    │    │  [4] Risk Assessment Agent                               │ │
    │    │       ↓                                                  │ │
    │    │  [5] Response Planning Agent                             │ │
    │    │       ↓                                                  │ │
    │    │  [6] Executive Report Agent                              │ │
    │    │       ↓                                                  │ │
    │    │  [7] Guardian Agent  ← validates every stage output     │ │
    │    └─────────────────────────────────────────────────────────┘ │
    │                                                               │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │                    MCP Tool Layer (5 tools)               │ │
    │  │  health  ·  list_incidents  ·  incident_details          │ │
    │  │  list_logs  ·  system_info                               │ │
    │  │  (domain tools planned — agents use services today)      │ │
    │  └─────────────────────────────────────────────────────────┘ │
    └─────────────────────────────────────────────────────────────┘
                          │
              ┌───────────▼───────────────────┐
              │       React Frontend            │
              │  Incident Board                 │
              │  Incident Detail                │
              │  MITRE ATT&CK Viewer           │
              │  Timeline Visualization         │
              │  Response Plan Approval         │
              │  Audit Trail Viewer             │
              │  Executive Reports              │
              └────────────────────────────────┘
```

---

## 3. Agent Architecture

### Coordination Model

Oz AI uses a **hierarchical, sequential pipeline multi-agent architecture**. A single Coordinator Agent is the entry point for all incident processing. It invokes specialist agents in a defined sequence, passing structured state through the ADK session context. Specialist agents do not communicate with each other directly — all coordination flows through the Coordinator.

```
Coordinator Agent
      │
      ├─ [1] Evidence Agent  (includes timeline generation)
      ├─ [2] Threat Intelligence Agent
      ├─ [3] MITRE Mapping Agent
      ├─ [4] Risk Assessment Agent
      ├─ [5] Response Planning Agent
      ├─ [6] Executive Report Agent
      └─ [7] Guardian Agent  (cross-cutting safety validator)
```

### State Management

ADK session state carries all inter-agent data. Each specialist agent reads the accumulated session state (including outputs of all prior agents) and appends its own structured output. Session state is checkpointed to the database at each stage transition, ensuring:
- The system can recover from failures without re-running completed stages.
- The frontend can show in-progress agent work, not just final results.
- The audit trail captures the state at every stage boundary.

### Tool Access

Every agent interacts with external systems exclusively through registered MCP tools. No agent contains direct database drivers, HTTP clients, or file system access. This rule is absolute. It enforces auditability: every external action an agent takes is a recorded, inspectable tool call.

### Failure Handling

Each specialist agent returns either a structured success result or a structured error result. The Coordinator Agent handles error states by:
1. Logging the failure to the audit trail via the `audit_log_write` tool.
2. Flagging the incident for mandatory human review.
3. Continuing with remaining pipeline stages where the missing input does not prevent execution.
4. Never silently swallowing errors or producing undefined output.

### Safety Layer

The Guardian Agent operates as a cross-cutting safety validator. It is invoked at two points:
1. **On ingestion:** Validates the incoming alert payload for prompt injection patterns before it is passed to the Evidence Agent.
2. **At pipeline completion:** Validates all accumulated agent outputs for PII exposure, safe-to-display content, and human approval gate compliance before the incident is marked ready for review.

---

## 4. Proposed Agents

---

### 4.1 Coordinator Agent

**Mission:** Orchestrate the full eight-stage incident response pipeline from initial alert to completed incident record.

**Responsibilities:**
- Receive an incident task from the backend with a normalized alert payload.
- Dispatch each specialist agent in sequence, passing accumulated session state.
- Monitor each agent's result for success or error.
- Update the incident status at each pipeline stage transition.
- Handle specialist agent failures by flagging the incident for human review and continuing where possible.
- Trigger the Guardian Agent at the start and end of the pipeline.
- Write stage-transition events to the audit trail.

**Inputs:** Normalized `Incident` record with raw alert payload and initial metadata.

**Outputs:** A fully populated `IncidentRecord` in the database with all specialist agent findings attached.

**Tools Used:** `incident_record_write`, `audit_log_write`

**Failure Behaviour:** If a specialist agent fails, the Coordinator logs the failure, marks the incident as `RequiresHumanReview`, and continues processing remaining stages that do not depend on the failed stage's output. It never raises an unhandled exception to the backend.

**Evaluation Metrics:**
- Pipeline completion rate (percentage of incidents that reach Executive Report stage).
- Correct specialist routing rate (percentage of incidents where all agents are called in the correct order).
- Mean pipeline duration (wall-clock time from dispatch to completion).

---

### 4.2 Evidence Agent

**Mission:** Collect, normalize, and structure all raw evidence related to the incident — including a chronological incident timeline — from available sources.

**Responsibilities:**
- Query log sources for events related to the incident's entities (IPs, hostnames, users, services) and time window.
- Retrieve supplementary alert data for the triggering alert.
- Retrieve the topology context for affected systems (ownership, criticality, relationships).
- Normalize all collected evidence into a structured `EvidenceBundle`.
- **Generate the incident timeline:** extract timestamped events, order them chronologically, identify causal relationships where evidence supports it, estimate time of initial compromise and escalation points, and flag timeline gaps.
- Identify and flag evidence gaps (what log sources were queried but returned no relevant results).

**Inputs:** Raw alert payload from the `Incident` record.

**Outputs:**
- A structured `EvidenceBundle` containing: correlated log events, alert details, system topology context, entity list (IPs, users, hostnames, services), evidence gaps, and evidence collection metadata.
- A structured `IncidentTimeline` containing: a chronologically ordered list of `TimelineEvent` records (timestamp, event description, source, affected entity), estimated compromise timeline, and gap analysis. MITRE technique annotations on timeline events are merged at display time once the MITRE Mapping Agent completes (frontend or API layer).

**Tools Used:** `evidence_collector`, `system_topology_query`, `incident_record_write`, `audit_log_write`

**Failure Behaviour:** If log sources are unavailable, the Evidence Agent returns a partial `EvidenceBundle` and best-effort `IncidentTimeline` with the available data and documents what is missing. It does not block the pipeline. Missing evidence and timeline uncertainty are surfaced to the human reviewer.

**Evaluation Metrics:**
- Entity extraction precision (percentage of extracted entities that are relevant).
- Entity extraction recall (percentage of relevant entities that are extracted).
- Evidence gap documentation completeness.
- Timeline event ordering accuracy on labeled scenarios.
- Time-of-compromise estimation error (minutes) on labeled scenarios.

---

### 4.3 Threat Intelligence Agent

**Mission:** Enrich the evidence bundle with threat intelligence context to characterize the nature and origin of the threat.

**Responsibilities:**
- Look up identified entities (IP addresses, domains, file hashes, user agents) against the threat intelligence knowledge base.
- Identify known indicators of compromise (IOCs) present in the evidence.
- Associate the incident with known threat actors or campaigns where evidence supports it.
- Assess the novelty of the threat (known vs. unknown actor, known vs. unknown technique).
- Document confidence levels for all threat intelligence attributions.

**Inputs:** `EvidenceBundle` from the Evidence Agent.

**Outputs:** A `ThreatIntelReport` containing: IOC matches, threat actor associations (with confidence scores), campaign context, novelty assessment, and intelligence gaps.

**Tools Used:** `threat_intel_lookup`, `knowledge_base_search`, `incident_record_write`, `audit_log_write`

**Failure Behaviour:** If threat intelligence sources return no matches, the agent documents this explicitly as "no known threat actor attribution" rather than leaving the field empty. An absence of attribution is itself a data point.

**Evaluation Metrics:**
- IOC identification precision (percentage of flagged IOCs that are genuine matches).
- Threat actor attribution accuracy on labeled evaluation scenarios.
- Intelligence gap documentation completeness.

---

### 4.4 MITRE Mapping Agent

**Mission:** Map the observed attacker behaviors from the evidence and threat intelligence to the MITRE ATT&CK framework.

**Responsibilities:**
- Analyze the `EvidenceBundle` and `ThreatIntelReport` to identify attacker behaviors.
- Map each identified behavior to the appropriate MITRE ATT&CK Tactic (e.g., Initial Access, Execution, Persistence).
- Identify the specific Technique and Sub-technique (e.g., T1078.003 — Valid Accounts: Cloud Accounts).
- Provide textual evidence justifying each mapping.
- Identify the kill chain stage reached by the attacker.
- Flag techniques for which evidence is suggestive but not conclusive.

**Inputs:** `EvidenceBundle` + `ThreatIntelReport`.

**Outputs:** A `MITREMapping` containing: a list of `TechniqueMapping` records (each with Tactic, Technique ID, Technique name, Sub-technique if applicable, confidence score, and supporting evidence), kill chain stage, and overall ATT&CK coverage assessment.

**Tools Used:** `mitre_attack_search`, `knowledge_base_search`, `incident_record_write`, `audit_log_write`

**Failure Behaviour:** If no ATT&CK technique mapping can be determined with confidence, the agent returns an explicit "insufficient evidence for ATT&CK mapping" result rather than a low-confidence guess. Low-confidence mappings are included but clearly labeled.

**Evaluation Metrics:**
- Technique mapping precision (percentage of mapped techniques that match ground truth).
- Technique mapping recall (percentage of ground-truth techniques that are identified).
- Tactic identification accuracy.

---

### 4.5 Risk Assessment Agent

**Mission:** Produce a comprehensive, structured risk assessment for the incident considering all available evidence and context.

**Responsibilities:**
- Assess the incident's severity level (Critical / High / Medium / Low).
- Evaluate the blast radius: which systems, data stores, and users are confirmed or potentially affected.
- Assess the criticality of affected assets (using system topology data).
- Evaluate regulatory and compliance exposure (data types at risk, applicable frameworks).
- Estimate business impact: service disruption, data loss, reputational risk.
- Produce an overall risk score with explicit reasoning.

**Inputs:** `EvidenceBundle` + `ThreatIntelReport` + `MITREMapping` + `IncidentTimeline`.

**Outputs:** A `RiskAssessment` containing: severity classification, blast radius analysis, affected asset inventory, regulatory exposure assessment, business impact estimate, overall risk score (0–100), and assessment confidence level.

**Tools Used:** `system_topology_query`, `knowledge_base_search`, `incident_record_write`, `audit_log_write`

**Failure Behaviour:** If asset criticality data is unavailable, the agent assumes maximum criticality for affected assets and documents this assumption. Risk assessments always err toward higher severity when data is missing.

**Evaluation Metrics:**
- Severity classification accuracy on labeled evaluation scenarios.
- Blast radius recall (percentage of actually affected systems identified).
- Risk score calibration against expert-labeled ground truth.

---

### 4.6 Response Planning Agent

**Mission:** Generate a structured, risk-annotated, prioritized response plan for the incident.

**Responsibilities:**
- Search the knowledge base for established response playbooks matching the incident's ATT&CK techniques and category.
- Adapt playbook steps to the specific context of the incident.
- Produce a prioritized list of response actions, distinguishing containment (stop the bleeding) from remediation (fix the root cause) and recovery (restore normal operations).
- Annotate each action with: risk classification, estimated effort, affected systems, prerequisites, rollback guidance, and whether human approval is required before execution.
- Flag any action that requires elevated privileges, system downtime, or irreversible changes.
- Every action that could have a consequential system impact must be marked as requiring human approval.

**Inputs:** All prior agent outputs (full session state).

**Outputs:** A `ResponsePlan` containing: a prioritized list of `ResponseAction` records, each with action description, phase (containment / remediation / recovery), risk level, effort estimate, prerequisites, rollback steps, approval requirement flag, and execution status (always `PendingApproval` at creation).

**Tools Used:** `knowledge_base_search`, `incident_record_write`, `audit_log_write`

**Failure Behaviour:** If no matching playbook is found, the agent generates a best-effort plan based on the MITRE technique context and clearly labels it as "no established playbook — agent-generated guidance." It never returns an empty plan.

**Evaluation Metrics:**
- Action relevance rating (human evaluation rubric: 1–5 scale).
- Containment vs. remediation vs. recovery phase classification accuracy.
- Coverage completeness (percentage of known-correct actions included in labeled scenarios).

---

### 4.7 Executive Report Agent

**Mission:** Transform the full incident record into audience-appropriate, human-readable reports.

**Responsibilities:**
- Produce a technical incident report for security engineering teams: full evidence, MITRE mapping, timeline, risk assessment, and response plan.
- Produce an executive summary for management: plain-language description of what happened, business impact, and current status. No technical jargon. No sensitive system details beyond what is necessary.
- Produce a compliance summary for audit and legal teams: regulatory exposure assessment, timeline, response actions taken, and documentation of the human approval decisions.
- Ensure that the executive and compliance summaries do not contain sensitive technical details that could increase exposure if shared broadly.

**Inputs:** All prior agent outputs (full session state).

**Outputs:** An `IncidentReportBundle` containing three `Report` objects: `TechnicalReport`, `ExecutiveSummary`, and `ComplianceSummary`.

**Tools Used:** `incident_record_write`, `audit_log_write`

**Failure Behaviour:** If input data is incomplete, the agent generates reports clearly noting which sections are incomplete and why, rather than omitting sections silently.

**Evaluation Metrics:**
- Executive summary accuracy (does it correctly convey the incident without technical error?).
- Audience-appropriateness score (human evaluation rubric: technical detail should not leak into executive summary).
- Compliance section completeness against a regulatory documentation checklist.

---

### 4.8 Guardian Agent

**Mission:** Act as the platform's safety, security, and human-oversight enforcement layer across the entire agent pipeline.

**Responsibilities:**

**Prompt Injection Detection:**
- Scan all incoming alert payloads for prompt injection patterns before they are processed by any specialist agent.
- Block or quarantine payloads that contain instruction-hijacking attempts.
- Log all detected injection attempts to the audit trail with the offending content redacted.

**PII Detection:**
- Scan all agent outputs before they are persisted or surfaced to the frontend.
- Identify and redact or flag accidental PII exposure (names, emails, phone numbers, national ID numbers, health data).
- Ensure that executive summaries and compliance reports do not contain PII beyond the minimum necessary.

**Tool Permission Validation:**
- Verify that each agent's tool calls are within its defined permitted tool set.
- Block and log any tool call that exceeds an agent's permissions.
- Prevent any agent from calling `notification_dispatch` or any write tool that the Coordinator has not authorized for that pipeline stage.

**Human Approval Enforcement:**
- Validate that no `ResponseAction` in the `ResponsePlan` is marked as executable without a corresponding human approval record in the database.
- Reject any pipeline output that attempts to bypass the approval gate.
- This validation runs before the incident is marked `ReadyForReview` and before any action status can transition to `Approved`.

**Safe Output Validation:**
- Validate that all final agent outputs conform to their defined Pydantic schemas.
- Reject outputs that contain structured data anomalies, unexpected fields, or content that fails safety checks.
- Ensure that all outputs are suitable for display in the frontend without additional sanitization.

**Inputs:** Raw alert payload (on ingestion) + all agent outputs (at pipeline completion).

**Outputs:** A `GuardianReport` containing: injection scan result, PII scan result, tool permission audit log, approval gate validation result, and output safety validation result.

**Tools Used:** `prompt_injection_detector`, `pii_scanner`, `audit_log_write`

**Failure Behaviour:** If the Guardian Agent detects any violation, it immediately halts the relevant pipeline stage, logs the violation with full context, flags the incident as `GuardianViolation`, and requires a human administrator to review before processing continues. Guardian failures are never silently ignored.

**Evaluation Metrics:**
- Prompt injection detection precision (false positive rate on benign payloads).
- Prompt injection detection recall (detection rate on synthetic injection test cases).
- PII detection precision and recall on labeled output samples.
- Tool permission violation detection rate on synthetic violation test cases.
- Zero tolerance for approval gate bypass: any bypass is a critical evaluation failure.

---

## 5. MCP Tool Layer (implemented — partial)

The MCP layer in `mcp/` provides a registry and five operational tools for health and data introspection. **Agents do not invoke MCP tools at runtime**; they call backend services directly. The planned domain tool set remains backlog work (Milestone 4).

### Registered tools (5)

| Tool Name | Purpose | Used by agents at runtime |
|---|---|---|
| `health` | Application health status | No |
| `list_incidents` | Paginated incident list via `IncidentService` | No |
| `incident_details` | Single incident by ID | No |
| `list_logs` | Uploaded log file metadata | No |
| `system_info` | Version, database, ADK, MCP status | No |

### Planned tools (not implemented)

| Tool Name | Planned agents |
|---|---|
| `evidence_collector` | Evidence Agent |
| `knowledge_base_search` | Threat Intel, MITRE, Risk, Response |
| `threat_intel_lookup` | Threat Intelligence Agent |
| `mitre_attack_search` | MITRE Mapping Agent |
| `system_topology_query` | Evidence, Risk |
| `incident_record_write` | All specialist agents |
| `audit_log_write` | All agents |
| `pii_scanner` | Guardian Agent (implemented in `agents/guardian/` directly) |
| `prompt_injection_detector` | Guardian Agent (implemented in `agents/guardian/` directly) |
| `notification_dispatch` | Coordinator (post-approval) |

### Tool design principles (target)

1. **Single responsibility:** Each tool does one thing and does it well. No tool aggregates multiple concerns.
2. **Structured responses:** Every tool returns a typed response: `{success: bool, data: T, error: str | None}`.
3. **No side effects beyond scope:** A tool that reads does not write. A tool that writes audits its own write.
4. **Testable in isolation:** Every tool can be unit-tested without an ADK runtime.
5. **Permission-gated:** The MCP layer registers which tools each agent is permitted to call. Calls outside the permitted set are rejected at the tool layer.

---

## 6. ADK Overview (implemented — partial)

Oz AI initializes **Google ADK** at startup (`backend/app/core/adk_runtime.py`). Agent modules define ADK-compatible configuration. **LLM calls use `google.genai.Client`** via agent services. ADK session state, MCP tool binding for agents, and `adk eval` are not yet implemented.

### ADK patterns

| ADK pattern | Oz AI usage (current) |
|---|---|
| ADK runtime init | Startup validation; Coordinator agent config loaded |
| Agent config objects | Each agent in `agents/` has prompt and schema definitions |
| `google.genai` | Direct LLM calls with rule-based fallbacks |
| MCP tool server | Registry with 5 tools; not wired to agent runtime |
| `adk eval` | Planned (M8-T08) |

### Agent-to-ADK Mapping

Each specialist agent corresponds to one `LlmAgent` configuration file in `agents/`. The configuration specifies:
- The agent's system prompt (loaded from a versioned prompt file).
- The list of permitted MCP tools.
- The expected output schema (validated by the Coordinator after each agent call).
- The failure policy (return error vs. raise exception).

---

## 7. Backend Architecture

The backend is a **FastAPI** application running with **Uvicorn**. Investigation workflows run synchronously within the request handler (`InvestigationWorkflowService`). There is no `BackgroundTasks` agent dispatch on incident creation.

### Application layers (implemented)

```
backend/app/
├── api/v1/       # HTTP routers (35 endpoints)
├── services/     # Business logic, agent services, investigation workflow
├── models/       # 15 SQLAlchemy ORM models
├── schemas/      # Pydantic API contracts
├── repositories/ # Data access
├── core/         # Config, logging, ADK/MCP runtimes
└── db/           # Session and engine
```

### Investigation dispatch (implemented)

When an operator calls `POST /api/v1/investigations/run`:
1. Validates `incident_id` (and optional `log_file_id`).
2. Creates an `InvestigationRun` record.
3. Runs the full pipeline synchronously: Coordinator → specialists with Guardian → Timeline → Evaluation.
4. Returns the investigation package with per-stage results.

Individual agent endpoints (`POST /api/v1/agents/*`) allow running single agents without the full workflow.

### API design (implemented — 35 endpoints)

| Resource | Endpoint | Method | Status |
|---|---|---|---|
| Root | `/` | GET | Implemented |
| Health | `/api/v1/health` | GET | Implemented |
| AI health | `/api/v1/ai/health` | GET | Implemented |
| Dashboard | `/api/v1/dashboard/stats` | GET | Implemented |
| System | `/api/v1/system/tables` | GET | Implemented |
| System | `/api/v1/system/mcp` | GET | Implemented |
| Incidents | `/api/v1/incidents` | GET, POST | Implemented |
| Incidents | `/api/v1/incidents/{id}` | GET, PUT, DELETE | Implemented |
| Incidents | `/api/v1/incidents/{id}/mitre` | GET | Implemented |
| Incidents | `/api/v1/incidents/{id}/threat-intelligence` | GET | Implemented |
| Incidents | `/api/v1/incidents/{id}/risk` | GET | Implemented |
| Incidents | `/api/v1/incidents/{id}/response` | GET | Implemented |
| Incidents | `/api/v1/incidents/{id}/executive-report` | GET | Implemented |
| Incidents | `/api/v1/incidents/{id}/timeline` | GET | Implemented |
| Incidents | `/api/v1/incidents/{id}/timeline/export` | GET | Implemented |
| Incidents | `/api/v1/incidents/{id}/guardian-audits` | GET | Implemented |
| Logs | `/api/v1/logs/upload` | POST | Implemented |
| Logs | `/api/v1/logs` | GET | Implemented |
| Logs | `/api/v1/logs/{id}` | GET, DELETE | Implemented |
| Agents | `/api/v1/agents/orchestrate` | POST | Implemented |
| Agents | `/api/v1/agents/evidence` | POST | Implemented |
| Agents | `/api/v1/agents/threat-intelligence` | POST | Implemented |
| Agents | `/api/v1/agents/mitre` | POST | Implemented |
| Agents | `/api/v1/agents/risk` | POST | Implemented |
| Agents | `/api/v1/agents/response` | POST | Implemented |
| Agents | `/api/v1/agents/executive-report` | POST | Implemented |
| Agents | `/api/v1/agents/guardian/validate` | POST | Implemented |
| Investigations | `/api/v1/investigations/run` | POST | Implemented |
| Investigations | `/api/v1/investigations/runs/{run_id}` | GET | Implemented |
| Evaluation | `/api/v1/evaluation` | GET | Implemented |
| Evaluation | `/api/v1/evaluation/{agent_name}` | GET | Implemented |
| Response approve/reject | `/api/v1/incidents/{id}/response/approve` | POST | Planned |
| Webhook ingestion | — | POST | Planned |

---

## 8. Frontend Architecture

### Framework

The frontend is a **React 19** single-page application written in **TypeScript**, styled with **Tailwind CSS**, and bundled with **Vite**. No additional state management libraries, data-fetching libraries, or validation libraries are introduced for the MVP.

### Application Structure

```
frontend/
│
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route-level page components
│   │   ├── IncidentBoard/
│   │   ├── IncidentDetail/
│   │   ├── MITREViewer/
│   │   ├── TimelineView/
│   │   ├── ResponseApproval/
│   │   ├── AuditTrail/
│   │   └── Reports/
│   ├── hooks/          # Custom React hooks (data fetching with native fetch + useEffect)
│   ├── services/       # Typed API client (native fetch wrapper)
│   ├── types/          # TypeScript interfaces mirroring backend Pydantic schemas
│   └── utils/          # Formatting, severity color mapping, date utilities
└── public/
```

### Key UI pages (implemented)

| Route | Page | Status |
|---|---|---|
| `/` | Dashboard with metrics | Implemented |
| `/incidents` | Incident list | Implemented |
| `/incidents/:id` | Incident detail (8 tabs) | Implemented |
| `/incidents/:id/investigate` | Investigation Runner | Implemented |
| `/logs` | Log upload and listing | Implemented |
| `/evaluation` | Agent evaluation dashboard | Implemented |
| `/reports` | Reports hub | Placeholder |
| `/settings` | Settings | Placeholder |

Incident Detail tabs: Overview, Timeline, Threat Intelligence, MITRE, Risk, Response, Executive Report, Guardian Audit.

Response approval workflow UI is **not implemented**.

### State Management

The MVP uses React's built-in `useState` and `useEffect` hooks with the native `fetch` API. No third-party state management or data-fetching library is introduced. The frontend polls the backend for incident status updates on a configurable interval.

---

## 9. Folder Structure

```
Kaggle/
├── agents/                   # 8 agent implementations
│   ├── coordinator/
│   ├── evidence/
│   ├── threat_intelligence/
│   ├── mitre/
│   ├── risk/
│   ├── response/
│   ├── executive_report/
│   └── guardian/
├── backend/app/              # FastAPI application (api, services, models, schemas)
├── evaluation/               # Evaluation framework (engine, benchmarks, results/)
├── frontend/src/             # React dashboard pages and services
├── mcp/                      # MCP registry + 5 operational tools
├── datasets/                 # Mostly empty — planned synthetic data
├── docker/                   # Dockerfile.backend, Dockerfile.frontend
├── docs/                     # Project documentation (+ 08_MILESTONES.md)
├── scripts/                  # dev.sh, dev-backend.sh, dev-frontend.sh
├── storage/uploads/          # Log file storage
├── tests/                    # Backend integration tests
├── design/                   # Architecture diagrams (may lag implementation)
├── docker-compose.yml
└── README.md
```

---

## 10. Database Overview

### MVP: SQLite

The MVP uses **SQLite** via **SQLAlchemy** async driver (`aiosqlite`). SQLite was chosen to eliminate infrastructure complexity. The SQLAlchemy ORM layer abstracts the database engine entirely; migration to PostgreSQL requires only a connection string change.

### Core tables (15 — implemented)

| Table / model | Description |
|---|---|
| `incidents` | Primary incident record (status, severity, metadata) |
| `log_files` | Uploaded log file metadata and storage paths |
| `evidence` | Evidence Agent output for an incident |
| `threat_intelligence_findings` | IOC and reputation findings |
| `mitre_findings` | ATT&CK technique mappings |
| `risk_assessments` | Severity, blast radius, risk score |
| `response_plans` | Response plan JSON and metadata |
| `executive_reports` | Technical and executive summaries |
| `timeline_events` | Chronological timeline events |
| `guardian_audits` | Guardian validation records per stage |
| `agent_executions` | Per-agent execution tracking |
| `audit_logs` | Append-only audit events |
| `investigations` | Investigation metadata |
| `investigation_runs` | End-to-end workflow run records |
| `evaluation_metrics` | Persisted agent evaluation scores |

### Integrity constraints (target vs implemented)

- `audit_logs` — append-only pattern in services; no update/delete endpoints.
- Response plan approval transitions — **not enforced** (approval API not implemented).
- `Incident.status` — basic state updates via `IncidentService`; full approval state machine not implemented.

---

## 11. Security Overview

### Principles

- **No autonomous consequential actions.** The Guardian Agent enforces the human approval gate at the architectural level.
- **Defense in depth.** Security is applied at the ingestion layer (Pydantic validation), agent layer (Guardian Agent), and persistence layer (append-only audit).
- **Secrets never in code.** All credentials and API keys are environment-variable-only.
- **Input validation everywhere.** All external inputs are validated with Pydantic schemas before any processing.
- **Audit trail integrity.** Append-only; no update or delete on `AuditEvent` records.

### MVP security controls (implemented vs planned)

| Control | Status |
|---|---|
| API authentication | **Not implemented** — all endpoints are open |
| Input validation | Pydantic on all request schemas |
| Prompt injection defense | Guardian rule-based detection in `agents/guardian/` |
| PII protection | Guardian PII masking when `MASK_PII=true` |
| Secret handling | Environment variables only |
| Audit trail | `audit_logs` table; append-only services |
| CORS | Permissive (`allow_origins=["*"]`) for development |
| Tool permissions | **Not implemented** at MCP layer |

---

## 12. Deployment Overview

### Local Development

```bash
cp .env.example .env        # Copy and populate with required API keys
docker compose up           # Start all services
```

Services started by `docker compose up`:
- `backend` — FastAPI application on port `8000`
- `frontend` — Vite dev server on port `5173`

### Environment Configuration

All configuration is environment-variable-driven. Key categories:
- **LLM:** Gemini API key, model name
- **Database:** SQLite file path
- **API Security:** Bearer token secret
- **Notifications:** Slack webhook URL (optional for MVP)
- **Evaluation:** Evaluation dataset path

### Production Path (Post-MVP)

| Concern | MVP | Production |
|---|---|---|
| Database | SQLite | Managed PostgreSQL |
| Container Orchestration | Docker Compose | Kubernetes |
| Secrets | `.env` files | HashiCorp Vault / Cloud KMS |
| Observability | FastAPI logs | OpenTelemetry + Grafana |
| CI/CD | Manual | GitHub Actions |

---

## 13. Evaluation Strategy

### Goal

Produce quantitative evidence that the agent pipeline operates at a useful level of accuracy across all pipeline stages.

### Evaluation Dimensions

| Dimension | Measurement |
|---|---|
| Evidence collection completeness | Entity recall on labeled scenarios |
| Timeline reconstruction (Evidence Agent) | Event ordering accuracy and time-of-compromise error on labeled scenarios |
| MITRE technique mapping | Precision and recall against ground-truth labels |
| Risk assessment severity classification | Accuracy on labeled severity scenarios |
| Response plan relevance | Human rubric: 1–5 relevance score |
| Guardian injection detection | Precision and recall on synthetic injection test suite |
| Guardian PII detection | Precision and recall on synthetic PII test suite |
| End-to-end pipeline latency | Wall-clock time from alert submission to incident ready |
| Coordinator routing accuracy | Percentage of correct agent invocation sequences |

### Tooling

- **ADK Eval** — Scenario-based pipeline evaluation using Google ADK's built-in evaluation framework.
- **Custom evaluation harness** — `evaluation/harness/` Python scripts that submit scenarios and collect structured outputs.
- **Labeled scenario library** — `evaluation/scenarios/` — 30 labeled incident scenarios covering 6 incident categories × 5 severity levels.

### Scenario Categories

Evaluation scenarios cover:
1. Credential compromise / account takeover
2. Data exfiltration attempt
3. Denial of service / resource abuse
4. Misconfiguration exposure
5. Malware / anomalous process execution
6. Insider threat indicators
