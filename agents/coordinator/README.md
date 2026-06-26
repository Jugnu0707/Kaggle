# Coordinator Agent

Google ADK Coordinator Agent for Oz AI incident response orchestration (Sprint 2 Task 3).

## Architecture

```text
POST /api/v1/agents/orchestrate
        │
        ▼
OrchestrationService
        │
        ▼
CoordinatorAgent (ADK config: name, description, prompt, schemas)
        │
        ▼
CoordinatorOrchestrator
   ├── validate_request()   → incident/log lookup via repositories
   ├── route_agents()       → placeholder deterministic workflow
   └── build_plan()         → OrchestrationPlan (no agent execution)
        │
        ▼
AgentExecution record (Coordinator only)
```

## ADK configuration

| Property | Value |
|----------|-------|
| Name | `coordinator` |
| Description | Orchestrates the Oz AI incident response pipeline |
| System prompt | `prompt.md` |
| Input schema | `CoordinatorInput` |
| Output schema | `OrchestrationPlan` |
| LLM | **Not invoked** in Sprint 2 Task 3 |

## Orchestration plan example

```json
{
  "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "log_id": null,
  "workflow_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "accepted",
  "workflow": [
    "Evidence Agent",
    "Threat Intelligence Agent",
    "MITRE Mapping Agent",
    "Risk Assessment Agent",
    "Response Planning Agent",
    "Executive Report Agent",
    "Guardian Agent"
  ]
}
```

## Current scope

- Accept `incident_id` and/or `log_id`
- Validate referenced resources
- Generate orchestration plan (no downstream agent execution)
- Log orchestration requests and persist `AgentExecution` records

## Future scope

- Invoke specialist agents via ADK session management
- Checkpoint workflow state to the database at each stage
- Guardian validation at pipeline boundaries
