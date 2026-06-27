# Limitations

Oz AI is an MVP designed for demonstration, evaluation, and capstone submission. The following limitations are intentional scope boundaries or known constraints. They are documented for transparency — not as defects awaiting immediate resolution.

---

## Infrastructure and persistence

| Limitation | Detail |
|------------|--------|
| **SQLite for demo** | Single-file SQLite database serializes writes and lacks row-level locking. Suitable for single-analyst demos; production deployments require PostgreSQL or equivalent. |
| **In-process execution** | Agent pipelines run within the FastAPI process. A runaway agent task could affect API responsiveness under extreme load. |
| **Vite dev frontend in Docker** | Docker Compose runs the Vite development server, not a production Nginx static build. |
| **No horizontal scaling** | Single backend instance; no load balancer or worker queue for agent execution. |

---

## AI and external services

| Limitation | Detail |
|------------|--------|
| **Free Gemini quota** | Google Gemini free-tier quotas limit AI-first agent enrichment. Quota exhaustion triggers fallbacks automatically but reduces output quality. |
| **Single model** | One `GOOGLE_MODEL` configuration (default `gemini-2.5-pro`); no per-agent model routing. |
| **No ADK session checkpointing** | ADK session state is not persisted across process restarts. Workflow state is in SQLite, but ADK-native checkpointing is not implemented. |
| **Offline threat intelligence** | Reputation enrichment uses local rules, not live VirusTotal, AbuseIPDB, or commercial feeds. |
| **No external MITRE API** | ATT&CK mapping uses local rules in `mappings.py`; technique database is not auto-updated from MITRE. |

---

## Security operations integration

| Limitation | Detail |
|------------|--------|
| **No real SIEM integration** | No Splunk, Microsoft Sentinel, Elastic, or CrowdStrike connectors. Logs are uploaded manually or via API. |
| **No webhook ingestion** | Incidents are created via REST API or dashboard; no alert webhook receiver. |
| **No automatic remediation** | Response plans are recommendations only. Oz AI does not isolate hosts, block IPs, or execute playbooks. |
| **No rate limiting** | Ingestion endpoints lack rate limiting; production deployments must add protection. |

---

## Human-in-the-loop and access control

| Limitation | Detail |
|------------|--------|
| **No API authentication** | All endpoints are unauthenticated. Bearer-token auth is planned for Sprint 4. |
| **No RBAC** | No role-based access control; any client with network access can read and modify data. |
| **Approval workflow not enforced** | Human approval for response actions is architecturally documented but not implemented in API or UI. Analysts cannot approve/reject response plans through the platform today. |
| **No multi-tenant isolation** | Single-tenant design; all incidents share one database. |

---

## MCP and agent wiring

| Limitation | Detail |
|------------|--------|
| **Operational MCP only** | Five tools (`health`, `list_incidents`, `incident_details`, `list_logs`, `system_info`) are registered. Domain tools (`evidence_collector`, `threat_intel_lookup`) are not implemented. |
| **Direct service calls** | Agents invoke backend services directly rather than through MCP tools at runtime. MCP is registered and introspectable but not the primary agent invocation path. |
| **No `adk eval`** | Google ADK evaluation CLI integration is not implemented. |

---

## Evaluation and submission artifacts

| Limitation | Detail |
|------------|--------|
| **No 30-scenario library** | Evaluation benchmarks exist but a comprehensive labeled scenario library is not yet populated. |
| **Styled screenshots** | Demo screenshots in `docs/demo/` are generated renders, not live browser captures. |
| **No submission notebook** | Kaggle submission notebook is not yet written. |
| **No demo video** | Demo video artifact is not yet produced. |
| **Empty datasets directory** | `datasets/alerts/` has no synthetic alert templates yet. |

---

## Frontend and UX

| Limitation | Detail |
|------------|--------|
| **Polling, not WebSockets** | Investigation status uses HTTP polling; small delay before UI reflects completion. |
| **No `/about` page** | Architecture overview page specified in UI spec is not implemented. |
| **No PDF export** | Executive reports export as JSON and Markdown only. |
| **No email notifications** | No alert or report delivery via email or Slack. |

---

## Summary

These limitations reflect MVP scope for a capstone demonstration. Oz AI prioritizes multi-agent coordination, Guardian safety, offline demo capability, and deployability over production enterprise features. Sprint 4 and subsequent releases address authentication, approval workflows, external integrations, and submission artifacts.
