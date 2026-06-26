# Evidence Agent

Google ADK Evidence Agent for Oz AI (Sprint 2 Task 4).

## Architecture

```text
POST /api/v1/agents/evidence
        │
        ▼
EvidenceAgentService
        │
        ▼
EvidenceAgent (ADK config: name, description, prompt, schemas)
        │
        ▼
EvidenceCollectionService
   ├── validate incident + log metadata
   ├── read supported file formats
   ├── normalize evidence package
   └── generate deterministic summary
        │
        ▼
AgentExecution record (Evidence Agent)
```

## Supported file types

| Extension | Behavior |
|-----------|----------|
| `.log` | Line-based parsing |
| `.txt` | Line-based parsing |
| `.json` | JSON array/object parsing |
| `.csv` | Row-based parsing |
| `.evtx` | Metadata only; returns Sprint 2 parse note |

## Example response

```json
{
  "status": "completed",
  "evidence_summary": {
    "file_type": "application_log",
    "total_entries": 3,
    "time_range": "2026-06-26T10:00:00 to 2026-06-26T11:00:00",
    "possible_log_source": "Generic application log",
    "data_quality_observations": [
      "Sample entries are available for review",
      "Timestamps detected in log entries"
    ]
  },
  "evidence_package": {
    "incident_id": "...",
    "uploaded_file_id": "...",
    "number_of_lines": 3,
    "detected_log_type": "application_log",
    "sample_entries": ["..."],
    "collection_timestamp": "..."
  }
}
```

## Current scope

- Evidence collection and normalization only
- No threat intelligence, MITRE mapping, or LLM reasoning
- Coordinator invokes Evidence Agent first when a log file is present
