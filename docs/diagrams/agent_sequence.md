# Agent Sequence

Sequence diagram for a full investigation run with Guardian validation at each stage.

```mermaid
sequenceDiagram
    autonumber
    participant Analyst
    participant API as FastAPI
    participant WF as Workflow
    participant CO as Coordinator
    participant EV as Evidence
    participant GR as Guardian
    participant TI as Threat Intel
    participant MI as MITRE
    participant RI as Risk
    participant RP as Response
    participant ER as Executive Report
    participant TL as Timeline
    participant EA as Evaluation
    participant DB as SQLite

    Analyst->>API: POST /investigations/run
    API->>WF: run_investigation(incident_id)
    WF->>DB: create investigation_run

    WF->>CO: validate & plan
    CO->>DB: agent_execution

    WF->>EV: collect evidence
    EV->>DB: evidence
    WF->>GR: validate Evidence
    GR->>DB: guardian_audit

    WF->>TI: extract IOCs
    TI->>DB: threat_intelligence_findings
    WF->>GR: validate Threat Intel
    GR->>DB: guardian_audit

    WF->>MI: map ATT&CK
    MI->>DB: mitre_findings
    WF->>GR: validate MITRE
    GR->>DB: guardian_audit

    WF->>RI: assess risk
    RI->>DB: risk_assessments
    WF->>GR: validate Risk
    GR->>DB: guardian_audit

    WF->>RP: draft response plan
    RP->>DB: response_plans
    WF->>GR: validate Response
    GR->>DB: guardian_audit

    WF->>ER: generate report
    ER->>DB: executive_reports
    WF->>GR: validate Executive Report
    GR->>DB: guardian_audit

    WF->>TL: build timeline
    TL->>DB: timeline_events
    WF->>EA: score outputs
    EA->>DB: evaluation_metrics

    WF->>DB: mark run complete
    API-->>Analyst: run_id + status
```

## Agent execution model

| Agent | AI | Fallback |
|-------|-----|----------|
| Coordinator | No | Validation errors |
| Evidence | No | Empty package |
| Threat Intelligence | Gemini | Offline reputation engine |
| MITRE | No | Empty techniques |
| Risk | Gemini | Rule scoring |
| Response | Gemini | Playbooks |
| Executive Report | Gemini | Templates |
| Guardian | No | Bypass if disabled |

## Replay API

After completion, each step is available via `GET /api/v1/investigations/{run_id}/replay` with `ai_used` and `fallback_used` metadata.
