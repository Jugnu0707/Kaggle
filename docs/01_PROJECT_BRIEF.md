# 01 — Project Brief

**Project Name:** Oz AI
**Subtitle:** Autonomous Enterprise Incident Response Platform
**Version:** 1.0 (MVP)
**Competition:** Kaggle — AI Agents Intensive Capstone
**Track:** Agents for Business
**Date:** 2026-06-26
**Status:** Architecture Frozen — Pre-Development

---

## Table of Contents

1. [Project Vision](#1-project-vision)
2. [Mission Statement](#2-mission-statement)
3. [Competition Alignment](#3-competition-alignment)
4. [Competition Requirements Mapping](#4-competition-requirements-mapping)
5. [Problem Statement](#5-problem-statement)
6. [Why This Problem Matters](#6-why-this-problem-matters)
7. [Goals](#7-goals)
8. [Non-Goals](#8-non-goals)
9. [Target Users](#9-target-users)
10. [User Personas](#10-user-personas)
11. [Business Value](#11-business-value)
12. [Success Criteria](#12-success-criteria)
13. [Technology Stack](#13-technology-stack)
14. [Engineering Principles](#14-engineering-principles)
15. [Coding Standards](#15-coding-standards)
16. [Repository Principles](#16-repository-principles)
17. [Git Strategy](#17-git-strategy)
18. [Future Roadmap](#18-future-roadmap)

---

## Safety Statement

> **Oz AI NEVER performs destructive actions automatically.**
>
> Every critical recommendation — including incident containment actions, system changes, and stakeholder notifications — requires explicit human approval before execution. The platform is a decision support system and a force multiplier for human engineers. It does not act autonomously on consequential decisions under any circumstances.
>
> This principle is non-negotiable and is enforced at the architectural level by the Guardian Agent and the human-in-the-loop approval gate built into the Response Planning workflow.

---

## 1. Project Vision

Oz AI is an autonomous, multi-agent platform that transforms enterprise incident response from a reactive, manual discipline into a proactive, AI-driven workflow. When a security or operational incident occurs, Oz AI detects it, gathers evidence, maps it to known threat frameworks, reconstructs a timeline, assesses risk, generates a response plan, and produces audience-appropriate reports — all within minutes, not hours.

The platform is designed for the modern enterprise: organizations that operate distributed systems, face sophisticated threats, and cannot afford the delays that manual incident triage has historically required. Oz AI acts as an always-on, tireless first responder that elevates the work of security and operations engineers — returning control and clarity to human decision-makers at the decisive moment.

---

## 2. Mission Statement

To reduce enterprise mean-time-to-respond (MTTR) to security and operational incidents by deploying a coordinated fleet of AI agents that autonomously detect, investigate, and structure responses — while keeping humans firmly in control of every consequential decision.

---

## 3. Competition Alignment

**Competition:** Kaggle — AI Agents Intensive Capstone
**Track:** Agents for Business

Oz AI is purpose-built to demonstrate mastery of the Kaggle competition's core evaluation dimensions. Every architectural decision — from agent design to tool layer implementation to evaluation strategy — is made with this alignment in mind.

| Evaluation Dimension | Oz AI Response |
|---|---|
| **Real-world business impact** | Targets enterprise incident response — a documented, multi-billion-dollar problem with measurable MTTR improvement |
| **Multi-agent coordination** | Eight specialized agents operating under a Coordinator in a directed, state-managed pipeline |
| **Google ADK usage** | All agent orchestration is built natively on Google Agent Development Kit |
| **MCP tool use** | All agent-to-system interactions are mediated by MCP tool servers |
| **Human-in-the-loop design** | Explicit human approval gates enforced by the Guardian Agent before any consequential action |
| **Security and safety** | Guardian Agent provides prompt injection detection, PII scanning, and output validation |
| **Evaluation pipeline** | Structured scenario-based evaluation with precision/recall metrics for agent outputs |
| **Deployability** | Single `docker compose up` command; self-contained environment |

---

## 4. Competition Requirements Mapping

This section maps each explicit competition requirement to the corresponding Oz AI implementation.

### Google ADK

Oz AI's entire agent orchestration layer is built on the Google Agent Development Kit. The Coordinator Agent is implemented as an ADK orchestrator. All eight specialist agents are implemented as ADK `LlmAgent` instances. ADK session management handles state persistence across the agent pipeline.

**Implementation location:** `agents/`

### MCP (Model Context Protocol)

All agent-to-external-system interactions — log queries, threat intelligence lookups, knowledge base searches, MITRE ATT&CK queries, audit writes, and notification dispatch — are implemented as MCP tools registered with the ADK runtime. No agent contains direct I/O logic.

**Implementation location:** `mcp/`

### Multi-Agent Architecture

Oz AI deploys eight specialized agents in a coordinated pipeline:
1. Coordinator Agent
2. Evidence Agent (includes timeline generation)
3. Threat Intelligence Agent
4. MITRE Mapping Agent
5. Risk Assessment Agent
6. Response Planning Agent
7. Executive Report Agent
8. Guardian Agent

Each agent has a single, well-defined mission and communicates exclusively through the ADK session state and MCP tool layer.

**Implementation location:** `agents/`

### Security and Responsible AI

The Guardian Agent is a dedicated safety layer responsible for:
- Detecting prompt injection attempts in incoming alert payloads.
- Scanning agent outputs for accidental PII exposure before surfacing to the frontend.
- Validating that tool calls are within each agent's permitted scope.
- Enforcing the human approval gate before any action in the `ResponsePlan` is marked as executable.
- Validating that final outputs meet safe-to-display criteria.

**Implementation location:** `agents/guardian_agent/`

### Evaluation

A dedicated evaluation harness runs synthetic incident scenarios against the full agent pipeline and produces quantitative metrics: triage precision/recall, MITRE mapping accuracy, timeline reconstruction quality, and response plan relevance. ADK Eval tooling is used for scenario-based pipeline validation.

**Implementation location:** `evaluation/`

### Deployability

The full system — backend API, frontend dashboard, and agent runtime — is containerized and orchestrated by Docker Compose. A fresh deployment from a clean environment requires only:
```
cp .env.example .env   # fill in API keys
docker compose up
```

**Implementation location:** `docker/`, `docker-compose.yml`

### Human in the Loop

The frontend dashboard presents every incident with its full agent analysis. The Response Planning workflow includes an explicit approval gate: no action from the `ResponsePlan` advances to an executable state without a human reviewer approving it in the dashboard. This gate is enforced at both the API layer and the Guardian Agent layer.

**Implementation location:** `frontend/`, `backend/api/`, `agents/guardian_agent/`

---

## 5. Problem Statement

Enterprise organizations are drowning in alerts. Security Operations Centers (SOCs) and Site Reliability Engineering (SRE) teams face thousands of events per day across disparate tools: SIEM platforms, cloud provider logs, APM dashboards, ticketing systems, and communication channels. The human cost of manually correlating, investigating, and responding to each event is unsustainable.

The core dysfunctions are:

- **Alert fatigue:** Engineers tune out high-volume, low-signal alerts, causing real threats to be missed.
- **Siloed tooling:** Incident data lives in dozens of disconnected systems. Correlation requires human effort spanning multiple tools and teams.
- **Slow triage:** Average enterprise MTTR for a security incident ranges from hours to days. Each minute of exposure increases blast radius and regulatory liability.
- **Knowledge bottlenecks:** Institutional knowledge of system architecture and past incidents lives in the heads of senior engineers who are not always available during off-hours incidents.
- **Inconsistent process:** Without automation, incident response quality varies dramatically based on who is on-call and their experience level.
- **Framework gaps:** Most teams lack the tooling to systematically map observed attacker behaviors to frameworks like MITRE ATT&CK, leading to incomplete threat characterization.

Oz AI addresses all six dysfunctions through a coordinated fleet of specialized AI agents that work continuously, consistently, and in parallel.

---

## 6. Why This Problem Matters

### Business Impact

The average cost of a data breach in 2025 was $4.88 million USD (IBM Cost of a Data Breach Report). Organizations with mature AI-assisted incident response capabilities reduced breach costs by an average of $2.2 million compared to organizations without automation. Every minute of reduced MTTR translates directly to reduced blast radius and lower remediation cost.

### Regulatory Pressure

Frameworks such as SOC 2, ISO 27001, GDPR, HIPAA, and NIS2 mandate documented, timely incident response processes. Manual processes create audit gaps. Oz AI's automated agent pipeline produces a traceable, time-stamped evidence chain and structured incident record that satisfies regulatory documentation requirements.

### Workforce Reality

The global cybersecurity workforce gap exceeds 4 million unfilled positions. Organizations cannot hire their way out of this problem. AI agents are not a replacement for skilled engineers — they are a force multiplier that allows existing teams to operate at a higher level of abstraction. Oz AI handles the evidence gathering and initial analysis that consumes the majority of a Tier 1 analyst's time, freeing that analyst for higher-order judgment.

### Operational Complexity

Modern enterprises run polyglot stacks across multi-cloud, on-premise, and edge environments. The combinatorial complexity of monitoring all inter-system interactions exceeds what any human team can manage manually at scale. Structured AI analysis of this complexity is no longer optional for organizations with serious security postures.

---

## 7. Goals

### Primary Goals (MVP)

1. **Automated Evidence Collection:** Ingest structured alert payloads and automatically gather correlated evidence from simulated log and alert sources via the Evidence Agent.
2. **Threat Intelligence Enrichment:** Enrich evidence with threat context — known IOCs, threat actor associations, and historical campaign data — via the Threat Intelligence Agent.
3. **MITRE ATT&CK Mapping:** Map observed attacker behaviors to the MITRE ATT&CK framework (Tactics, Techniques, Sub-techniques) via the MITRE Mapping Agent.
4. **Timeline Reconstruction:** Reconstruct a chronological, structured timeline of the incident from correlated evidence via the Evidence Agent (displayed in the Timeline UI tab).
5. **Risk Assessment:** Assess the incident's severity, blast radius, affected asset criticality, and regulatory exposure via the Risk Assessment Agent.
6. **Response Planning:** Generate a ranked, human-reviewable response plan with risk annotations for each proposed action via the Response Planning Agent.
7. **Audience-Appropriate Reporting:** Produce technical, executive, and compliance-oriented incident reports via the Executive Report Agent.
8. **Guardian Safety Layer:** Validate all inputs and outputs for safety, PII, and authorization via the Guardian Agent.
9. **Human-in-the-Loop Enforcement:** Provide a dashboard where engineers can review, approve, override, or reject agent-recommended actions before any action advances.
10. **Immutable Audit Trail:** Maintain a full, append-only log of every agent decision, tool call, and human action for post-incident review and regulatory compliance.

### Secondary Goals

1. Demonstrate production-quality multi-agent coordination using Google ADK.
2. Expose a clean, well-documented REST API for integration with external tooling.
3. Build a professional-grade frontend dashboard for incident visualization and analyst workflow.
4. Implement a rigorous evaluation pipeline measuring agent output quality across all pipeline stages.

---

## 8. Non-Goals

The following are explicitly out of scope for the MVP:

- **Autonomous remediation execution:** Oz AI will never autonomously execute system changes, firewall modifications, credential rotations, or any other environment-affecting action. Response plans are always advisory and always require human approval.
- **Real-time event streaming:** The MVP uses webhook and REST API ingestion. Kafka, Kinesis, or other streaming infrastructure is post-MVP.
- **Multi-tenant SaaS architecture:** The MVP is single-tenant. Tenant isolation and billing infrastructure are post-MVP.
- **Commercial SIEM native connectors:** Out-of-the-box connectors for Splunk, CrowdStrike, or Microsoft Sentinel are post-MVP. The MVP uses a generic API ingestion contract.
- **Custom LLM fine-tuning:** The MVP relies on foundation model APIs. Fine-tuning on organization-specific data is post-MVP.
- **Mobile application:** No mobile interface is planned for the MVP.
- **Live threat intelligence feeds:** The MVP uses a static or locally hosted knowledge base. Live API integrations with commercial threat intel providers (VirusTotal, Shodan, etc.) are post-MVP.

---

## 9. Target Users

| User Type | Role | Interaction Mode |
|---|---|---|
| Security Analyst (Tier 1) | Reviews agent analysis, approves/rejects response plans | Dashboard — read-heavy |
| Security Engineer (Tier 2/3) | Configures agent behavior, investigates escalated incidents | Dashboard + API |
| SRE / DevOps Engineer | Monitors operational incidents, integrates with deployment pipelines | API + Dashboard |
| CISO / Security Manager | Reviews summary dashboards, exports compliance reports | Dashboard — summary views |
| Platform Administrator | Manages agent configuration, secret rotation, integrations | Admin panel + config files |

---

## 10. User Personas

### Persona 1 — Alex, Tier 1 SOC Analyst

**Age:** 27 | **Experience:** 2 years in security operations

**Context:** Alex handles Level 1 triage at a mid-size fintech company. Their queue contains 300–500 alerts per shift. They rely on runbooks but are often uncertain about context when alerts are ambiguous.

**Pain Points:**
- Spends 60% of shift reviewing alerts that turn out to be false positives.
- Lacks context about system topology when investigating unfamiliar services.
- Cannot consistently map incidents to MITRE ATT&CK without senior guidance.

**How Oz AI Helps:**
- Delivers a fully analyzed incident with evidence, threat intel enrichment, MITRE mapping, and timeline — before Alex touches the alert.
- Presents a ranked response plan so Alex approves rather than creates.
- Provides a plain-language executive summary and a technical report in the same interface.

---

### Persona 2 — Priya, Senior Security Engineer

**Age:** 34 | **Experience:** 8 years in application security and incident response

**Context:** Priya is on-call every third week at a large SaaS company. She is responsible for P1 incident ownership and post-incident reviews.

**Pain Points:**
- On-call interruptions at 2 AM with incomplete alert context.
- Manually correlating logs from five different systems to understand blast radius.
- Writing post-mortem reports from scratch under time pressure.

**How Oz AI Helps:**
- Receives a structured incident briefing when paged, including correlated evidence, a MITRE ATT&CK mapping, a risk assessment, and a reconstructed timeline.
- Queries the agent audit trail to reconstruct investigation steps for the post-mortem.
- Reviews and approves response steps rather than designing them under stress.

---

### Persona 3 — Marcus, CISO

**Age:** 51 | **Experience:** 20 years in information security leadership

**Context:** Marcus oversees security posture for a healthcare organization subject to HIPAA. He needs demonstrable incident response processes for auditors and board reporting.

**Pain Points:**
- Cannot get consistent, quantitative MTTR metrics from his team.
- Audit preparation requires manual aggregation of evidence from multiple systems.
- Board-level reporting requires translating technical incidents into business impact narratives.

**How Oz AI Helps:**
- Provides a real-time and historical dashboard of incident volume, severity, MTTR, and resolution rates.
- Generates audit-ready incident reports with full decision timelines and Guardian Agent safety validation.
- The Executive Report Agent produces board-ready plain-language summaries alongside the technical record.

---

## 11. Business Value

### Quantifiable Value

| Metric | Without Oz AI | With Oz AI (Projected MVP) |
|---|---|---|
| Mean Time to Triage | 45–90 minutes | 2–5 minutes |
| MITRE ATT&CK Mapping | Manual, requires senior analyst | Automated by MITRE Mapping Agent |
| Incident Timeline Reconstruction | 1–3 hours (manual) | Generated by Evidence Agent |
| Incident Documentation Time | 2–4 hours (manual) | Generated from audit trail |
| Response Plan Creation | Manual, variable quality | Structured, risk-annotated, agent-generated |
| Executive Reporting | Ad hoc, hours of effort | Generated by Executive Report Agent |

### Qualitative Value

- **Engineer retention:** Reducing alert fatigue and improving on-call experience directly improves retention of security talent.
- **Consistent process quality:** Agent-driven analysis follows the same investigation logic regardless of time of day or on-call engineer experience.
- **Institutional knowledge capture:** Agent behavior operationalizes the runbook knowledge that currently exists only in senior engineers' heads.
- **Audit readiness:** The immutable audit trail and structured incident records satisfy regulatory documentation requirements continuously, not just at audit time.

---

## 12. Success Criteria

### MVP Success Criteria

The MVP is considered successful when:

1. A simulated incident payload submitted via the API results in a fully populated incident record — evidence, threat intel, MITRE mapping, timeline, risk assessment, response plan, and executive report — within 90 seconds.
2. The Coordinator Agent correctly routes sub-tasks to the appropriate specialist agents in 90%+ of test cases.
3. The MITRE Mapping Agent correctly maps at least one relevant ATT&CK technique in 80%+ of evaluation scenarios.
4. The Guardian Agent detects prompt injection patterns in 90%+ of synthetic injection test cases.
5. The human-in-the-loop dashboard renders all active incidents with full agent analysis and allows approve/reject actions on response plans.
6. All agent decisions, tool calls, and human approvals are logged to the audit trail with timestamps.
7. The full system deploys from `docker compose up` in a clean environment with no additional configuration beyond `.env`.

### Stretch Success Criteria

1. An evaluation harness runs 30 synthetic incident scenarios and produces precision/recall metrics for MITRE mapping and risk assessment classification.
2. An executive summary report can be exported for a given time window.

---

## 13. Technology Stack

The MVP technology stack is intentionally minimal. Complexity is the enemy of a competition deadline and a clean evaluation. Every library in this stack is justified.

### Backend

| Component | Technology | Justification |
|---|---|---|
| Language | Python 3.12 | AI/ML ecosystem lingua franca; ADK is Python-native |
| API Framework | FastAPI | Async-native, automatic OpenAPI docs, strong Pydantic integration |
| Agent Framework | Google ADK | Competition-required; purpose-built for multi-agent coordination |
| Agent LLM | Google Gemini (via ADK) | Native ADK integration; state-of-the-art reasoning |
| Data Validation | Pydantic v2 | Type-safe request/response modeling; ADK schema integration |
| ORM | SQLAlchemy (async) | Database-agnostic; supports SQLite→PostgreSQL migration |
| Database | SQLite | Zero-infrastructure overhead for MVP |
| Tool Layer | MCP (Model Context Protocol) | Standardized, auditable agent-to-tool interface |

### Frontend

| Component | Technology | Justification |
|---|---|---|
| Framework | React 19 + TypeScript | Mature, typed, component-based UI |
| Styling | Tailwind CSS | Utility-first; fast iteration; no component library lock-in |
| Build Tool | Vite | Fast dev server; modern bundling |

### Infrastructure

| Component | Technology | Justification |
|---|---|---|
| Containerization | Docker | Reproducible builds; clean isolation |
| Orchestration | Docker Compose | Single-command local deployment |

### Explicitly Excluded from MVP

The following are explicitly **not** part of the MVP stack. Any proposal to introduce these requires a new ADR:

- Celery, Redis, RabbitMQ, Kafka (task queuing / streaming)
- React Query, Zustand, Zod (frontend state/validation libraries)
- Structlog, OpenTelemetry (observability frameworks)
- Kubernetes, Nginx, Caddy (production infrastructure)
- Any additional Python or Node package not listed above

---

## 14. Engineering Principles

1. **Clarity over cleverness.** Code should be readable by any engineer on the team without explanation. Prefer explicit over implicit.
2. **Modularity first.** Each agent, MCP tool, and service module is independently testable and has a single, clear responsibility.
3. **Fail safely.** When an agent cannot complete a task, it returns a structured error result. The Guardian Agent validates all outputs before they are surfaced. Human review is always the fallback.
4. **Human oversight is non-negotiable.** No consequential action is taken without passing through the human approval gate. This is an architectural invariant, not a preference.
5. **Audit everything.** Every agent action, tool call, LLM invocation, and human decision is logged with a timestamp, actor identity, and outcome. The audit trail is the system of record.
6. **Configuration over hardcoding.** All environment-specific values — API keys, endpoints, thresholds — are configurable via environment variables. Nothing is hardcoded.
7. **Security is a first-class concern.** Secrets are never logged, committed, or hardcoded. The Guardian Agent validates inputs and outputs at the agent layer. Pydantic validates all external inputs at the API layer.
8. **Test at every layer.** Unit tests for business logic, integration tests for agent workflows, and end-to-end tests for critical user journeys are all required — not optional.
9. **No new dependencies without approval.** Adding a library introduces risk: security vulnerabilities, version conflicts, maintenance burden. Every addition must be justified and recorded in `04_DECISIONS.md`.

---

## 15. Coding Standards

### Python

- Target **Python 3.12+**.
- **Type hints** on all function signatures, class attributes, and return types. No untyped code.
- Use **Pydantic v2** for all data models and API schemas.
- Follow **PEP 8** with a maximum line length of 100 characters.
- Use `black` for formatting and `ruff` for linting. Both run in CI.
- Prefer `async/await` throughout the backend; avoid blocking I/O in async contexts.
- Docstrings follow **Google style** for all public functions and classes.
- No bare `except` clauses; always catch specific exception types.
- No `Any` type unless absolutely unavoidable; add a comment explaining why.

### TypeScript / React

- Use **strict TypeScript** mode (`"strict": true` in `tsconfig.json`).
- Components are **functional** with React hooks. No class components.
- All props typed with explicit interfaces. Never use `any`.
- Follow **component co-location**: a component's types and local utilities live adjacent to the component file.

### General

- No commented-out code in commits. Use version control.
- No `TODO` comments merged without an associated task in `03_TASKS.md`.
- Meaningful variable and function names. Abbreviations only when universally understood.
- Comments explain **why**, never **what**. The code explains what.
- Functions do one thing. If a function requires a multi-line comment to explain what it does, it should be split.

---

## 16. Repository Principles

- **Monorepo:** All components live in a single repository for the MVP.
- **Never rename top-level folders** without updating all documentation and creating an ADR.
- **`.env` is never committed.** `.env.example` with all required keys (no values) is always current.
- **Dependencies are pinned.** No open-ended version ranges in `pyproject.toml` or `package.json`.
- **Documentation is updated in the same PR as the code it describes.** Not separately, not later.
- **`05_PROGRESS.md` is updated at the end of every working session.**
- **`04_DECISIONS.md` is updated whenever any architectural or technology decision is made.**

---

## 17. Git Strategy

### Branch Strategy

| Branch | Purpose | Rules |
|---|---|---|
| `main` | Production-ready, always deployable | Protected; only merges from `release/*` or emergency `hotfix/*` |
| `develop` | Integration branch for completed features | Protected; only merges from `feature/*` or `bugfix/*` via PR |
| `feature/<task-id>-short-description` | Individual feature or task development | Created from `develop`; merged to `develop` via PR |
| `bugfix/<issue-id>-short-description` | Bug fixes against `develop` | Created from `develop`; merged to `develop` via PR |
| `release/<version>` | Release preparation and final testing | Created from `develop`; merged to `main` and `develop` |

**Examples:**
- `feature/M2-T01-incident-orm-model`
- `feature/M5-T05-evidence-agent`
- `bugfix/42-guardian-pii-false-positive`
- `release/1.0.0`

### Commit Convention

All commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to Use |
|---|---|
| `feat:` | A new feature or agent capability |
| `fix:` | A bug fix |
| `docs:` | Documentation-only changes |
| `refactor:` | Code restructuring without behavior change |
| `test:` | Adding or updating tests |
| `style:` | Formatting, linting (no logic changes) |
| `chore:` | Build scripts, dependency updates, CI config |

**Format:** `<type>(<scope>): <description>`
**Example:** `feat(M5-T05): implement evidence agent with log query tool integration`

The commit body must reference the task ID: `Resolves M5-T05`.

### Semantic Versioning

The project follows [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

- **MAJOR:** Breaking API or architectural change.
- **MINOR:** New feature, new agent, new API endpoint (backward-compatible).
- **PATCH:** Bug fix, documentation update, minor improvement.

The MVP release target is `v1.0.0`.

---

## 18. Future Roadmap

### Phase 2 — Autonomous Remediation (Post-MVP)
- Introduce an Execution Agent capable of running pre-approved playbook actions with cryptographic approval signing.
- Integrate with cloud provider APIs (AWS, GCP, Azure) for automated response.

### Phase 3 — Live Threat Intelligence
- Connect the Threat Intelligence Agent to live external feeds (VirusTotal, Shodan, MISP).
- Correlate internal incidents against live threat actor campaign data.

### Phase 4 — Predictive Posture Management
- Deploy a Posture Agent that continuously evaluates configuration drift and exposure surface changes.
- Shift from reactive incident response to proactive risk reduction.

### Phase 5 — Multi-Tenant SaaS
- Introduce tenant isolation at database, agent, and API layers.
- Self-service onboarding, usage-based billing, and entitlement management.

### Phase 6 — Compliance Automation
- Automated evidence collection for SOC 2, ISO 27001, HIPAA, and GDPR audits.
- Continuous compliance scoring dashboards.
- Audit report generation tied to real incident timelines and Guardian Agent validation records.
