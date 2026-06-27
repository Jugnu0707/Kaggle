# Database Entity-Relationship Diagram

Oz AI uses SQLite with SQLAlchemy ORM. Sixteen tables model incidents, investigations, agent outputs, audit trails, and evaluation metrics.

## ER diagram

```mermaid
erDiagram
    incidents ||--o{ log_files : has
    incidents ||--o{ investigations : has
    incidents ||--o{ evidence : has
    incidents ||--o{ mitre_findings : has
    incidents ||--o{ threat_intelligence_findings : has
    incidents ||--o{ risk_assessments : has
    incidents ||--o{ response_plans : has
    incidents ||--o{ executive_reports : has
    incidents ||--o{ guardian_audits : has
    incidents ||--o{ timeline_events : has
    incidents ||--o{ agent_executions : has
    incidents ||--o{ audit_logs : has

    investigations ||--o{ investigation_runs : has
    investigation_runs ||--o{ investigation_replays : has

    incidents {
        uuid id PK
        string title
        string severity
        string status
        datetime created_at
    }

    log_files {
        uuid id PK
        uuid incident_id FK
        string filename
        string storage_path
        string checksum_sha256
    }

    investigations {
        uuid id PK
        uuid incident_id FK
        string status
    }

    investigation_runs {
        uuid id PK
        uuid investigation_id FK
        string status
        datetime started_at
        datetime completed_at
    }

    investigation_replays {
        uuid id PK
        uuid investigation_run_id FK
        int step_number
        string agent_name
        int duration_ms
        bool ai_used
        bool fallback_used
    }

    evidence {
        uuid id PK
        uuid incident_id FK
        json normalized_data
    }

    mitre_findings {
        uuid id PK
        uuid incident_id FK
        string technique_id
        string technique_name
    }

    threat_intelligence_findings {
        uuid id PK
        uuid incident_id FK
        json iocs
        json enrichment
    }

    risk_assessments {
        uuid id PK
        uuid incident_id FK
        string risk_level
        float score
    }

    response_plans {
        uuid id PK
        uuid incident_id FK
        json plan_data
    }

    executive_reports {
        uuid id PK
        uuid incident_id FK
        json report_data
        text markdown
    }

    guardian_audits {
        uuid id PK
        uuid incident_id FK
        string agent_name
        bool passed
        json findings
    }

    timeline_events {
        uuid id PK
        uuid incident_id FK
        datetime timestamp
        string event_type
        string description
    }

    agent_executions {
        uuid id PK
        uuid incident_id FK
        string agent_name
        string status
    }

    audit_logs {
        uuid id PK
        uuid incident_id FK
        string action
        json metadata
    }

    evaluation_metrics {
        uuid id PK
        string agent_name
        string metric_name
        float value
    }
```

## Table inventory

| Table | Purpose |
|-------|---------|
| `incidents` | Core incident records |
| `log_files` | Uploaded log metadata and storage paths |
| `investigations` | Investigation session records |
| `investigation_runs` | Workflow execution runs |
| `investigation_replays` | Step-by-step replay for explainability |
| `evidence` | Normalized evidence from Evidence Agent |
| `mitre_findings` | MITRE ATT&CK technique mappings |
| `threat_intelligence_findings` | IOC extraction and enrichment |
| `risk_assessments` | Risk scores and narratives |
| `response_plans` | Structured response recommendations |
| `executive_reports` | Executive summaries (JSON + Markdown) |
| `guardian_audits` | Guardian validation results |
| `timeline_events` | Reconstructed incident timeline |
| `agent_executions` | Per-agent execution tracking |
| `audit_logs` | Append-only audit trail |
| `evaluation_metrics` | Agent evaluation benchmark results |

## Implementation

- Models: `backend/app/models/`
- Repositories: `backend/app/repositories/`
- Schema introspection: `GET /api/v1/system/tables`
