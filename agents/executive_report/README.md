# Executive Report Agent

Google ADK Executive Report Agent for Oz AI (Sprint 3 Task 2).

## Architecture

```text
POST /api/v1/agents/executive-report
        │
        ▼
ExecutiveReportAgentService
        │
        ▼
ExecutiveReportAgent (ADK config: name, description, prompt, schemas)
        │
        ▼
ExecutiveReportService
   ├── gather incident, evidence, MITRE, threat intel, risk, and response context
   ├── try Gemini JSON report (AI-first)
   ├── markdown_generator.py for complete Markdown output
   └── automatic fallback template engine on any AI failure
        │
        ▼
ExecutiveReport persistence + AgentExecution record
```

## Execution flow

1. Try Google Gemini with JSON-only response validation.
2. Generate Markdown from structured sections when AI succeeds.
3. On quota, timeout, invalid JSON, network, auth, or ADK errors, run `fallback.py`.
4. Always return a valid structured executive report with Markdown.

## Report sections

| Section | Description |
| --- | --- |
| Executive Summary | Plain-language incident overview for leadership |
| Business Impact | Operational and organizational impact |
| Incident Timeline Summary | High-level event sequence (no raw logs) |
| Key Findings | Executive bullet findings |
| MITRE Summary | Business-readable attack technique summary |
| Risk Summary | Enterprise risk posture |
| Recommended Actions | Leadership and operational next steps |
| Lessons Learned | Readiness improvements |

## Input

```json
{
  "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

## Coordinator sequence

```text
Coordinator → Evidence → Threat Intelligence → MITRE → Risk Assessment → Response Planning → Executive Report
```

## Constraints

- AI-first with automatic fallback
- Application never fails due to Gemini unavailability
- No PDF generation (Sprint 4)
- No email sending
- No Guardian agent in Sprint 3 Task 2
- No raw logs in executive output
