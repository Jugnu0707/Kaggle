# Security

**Related:** [05 AI Agents](05_ai_agents.md) · [09 Limitations](09_limitations.md) · [Security architecture](../architecture/08_security_architecture.md)

Oz AI implements security controls through the Guardian Agent, applied between every specialist workflow stage. The platform is decision-support only — it does not execute remediation actions.

---

## Guardian Agent

Location: `agents/guardian/validator.py`

The Guardian Agent is rule-based (no LLM). It runs automatically via `orchestration_guardian.run_stage_with_guardian` after each specialist stage and can be invoked directly at `POST /api/v1/agents/guardian/validate`.

### Validation pipeline

1. Empty response check
2. Prompt injection scan
3. PII detection and optional masking
4. Secret detection and optional masking
5. JSON schema validation per agent type
6. Mandatory field completeness check
7. Confidence threshold enforcement
8. Persist audit record to `guardian_audits`

### Validation statuses

| Status | Behavior |
|--------|----------|
| `approved` | Pipeline continues |
| `warning` | Non-blocking issues logged; pipeline continues |
| `rejected` | Triggers retry without Gemini or agent fallback path |

When Guardian rejects an AI output, `orchestration_guardian.py` may patch `_call_gemini` to return `None` and re-run the agent with fallback logic.

---

## Prompt injection protection

Location: `agents/guardian/prompt_injection.py`

Scans agent outputs for patterns indicating prompt injection:

- Instruction override phrases
- Role manipulation attempts
- System prompt extraction patterns
- Delimiter escape sequences

Function: `scan_response_for_injection()`. Findings contribute to rejection or warning status.

---

## Secret masking

Location: `agents/guardian/secret_detector.py`

| Setting | Default |
|---------|---------|
| `MASK_SECRETS` | `true` |

Detects API keys, bearer tokens, AWS credentials, private keys, and common secret formats. Function: `mask_secrets_in_response()`.

Secrets are configured via environment variables only (`.env`, gitignored). Never committed to the repository.

---

## PII masking

Location: `agents/guardian/pii_detector.py`

| Setting | Default |
|---------|---------|
| `MASK_PII` | `true` |

Detects email addresses, phone numbers, SSN patterns, and credit card numbers. Function: `mask_pii_in_response()`.

Executive reports exclude raw logs from leadership output by design.

---

## Confidence validation

Location: `agents/guardian/confidence.py`

| Setting | Default |
|---------|---------|
| `MIN_AI_CONFIDENCE` | `70` |

AI-first agent outputs include confidence scores. Guardian rejects outputs below the threshold, triggering fallback execution.

Function: `validate_confidence()`.

---

## Audit trail

### Guardian audits (`guardian_audits`)

Every validation event is persisted with agent name, status, issues found, and action taken. Records are append-only by application design.

Readable via incident endpoints and Guardian tab in the UI.

### System audit logs (`audit_logs`)

General-purpose immutable trail for entity creation and updates.

### Sanitized replay export

Location: `backend/app/utils/sanitize.py`

Replay export removes sensitive values before external sharing.

---

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `GUARDIAN_ENABLED` | `true` | Enable/disable validation |
| `MIN_AI_CONFIDENCE` | `70` | Confidence threshold |
| `MASK_PII` | `true` | PII detection and masking |
| `MASK_SECRETS` | `true` | Secret detection and masking |

Source: `backend/app/core/guardian_config.py`, `.env.example`

---

## Security limitations (current)

| Gap | Status |
|-----|--------|
| API authentication | Not implemented |
| RBAC | Not implemented |
| Rate limiting | Not implemented |
| Human approval enforcement | Documented only |
| Automated remediation | Not implemented (by design) |

See [09 Limitations](09_limitations.md) for full list.
