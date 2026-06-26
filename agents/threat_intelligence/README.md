# Threat Intelligence Agent

Google ADK Threat Intelligence Agent for Oz AI (Sprint 2 Task 5).

## Architecture

```text
POST /api/v1/agents/threat-intelligence
        │
        ▼
ThreatIntelligenceAgentService
        │
        ▼
ThreatIntelligenceAgent (ADK config: name, description, prompt, schemas)
        │
        ▼
ThreatIntelligenceService
   ├── load Evidence Package via Evidence Agent collection
   ├── extract IOCs with IOCExtractor
   ├── classify indicators with rule-based confidence
   └── generate ThreatIntelligenceReport
        │
        ▼
AgentExecution record (Threat Intelligence Agent)
```

## Input

`evidence_id` refers to the uploaded log file ID (`uploaded_file_id`) from the Evidence Package.

```json
{
  "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "evidence_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

## Example response

```json
{
  "status": "completed",
  "ioc_count": 4,
  "report": {
    "total_iocs": 4,
    "ioc_breakdown": {
      "ipv4": 2,
      "domain": 0,
      "url": 1,
      "email": 0,
      "sha256": 1,
      "windows_username": 1
    },
    "suspicious_indicators": [
      "Encoded or suspicious PowerShell activity pattern detected",
      "External IPv4 address observed in evidence entries"
    ],
    "interesting_findings": [
      "4 unique IOCs extracted from evidence sample"
    ],
    "data_quality_notes": [
      "Sample entries were used for IOC extraction"
    ]
  },
  "iocs": [
    {
      "type": "IPv4",
      "value": "185.234.72.19",
      "confidence": 90,
      "source": "PowerShell Log"
    }
  ]
}
```

## Coordinator workflow

```text
Coordinator → Evidence Agent → Threat Intelligence Agent → (placeholders)
```

## Current scope

- Local regex-based IOC extraction only
- No VirusTotal, AbuseIPDB, MISP, or other external APIs
- No MITRE mapping or malware family detection
