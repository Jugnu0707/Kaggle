# Agent Workflow

Oz AI deploys eight specialist agents orchestrated by the Coordinator Agent and validated by the Guardian Agent at each stage.

## Investigation pipeline

```mermaid
flowchart LR
    START(["POST /investigations/run"]) --> CO["Coordinator"]
    CO --> EV["Evidence"]
    EV --> G1["Guardian"]
    G1 --> TI["Threat Intelligence"]
    TI --> G2["Guardian"]
    G2 --> MI["MITRE Mapping"]
    MI --> G3["Guardian"]
    G3 --> RI["Risk Assessment"]
    RI --> G4["Guardian"]
    G4 --> RP["Response Planning"]
    RP --> G5["Guardian"]
    G5 --> ER["Executive Report"]
    ER --> G6["Guardian"]
    G6 --> TL["Timeline Engine"]
    TL --> EVA["Evaluation Engine"]
    EVA --> DONE(["Investigation Complete"])
```

## Agent responsibilities

| Agent | Mission | AI / Fallback |
|-------|---------|---------------|
| **Coordinator** | Validate context and build execution plan | Rule-based |
| **Evidence** | Normalize uploaded logs, extract entities | Rule-based |
| **Threat Intelligence** | IOC extraction and reputation enrichment | Gemini + offline engine |
| **MITRE Mapping** | Map evidence to ATT&CK techniques | Rule-based |
| **Risk Assessment** | Enterprise risk scoring and narrative | Gemini + rules |
| **Response Planning** | Containment, eradication, recovery plan | Gemini + templates |
| **Executive Report** | CISO-ready summary and recommendations | Gemini + templates |
| **Guardian** | Prompt injection, PII, schema, confidence checks | Rule-based |

## Implementation locations

| Component | Path |
|-----------|------|
| Agent definitions | `agents/*/agent.py` |
| Agent services | `agents/*/service.py` |
| Workflow orchestration | `backend/app/services/investigation_workflow_service.py` |
| Guardian integration | `backend/app/services/orchestration_guardian.py` |
| ADK runtime | `backend/app/core/adk_runtime.py` |

## Replay and explainability

After a run completes, replay steps are persisted to `investigation_replays` and exposed via:

- `GET /api/v1/investigations/{run_id}/replay`
- `GET /api/v1/investigations/{run_id}/explain`
- `GET /api/v1/investigations/{run_id}/replay/export`

See [`investigation-sequence.md`](investigation-sequence.md) for the full request sequence.
