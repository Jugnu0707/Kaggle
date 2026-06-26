# Guardian Agent

Google ADK Guardian Agent for Oz AI (Sprint 3 Task 3).

## Architecture

```text
Specialist Agent Output
        │
        ▼
POST /api/v1/agents/guardian/validate
        │
        ▼
GuardianAgentService
        │
        ▼
GuardianValidator
   ├── empty response detection
   ├── JSON schema validation (+ retry / fallback signal)
   ├── mandatory field checks
   ├── prompt injection detection
   ├── secret detection + masking
   ├── PII detection + masking
   └── confidence threshold validation
        │
        ▼
GuardianAudit persistence
```

## Coordinator sequence

```text
Coordinator → Evidence → Guardian → Threat Intelligence → Guardian → MITRE → Guardian
→ Risk Assessment → Guardian → Response Planning → Guardian → Executive Report → Guardian
```

## Validation outcomes

| Status | Meaning |
| --- | --- |
| approved | Output passed all blocking checks |
| warning | Non-blocking issues such as IP warnings or masked values |
| rejected | Blocking issue detected; fallback may be required |

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `GUARDIAN_ENABLED` | `true` | Enable or bypass validation |
| `MIN_AI_CONFIDENCE` | `70` | Minimum AI confidence threshold |
| `MASK_SECRETS` | `true` | Mask detected secrets |
| `MASK_PII` | `true` | Mask detected PII |

## Constraints

- Output validation and governance only
- No authentication, RBAC, email alerts, or SIEM integration in Sprint 3 Task 3
