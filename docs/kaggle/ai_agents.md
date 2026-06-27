# AI Agents

Oz AI implements eight specialist agents under Google ADK configuration. Each agent has a single mission, defined input/output schemas, and a dedicated service layer. The Investigation Workflow invokes agents in sequence; individual agent endpoints allow isolated execution for testing and development.

---

## Coordinator Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Validate incident/log context and produce a structured orchestration plan defining the investigation workflow order |
| **Inputs** | `incident_id` (required), optional `log_id` via `POST /api/v1/agents/orchestrate` |
| **Outputs** | `OrchestrationPlan` — workflow ID, status, ordered agent list; persisted `AgentExecution` record |
| **AI or Rule Engine** | **Rule engine** — no LLM invocation |
| **Fallback behavior** | Returns validation errors when incident or log references are invalid; does not proceed without valid context |

**Implementation:** `agents/coordinator/`, `agents/coordinator/orchestrator.py`

---

## Evidence Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Collect, validate, normalize, and summarize uploaded log evidence without threat analysis |
| **Inputs** | `incident_id` via `POST /api/v1/agents/evidence` |
| **Outputs** | `evidence_summary`, `evidence_package` (line counts, log type, sample entries, timestamps); persisted `Evidence` record |
| **AI or Rule Engine** | **Rule engine** — deterministic log parsing for `.log`, `.txt`, `.json`, `.csv`; `.evtx` metadata only |
| **Fallback behavior** | Returns structured empty package with quality observations when logs are missing or unreadable |

**Supported formats:** `.log`, `.txt`, `.json`, `.csv`, `.evtx` (metadata)

**Implementation:** `agents/evidence/`, `agents/evidence/service.py`

---

## Threat Intelligence Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Extract indicators of compromise (IOCs) from evidence and enrich with reputation context and analyst notes |
| **Inputs** | `incident_id` via `POST /api/v1/agents/threat-intelligence` |
| **Outputs** | IOC list with reputation labels, descriptions, analyst notes; persisted `ThreatIntelligenceFinding` |
| **AI or Rule Engine** | **AI-first (Gemini JSON)** with **offline reputation engine** fallback |
| **Fallback behavior** | On quota, timeout, auth failure, or invalid JSON: `fallback.py` applies offline rules (private IP → Safe, suspicious URL → Suspicious, known hash → Malicious). Workflow never blocks |

**Offline rules:** `agents/threat_intelligence/reputation_engine.py`, `ioc_extractor.py`

**Implementation:** `agents/threat_intelligence/service.py`

---

## MITRE Mapping Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Map normalized evidence to MITRE ATT&CK techniques using local rule matching |
| **Inputs** | `incident_id` via `POST /api/v1/agents/mitre` |
| **Outputs** | `techniques[]` with `technique_id`, `technique_name`, `tactic`, `confidence`, `matched_evidence`; persisted `MitreFinding` records |
| **AI or Rule Engine** | **Rule engine** — local mappings in `mappings.py`, no external MITRE API, no LLM |
| **Fallback behavior** | Returns empty techniques array with `"No mapping found."` when no rules match |

**Example mappings:** PowerShell → T1059.001, ransomware → T1486, failed logins → T1110, credential dump → T1003

**Implementation:** `agents/mitre/`, `agents/mitre/mappings.py`

---

## Risk Assessment Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Produce structured enterprise risk assessment from incident, evidence, MITRE, and threat intelligence context |
| **Inputs** | `incident_id` via `POST /api/v1/agents/risk` |
| **Outputs** | Risk level, score, narrative, contributing factors; persisted `RiskAssessment` |
| **AI or Rule Engine** | **AI-first (Gemini JSON)** with **rule engine** fallback |
| **Fallback behavior** | `fallback.py` assigns Critical/High/Medium/Low based on severity, ransomware (T1486), technique count, and PowerShell patterns. Always returns valid assessment |

**Implementation:** `agents/risk/service.py`, `agents/risk/fallback.py`

---

## Response Planning Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Draft structured incident response plan — containment, eradication, recovery, monitoring — recommendations only, never execution |
| **Inputs** | `incident_id` via `POST /api/v1/agents/response` |
| **Outputs** | Priority, containment, eradication, recovery, monitoring, executive summary; persisted `ResponsePlan` |
| **AI or Rule Engine** | **AI-first (Gemini JSON)** with **playbook** fallback |
| **Fallback behavior** | `fallback.py` selects scenario playbooks (ransomware/T1486, PowerShell/T1059.001, brute force/T1110, generic). Always returns valid plan |

**Implementation:** `agents/response/service.py`, `agents/response/fallback.py`

---

## Executive Report Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Transform technical investigation outputs into executive-friendly JSON and Markdown reports for leadership |
| **Inputs** | `incident_id` via `POST /api/v1/agents/executive-report` |
| **Outputs** | Structured sections (executive summary, business impact, timeline summary, findings, MITRE summary, risk summary, actions, lessons learned) plus Markdown; persisted `ExecutiveReport` |
| **AI or Rule Engine** | **AI-first (Gemini JSON)** with **template engine** fallback |
| **Fallback behavior** | `fallback.py` generates complete report from templates; `markdown_generator.py` produces Markdown. No raw logs in output. Always returns valid report |

**Implementation:** `agents/executive_report/service.py`, `agents/executive_report/fallback.py`

---

## Guardian Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Validate specialist agent outputs for security, governance, schema compliance, prompt injection, secret exposure, PII leakage, and confidence thresholds |
| **Inputs** | Agent name, output payload via `POST /api/v1/agents/guardian/validate`; also invoked automatically between workflow stages |
| **Outputs** | Validation status (`approved`, `warning`, `rejected`), findings list, masked values; persisted `GuardianAudit` |
| **AI or Rule Engine** | **Rule engine** — pattern-based injection detection, PII/secret scanners, schema validation |
| **Fallback behavior** | When `GUARDIAN_ENABLED=false`, validation is bypassed. Rejected outputs signal workflow to accept fallback paths; audits are always persisted |

**Configuration:** `GUARDIAN_ENABLED`, `MIN_AI_CONFIDENCE`, `MASK_SECRETS`, `MASK_PII`

**Implementation:** `agents/guardian/validator.py`, `backend/app/services/orchestration_guardian.py`

---

## Non-agent engines

| Engine | Role | Location |
|--------|------|----------|
| Timeline Engine | Reconstruct chronological incident timeline from agent outputs | `backend/app/services/timeline/` |
| Evaluation Engine | Score agent outputs, persist metrics, surface health dashboard | `evaluation/`, `GET /api/v1/evaluation` |

## Agent inventory summary

| Agent | AI | Fallback | Persisted table |
|-------|-----|----------|-----------------|
| Coordinator | No | Validation errors | `agent_executions` |
| Evidence | No | Empty package | `evidence` |
| Threat Intelligence | Gemini | Offline reputation | `threat_intelligence_findings` |
| MITRE | No | Empty techniques | `mitre_findings` |
| Risk | Gemini | Rule scoring | `risk_assessments` |
| Response | Gemini | Playbooks | `response_plans` |
| Executive Report | Gemini | Templates | `executive_reports` |
| Guardian | No | Bypass if disabled | `guardian_audits` |
