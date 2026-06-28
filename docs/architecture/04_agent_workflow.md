# Agent Workflow

**Related:** [Component Diagram](02_component_diagram.md) · [Sequence Diagram](03_sequence_diagram.md) · [ADK Runtime](07_adk_runtime.md) · [Security Architecture](08_security_architecture.md)

Oz AI implements eight specialist agents orchestrated by the Coordinator. Guardian validates outputs between stages. Timeline and Evaluation are post-pipeline engines, not ADK agents.

---

## Pipeline Order

```text
Coordinator → Evidence → Guardian → Threat Intelligence → Guardian → MITRE → Guardian
  → Risk → Guardian → Response → Guardian → Executive Report → Guardian
  → Timeline Engine → Evaluation Engine
```

Full investigation trigger: `POST /api/v1/investigations/run`

---

## Coordinator Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Validate incident and log context; produce a structured orchestration plan |
| **Inputs** | `incident_id` (required), optional `log_id` |
| **Outputs** | `OrchestrationPlan` — workflow ID, status, ordered agent list |
| **AI or Rule Engine** | Rule engine — no LLM invocation |
| **Fallback** | Returns validation errors when references are invalid; does not proceed |
| **API Endpoint** | `POST /api/v1/agents/orchestrate` |

Implementation: `agents/coordinator/`, `agents/coordinator/orchestrator.py`

---

## Evidence Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Collect, validate, normalize, and summarize uploaded log evidence |
| **Inputs** | `incident_id`, optional `log_file_id` |
| **Outputs** | `evidence_summary`, `evidence_package` (line counts, log type, sample entries) |
| **AI or Rule Engine** | Rule engine — deterministic parsing for `.log`, `.txt`, `.json`, `.csv`; `.evtx` metadata only |
| **Fallback** | Structured empty package with quality observations when logs are missing |
| **API Endpoint** | `POST /api/v1/agents/evidence` |

Persisted to: `evidence` table

---

## Threat Intelligence Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Extract IOCs from evidence and enrich with reputation context |
| **Inputs** | `incident_id` or evidence package from prior stage |
| **Outputs** | IOC list with reputation labels, descriptions, analyst notes |
| **AI or Rule Engine** | AI-first (Gemini JSON) with offline reputation engine fallback |
| **Fallback** | `reputation_engine.py` applies local rules (private IP → Safe, suspicious URL → Suspicious) |
| **API Endpoint** | `POST /api/v1/agents/threat-intelligence` |

Persisted to: `threat_intelligence_findings` table

---

## MITRE Mapping Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Map normalized evidence to MITRE ATT&CK techniques |
| **Inputs** | `incident_id` or evidence package |
| **Outputs** | `techniques[]` with `technique_id`, `technique_name`, `tactic`, `confidence` |
| **AI or Rule Engine** | Rule engine — local mappings in `mappings.py`, no external MITRE API |
| **Fallback** | Empty techniques array with `"No mapping found."` when no rules match |
| **API Endpoint** | `POST /api/v1/agents/mitre` |

Persisted to: `mitre_findings` table

---

## Risk Assessment Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Produce structured enterprise risk assessment from investigation context |
| **Inputs** | `incident_id` |
| **Outputs** | Risk level, score, narrative, contributing factors |
| **AI or Rule Engine** | AI-first (Gemini JSON) with rule engine fallback |
| **Fallback** | Severity, ransomware (T1486), technique count, and PowerShell pattern scoring |
| **API Endpoint** | `POST /api/v1/agents/risk` |

Persisted to: `risk_assessments` table

---

## Response Planning Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Draft containment, eradication, recovery, and monitoring steps — recommendations only |
| **Inputs** | `incident_id` |
| **Outputs** | Priority, containment, eradication, recovery, monitoring, executive summary |
| **AI or Rule Engine** | AI-first (Gemini JSON) with playbook fallback |
| **Fallback** | Scenario playbooks for ransomware, PowerShell, brute force, and generic incidents |
| **API Endpoint** | `POST /api/v1/agents/response` |

Persisted to: `response_plans` table

---

## Executive Report Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Transform investigation outputs into executive-friendly JSON and Markdown reports |
| **Inputs** | `incident_id` |
| **Outputs** | Executive summary, business impact, findings, MITRE summary, risk summary, actions, lessons learned, Markdown |
| **AI or Rule Engine** | AI-first (Gemini JSON) with template engine fallback |
| **Fallback** | `fallback.py` generates complete report from templates; no raw logs in output |
| **API Endpoint** | `POST /api/v1/agents/executive-report` |

Persisted to: `executive_reports` table

---

## Guardian Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Validate specialist outputs for security, governance, schema compliance, and confidence |
| **Inputs** | Agent name, output payload, optional `incident_id` |
| **Outputs** | Validation status (`approved`, `warning`, `rejected`), findings list, masked values |
| **AI or Rule Engine** | Rule engine — pattern-based scanners and schema validation |
| **Fallback** | When `GUARDIAN_ENABLED=false`, validation is bypassed; audits still persist |
| **API Endpoint** | `POST /api/v1/agents/guardian/validate` |

Persisted to: `guardian_audits` table

Also invoked automatically between workflow stages via `orchestration_guardian.py`.

---

## Timeline Engine

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Reconstruct chronological incident timeline from agent outputs |
| **Inputs** | Incident ID, persisted evidence and findings |
| **Outputs** | Ordered timeline events with timestamps and descriptions |
| **AI or Rule Engine** | Rule engine — deterministic event extraction |
| **Fallback** | Empty timeline when source data is insufficient |
| **API Endpoint** | Generated during workflow; readable via incident endpoints |

Persisted to: `timeline_events` table

---

## Evaluation Engine

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Score agent performance and persist metrics for the evaluation dashboard |
| **Inputs** | Investigation run results, agent execution records |
| **Outputs** | Health scores (availability, reliability, performance, accuracy) |
| **AI or Rule Engine** | Rule engine — weighted scoring in `evaluation/scorer.py` |
| **Fallback** | N/A — always produces metrics from available execution data |
| **API Endpoint** | `GET /api/v1/evaluation`, `GET /api/v1/evaluation/{agent_name}` |

Persisted to: `evaluation_metrics` table

---

## Agent Summary

| Agent | AI | Fallback | Persisted Table |
|-------|-----|----------|-----------------|
| Coordinator | No | Validation errors | `agent_executions` |
| Evidence | No | Empty package | `evidence` |
| Threat Intelligence | Gemini | Offline reputation | `threat_intelligence_findings` |
| MITRE | No | Empty techniques | `mitre_findings` |
| Risk | Gemini | Rule scoring | `risk_assessments` |
| Response | Gemini | Playbooks | `response_plans` |
| Executive Report | Gemini | Templates | `executive_reports` |
| Guardian | No | Bypass if disabled | `guardian_audits` |

Detailed reference: [`docs/kaggle/ai_agents.md`](../kaggle/ai_agents.md)
