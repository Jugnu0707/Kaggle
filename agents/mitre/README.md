# MITRE Mapping Agent

Google ADK MITRE Mapping Agent for Oz AI (Sprint 2 Task 6).

## Architecture

```text
POST /api/v1/agents/mitre
        │
        ▼
MitreAgentService
        │
        ▼
MitreMappingAgent (ADK config: name, description, prompt, schemas)
        │
        ▼
MitreMappingService
   ├── collect Evidence Packages for the incident
   ├── apply local mapping rules in mappings.py
   └── return MappedTechnique records
        │
        ▼
MitreFinding persistence + AgentExecution record
```

## Input

```json
{
  "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

## Example response

```json
{
  "status": "completed",
  "techniques": [
    {
      "technique_id": "T1059.001",
      "technique_name": "PowerShell",
      "tactic": "Execution",
      "confidence": 96,
      "matched_evidence": ["powershell.exe", "-encodedcommand"]
    }
  ]
}
```

When no rules match:

```json
{
  "status": "completed",
  "techniques": [],
  "message": "No mapping found."
}
```

## Mapping rules

| Behavior | Technique |
| --- | --- |
| PowerShell Execution | T1059.001 |
| Encoded PowerShell | T1027 |
| Failed Login Attempts | T1110 |
| Credential Dump | T1003 |
| Remote Service | T1021 |
| Ransomware Activity | T1486 |
| Network Discovery | T1046 |

## Coordinator sequence

```text
Coordinator → Evidence Agent → MITRE Mapping Agent → (remaining placeholders)
```

## Constraints

- No external MITRE API
- No LLM reasoning
- Rule-based mapping only
