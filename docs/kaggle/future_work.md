# Future Work

Oz AI's roadmap extends the MVP into a production-grade enterprise incident response platform. The following items are planned or recommended based on current architecture gaps and competition feedback.

---

## Threat intelligence integrations

| Integration | Purpose |
|-------------|---------|
| **VirusTotal** | Live hash and URL reputation lookups for IOC enrichment |
| **AbuseIPDB** | IP reputation scoring and abuse confidence |
| **AlienVault OTX** | Community threat pulse and indicator feeds |
| **MISP** | Structured threat sharing and indicator import |

Implementation path: extend `agents/threat_intelligence/reputation_engine.py` with provider adapters behind the existing agent API surface.

---

## SIEM and security platform connectors

| Platform | Integration type |
|----------|------------------|
| **Splunk** | Log ingestion via SPL queries and alert webhook receiver |
| **Microsoft Sentinel** | Azure Log Analytics connector and incident sync |
| **Elastic Security** | ECS log ingestion and detection rule mapping |
| **CrowdStrike Falcon** | Endpoint telemetry and IOC enrichment |
| **QRadar / Chronicle** | Enterprise SIEM alert normalization |

Implementation path: new ingestion service layer with webhook receivers and normalized alert schema mapping to Oz AI incidents.

---

## Human approval and governance

| Feature | Description |
|---------|-------------|
| **Response plan approval workflow** | Approve/reject API and UI for containment and remediation recommendations |
| **Approval audit trail** | Persist approver identity, timestamp, and decision rationale |
| **Escalation policies** | Route critical incidents to on-call analysts |
| **SLA tracking** | Measure time-to-approve against organizational SLAs |

Implementation path: M6 milestone in `docs/03_TASKS.md`; API endpoints `POST /incidents/{id}/response/approve` and `reject`.

---

## Authentication and access control

| Feature | Description |
|---------|-------------|
| **Bearer token API auth** | Protect all endpoints with configurable API keys or JWT |
| **Production RBAC** | Roles: Analyst, Senior Analyst, CISO, Admin |
| **SSO integration** | OAuth 2.0 / SAML for enterprise identity providers |
| **Multi-tenant isolation** | Organization-scoped incidents and data separation |

Implementation path: M1-T25 auth middleware; Sprint 4 deliverable.

---

## MCP and ADK maturity

| Feature | Description |
|---------|-------------|
| **Domain MCP tools** | `evidence_collector`, `threat_intel_lookup`, `mitre_mapper`, `risk_scorer` |
| **ADK-native tool calls** | Agents invoke MCP tools instead of direct service calls |
| **ADK session checkpointing** | Persist agent session state across restarts |
| **`adk eval` integration** | Run Google ADK evaluation CLI against labeled scenarios |

---

## Evaluation and quality

| Feature | Description |
|---------|-------------|
| **30-scenario evaluation library** | Labeled incidents with expected agent outputs |
| **Regression gates in CI** | Fail builds when agent scores drop below thresholds |
| **Synthetic alert datasets** | `datasets/alerts/` with ≥10 attack-type templates |
| **`simulate_alert.py`** | Generate and inject synthetic alerts for demos |

---

## Infrastructure and deployment

| Feature | Description |
|---------|-------------|
| **PostgreSQL migration** | Replace SQLite for production write concurrency |
| **Docker production profile** | Nginx static frontend, non-root containers, health checks |
| **Process isolation** | Agent execution in worker processes or containers |
| **Rate limiting** | Protect ingestion and agent endpoints |
| **Observability** | Structured logging, metrics export, distributed tracing |

---

## User experience

| Feature | Description |
|---------|-------------|
| **WebSocket live updates** | Real-time investigation progress in dashboard |
| **`/about` page** | Architecture overview for judges and new users |
| **PDF executive reports** | Export leadership summaries as PDF |
| **Email/Slack notifications** | Alert analysts on critical findings |
| **Live browser screenshots** | Replace generated demo assets with real captures |

---

## Kaggle submission completion

| Artifact | Status |
|----------|--------|
| Submission notebook | Not started |
| Demo video (≤ 3 minutes) | Not started |
| Live demo environment URL | Optional |
| Competition write-up | `docs/kaggle/` (this directory) |

See [`ROADMAP.md`](../../ROADMAP.md) and [`docs/08_MILESTONES.md`](../../08_MILESTONES.md) for sprint-level tracking.
