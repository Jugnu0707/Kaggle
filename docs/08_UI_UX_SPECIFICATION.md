# 08 — UI/UX Specification

**Project Name:** Oz AI  
**Subtitle:** Autonomous Enterprise Incident Response Platform  
**Version:** 1.0 (MVP)  
**Date:** 2026-06-27  
**Status:** Implemented (partial) — see §3 Navigation for actual routes  
**Author:** Product Design / UX Architecture

> This document is the authoritative UI and UX specification for Oz AI. After approval, no visual, navigational, or interaction design decisions may be implemented without updating this document. Implementation must align with `01_PROJECT_BRIEF.md`, `02_ARCHITECTURE.md`, and `06_PRODUCT_REQUIREMENTS.md`.

---

## Document Control

| Property | Value |
|---|---|
| Related Documents | `01_PROJECT_BRIEF.md`, `02_ARCHITECTURE.md`, `06_PRODUCT_REQUIREMENTS.md`, `design/UI_WIREFRAMES.md` |
| Frontend Stack (MVP) | React 19, TypeScript, Tailwind CSS, Vite |
| Default Theme | Dark Mode |
| Primary Users | Tier 1 SOC Analyst, Senior Security Engineer, CISO, Platform Administrator |

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Branding](#2-branding)
3. [Navigation](#3-navigation)
4. [User Flow](#4-user-flow)
5. [Dashboard](#5-dashboard)
6. [Incident Details](#6-incident-details)
7. [Reports](#7-reports)
8. [Evaluation Dashboard](#8-evaluation-dashboard)
9. [Settings](#9-settings)
10. [Error States](#10-error-states)
11. [Responsive Design](#11-responsive-design)
12. [Accessibility](#12-accessibility)
13. [UI Components](#13-ui-components)
14. [Future UI](#14-future-ui)
15. [Screens](#15-screens)

---

## 1. Design Philosophy

Oz AI serves security professionals who operate under time pressure, cognitive load, and accountability. The interface must reduce noise, surface signal, and preserve human authority over consequential decisions. Every design choice serves clarity, trust, and speed.

### Design Goals

| Goal | Definition | Design Implication |
|---|---|---|
| **Enterprise** | The product must feel credible in a Fortune 500 SOC, not like a demo or hobby project. | Consistent layout grid, restrained visual language, no playful or consumer-style patterns. |
| **Professional** | Analysts and executives must trust what they see. | Neutral typography, structured hierarchy, explicit labels, no ambiguous icon-only controls for critical actions. |
| **Minimal** | Every pixel must earn its place. | No decorative elements. Information is grouped by task, not by visual novelty. |
| **Cybersecurity** | The UI must communicate security posture and incident severity at a glance. | Severity-coded badges, pipeline stage visibility, Guardian status always accessible, audit trail never hidden. |
| **Fast** | Analysts need answers in seconds, not minutes of navigation. | High information density on desktop, keyboard shortcuts for common actions, minimal page transitions within an incident. |
| **Readable** | Long sessions in low-light environments are normal. | Strong contrast, generous line height for report text, monospace for logs and IDs. |
| **High Information Density** | A single screen should answer "What happened? How bad is it? What do I do?" | Dashboard and Overview tab prioritize scannable summaries before deep detail. |
| **Accessible** | Security tooling must be usable by all qualified analysts. | WCAG 2.1 AA contrast targets, keyboard navigation, screen reader support, no color-only status encoding. |
| **Modern** | The product reflects current enterprise SaaS expectations without trend-chasing. | Clean sidebar navigation, card-based content blocks, subtle elevation, responsive layout foundations. |

### Core UX Principles

1. **Human authority is visible.** Approval controls for response actions are never buried. The UI must constantly reinforce that Oz AI recommends — humans decide.
2. **Pipeline transparency.** Users always know whether agents are running, completed, failed, or awaiting review. Ambiguous "loading" states are unacceptable for incident status.
3. **Progressive disclosure.** Summary first, detail on demand. Overview and Dashboard show summaries; tabs reveal depth.
4. **Safety is first-class UI.** Guardian validation status is not an afterthought — it appears in navigation badges, incident rows, and a dedicated tab.
5. **Consistency over creativity.** Severity colors, status badges, and tab order are identical everywhere they appear.

---

## 2. Branding

### Project Identity

| Element | Value |
|---|---|
| **Project Name** | Oz AI |
| **Subtitle** | Autonomous Enterprise Incident Response Platform |
| **Product Descriptor (short)** | Enterprise Incident Response Platform |
| **Tagline (internal)** | AI recommends. Humans decide. |

### Color System

Colors are defined as design tokens. Implementation will map these to Tailwind custom properties. All tokens must meet WCAG 2.1 AA contrast requirements against their intended backgrounds.

#### Primary Color

| Token | Hex | Usage |
|---|---|---|
| `color-primary` | `#2563EB` | Primary actions, active navigation, links, focus rings |
| `color-primary-hover` | `#1D4ED8` | Hover state for primary buttons and links |
| `color-primary-muted` | `#1E3A5F` | Primary tint backgrounds in dark mode (selected nav item) |

Primary blue communicates trust, stability, and enterprise software familiarity. It is used sparingly — only for interactive emphasis, never as a decorative fill.

#### Secondary Color

| Token | Hex | Usage |
|---|---|---|
| `color-secondary` | `#64748B` | Secondary text, borders, dividers, inactive icons |
| `color-secondary-surface` | `#334155` | Secondary card backgrounds, input borders (dark mode) |
| `color-accent` | `#06B6D4` | Pipeline-in-progress indicators, informational highlights |

#### Severity Colors

Severity colors are used consistently across badges, chart segments, table row accents, and dashboard cards. Each severity level includes a text-safe variant for use on dark backgrounds.

| Severity | Token | Hex | Badge Background (Dark) | Usage |
|---|---|---|---|---|
| Critical | `severity-critical` | `#DC2626` | `#450A0A` | Immediate action required |
| High | `severity-high` | `#EA580C` | `#431407` | Urgent review required |
| Medium | `severity-medium` | `#CA8A04` | `#422006` | Review within SLA |
| Low | `severity-low` | `#2563EB` | `#1E3A5F` | Monitor and triage |
| Informational | `severity-info` | `#64748B` | `#1E293B` | Awareness only |

Severity must never be communicated by color alone. Every severity indicator includes a text label (e.g., "CRITICAL").

#### Status Colors

| Status | Token | Hex | Usage |
|---|---|---|---|
| Active / Pipeline Running | `status-active` | `#2563EB` | Agent pipeline in progress |
| Awaiting Review | `status-awaiting` | `#F59E0B` | Human approval required |
| Resolved / Approved | `status-resolved` | `#16A34A` | Incident closed or plan approved |
| Rejected | `status-rejected` | `#EF4444` | Plan or action rejected |
| Pipeline Error | `status-error` | `#991B1B` | Unrecoverable pipeline failure |
| Guardian Violation | `guardian-fail` | `#DC2626` | Safety validation failed |
| Guardian Passed | `guardian-pass` | `#16A34A` | Safety validation passed |

#### Surface Colors (Dark Mode — Default)

| Token | Hex | Usage |
|---|---|---|
| `surface-base` | `#0F172A` | Application background |
| `surface-raised` | `#1E293B` | Cards, sidebar, panels |
| `surface-overlay` | `#334155` | Modals, dropdowns, tooltips |
| `text-primary` | `#F8FAFC` | Headings, primary body text |
| `text-secondary` | `#94A3B8` | Labels, metadata, timestamps |
| `border-default` | `#334155` | Card borders, dividers |

#### Surface Colors (Light Mode)

| Token | Hex | Usage |
|---|---|---|
| `surface-base` | `#F8FAFC` | Application background |
| `surface-raised` | `#FFFFFF` | Cards, sidebar, panels |
| `surface-overlay` | `#F1F5F9` | Modals, dropdowns |
| `text-primary` | `#0F172A` | Headings, primary body text |
| `text-secondary` | `#64748B` | Labels, metadata |
| `border-default` | `#E2E8F0` | Card borders, dividers |

#### Default Theme

**Dark Mode is the default theme.** Security operations environments typically run in low-light conditions. Dark mode reduces eye strain during extended incident review sessions. Light mode is available via Settings and must be fully supported — not a partial afterthought.

### Typography

| Role | Font | Weight | Size (Desktop) | Usage |
|---|---|---|---|---|
| Display | Inter | 600 (Semibold) | 28px / 1.75rem | Page titles |
| Heading 1 | Inter | 600 | 24px / 1.5rem | Section headings |
| Heading 2 | Inter | 600 | 20px / 1.25rem | Card titles, tab section headers |
| Heading 3 | Inter | 500 (Medium) | 16px / 1rem | Subsection labels |
| Body | Inter | 400 (Regular) | 14px / 0.875rem | Primary content, report text |
| Body Small | Inter | 400 | 12px / 0.75rem | Metadata, timestamps, captions |
| Monospace | JetBrains Mono | 400 | 13px / 0.8125rem | Incident IDs, log lines, IOC values, ATT&CK IDs |
| Label | Inter | 500 | 11px / 0.6875rem | Badge text, table column headers (uppercase, letter-spacing 0.05em) |

**Line height:** 1.5 for body text, 1.25 for headings, 1.6 for report prose.  
**Maximum line length:** 80 characters for report narrative text to maintain readability.

### Spacing

Spacing follows a 4px base grid.

| Token | Value | Usage |
|---|---|---|
| `space-1` | 4px | Tight internal padding (badge) |
| `space-2` | 8px | Icon-to-label gap |
| `space-3` | 12px | Compact card padding |
| `space-4` | 16px | Standard card padding |
| `space-6` | 24px | Section separation |
| `space-8` | 32px | Page section margins |
| `space-12` | 48px | Major layout gaps |

**Layout grid:** 12-column grid on desktop. Sidebar fixed at 240px. Main content area fluid with max-width 1440px centered.

### Card Style

Cards are the primary content container throughout the application.

| Property | Specification |
|---|---|
| Background | `surface-raised` |
| Border | 1px solid `border-default` |
| Border radius | 8px |
| Padding | 16px (`space-4`) standard; 24px (`space-6`) for report cards |
| Shadow (dark mode) | None — elevation communicated via border and background contrast |
| Shadow (light mode) | `0 1px 3px rgba(0,0,0,0.08)` |
| Header | Optional card header with title (Heading 2) and right-aligned actions |
| Hover (interactive cards) | Border shifts to `color-primary` at 50% opacity |

Incident rows on list views use a flattened card variant: no border radius on individual rows, grouped inside a container card.

### Buttons

| Variant | Appearance | Usage |
|---|---|---|
| **Primary** | Filled `color-primary`, white text | Approve action, submit, confirm |
| **Secondary** | Outlined `border-default`, `text-primary` | Cancel, back, low-priority actions |
| **Destructive** | Filled `severity-critical`, white text | Reject plan, dismiss with confirmation |
| **Ghost** | No border, text only | Tertiary actions, icon buttons |
| **Disabled** | 50% opacity, no pointer events | Unavailable actions |

**Size variants:** Small (32px height) for inline table actions; Medium (40px) default; Large (48px) for primary page CTAs.

**Critical rule:** Destructive actions (Reject All, Dismiss Guardian Violation) always require a confirmation dialog. No one-click destructive actions.

### Icons

Icons use a consistent stroke-based icon set (Lucide-compatible naming for implementation reference). Icons are always paired with a text label except in the sidebar navigation, where tooltips provide labels on collapse.

| Context | Icon Convention |
|---|---|
| Navigation | 20px, `text-secondary`, active item `color-primary` |
| Status indicators | 16px inside badges |
| Actions | 16px left of button label |
| Empty states | 48px, `text-secondary` at 50% opacity |

Icon-only buttons are permitted only for: copy-to-clipboard, expand/collapse, and close dialog. All other actions require visible text labels.

---

## 3. Navigation

### Layout Structure

The application uses a persistent **left sidebar navigation** with a **top header bar**. The sidebar is always visible on desktop and laptop. On tablet, the sidebar collapses to an icon rail. On mobile, the sidebar becomes a bottom navigation bar.

```
┌──────────────┬──────────────────────────────────────────────────────┐
│              │  TOP HEADER                                          │
│   SIDEBAR    │  Breadcrumb · Incident Count · User/Session · Theme  │
│   (240px)    ├──────────────────────────────────────────────────────┤
│              │                                                      │
│  Navigation  │              MAIN CONTENT AREA                       │
│   Items      │                                                      │
│              │                                                      │
└──────────────┴──────────────────────────────────────────────────────┘
```

### Sidebar navigation items (implemented)

| Order | Label | Route | Status | Notes |
|---|---|---|---|---|
| 1 | **Dashboard** | `/` | Implemented | Metrics via `GET /api/v1/dashboard/stats` |
| 2 | **Incidents** | `/incidents` | Implemented | List and detail views |
| 3 | **Log Uploads** | `/logs` | Implemented | Not in original 7-item nav spec |
| 4 | **Reports** | `/reports` | Placeholder | Stub page |
| 5 | **Evaluation** | `/evaluation` | Implemented | `GET /api/v1/evaluation` |
| 6 | **Settings** | `/settings` | Placeholder | Stub page |

**Investigation Runner** (not a sidebar item): `/incidents/:id/investigate` — launched from Incident Detail **Start Investigation** button.

**Incident Detail:** `/incidents/:id` — tabs: Overview, Timeline, Threat Intelligence, MITRE, Risk, Response, Executive Report, Guardian Audit.

**Not implemented:** `/about`, `/investigation` standalone route, API key login, approval workflow UI.

### Route mapping (implemented)

| UI screen | Primary API resources |
|---|---|
| Dashboard | `GET /api/v1/dashboard/stats`, `GET /api/v1/incidents` |
| Incidents | `GET /api/v1/incidents`, `POST /api/v1/incidents` |
| Incident Detail | `GET /api/v1/incidents/{id}` + sub-resource GETs |
| Investigation Runner | `POST /api/v1/investigations/run`, `GET /api/v1/investigations/runs/{run_id}` |
| Log Uploads | `POST /api/v1/logs/upload`, `GET /api/v1/logs` |
| Evaluation | `GET /api/v1/evaluation`, `GET /api/v1/evaluation/{agent_name}` |
| Reports | Planned — aggregate report endpoints not implemented |
| Settings | `GET /api/v1/health`, `GET /api/v1/system/mcp` (no dedicated settings API) |

---

## 4. User Flow

### Primary Analyst Flow

The following is the complete end-to-end user journey for a Tier 1 SOC analyst responding to an incident.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ACCESS / LOGIN                               │
│  Analyst enters API key → session validated → redirected to Dashboard│
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           DASHBOARD                                  │
│  Review severity distribution, pipeline status, recent incidents    │
│  Identify incident requiring attention (Awaiting Review badge)       │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OPEN INCIDENT                                   │
│  Navigate: Dashboard card click OR Incidents list OR Investigation   │
│  Lands on: Incident Detail → Overview tab                            │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
                    ┌───────────┴───────────┐
                    │   REVIEW TABS (ORDER)  │
                    └───────────┬───────────┘
                                ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ EVIDENCE │ → │  MITRE   │ → │ TIMELINE │ → │   RISK   │ → │ RESPONSE │
│ + Timeline│  │  ATT&CK  │   │  (view)  │   │ Assess-  │   │   PLAN   │
│  data    │   │ mapping  │   │          │   │   ment   │   │  review  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         GUARDIAN                                   │
│  Verify: injection scan passed, PII clear, approval gate intact    │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          APPROVE                                   │
│  Approve/reject individual response actions or full plan           │
│  Rejection requires documented reason (minimum 10 characters)        │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          REPORT                                    │
│  Review Technical, Executive, and Compliance reports               │
│  Export PDF or Markdown for stakeholders                           │
└─────────────────────────────────────────────────────────────────────┘
```

### Access / Login Flow

The MVP does not implement full OAuth or SSO. Access is controlled via **API key authentication** aligned with `02_ARCHITECTURE.md`.

| Step | User Action | System Response |
|---|---|---|
| 1 | User navigates to application URL | If no session, redirect to Access screen |
| 2 | User enters API key (Bearer token) | Key stored in session storage (not localStorage) |
| 3 | System validates key against `GET /api/v1/health` or lightweight auth probe | Success → redirect to Dashboard; Failure → inline error |
| 4 | Session active | All API requests include `Authorization: Bearer {key}` header |
| 5 | Session expired or 401 received | Redirect to Access screen with "Session expired" message |

**Access screen design:** Minimal. Centered card. Oz AI logo and subtitle. Single API key input field (password type). "Connect" primary button. Link to documentation for key configuration.

### Secondary Flows

| Flow | Entry Point | Outcome |
|---|---|---|
| CISO Reporting | Reports nav → date range filter | Aggregate metrics + executive summaries |
| Evaluation Review | Evaluation nav | Agent accuracy and latency metrics |
| Guardian Violation Review | Incidents list (red badge) → Guardian tab | Administrator reviews quarantined incident |
| Pipeline Error Recovery | Incidents list (error badge) → Overview tab | Engineer reviews partial results and audit trail |

### Recommended Tab Review Order

When investigating an incident for the first time, the UI presents a **Review Progress indicator** on the Overview tab suggesting this order:

1. Overview (situational awareness)
2. Evidence (what was collected)
3. Threat Intelligence (who/what is the threat)
4. MITRE ATT&CK (how they operated)
5. Timeline (when things happened)
6. Risk Assessment (how bad is it)
7. Response Plan (what to do)
8. Guardian Report (is it safe to act)
9. Audit Trail (full decision record)

Users may navigate tabs in any order. The progress indicator tracks which tabs have been viewed.

---

## 5. Dashboard

### Purpose

The Dashboard is the operational command center. It answers: **"What is happening right now, and what needs my attention?"** It is the default landing page after login.

### Visible Elements

#### Summary Metric Cards (Top Row)

Four equal-width cards displayed in a single row on desktop.

| Card | Data Source | Display |
|---|---|---|
| **Active Incidents** | Count of incidents not in `Resolved` or `Rejected` | Large number + trend arrow (vs. previous 24h) |
| **Awaiting Review** | Count of incidents in `AwaitingReview` status | Large number + amber accent if > 0 |
| **Critical / High** | Count of open Critical + High severity incidents | Large number + severity color accent |
| **Avg Investigation Time** | Mean time from `Received` to `AwaitingReview` (MTTR proxy) | Duration formatted (e.g., "4m 32s") + sparkline |

#### Severity Distribution

Horizontal bar chart or donut chart showing open incident count by severity level (Critical, High, Medium, Low, Informational). Each segment uses severity color tokens. Clicking a segment navigates to Incidents list with that severity filter applied.

#### Pipeline Status

A compact status panel showing the current state of the agent pipeline across all active incidents.

| Element | Description |
|---|---|
| Active Pipelines | Count of incidents with pipeline currently running |
| Stage Breakdown | Horizontal stacked bar showing how many incidents are at each pipeline stage |
| Last Completed | Timestamp of most recently completed pipeline |
| Error Count | Count of incidents in `PipelineError` or `GuardianViolation` status (red if > 0) |

#### Agent Pipeline Widget

A dedicated, demo-friendly widget showing real-time specialist agent progress for the **most recently active incident** (or the incident with the highest severity if multiple are active). This widget is a primary visual for competition demonstrations.

**Display format:** Vertical list of pipeline stages with status icons:

| Stage Label | Status Icons |
|---|---|
| Evidence | ✔ complete · ⏳ in progress · ○ pending · ✖ failed |
| Threat Intel | same |
| MITRE | same |
| Risk | same |
| Response | same |
| Guardian | same |

**Example (in-progress incident):**

```
Agent Pipeline — INC-00141
─────────────────────────
Evidence      ✔
Threat Intel  ✔
MITRE         ⏳
Risk          ○
Response      ○
Guardian      ○
```

**Behavior:**
- Updates on each dashboard poll cycle (5s when pipelines active)
- Clicking the widget navigates to that incident's detail view
- Failed stages show ✖ with tooltip explaining the error
- Guardian row reflects validation phase only (ingestion-phase Guardian scan is not shown in this widget — it completes before Evidence begins)
- When no pipeline is active, widget shows: "No active pipelines. All incidents idle." with last completed pipeline summary

**Placement:** Right column below Severity Distribution on desktop; full-width card below metric cards on tablet/mobile.

#### Recent Incidents

A table showing the 10 most recent incidents.

| Column | Content |
|---|---|
| ID | Monospace incident ID (link to detail) |
| Severity | Severity badge |
| Status | Status badge |
| Pipeline Stage | Compact progress indicator |
| Summary | One-line AI-generated summary (from Overview) |
| Created | Relative timestamp ("3 min ago") |
| Action | "Review" button if `AwaitingReview`, "View" otherwise |

#### Latest Reports

Card showing the 3 most recently generated executive summaries.

| Element | Content |
|---|---|
| Incident ID | Link to incident |
| Report Excerpt | First 120 characters of executive summary |
| Generated | Timestamp |
| Action | "View Report" link |

#### Quick Actions

A row of action buttons below the metric cards.

| Action | Behavior |
|---|---|
| **View All Incidents** | Navigate to `/incidents` |
| **Review Pending** | Navigate to `/incidents?status=awaiting_review` |
| **Run Evaluation** | Navigate to `/evaluation` (administrators) |
| **System Status** | Navigate to `/settings` system info section |

### Dashboard ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Oz AI — Dashboard                                    [3 Awaiting Review]   │
├──────────────┬──────────────────────────────────────────────────────────────┤
│              │                                                              │
│  Dashboard ● │   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│  Incidents   │   │   ACTIVE   │ │  AWAITING  │ │ CRIT / HIGH│ │ AVG TIME │ │
│  Investigation│  │     12     │ │  REVIEW    │ │     3      │ │  4m 32s  │ │
│  Reports     │   │            │ │     3  ⚠   │ │            │ │          │ │
│  Evaluation  │   └────────────┘ └────────────┘ └────────────┘ └──────────┘ │
│  Settings    │                                                              │
│  About       │   QUICK ACTIONS                                               │
│              │   [View All Incidents] [Review Pending] [System Status]      │
│              │                                                              │
│              │   ┌─────────────────────────────┐ ┌─────────────────────────┐ │
│              │   │  SEVERITY DISTRIBUTION      │ │  AGENT PIPELINE         │ │
│              │   │  ████ Critical  (2)         │ │  INC-00141              │ │
│              │   │  ██████ High    (3)         │ │  Evidence      ✔        │ │
│              │   │  ████ Medium    (2)         │ │  Threat Intel  ✔        │ │
│              │   │  ██ Low         (1)         │ │  MITRE         ⏳        │ │
│              │   │  █ Info         (1)         │ │  Risk          ○        │ │
│              │   └─────────────────────────────┘ │  Response      ○        │ │
│              │                                   │  Guardian      ○        │ │
│              │                                   └─────────────────────────┘ │
│              │                                                              │
│              │   RECENT INCIDENTS                          [View All →]     │
│              │   ┌─────────────────────────────────────────────────────────┐│
│              │   │ ID          Sev    Status         Stage      Time  Act  ││
│              │   │ INC-00142   CRIT   Awaiting Rev.  Complete   3m    [Review]│
│              │   │ INC-00141   HIGH   Active         MITRE Map  8m    [View] ││
│              │   │ INC-00140   MED    Resolved       —          1h    [View] ││
│              │   └─────────────────────────────────────────────────────────┘│
│              │                                                              │
│              │   LATEST REPORTS                                             │
│              │   ┌─────────────────────────────────────────────────────────┐│
│              │   │ INC-00142 — Credential compromise detected in cloud...  ││
│              │   │ INC-00140 — Misconfiguration exposed internal API...    ││
│              │   └─────────────────────────────────────────────────────────┘│
└──────────────┴──────────────────────────────────────────────────────────────┘
```

### Dashboard Refresh Behavior

The Dashboard polls `GET /api/v1/incidents` every **5 seconds** when any incident has an active pipeline. When all incidents are idle, polling interval increases to **30 seconds** to reduce load. A manual refresh button is always available in the header.

---

## 6. Incident Details

### Page Structure

**Route:** `/incidents/{id}` (also accessible via Investigation workspace)  
**Layout:** Page header (incident ID, severity, status, pipeline indicator) + horizontal tab bar + tab content area.

### Page Header (Persistent Across All Tabs)

| Element | Description |
|---|---|
| Incident ID | Monospace, copyable (e.g., `INC-2024-00142`) |
| Severity Badge | Critical / High / Medium / Low / Informational |
| Status Badge | Current incident status |
| Pipeline Stage Indicator | Horizontal step bar showing 6 specialist stages + Guardian validation |
| Created / Updated | Timestamps |
| Guardian Status | Compact pass/fail badge |
| Primary Actions | "Approve All" / "Reject All" (visible only when `AwaitingReview`) |

### Tab Definitions

---

#### Tab 1: Overview

**Purpose:** Provide immediate situational awareness without requiring the analyst to read every subsequent tab.

**Displayed Information:**
- One-paragraph AI-generated incident summary (plain language)
- **AI Confidence:** Aggregate confidence score (0–100%) derived from agent output confidence fields; displayed with High / Medium / Low label and color indicator
- **Investigation Duration:** Elapsed time from incident `created_at` to pipeline completion (`AwaitingReview`); live counter while pipeline is running
- **Processing Status:** Current pipeline stage label (e.g., "Mapping ATT&CK Techniques") with in-progress spinner, or "Complete — Awaiting Review" when finished
- Key metrics row: risk score, MITRE technique count, affected entity count, evidence gap count
- Pipeline stage progress (Agent Pipeline mini-widget — same format as Dashboard widget)
- Guardian status summary (pass / violation / pending)
- Response plan status (pending approval / partially approved / approved / rejected)
- **Reports:** Compact summary showing availability of Technical, Executive, and Compliance reports with quick-view links (or "Generating…" while pipeline incomplete)
- Recommended review order checklist (tracks viewed tabs)
- Alert source metadata: source system, alert type, original timestamp

**Possible User Actions:**
- Navigate to any tab via quick-link buttons
- Copy incident ID
- Approve All / Reject All (when status is `AwaitingReview`)
- Export incident summary (Markdown)
- Open full Reports view (Technical / Executive / Compliance)
- Download report PDF or Markdown from Overview (when reports are ready)

---

#### Tab 2: Evidence

**Purpose:** Show what raw and correlated evidence the Evidence Agent collected.

**Displayed Information:**
- **Entity List:** Grouped by type (IP addresses, hostnames, users, services) with count badges
- **Correlated Events:** Total log events found, broken down by source system
- **Event Sample Table:** Timestamp, source, event description, entity (paginated, max 50 visible)
- **System Topology:** Affected asset cards showing asset name, criticality level, owner team
- **Evidence Gaps:** Explicit list of queried sources that returned no results, with explanation
- **Collection Metadata:** Timestamp, agent confidence indicator

**Possible User Actions:**
- Filter entities by type
- Expand event rows for full log detail
- Copy entity values (IP, hostname)
- View raw alert payload (collapsible JSON viewer, monospace)
- Flag evidence gap for manual investigation (notes field, MVP: local UI state only)

---

#### Tab 3: Timeline

**Purpose:** Display the chronological sequence of the incident. Timeline data is **generated by the Evidence Agent** and persisted as `IncidentTimeline`. The tab remains a first-class investigation surface for analysts.

**Data source:** `GET /api/v1/incidents/{id}/timeline` — produced during the Evidence Agent stage. MITRE technique annotations on events are merged at display time once MITRE mapping is available.

**Displayed Information:**
- **Compromise Timeline Bar:** Estimated initial compromise → escalation → peak activity (horizontal)
- **Event List:** Chronological, each event showing:
  - Timestamp (localized, with timezone label)
  - Event description
  - Source system
  - Affected entity
  - MITRE technique annotation badge (if mapped)
- **Gap Markers:** Dashed connectors with "Evidence Gap — no data for this period" labels
- **Uncertainty Markers:** Events with unreliable timestamps flagged with warning icon

**Possible User Actions:**
- Filter: All events / MITRE-annotated only / By entity
- Sort: Chronological (default) / Reverse
- Export timeline as CSV
- Click MITRE badge to jump to MITRE ATT&CK tab filtered to that technique

---

#### Tab 4: MITRE ATT&CK

**Purpose:** Display the MITRE Mapping Agent's ATT&CK framework analysis.

**Displayed Information:**
- **Kill Chain Stage:** Prominent label (e.g., "Initial Access → Execution")
- **Technique Cards:** One card per mapped technique:
  - Tactic name (e.g., "Initial Access")
  - Technique ID and name (e.g., "T1078 — Valid Accounts")
  - Sub-technique if applicable (e.g., "T1078.003 — Cloud Accounts")
  - Confidence badge (High ≥ 0.8 / Medium ≥ 0.5 / Low < 0.5)
  - Supporting evidence citation (expandable)
- **Low Confidence Section:** Separated visually, labeled "Low Confidence Mappings"
- **Coverage Assessment:** Text summary of ATT&CK coverage for this incident
- **No Mapping State:** Explicit message if insufficient evidence (not empty)

**Possible User Actions:**
- Expand/collapse evidence citations per technique
- Filter by tactic
- Copy technique ID
- External link to MITRE ATT&CK official entry (opens in new tab)

---

#### Tab 5: Threat Intelligence

**Purpose:** Display threat context from the Threat Intelligence Agent.

**Displayed Information:**
- **IOC Matches:** Table of matched indicators (IP, domain, hash) with match confidence and threat label
- **Threat Actor Associations:** Named threat actors or campaigns with confidence scores
- **Novelty Assessment:** Known vs. unknown threat classification
- **Intelligence Gaps:** Explicit "no attribution found" messaging when applicable
- **Source References:** Which threat intel sources were queried

**Possible User Actions:**
- Copy IOC values
- Filter IOC table by type (IP / domain / hash)
- Expand threat actor detail card

---

#### Tab 6: Risk Assessment

**Purpose:** Communicate the incident's severity, blast radius, and business impact.

**Displayed Information:**
- **Risk Score:** Large numeric display (0–100) with color gradient (green → red)
- **Severity Classification:** Large severity badge (may differ from alert severity hint)
- **Blast Radius:** Visual list of affected systems with criticality indicators
- **Affected Assets Table:** Asset name, type, criticality, data classification, owner
- **Regulatory Exposure:** Applicable frameworks (SOC 2, HIPAA, GDPR, etc.) with explanation
- **Business Impact Estimate:** Categories: Service Disruption / Data Loss / Reputational / Financial
- **Assessment Confidence:** High / Medium / Low with explanation of data completeness

**Possible User Actions:**
- Expand asset detail
- Copy risk assessment summary
- View which assumptions were made due to missing data (expandable "Assumptions" panel)

---

#### Tab 7: Response Plan

**Purpose:** Present the agent-generated response plan and enable human-in-the-loop approval. **This is the most critical interactive surface in the application.**

**Displayed Information:**
- **Plan Summary:** Total actions, approved count, rejected count, pending count
- **Phase Sections:** Collapsible groups — Containment / Remediation / Recovery
- **Action Cards:** One card per `ResponseAction`:
  - Action description
  - Phase badge
  - Risk level badge (Low / Medium / High / Critical)
  - Estimated effort
  - Affected systems
  - Prerequisites (expandable)
  - Rollback steps (expandable)
  - Requires approval flag
  - Current approval status
  - Approved by / timestamp (post-decision)
  - Rejection reason (if rejected)

**Possible User Actions:**
- **Approve** individual action
- **Reject** individual action (requires reason, minimum 10 characters)
- **Approve All** (confirmation dialog listing all actions)
- **Reject All** (requires reason)
- Approve all actions in a phase (e.g., "Approve All Containment")
- Expand/collapse phase sections
- View playbook source (if matched from knowledge base)

**Critical UX Rules:**
- Actions with `requires_approval: true` display a lock icon until approved
- No action shows an "Execute" button in MVP — approval is the terminal state
- Rejection reason field is mandatory and cannot be dismissed
- After approval/rejection, the action card updates in place without page reload

---

#### Tab 8: Guardian Report

**Purpose:** Display the Guardian Agent's safety validation results.

**Displayed Information:**
- **Overall Status:** Large PASSED (green) or VIOLATION (red) banner
- **Injection Scan:** Result, patterns checked count, detection details (redacted) if failed
- **PII Scan:** Result, fields scanned, flagged content (redacted display)
- **Tool Permission Audit:** List of all tool calls with permission check result per call
- **Approval Gate Validation:** Confirmation that all actions remain in `PendingApproval` at pipeline completion
- **Output Safety Validation:** Schema validation result for all agent outputs
- **Report Timestamp**

**Possible User Actions:**
- Expand tool permission audit log
- Copy Guardian report summary
- Administrator: acknowledge Guardian violation (future — MVP displays read-only)

---

#### Tab 9: Audit Trail

**Purpose:** Provide a complete, immutable record of all system and human actions for the incident.

**Displayed Information:**
- Chronological list (ascending) of all `AuditEvent` records
- Per event: timestamp, actor (agent name or "human"), event type badge, action description, outcome badge
- Expandable metadata JSON per event (monospace viewer)

**Possible User Actions:**
- Filter: All / Agent actions only / Human decisions only / Guardian events only
- Search audit log by keyword
- Export audit trail (CSV or JSON)
- Copy event metadata

---

## 7. Reports

### Purpose

Reports transform incident analysis into audience-appropriate documents. The Executive Report Agent generates all three variants; the UI renders and enables export.

### Report Types

#### Technical Report

| Property | Specification |
|---|---|
| **Audience** | Security engineers, SOC analysts |
| **Content** | Full evidence summary, IOC list, MITRE mapping, timeline, risk assessment, response plan, audit trail summary |
| **Tone** | Precise, technical, includes ATT&CK IDs, log references, system names |
| **Format** | Structured sections with headings, tables for IOCs and actions |
| **Sensitive Data** | Includes internal system names and technical identifiers |

#### Executive Report

| Property | Specification |
|---|---|
| **Audience** | CISO, VP Engineering, board members |
| **Content** | Plain-language incident summary, business impact, current status, recommended next steps |
| **Tone** | Clear, non-technical, no jargon, no alarmist language |
| **Format** | Short sections, bullet points, maximum 2 pages equivalent |
| **Sensitive Data** | Omits internal IPs, vulnerability details, and raw log data |
| **Banner** | UI displays: "This report omits sensitive technical details." |

#### Compliance Report

| Property | Specification |
|---|---|
| **Audience** | Audit, legal, compliance teams |
| **Content** | Regulatory exposure assessment, incident timeline, response actions taken, human approval decisions, Guardian validation record |
| **Tone** | Formal, factual, audit-ready |
| **Format** | Numbered sections suitable for regulatory submission |
| **Sensitive Data** | Includes decision timestamps and approval records; omits raw exploit details |

### Report Access Points

| Location | Behavior |
|---|---|
| Incident Detail → (via Reports section in Overview or dedicated export) | Per-incident report viewer |
| Reports page (`/reports`) | Aggregate access, date-filtered incident list with report links |
| Dashboard → Latest Reports | Quick access to recent executive summaries |

### Export and Share Options

| Format | Behavior |
|---|---|
| **Download PDF** | Generates a formatted PDF of the selected report variant. Includes Oz AI header, incident ID, generation timestamp, and page numbers. |
| **Download Markdown** | Downloads raw Markdown file suitable for Confluence, GitHub, or wiki paste. |
| **Copy to Clipboard** | Copies report text to clipboard with confirmation toast. |
| **Share Link** | *(Future feature — post-MVP)* Generates a time-limited, read-only URL for external stakeholders. Disabled in MVP with tooltip: "Share links coming in a future release." Button visible but non-functional (greyed out) to communicate roadmap intent. |

**Export naming convention:** `oz-ai_{incident-id}_{report-type}_{date}.pdf` (e.g., `oz-ai_INC-00142_executive_2026-06-26.pdf`)

---

## 8. Evaluation Dashboard

### Purpose

The Evaluation Dashboard surfaces agent pipeline performance metrics for engineers and competition evaluators. It connects to the evaluation harness defined in `evaluation/harness/`.

**Route:** `/evaluation`  
**Primary Audience:** Security Engineer, Platform Administrator, Competition Evaluators

### Metrics Display

#### Summary Cards (Top Row)

| Card | Metric | Description |
|---|---|---|
| **Accuracy** | Overall pipeline accuracy score | Weighted average of MITRE precision, severity accuracy, and response relevance |
| **Latency** | Mean pipeline duration | Wall-clock time from alert submission to `AwaitingReview` |
| **Agent Success Rate** | Pipeline completion rate | Percentage of scenarios reaching Executive Report stage |
| **Security Score** | Guardian effectiveness | Combined injection detection recall + PII detection recall |

#### Detailed Metrics Panels

| Panel | Metrics |
|---|---|
| **MITRE Mapping** | Precision, recall, F1 score; per-technique breakdown table |
| **Risk Assessment** | Severity classification accuracy; risk score calibration error |
| **Response Plan** | Human relevance rubric score (1–5); action coverage percentage |
| **Guardian Agent** | Injection detection precision/recall; PII detection precision/recall; false positive rate |
| **MCP Tool Usage** | Tool call count by tool name; permission denial count; error rate by tool |
| **Latency Breakdown** | Per-agent mean duration bar chart |

#### Evaluation Charts

| Chart | Type | Data |
|---|---|---|
| Accuracy by Scenario Category | Grouped bar chart | 6 incident categories × accuracy score |
| Latency Distribution | Histogram | Pipeline duration across all scenarios |
| Agent Success Rate | Donut chart | Completed / Partial / Failed pipelines |
| MITRE Precision vs. Recall | Scatter plot | Per-scenario data points |
| MCP Tool Call Volume | Horizontal bar chart | Calls per tool, sorted by volume |
| Security Score Trend | Line chart | Score across evaluation runs (if multiple runs stored) |

#### Evaluation Run Controls

| Control | Behavior |
|---|---|
| Scenario Count | Display total scenarios in library (target: 30) |
| Last Run Timestamp | When evaluation was last executed |
| Run Evaluation | Button to trigger harness (MVP: navigates to documentation; post-MVP: triggers run) |
| Export Results | Download evaluation results JSON |

### Empty State

When no evaluation has been run: "No evaluation results available. Run the evaluation harness to generate metrics." with link to `evaluation/harness/` documentation.

---

## 9. Settings

### Purpose

Settings provides configuration visibility and system information for platform administrators. The MVP does not expose runtime configuration changes for all settings — some are environment-variable-only per architecture.

**Route:** `/settings`  
**Layout:** Vertical tab list (left) + settings panel (right) on desktop; accordion on mobile.

### Settings Sections

#### API Keys

| Element | Specification |
|---|---|
| Current Session Key | Masked display (e.g., `ozai_••••••••••••1234`) |
| Key Status | Valid / Expired / Not configured |
| Change Key | Input field + "Update Session" button (updates session storage, re-validates) |
| Note | "API keys are configured server-side via environment variables. This field controls your current browser session only." |

#### Model Selection

| Element | Specification |
|---|---|
| Current Model | Display only — e.g., "Gemini 1.5 Pro (via Google ADK)" |
| Model Source | Read from backend system status endpoint |
| Note | "Model selection is configured via server environment. Contact your administrator to change." |

MVP is read-only. Post-MVP may expose model selection for administrators.

#### Theme

| Element | Specification |
|---|---|
| Theme Toggle | Dark Mode / Light Mode radio selector |
| Preview | Mini preview card showing current theme colors |
| Default | Dark Mode (reset button) |
| Persistence | Theme preference stored in localStorage |

#### System Information

| Element | Specification |
|---|---|
| Backend Status | Online / Degraded / Offline (from `GET /api/v1/system/status`) |
| Backend Version | Version string |
| Database Status | Connected / Error |
| Active Pipelines | Current count |
| Total Incidents Processed | Lifetime count |
| Uptime | Backend uptime duration |
| Last Health Check | Timestamp of last successful health probe |
| Environment | "Docker Compose (Development)" or configured label |

This section replaces the "System Health" page from earlier documentation, consolidated into Settings.

---

## 10. Error States

Every error state must communicate: what happened, whether user action is required, and what to do next. Generic "Something went wrong" messages are not permitted.

### No Incidents

| Context | Message | Visual | Action |
|---|---|---|---|
| Dashboard — Recent Incidents | "No incidents yet. Oz AI is ready to receive alerts." | Shield icon, muted | Link to documentation for alert submission |
| Incidents list (no filter) | Same as above | Full-width empty state card | — |
| Incidents list (filtered) | "No incidents match your filters." | Filter icon | "Clear Filters" button |

### No Results

| Context | Message | Action |
|---|---|---|
| Search (audit trail, entities) | "No results found for '{query}'." | Clear search |
| Filtered table | "No items match the selected filters." | Clear filters |
| Evaluation (no runs) | "No evaluation results available." | Link to run harness |

### Backend Offline

| Context | Message | Visual | Action |
|---|---|---|---|
| API unreachable | "Unable to connect to Oz AI backend. Check that the service is running." | Red status banner, persistent at top of page | "Retry Connection" button |
| Health check failed | "Backend is degraded. Some features may be unavailable." | Amber banner | Link to Settings → System Information |

### Agent Failed

| Context | Message | Visual | Action |
|---|---|---|---|
| Pipeline stage error | "The {Agent Name} encountered an error. Partial results are available." | Amber warning banner on Overview tab | Link to Audit Trail |
| Full pipeline failure | "Incident analysis could not be completed." | Red status badge | View Audit Trail for error details |
| Partial pipeline | "Analysis completed with warnings. Review evidence gaps before approving." | Amber "Partial" badge | Evidence tab pre-highlighted |

### Permission Denied

| Context | Message | Action |
|---|---|---|
| 401 Unauthorized | "Your session has expired. Please re-enter your API key." | Redirect to Access screen |
| 403 Forbidden | "You do not have permission to perform this action." | — |
| Guardian violation | "This incident was flagged by the Guardian Agent and requires administrator review." | Guardian tab link |

### Loading

| Context | Pattern | Duration Handling |
|---|---|---|
| Initial page load | Full-page skeleton matching layout shape | Show after 300ms delay (avoid flash) |
| Tab content load | Inline skeleton for tab content area | — |
| Pipeline in progress | Animated pipeline stage indicator with current stage label | Show elapsed time after 30s |
| API request | Subtle spinner on affected component only | Show "Taking longer than expected" after 10s |

### Empty Tables

Tables never render as completely blank. When a table has no rows:
- Display column headers (preserved)
- Replace body with centered empty state row: icon + message + optional action
- Maintain table height (minimum 200px) to prevent layout shift

---

## 11. Responsive Design

### Breakpoints

| Name | Width | Primary Use |
|---|---|---|
| Desktop | ≥ 1440px | Full layout, all panels visible |
| Laptop | 1024px – 1439px | Full layout, slightly compressed cards |
| Tablet | 768px – 1023px | Collapsed sidebar (icon rail), stacked dashboard cards |
| Mobile | < 768px | Bottom navigation, single-column layout, simplified tables |

### Desktop (≥ 1440px)

- Full 240px sidebar with labels
- Dashboard: 4-column metric cards, 2-column charts
- Incident Detail: full tab bar, all columns in tables
- All features available

### Laptop (1024px – 1439px)

- Full sidebar
- Dashboard: 4-column metrics, charts stack if needed
- Incident Detail: full tabs, tables may scroll horizontally

### Tablet (768px – 1023px)

- Sidebar collapses to 64px icon rail (expand on hover or toggle)
- Dashboard: 2×2 metric card grid, charts full width
- Incident Detail: tab bar scrolls horizontally; tables show priority columns only
- Response Plan: action cards stack vertically

### Mobile (< 768px)

- Bottom navigation bar (5 items: Dashboard, Incidents, Investigation, Reports, Settings)
- Evaluation and About accessible via Settings or More menu
- Dashboard: single column, swipeable metric cards
- Incident Detail: tabs become a dropdown selector
- Response Plan: one action card per screen width, swipe to next
- Approval actions: full-width buttons at bottom of screen (sticky footer)
- Reports: single report variant per view, tab selector at top

**Mobile priority:** Read and approve workflows must be functional. Evaluation dashboard and detailed audit trail are lower priority on mobile — displayable but not optimized.

---

## 12. Accessibility

Oz AI targets **WCAG 2.1 Level AA** compliance for all MVP screens.

### Keyboard Navigation

| Action | Key |
|---|---|
| Navigate sidebar items | `Alt+1` through `Alt+7` |
| Navigate tabs (Incident Detail) | `Arrow Left` / `Arrow Right` |
| Activate focused element | `Enter` / `Space` |
| Close dialog | `Escape` |
| Approve focused action | `Enter` (when action card focused) |
| Skip to main content | `Skip link` (first focusable element on page) |

All interactive elements must be reachable and operable by keyboard alone. Focus order must follow visual reading order (left-to-right, top-to-bottom).

**Focus indicator:** 2px solid `color-primary` outline, 2px offset. Never remove focus outlines.

### ARIA

| Component | ARIA Requirements |
|---|---|
| Sidebar navigation | `<nav aria-label="Main navigation">` |
| Tab bar | `role="tablist"`, tabs with `aria-selected`, panels with `role="tabpanel"` |
| Severity badges | `aria-label="Severity: Critical"` (not color alone) |
| Pipeline stage indicator | `aria-label="Pipeline stage: MITRE Mapping, step 4 of 9"` |
| Loading skeletons | `aria-busy="true"`, `aria-label="Loading incident data"` |
| Toast notifications | `role="status"`, `aria-live="polite"` |
| Confirmation dialogs | `role="alertdialog"`, focus trapped inside |
| Data tables | `<th scope="col">`, sortable columns with `aria-sort` |
| Approval buttons | `aria-label="Approve action: Block source IP 192.168.1.1"` |

### Contrast

- All text meets WCAG AA contrast ratio: 4.5:1 for normal text, 3:1 for large text (≥ 18px or 14px bold).
- Severity badge text on badge backgrounds must meet 4.5:1.
- `severity-medium` (yellow) uses dark text (`#422006`) on light yellow background in both themes to maintain contrast.
- Interactive elements in disabled state must still meet 3:1 against background.

### Screen Reader

- Page title updates dynamically: `"INC-00142 — Response Plan — Oz AI"`
- Status changes announced via `aria-live` region: "Incident INC-00142 is now awaiting review"
- Pipeline progress updates announced at stage transitions (not every poll)
- Report export success/failure announced via toast with `aria-live="polite"`
- All icons used without visible text have `aria-label` or are `aria-hidden="true"` with adjacent text

---

## 13. UI Components

This section defines the reusable component library. Implementation will use React + TypeScript + Tailwind CSS. Component names here are specification labels, not code.

### Tables

| Property | Specification |
|---|---|
| Usage | Incident lists, audit trails, IOC tables, entity lists |
| Header | Sticky on scroll, uppercase column labels, sortable where noted |
| Rows | Hover highlight (`surface-overlay`), clickable rows navigate to detail |
| Row accent | 3px left border in severity color for incident tables |
| Pagination | Bottom pagination bar: "Showing 1–20 of 142" + page controls |
| Empty | See Empty Tables (Section 10) |
| Loading | Skeleton rows matching column count |
| Responsive | Priority columns on tablet; horizontal scroll with shadow indicator on mobile |

### Cards

| Variant | Usage |
|---|---|
| Metric Card | Dashboard summary numbers |
| Incident Card | Recent incidents, investigation workspace |
| Action Card | Response plan actions (most complex card) |
| Technique Card | MITRE ATT&CK technique display |
| Asset Card | System topology display |
| Report Card | Report preview with excerpt |

All cards use the card style defined in Section 2. Interactive cards have hover border accent.

### Badges

| Badge Type | Shape | Content |
|---|---|---|
| Severity | Pill | Uppercase text + optional icon |
| Status | Pill | Status name |
| Confidence | Pill | High / Medium / Low |
| Phase | Pill | Containment / Remediation / Recovery |
| Risk Level | Pill | Low / Medium / High / Critical |
| Event Type | Small pill | Audit event type |
| Guardian | Pill | Passed / Violation |

Badges always include text. Color is supplementary, never sole indicator.

### Timeline

| Property | Specification |
|---|---|
| Layout | Vertical timeline with connecting line (desktop); compact list (mobile) |
| Node | Circle marker — filled for confirmed events, dashed for gap markers |
| Content | Timestamp (left), event card (right) |
| MITRE annotation | Small badge below event description |
| Gap marker | Dashed node + italic "Evidence Gap" label |
| Uncertainty | Warning icon on timestamp |

### Charts

| Chart | Library (Implementation Reference) | Usage |
|---|---|---|
| Bar chart | Lightweight SVG or Recharts (requires ADR if added) | Severity distribution, latency breakdown |
| Donut chart | Same | Agent success rate |
| Sparkline | Same | Metric card trends |
| Histogram | Same | Latency distribution |

**Note:** The MVP stack excludes chart libraries by default. Charts may be implemented as styled CSS/SVG components. If a chart library is required, an ADR must be created before introduction.

### Dialogs

| Dialog | Trigger | Content |
|---|---|---|
| Confirm Approve All | "Approve All" button | List of all actions to be approved, Confirm / Cancel |
| Confirm Reject | "Reject" button | Reason textarea (required), Confirm / Cancel |
| Confirm Reject All | "Reject All" button | Reason textarea (required), list of affected actions |
| Session Expired | 401 response | API key re-entry form |

Dialogs are modal, focus-trapped, and close on `Escape` (except destructive confirmations — Escape maps to Cancel).

### Toast Notifications

| Type | Color | Duration | Example |
|---|---|---|---|
| Success | Green | 4 seconds | "Action approved successfully" |
| Error | Red | Persistent (manual dismiss) | "Failed to approve action. Please retry." |
| Warning | Amber | 6 seconds | "Evidence collection was incomplete" |
| Info | Blue | 4 seconds | "Report copied to clipboard" |

Position: bottom-right on desktop; bottom-center on mobile. Maximum 3 visible simultaneously.

### Progress Indicators

| Indicator | Usage |
|---|---|
| Pipeline Stage Bar | 6 specialist stages + Guardian validation |
| Tab Review Checklist | Overview tab — viewed/unviewed tab tracker |
| Loading Skeleton | All async content areas |
| Spinner | Inline button loading state (replaces button label) |
| Polling Indicator | Subtle pulse dot in header when active polling is running |

---

## 14. Future UI

The following UI capabilities are planned for post-MVP phases. They are documented here to guide architectural decisions and prevent MVP implementations that block future additions.

### Voice Interaction

- Spoken incident summary for on-call analysts ("Oz, summarize incident INC-00142")
- Voice-driven approval for low-risk containment actions (with explicit confirmation)
- Requires: speech-to-text integration, ADR, Guardian Agent validation of voice commands

### Live Pipeline Animation

- Real-time animated visualization of agent pipeline execution
- Agent nodes light up as each stage completes
- Tool call activity shown as animated edges
- Requires: WebSocket or Server-Sent Events (architectural change from polling — requires ADR)

### Realtime Updates

- Replace polling with WebSocket push for incident status changes
- Sub-second dashboard updates when pipeline stages complete
- Requires: WebSocket infrastructure (post-MVP, documented in `01_PROJECT_BRIEF.md` Future Roadmap)

### Dark / Light Theme Switch

- **Included in MVP** (see Section 9 — Theme settings)
- Future: system preference auto-detection (`prefers-color-scheme`)
- Future: scheduled theme switching for SOC shift changes

---

## 15. Screens

Complete inventory of every screen in the Oz AI MVP application.

| # | Screen Name | Route | Purpose | Primary User |
|---|---|---|---|---|
| 1 | **Access** | `/access` | API key entry and session establishment | All |
| 2 | **Dashboard** | `/` | Operational command center, metrics, recent activity | All |
| 3 | **Incident List** | `/incidents` | Searchable, filterable list of all incidents | Analyst, Engineer |
| 4 | **Incident Details** | `/incidents/{id}` | Full incident analysis with 9 tabs | Analyst, Engineer |
| 5 | **Investigation Workspace** | `/investigation` | Active investigation view; lists in-progress and awaiting-review incidents with quick tab access | Analyst, Engineer |
| 6 | **Reports** | `/reports` | Aggregate reporting, CISO metrics, report export | CISO, Manager |
| 7 | **Evaluation Dashboard** | `/evaluation` | Agent performance metrics and evaluation results | Engineer, Administrator |
| 8 | **Settings** | `/settings` | API key session, theme, model info, system status | Administrator |
| 9 | **About** | `/about` | Project information, competition context, documentation links, license | All |

### Screen Details

#### Access (`/access`)
- API key input, connect button, error state, documentation link
- Redirects to Dashboard on success
- Redirect target if user navigates here while session is valid

#### Dashboard (`/`)
- See Section 5

#### Incident List (`/incidents`)
- Full-page table with all filter and sort capabilities
- Supports URL query params: `?severity=critical&status=awaiting_review`
- Bulk actions: none in MVP (individual incident actions only)

#### Incident Details (`/incidents/{id}`)
- See Section 6
- 9 tabs: Overview, Evidence, Timeline, MITRE ATT&CK, Threat Intelligence, Risk Assessment, Response Plan, Guardian Report, Audit Trail

#### Investigation Workspace (`/investigation`)
- Focused view for analysts actively working incidents
- Split layout: incident queue (left, 320px) + active incident detail (right)
- Queue shows only `Active`, `AwaitingReview`, and `PartialPipelineWarning` incidents
- Selecting a queue item loads incident detail inline (no page navigation)
- Default tab: Overview

#### Reports (`/reports`)
- Date range selector
- Aggregate metrics cards
- Incident table with report links
- Per-incident report viewer modal (Technical / Executive / Compliance tabs)
- Export controls

#### Evaluation Dashboard (`/evaluation`)
- See Section 8

#### Settings (`/settings`)
- See Section 9
- Sections: API Keys, Model Selection, Theme, System Information

#### About (`/about`)
- Oz AI project name and subtitle
- Short project description (2–3 sentences)
- Competition context: Kaggle AI Agents Intensive Capstone, Agents for Business track
- Links to: GitHub repository, documentation (`docs/`), architecture overview
- License: MIT
- Version number (from backend system status)
- Credits / team information

---

## Appendix A — Consistency Review

This specification was reviewed against project documentation for consistency.

| Document | Alignment | Notes |
|---|---|---|
| `01_PROJECT_BRIEF.md` | ✅ Aligned | Safety statement (no autonomous destructive actions) reflected in Response Plan UX. Technology stack (React, TypeScript, Tailwind) respected. No excluded libraries introduced. |
| `02_ARCHITECTURE.md` | ✅ Aligned | Eight agents; timeline generated by Evidence Agent; Guardian tab; human approval gate in Response Plan tab. |
| `04_DECISIONS.md` | ✅ Aligned | ADR-003 documents Timeline Agent removal. |
| `06_PRODUCT_REQUIREMENTS.md` | ✅ Aligned | All user stories (US-001 through US-017) are supported by defined screens. Acceptance criteria AC-09 through AC-12 mapped to Incident List and Incident Detail screens. Failure flows from Section 8 reflected in Error States (Section 10). |
| `03_TASKS.md` | ✅ Aligned | Milestone 7 frontend tasks updated conceptually — Dashboard, Incident Board (now Incident List), Incident Detail tabs, Reports, Settings/System Health consolidated. Evaluation Dashboard aligns with Milestone 8. |
| `design/UI_WIREFRAMES.md` | ⚠️ Superseded | This document (`08_UI_UX_SPECIFICATION.md`) is now the authoritative UI reference. `UI_WIREFRAMES.md` remains as a diagram workspace but navigation and screen inventory defer to this spec. |

### Changes from Prior Documentation

The following intentional expansions were made relative to earlier docs:

1. **Navigation expanded** from 3 items (Incident Board, Reports, System Health) to 7 items (Dashboard, Incidents, Investigation, Reports, Evaluation, Settings, About).
2. **Dashboard** is now a distinct landing page with aggregate metrics, not just an incident list.
3. **Investigation Workspace** is a new split-pane screen for active analyst workflow.
4. **Evaluation Dashboard** is a new screen connecting to the evaluation harness.
5. **System Health** consolidated into Settings → System Information.
6. **Access screen** added for API key session management (consistent with Bearer token architecture).
7. **Agent Pipeline widget** added to Dashboard for live demo visibility of specialist agent progress.
8. **Timeline Agent removed** (ADR-003) — timeline generated by Evidence Agent; Timeline UI tab retained.
9. **Overview tab enriched** with AI Confidence, Investigation Duration, Processing Status, and Reports quick access.
10. **Share Link** added to Reports export options as a disabled future-feature button.

---

## Appendix B — Approval

| Role | Name | Date | Status |
|---|---|---|---|
| Product Design | — | — | Pending |
| UX Architecture | — | — | Pending |
| Engineering Lead | — | — | Pending |
| Chief Architect | — | — | Pending |

**This document is frozen upon approval. Changes require a design review and update to this specification before implementation.**

---

*End of UI/UX Specification — Oz AI v1.0 MVP*
