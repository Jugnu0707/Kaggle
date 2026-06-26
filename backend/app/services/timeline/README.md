# Investigation Timeline Engine

Deterministic service that reconstructs an incident chronologically from collected evidence and agent outputs.

## Responsibilities

- Collect events from incident metadata, uploaded logs, evidence, threat intelligence, MITRE findings, risk assessment, and response planning outputs
- Normalize timestamps to UTC
- Remove duplicate events
- Sort chronologically and assign sequence numbers
- Generate an investigation summary
- Persist results as `TimelineEvent` records

## Components

| Module | Purpose |
|--------|---------|
| `engine.py` | Orchestrates collection, processing, and summary generation |
| `parser.py` | Timestamp normalization and log-line event inference |
| `models.py` | Internal Pydantic models |
| `schemas.py` | API response schemas and Markdown export helper |

## API

- `GET /api/v1/incidents/{incident_id}/timeline` — JSON timeline payload
- `GET /api/v1/incidents/{incident_id}/timeline/export?format=markdown` — Markdown export
- `GET /api/v1/incidents/{incident_id}/timeline/export?format=json` — Raw JSON export

## Constraints

- No AI inference
- Does not modify evidence records
- Does not generate executive or compliance reports
