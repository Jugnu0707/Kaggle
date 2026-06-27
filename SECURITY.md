# Security Policy

## Reporting a vulnerability

**Do not report security vulnerabilities through public GitHub Issues.**

Report vulnerabilities privately via [GitHub Private Vulnerability Reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) or by contacting the repository maintainer directly.

Include:

- Description and impact
- Affected component
- Steps to reproduce
- Environment details (OS, Docker version, commit hash)

## Response timeline

| Action | Target |
|--------|--------|
| Acknowledgment | 48 hours |
| Severity assessment | 5 business days |
| Status update | 10 business days |
| Patch (critical/high) | 30 days |

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x | Yes |
| < 0.1 | No |

## Security design principles

1. **Human approval gate** — Response actions require explicit human approval before execution (enforcement planned Sprint 4).
2. **Guardian safety layer** — Prompt injection detection, PII scanning, and output validation between pipeline stages.
3. **Append-only audit trail** — Audit and guardian records are never modified after creation.
4. **Secrets in environment variables** — API keys and tokens must never appear in source code, logs, or API responses.
5. **MCP tool permissions** — Agents are restricted to their permitted tool set.

## Known MVP limitations

- SQLite write concurrency under high load
- No rate limiting on ingestion endpoints
- In-process agent execution (single-process FastAPI)
- Local threat intelligence datasets (integrity depends on deployment)

A detailed security policy is available in [.github/SECURITY.md](.github/SECURITY.md).
