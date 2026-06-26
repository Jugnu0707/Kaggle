# Threat Intelligence Agent

Google ADK Threat Intelligence Agent for Oz AI (Sprint 3 Task 1).

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
   ├── IOCExtractor (ioc_extractor.py)
   ├── ReputationEngine (reputation_engine.py)
   ├── try Gemini JSON enrichment (AI-first)
   └── fallback.py offline enrichment on any AI failure
        │
        ▼
ThreatIntelligenceFinding persistence + AgentExecution record
```

## Execution flow

1. Extract IOCs from incident evidence (offline).
2. Assign offline reputation via `reputation_engine.py`.
3. Try Gemini for descriptions and analyst notes.
4. On any AI failure, use `fallback.py`.
5. Persist enriched findings — never block or quarantine.

## Offline reputation rules

| Indicator | Reputation |
| --- | --- |
| RFC1918 / private IPv4 | Safe |
| Unknown public IP | Unknown |
| Suspicious PowerShell URL | Suspicious |
| Known ransomware hash | Malicious |

## Input

```json
{
  "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

## Coordinator sequence

```text
Coordinator → Evidence → Threat Intelligence → MITRE → Risk Assessment → Response Planning
```

## Extensibility

External providers (VirusTotal, AbuseIPDB) can be added behind the reputation engine without changing the agent API surface.
