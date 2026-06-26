# Risk Assessment Agent

Google ADK Risk Assessment Agent for Oz AI (Sprint 2 Task 7).

## Architecture

```text
POST /api/v1/agents/risk
        │
        ▼
RiskAgentService
        │
        ▼
RiskAssessmentAgent (ADK config: name, description, prompt, schemas)
        │
        ▼
RiskAssessmentService
   ├── gather incident, evidence, MITRE, and threat intel context
   ├── try Gemini JSON assessment (AI-first)
   └── automatic fallback rule engine on any AI failure
        │
        ▼
RiskAssessment persistence + AgentExecution record
```

## Execution flow

1. Try Google Gemini with JSON-only response validation.
2. Save AI assessment when successful.
3. On quota, timeout, invalid JSON, network, auth, or ADK errors, run `fallback.py`.
4. Always return a valid structured assessment.

## Fallback rules

| Level | Triggers |
| --- | --- |
| Critical | Critical severity, ransomware, MITRE T1486 |
| High | High severity, >3 MITRE techniques, MITRE confidence > 90 |
| Medium | Medium severity, failed logins (T1110), PowerShell (T1059.001) |
| Low | Otherwise |

## Input

```json
{
  "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

## Coordinator sequence

```text
Coordinator → Evidence → MITRE → Threat Intelligence → Risk Assessment
```

## Constraints

- AI-first with automatic fallback
- Application never fails due to Gemini unavailability
- No Response Planning, Executive Report, or Guardian agents in this sprint
