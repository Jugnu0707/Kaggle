# Database ER Diagram

Entity-relationship model for Oz AI (16 tables).

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
    }

    log_files {
        uuid id PK
        uuid incident_id FK
        string filename
        string storage_path
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
    }

    threat_intelligence_findings {
        uuid id PK
        uuid incident_id FK
        json iocs
    }

    risk_assessments {
        uuid id PK
        uuid incident_id FK
        string risk_level
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
    }

    guardian_audits {
        uuid id PK
        uuid incident_id FK
        string agent_name
        bool passed
    }

    timeline_events {
        uuid id PK
        uuid incident_id FK
        datetime timestamp
    }

    investigation_runs {
        uuid id PK
        uuid investigation_id FK
        string status
    }

    investigation_replays {
        uuid id PK
        uuid investigation_run_id FK
        int step_number
        string agent_name
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
| `log_files` | Uploaded log metadata |
| `investigations` | Investigation sessions |
| `investigation_runs` | Workflow execution runs |
| `investigation_replays` | Step replay for explainability |
| `evidence` | Evidence Agent output |
| `mitre_findings` | MITRE ATT&CK mappings |
| `threat_intelligence_findings` | IOC enrichment |
| `risk_assessments` | Risk scores |
| `response_plans` | Response recommendations |
| `executive_reports` | Leadership summaries |
| `guardian_audits` | Safety validation results |
| `timeline_events` | Reconstructed timeline |
| `agent_executions` | Per-agent run tracking |
| `audit_logs` | Append-only audit trail |
| `evaluation_metrics` | Benchmark results |

Introspection: `GET /api/v1/system/tables`
