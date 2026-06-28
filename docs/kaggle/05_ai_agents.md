# AI Agents

**Related:** [02 Solution](02_solution.md) · [03 Architecture](03_architecture.md) · [06 Security](06_security.md)

Oz AI implements eight specialist agents under Google ADK configuration. Each agent has a single mission, defined input/output schemas, and a dedicated service layer. The Investigation Workflow invokes agents in sequence; individual agent endpoints allow isolated execution for testing.

Full investigation trigger: `POST /api/v1/investigations/run`

---

## Coordinator Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Validate incident/log context and produce a structured orchestration plan |
| **Inputs** | `incident_id` (required), optional `log_id` |
| **Outputs** | `OrchestrationPlan` — workflow ID, status, ordered agent list; persisted `AgentExecution` |
| **AI or Rule Engine** | Rule engine — no LLM invocation |
| **Fallback** | Returns validation errors when references are invalid; does not proceed |
| **API Endpoint** | `POST /api/v1/agents/orchestrate` |

Implementation: `agents/coordinator/`, `agents/coordinator/orchestrator.py`

---

## Evidence Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Collect, validate, normalize, and summarize uploaded log evidence without threat analysis |
| **Inputs** | `incident_id`, optional `log_file_id` |
| **Outputs** | `evidence_summary`, `evidence_package`; persisted `Evidence` |
| **AI or Rule Engine** | Rule engine — parsing for `.log`, `.txt`, `.json`, `.csv`; `.evtx` metadata only |
| **Fallback** | Structured empty package with quality observations when logs are missing |
| **API Endpoint** | `POST /api/v1/agents/evidence` |

Implementation: `agents/evidence/service.py`

---

## Threat Intelligence Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Extract IOCs and enrich with reputation context and analyst notes |
| **Inputs** | `incident_id` or evidence package from prior stage |
| **Outputs** | IOC list with reputation labels; persisted `ThreatIntelligenceFinding` |
| **AI or Rule Engine** | AI-first (Gemini JSON) with offline reputation engine fallback |
| **Fallback** | Offline rules via `reputation_engine.py` and `fallback.py`; workflow never blocks |
| **API Endpoint** | `POST /api/v1/agents/threat-intelligence` |

Implementation: `agents/threat_intelligence/service.py`

---

## MITRE Mapping Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Map normalized evidence to MITRE ATT&CK techniques via local rule matching |
| **Inputs** | `incident_id` or evidence package |
| **Outputs** | `techniques[]` with ID, name, tactic, confidence; persisted `MitreFinding` |
| **AI or Rule Engine** | Rule engine — `mappings.py`, no external MITRE API |
| **Fallback** | Empty techniques array when no rules match |
| **API Endpoint** | `POST /api/v1/agents/mitre` |

Example mappings: PowerShell → T1059.001, ransomware → T1486, brute force → T1110

Implementation: `agents/mitre/mappings.py`

---

## Risk Assessment Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Produce structured enterprise risk assessment from investigation context |
| **Inputs** | `incident_id` |
| **Outputs** | Risk level, score, narrative; persisted `RiskAssessment` |
| **AI or Rule Engine** | AI-first (Gemini JSON) with rule engine fallback |
| **Fallback** | Severity, ransomware (T1486), technique count, PowerShell pattern scoring |
| **API Endpoint** | `POST /api/v1/agents/risk` |

Implementation: `agents/risk/service.py`, `agents/risk/fallback.py`

---

## Response Planning Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Draft containment, eradication, recovery, monitoring — recommendations only |
| **Inputs** | `incident_id` |
| **Outputs** | Priority, containment, eradication, recovery, monitoring; persisted `ResponsePlan` |
| **AI or Rule Engine** | AI-first (Gemini JSON) with playbook fallback |
| **Fallback** | Scenario playbooks for ransomware, PowerShell, brute force, generic incidents |
| **API Endpoint** | `POST /api/v1/agents/response` |

Implementation: `agents/response/service.py`, `agents/response/fallback.py`

---

## Executive Report Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Transform investigation outputs into executive JSON and Markdown reports |
| **Inputs** | `incident_id` |
| **Outputs** | Structured sections plus Markdown; persisted `ExecutiveReport` |
| **AI or Rule Engine** | AI-first (Gemini JSON) with template engine fallback |
| **Fallback** | Template-based report via `fallback.py`; no raw logs in output |
| **API Endpoint** | `POST /api/v1/agents/executive-report` |

Implementation: `agents/executive_report/service.py`, `agents/executive_report/fallback.py`

---

## Guardian Agent

| Attribute | Detail |
|-----------|--------|
| **Responsibility** | Validate outputs for security, schema compliance, injection, PII, secrets, confidence |
| **Inputs** | Agent name, output payload; invoked automatically between workflow stages |
| **Outputs** | Status (`approved`, `warning`, `rejected`); persisted `GuardianAudit` |
| **AI or Rule Engine** | Rule engine — pattern scanners and schema validation |
| **Fallback** | Bypass when `GUARDIAN_ENABLED=false`; rejection triggers agent fallback path |
| **API Endpoint** | `POST /api/v1/agents/guardian/validate` |

Implementation: `agents/guardian/validator.py`, `backend/app/services/orchestration_guardian.py`

---

## Non-agent engines

| Engine | Role | API |
|--------|------|-----|
| Timeline Engine | Reconstruct chronological events from agent outputs | Generated during workflow |
| Evaluation Engine | Score agent performance, persist metrics | `GET /api/v1/evaluation` |

---

## Agent summary

| Agent | AI | Fallback | Table |
|-------|-----|----------|-------|
| Coordinator | No | Validation errors | `agent_executions` |
| Evidence | No | Empty package | `evidence` |
| Threat Intelligence | Gemini | Offline reputation | `threat_intelligence_findings` |
| MITRE | No | Empty techniques | `mitre_findings` |
| Risk | Gemini | Rule scoring | `risk_assessments` |
| Response | Gemini | Playbooks | `response_plans` |
| Executive Report | Gemini | Templates | `executive_reports` |
| Guardian | No | Bypass if disabled | `guardian_audits` |

Per-agent README files: `agents/*/README.md`
