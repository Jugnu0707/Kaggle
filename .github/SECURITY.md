# Security Policy

**Project Name:** Oz AI
**Version:** 1.0 (MVP)

---

## Reporting a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

Public disclosure of a security vulnerability before it is patched puts all users of the project at risk. We ask that you follow responsible disclosure practices.

### How to Report

Report security vulnerabilities by:

1. **Email (preferred):** Send a detailed report to the project maintainer's email address. Include "Oz AI Security Vulnerability" in the subject line.

2. **GitHub Private Vulnerability Reporting:** If enabled on this repository, use [GitHub's private security advisory feature](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) to submit a vulnerability report.

### What to Include in Your Report

A useful security report includes:

- A clear description of the vulnerability and its potential impact.
- The affected component(s) (e.g., "Guardian Agent prompt injection detection," "MCP tool permission enforcement").
- Steps to reproduce the vulnerability, including any proof-of-concept code or payload.
- The environment in which you discovered the vulnerability (OS, Docker version, Oz AI version/commit hash).
- Your assessment of the severity (Critical / High / Medium / Low) and why.

### Response Timeline

We are committed to responding to security reports promptly:

| Action | Target Timeline |
|---|---|
| Acknowledgment of receipt | Within 48 hours |
| Initial severity assessment | Within 5 business days |
| Status update to reporter | Within 10 business days |
| Patch release (for critical/high issues) | Within 30 days |

We will keep you informed of our progress. If we need additional information, we will contact you.

---

## Supported Versions

| Version | Supported |
|---|---|
| 1.0.x (MVP) | Yes |
| < 1.0 | No |

Security patches are applied to the latest released version. Older versions are not patched.

---

## Security Design Principles

The following security principles are foundational to Oz AI's design. Reports that demonstrate a bypass of any of these principles are considered high or critical severity:

### 1. Human Approval Gate

Oz AI **never performs consequential actions automatically**. Every `ResponseAction` must be explicitly approved by a human through the dashboard before it can advance to an executable state. Any vulnerability that allows a response action to bypass the human approval gate is a Critical severity finding.

### 2. Guardian Agent Safety Layer

The Guardian Agent is responsible for:
- Detecting prompt injection in all incoming alert payloads.
- Scanning all agent outputs for PII before persistence.
- Validating tool permission compliance.
- Enforcing the human approval gate at the agent layer.

Any bypass of the Guardian Agent's controls is a High or Critical severity finding.

### 3. Append-Only Audit Trail

The `AuditEvent` table is append-only. No application code path may update or delete audit records. Any vulnerability that allows modification or deletion of audit records is a High severity finding.

### 4. Secrets in Environment Variables

All secrets (API keys, tokens, passwords) must be in environment variables and must never appear in source code, logs, or API responses. Any discovery of a committed secret is Critical severity — please report it immediately.

### 5. MCP Tool Permission Enforcement

Each agent is permitted to call only a defined subset of MCP tools. The permission registry must prevent agents from calling tools outside their permitted set. Any bypass of tool permission enforcement is a High severity finding.

---

## Known Security Limitations (MVP)

The following are known security limitations of the MVP. They are documented here for transparency and are not considered new vulnerabilities:

1. **SQLite write concurrency:** SQLite serializes writes and does not support row-level locking. Under high concurrent load, write contention could affect availability. This is a known MVP constraint; migration to PostgreSQL resolves it.

2. **Polling-based frontend:** The frontend uses polling rather than WebSockets. This creates a small window where a new incident's status is not immediately reflected in the UI. This is not a security vulnerability.

3. **In-process agent execution:** Agent pipelines run as FastAPI `BackgroundTask`s in the same process as the API. A runaway agent task could theoretically affect API responsiveness. For the MVP's single-user workload, this is acceptable. Production deployment uses proper process isolation.

4. **Local knowledge base:** Threat intelligence and MITRE ATT&CK data is served from local dataset files. Tampering with these files could influence agent output. Production deployments should use integrity-verified or externally sourced knowledge bases.

5. **No rate limiting on ingestion API:** The MVP does not implement rate limiting on `POST /api/v1/incidents`. Production deployments must add rate limiting to prevent abuse.

---

## Security Contact

For non-urgent security questions (architecture review, security design discussion), open a GitHub Issue labeled `security-discussion`.

For actual vulnerability reports, use the private reporting channels described above.
