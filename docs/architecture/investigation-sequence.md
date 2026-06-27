# Investigation Sequence

End-to-end sequence for a full investigation run from dashboard trigger through replay export.

## Sequence diagram

```mermaid
sequenceDiagram
    autonumber
    participant Analyst as Security Analyst
    participant UI as React Dashboard
    participant API as FastAPI
    participant WF as InvestigationWorkflow
    participant CO as Coordinator
    participant Agents as Specialist Agents
    participant GR as Guardian
    participant TL as Timeline Engine
    participant EV as Evaluation Engine
    participant DB as SQLite

    Analyst->>UI: Open /incidents/:id/investigate
    Analyst->>UI: Start Investigation
    UI->>API: POST /api/v1/investigations/run
    API->>WF: run_investigation(incident_id)
    WF->>DB: create investigation_run (running)

    loop Each pipeline stage
        WF->>CO: build execution plan (first stage)
        WF->>Agents: execute agent service
        Agents->>DB: persist agent output
        WF->>GR: validate output
        GR->>DB: persist guardian_audit
        WF->>DB: record replay step
    end

    WF->>TL: build timeline
    TL->>DB: persist timeline_events
    WF->>EV: score investigation
    EV->>DB: persist evaluation_metrics
    WF->>DB: mark investigation_run complete
    API-->>UI: run_id + status

    Analyst->>UI: View replay
    UI->>API: GET /investigations/{run_id}/replay
    API->>DB: load investigation_replays
    API-->>UI: step timeline + metadata

    Analyst->>UI: Export replay
    UI->>API: GET /investigations/{run_id}/replay/export?format=markdown
    API-->>UI: downloadable report
```

## API flow

| Step | Endpoint | Purpose |
|------|----------|---------|
| 1 | `POST /api/v1/logs/upload` | Upload incident logs |
| 2 | `POST /api/v1/investigations/run` | Start full pipeline |
| 3 | `GET /api/v1/investigations/runs/{run_id}` | Poll run status |
| 4 | `GET /api/v1/incidents/{id}/timeline` | View timeline |
| 5 | `GET /api/v1/investigations/{run_id}/replay` | Step replay |
| 6 | `GET /api/v1/investigations/{run_id}/explain` | Explainability metadata |
| 7 | `GET /api/v1/evaluation` | Agent evaluation dashboard |

## Failure handling

- **Gemini unavailable** — Agents fall back to deterministic rules; workflow continues.
- **Guardian rejection** — Stage marked with findings; workflow may continue with fallback output.
- **Missing logs** — Investigation returns 404 or validation error before pipeline starts.

See [`agent-workflow.md`](agent-workflow.md) for the agent order and [`02_ARCHITECTURE.md`](../02_ARCHITECTURE.md) for service boundaries.
