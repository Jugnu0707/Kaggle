# UI Wireframes

**Project Name:** Oz AI
**Document Status:** Outline Only — Wireframes Pending Development Phase
**Date:** 2026-06-26

> This document defines the UI wireframe requirements for the Oz AI dashboard. Actual wireframes (ASCII, image, or Figma exports) are to be added here during the development phase. Section headings define which screens must be wireframed before the corresponding frontend milestone begins. No frontend implementation should begin without an approved wireframe for the relevant page.

---

## Table of Contents

1. [Design System](#1-design-system)
2. [Navigation Structure](#2-navigation-structure)
3. [Incident Board](#3-incident-board)
4. [Incident Detail — Overview Tab](#4-incident-detail--overview-tab)
5. [Incident Detail — Evidence Tab](#5-incident-detail--evidence-tab)
6. [Incident Detail — MITRE ATT&CK Tab](#6-incident-detail--mitre-attck-tab)
7. [Incident Detail — Timeline Tab](#7-incident-detail--timeline-tab)
8. [Incident Detail — Risk Assessment Tab](#8-incident-detail--risk-assessment-tab)
9. [Incident Detail — Response Plan Tab](#9-incident-detail--response-plan-tab)
10. [Incident Detail — Reports Tab](#10-incident-detail--reports-tab)
11. [Incident Detail — Audit Trail Tab](#11-incident-detail--audit-trail-tab)
12. [Incident Detail — Guardian Tab](#12-incident-detail--guardian-tab)
13. [Reports Page](#13-reports-page)
14. [System Health Page](#14-system-health-page)
15. [Empty States and Error States](#15-empty-states-and-error-states)

---

## 1. Design System

### 1.1 Color Palette

*Pending: Final color values. Defined as Tailwind CSS custom tokens.*

| Token | Purpose | Tailwind Class (Proposed) |
|---|---|---|
| `severity-critical` | Critical severity incidents and badges | `red-700` |
| `severity-high` | High severity | `orange-600` |
| `severity-medium` | Medium severity | `yellow-500` |
| `severity-low` | Low severity | `blue-500` |
| `severity-info` | Informational | `gray-400` |
| `status-active` | Active pipeline running | `blue-600` |
| `status-awaiting` | Awaiting human review | `amber-500` |
| `status-resolved` | Resolved | `green-600` |
| `status-rejected` | Rejected | `red-500` |
| `status-error` | Pipeline error | `red-800` |
| `guardian-pass` | Guardian validation passed | `green-500` |
| `guardian-fail` | Guardian violation | `red-700` |

### 1.2 Typography

*Pending: Font selections. Expected: Inter for body text, JetBrains Mono for code/log data.*

### 1.3 Severity Badge Component

*Pending: Wireframe for the reusable severity badge component. Expected: pill shape, background color from severity token, uppercase text.*

### 1.4 Status Badge Component

*Pending: Wireframe for the reusable status badge component.*

### 1.5 Pipeline Stage Indicator

*Pending: Wireframe for the pipeline stage progress indicator. Expected: horizontal step indicator showing completed, active, and pending stages.*

---

## 2. Navigation Structure

### 2.1 Sidebar Navigation Wireframe

*Pending: Wireframe for the left sidebar navigation.*

Expected navigation items:
- **Incident Board** (default landing page) — icon: shield-alert
- **Reports** — icon: chart-bar
- **System Health** — icon: activity

### 2.2 Top Header Wireframe

*Pending: Wireframe for the top header.*

Expected header contents:
- Project name "Oz AI" with logo placeholder
- Current page breadcrumb
- Incident count badge (active incidents)
- Authentication status indicator

---

## 3. Incident Board

*Pending: Full wireframe for the Incident Board page (`/`).*

### 3.1 Layout Structure

Expected layout:
```
┌─────────────────────────────────────────────────────────┐
│  HEADER: "Oz AI — Incident Response"   [Active: N]       │
├──────────┬──────────────────────────────────────────────┤
│          │  FILTERS: Severity [All ▼]  Status [All ▼]   │
│ SIDEBAR  │                                               │
│          │  INCIDENT LIST                                │
│  Nav     │  ┌─────────────────────────────────────────┐ │
│  Items   │  │ [CRITICAL] INC-001  Credential Compromise│ │
│          │  │ Status: Awaiting Review · 3 min ago      │ │
│          │  │ Pipeline: ████████████░░ 85% complete     │ │
│          │  └─────────────────────────────────────────┘ │
│          │  ┌─────────────────────────────────────────┐ │
│          │  │ [HIGH]    INC-002  Data Exfiltration...  │ │
│          │  │ Status: Active · 12 min ago              │ │
│          │  │ Pipeline: ██████░░░░░░░░ 40% complete    │ │
│          │  └─────────────────────────────────────────┘ │
│          │  ... more incidents                          │
└──────────┴──────────────────────────────────────────────┘
```

### 3.2 Incident Row Component

*Pending: Detailed wireframe for a single incident row showing all required fields.*

### 3.3 Filter Bar Component

*Pending: Wireframe for the severity and status filter bar.*

### 3.4 Empty State

*Pending: Wireframe for the empty state when no incidents exist.*

---

## 4. Incident Detail — Overview Tab

*Pending: Full wireframe for the Incident Detail Overview tab (`/incidents/{id}`).*

Expected content:
- Incident ID, title, and severity badge (prominent)
- Status badge and pipeline stage indicator
- Timestamps: created, last updated, time since creation
- Source system and alert type
- Quick summary: number of affected entities, MITRE techniques identified, risk score
- Action buttons: Approve All / Reject All (only visible when status is `AwaitingReview`)
- Tab navigation for all 10 tabs

---

## 5. Incident Detail — Evidence Tab

*Pending: Full wireframe for the Evidence tab.*

Expected content:
- Entity list: extracted entities grouped by type (IPs, users, hostnames, services) with count badges
- Correlated events: count of log events found, source systems queried
- System topology: affected asset cards showing asset name, criticality, and ownership
- Evidence gaps: list of queried sources that returned no results (with explanatory text)
- Evidence collection timestamp and confidence indicator

---

## 6. Incident Detail — MITRE ATT&CK Tab

*Pending: Full wireframe for the MITRE ATT&CK tab.*

Expected content:
- Kill chain stage reached (displayed prominently as a horizontal kill chain bar)
- Technique cards: one card per mapped technique showing:
  - ATT&CK Tactic (e.g., "Initial Access")
  - Technique ID and name (e.g., "T1078 — Valid Accounts")
  - Sub-technique if applicable (e.g., "T1078.003 — Cloud Accounts")
  - Confidence badge (High / Medium / Low)
  - Supporting evidence citation (collapsible)
- Low-confidence technique section (visually separated, labeled "Low Confidence")
- Coverage assessment text
- Link to MITRE ATT&CK Navigator for reference

---

## 7. Incident Detail — Timeline Tab

*Pending: Full wireframe for the Timeline tab.*

Expected content:
- Horizontal timeline bar showing estimated attack progression (compromise → escalation → peak activity)
- Vertical event list: chronological list of all events with:
  - Timestamp (localized)
  - Event description
  - Source system
  - Affected entity
  - MITRE technique annotation badge (if applicable)
- Gap indicators: visual markers where evidence is absent (dashed line with "Evidence Gap" label)
- Filter: show all events / show MITRE-annotated only

---

## 8. Incident Detail — Risk Assessment Tab

*Pending: Full wireframe for the Risk Assessment tab.*

Expected content:
- Risk score: large prominent numeric display (0–100) with color coding
- Severity classification: large severity badge
- Blast radius: visual representation of affected systems (list with asset criticality indicators)
- Regulatory exposure: list of applicable frameworks (SOC 2, HIPAA, GDPR, etc.) with explanation
- Business impact estimate: categorized (Service Disruption / Data Loss / Reputational / Financial)
- Confidence level indicator
- Assessment timestamp

---

## 9. Incident Detail — Response Plan Tab

*Pending: Full wireframe for the Response Plan tab. This is the most critical UI surface for the human-in-the-loop workflow.*

Expected content:
- Phase sections: Containment / Remediation / Recovery (each as a collapsible section)
- Per action card:
  - Action description
  - Risk level badge
  - Estimated effort
  - Affected systems list
  - Prerequisites (if any)
  - Rollback steps (collapsible)
  - Approval controls: `[Approve]` `[Reject]` buttons (visible only when `PendingApproval`)
  - Approval status badge (once decided)
  - Rejection reason input (text field, appears when rejecting)
- "Approve All Containment Actions" shortcut button
- "Reject All" button with mandatory reason input
- Approved/rejected action count summary at top

---

## 10. Incident Detail — Reports Tab

*Pending: Full wireframe for the Reports tab.*

Expected content:
- Three tab sub-sections: Technical Report / Executive Summary / Compliance Summary
- Each report rendered as formatted text with clear section headings
- Copy-to-clipboard button
- Print-friendly view toggle
- Report generation timestamp
- Warning banner on Executive Summary: "This report omits sensitive technical details"

---

## 11. Incident Detail — Audit Trail Tab

*Pending: Full wireframe for the Audit Trail tab.*

Expected content:
- Chronological list of audit events (newest last — ascending order)
- Per event row: timestamp, actor (agent icon or human icon), action type badge, outcome badge, metadata expand toggle
- Filter: show all / agent actions only / human decisions only
- Export button (CSV or JSON)

---

## 12. Incident Detail — Guardian Tab

*Pending: Full wireframe for the Guardian tab.*

Expected content:
- Overall Guardian status: `PASSED` (green) / `VIOLATION` (red)
- Injection Scan section: result (passed/detected), patterns checked count, detection details if applicable
- PII Scan section: result, fields scanned, any flagged content (redacted)
- Tool Permission Audit: list of tool calls made during the pipeline with permission check result
- Approval Gate: status of the human approval gate check
- Output Safety: result of schema validation and content safety checks
- Guardian report generation timestamp

---

## 13. Reports Page

*Pending: Full wireframe for the aggregate Reports page (`/reports`).*

Expected content:
- Date range selector (Last 24h / Last 7d / Last 30d / Custom)
- Summary metric cards: Total Incidents, By Severity (breakdown), Average MTTR, Resolution Rate
- Incident list table for the selected period with severity, status, and MTTR columns
- Export button (CSV)

---

## 14. System Health Page

*Pending: Full wireframe for the System Health page (`/health`).*

Expected content:
- Service status cards: Backend API (status indicator + response time), Database (status + size), Agent Runtime (status)
- Active incident count
- Total incidents processed
- Backend version and uptime
- Last health check timestamp

---

## 15. Empty States and Error States

### 15.1 Incident Board — No Incidents

*Pending: Wireframe for the empty incident board state.*

Expected: Shield icon, text "No incidents detected. Oz AI is monitoring and ready.", and a "Simulate Alert" button (visible in development mode only).

### 15.2 Incident Detail — Pipeline In Progress

*Pending: Wireframe for the incident detail view when the agent pipeline is still running.*

Expected: Each tab shows a loading skeleton with "Agent analysis in progress..." text and the current pipeline stage highlighted.

### 15.3 Incident Detail — Pipeline Error

*Pending: Wireframe for the incident detail view when the pipeline encountered an error.*

Expected: Error banner at top with the failed stage name and a link to the audit trail for error details.

### 15.4 API Error State

*Pending: Wireframe for the generic API error state displayed when any API call fails.*

Expected: Inline error message with the error type and a retry button.

### 15.5 Guardian Violation State

*Pending: Wireframe for the incident card and detail view when the Guardian Agent detected a violation.*

Expected: Red "Guardian: Violation Detected" badge prominently displayed. All other tabs grayed out with "Under Guardian Review" overlay until an administrator clears the violation.
