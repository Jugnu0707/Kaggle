# Coordinator Agent

Minimal Coordinator Agent placeholder for Google ADK framework integration (Sprint 2 Task 1).

## Current scope

- Initializes successfully at application startup
- Accepts a request via `handle_request()`
- Returns a static placeholder response (no LLM calls, no tools)

## Placeholder response

```json
{
  "status": "Coordinator initialized",
  "message": "Ready for agent orchestration."
}
```

## Future scope

In later sprints, this agent will orchestrate the full incident response pipeline using Google ADK session management and specialist agents.
