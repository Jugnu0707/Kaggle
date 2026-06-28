# Sequence Diagram

**Related:** [System Overview](01_system_overview.md) · [Component Diagram](02_component_diagram.md) · [Agent Workflow](04_agent_workflow.md)

Scenario: analyst uploads logs, creates an incident, runs an investigation, and receives an executive report.

---

## Investigation Sequence

```mermaid
sequenceDiagram
    actor Analyst
    participant UI as React Frontend
    participant API as FastAPI
    participant LogSvc as Log Service
    participant IncSvc as Incident Service
    participant WF as Investigation Workflow
    participant CO as Coordinator
    participant Agents as Specialist Agents
    participant GR as Guardian
    participant TL as Timeline Engine
    participant EV as Evaluation Engine
    participant DB as SQLite

    Analyst->>UI: Upload log file
    UI->>API: POST /api/v1/logs/upload
    API->>LogSvc: Store file metadata
    LogSvc->>DB: INSERT log_files
    LogSvc-->>UI: Log file ID

    Analyst->>UI: Create incident
    UI->>API: POST /api/v1/incidents
    API->>IncSvc: Create incident record
    IncSvc->>DB: INSERT incidents
    IncSvc-->>UI: Incident ID

    Analyst->>UI: Run investigation
    UI->>API: POST /api/v1/investigations/run
    API->>WF: run(incident_id)
    WF->>DB: INSERT investigation_runs

    WF->>CO: Validate context, build plan
    CO->>DB: INSERT agent_executions
    CO-->>WF: Orchestration plan

    loop Each specialist stage
        WF->>Agents: Execute agent service
        Agents->>DB: Persist stage output
        Agents-->>WF: Structured result
        WF->>GR: Validate output
        GR->>DB: INSERT guardian_audits
        GR-->>WF: approved / warning / rejected
        alt Guardian rejects AI output
            WF->>Agents: Re-run with fallback
            Agents->>DB: Persist fallback output
        end
        WF->>DB: INSERT investigation_replays
    end

    WF->>TL: Reconstruct timeline
    TL->>DB: INSERT timeline_events

    WF->>EV: Score agent performance
    EV->>DB: INSERT evaluation_metrics

    WF->>DB: UPDATE investigation_runs
    WF-->>API: Investigation package
    API-->>UI: Executive report + all stage outputs
    UI-->>Analyst: Display incident tabs
```

---

## Key Endpoints

| Step | Method | Path |
|------|--------|------|
| Upload log | `POST` | `/api/v1/logs/upload` |
| Create incident | `POST` | `/api/v1/incidents` |
| Run investigation | `POST` | `/api/v1/investigations/run` |
| View replay | `GET` | `/api/v1/investigations/{run_id}/replay` |
| View evaluation | `GET` | `/api/v1/evaluation` |

---

## Behavioral Notes

- Creating an incident does **not** automatically start the agent pipeline.
- The workflow runs synchronously in the HTTP request thread.
- Replay steps record `ai_used` and `fallback_used` for each stage.
- Guardian may trigger a single retry with Gemini disabled before accepting fallback output.

See [04_agent_workflow.md](04_agent_workflow.md) for agent-level detail.
