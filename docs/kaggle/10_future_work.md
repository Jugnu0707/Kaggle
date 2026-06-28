# Future Work

**Related:** [09 Limitations](09_limitations.md) · [ROADMAP.md](../../ROADMAP.md) · [10 Decision Records](../architecture/10_decision_records.md)

Planned extensions based on current architecture gaps and documented roadmap.

---

## Database and infrastructure

| Item | Description |
|------|-------------|
| **PostgreSQL** | Replace SQLite for production write concurrency |
| **Docker production profile** | Nginx static frontend, non-root containers |
| **Process isolation** | Agent execution in worker processes |
| **Rate limiting** | Protect ingestion and agent endpoints |
| **Observability** | Metrics export, distributed tracing |

---

## Threat intelligence integrations

| Integration | Purpose |
|-------------|---------|
| **VirusTotal** | Live hash and URL reputation |
| **AbuseIPDB** | IP reputation scoring |
| **AlienVault OTX** | Community indicator feeds |
| **MISP** | Structured threat sharing |

Implementation path: provider adapters behind `agents/threat_intelligence/reputation_engine.py`.

---

## SIEM and security platform connectors

| Platform | Integration type |
|----------|------------------|
| **Splunk** | Log ingestion and alert webhook receiver |
| **Microsoft Sentinel** | Azure Log Analytics connector |
| **Elastic Security** | ECS log ingestion |
| **CrowdStrike Falcon** | Endpoint telemetry enrichment |

Implementation path: ingestion service with webhook receivers mapping alerts to Oz AI incidents.

---

## Human approval and governance

| Feature | Description |
|---------|-------------|
| **Response plan approval** | Approve/reject API and UI for recommendations |
| **Approval audit trail** | Persist approver identity and decision |
| **Escalation policies** | Route critical incidents to on-call |
| **SLA tracking** | Measure time-to-approve |

Planned endpoints: `POST /incidents/{id}/response/approve`, `reject`.

---

## Authentication and access control

| Feature | Description |
|---------|-------------|
| **Bearer token API auth** | Protect all endpoints |
| **RBAC** | Analyst, Senior Analyst, CISO, Admin roles |
| **SSO** | OAuth 2.0 / SAML |
| **Multi-tenant isolation** | Organization-scoped data |

---

## MCP and ADK maturity

| Feature | Description |
|---------|-------------|
| **Domain MCP tools** | `evidence_collector`, `threat_intel_lookup`, `mitre_mapper` |
| **ADK-native tool calls** | Agents invoke MCP instead of direct services |
| **ADK session checkpointing** | Persist session state across restarts |
| **`adk eval` integration** | ADK evaluation CLI against labeled scenarios |

---

## Evaluation and quality

| Feature | Description |
|---------|-------------|
| **30-scenario evaluation library** | Labeled incidents with expected outputs |
| **CI regression gates** | Fail builds on score regression |
| **Synthetic alert datasets** | `datasets/alerts/` templates |
| **Live browser screenshots** | Replace generated demo assets |

---

## User experience

| Feature | Description |
|---------|-------------|
| **WebSocket live updates** | Real-time investigation progress |
| **`/about` page** | Architecture overview for judges |
| **PDF executive reports** | Leadership export format |
| **Email/Slack notifications** | Alert delivery |

---

## Kaggle submission completion

| Artifact | Status |
|----------|--------|
| Submission notebook | Not started |
| Demo video (≤ 3 minutes) | Not started |
| Live demo environment URL | Optional |

Track progress: [`ROADMAP.md`](../../ROADMAP.md), [`docs/08_MILESTONES.md`](../08_MILESTONES.md)
