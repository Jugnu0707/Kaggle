# Response Planning Agent

Google ADK Response Planning Agent for Oz AI (Sprint 2 Task 8).

## Architecture

```text
POST /api/v1/agents/response
        │
        ▼
ResponseAgentService
        │
        ▼
ResponsePlanningAgent (ADK config: name, description, prompt, schemas)
        │
        ▼
ResponsePlanningService
   ├── gather incident, evidence, MITRE, threat intel, and risk context
   ├── try Gemini JSON plan (AI-first)
   └── automatic fallback rule engine on any AI failure
        │
        ▼
ResponsePlan persistence + AgentExecution record
```

## Execution flow

1. Try Google Gemini with JSON-only response validation.
2. Save AI plan when successful.
3. On quota, timeout, invalid JSON, network, auth, or ADK errors, run `fallback.py`.
4. Always return a valid structured response plan.

## Fallback playbooks

| Scenario | Example actions |
| --- | --- |
| Ransomware / T1486 | Isolate host, disable SMB, preserve evidence, restore from backup |
| PowerShell / T1059.001 | Isolate endpoint, collect memory, block PowerShell, review parent process |
| Failed login / T1110 | Block source IP, reset password, enable MFA, monitor auth logs |
| Generic | Document scope, restrict access, remove artifacts, monitor recurrence |

## Input

```json
{
  "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

## Coordinator sequence

```text
Coordinator → Evidence → MITRE → Threat Intelligence → Risk Assessment → Response Planning
```

## Constraints

- Recommendations only — never execute remediation
- AI-first with automatic fallback
- Application never fails due to Gemini unavailability
