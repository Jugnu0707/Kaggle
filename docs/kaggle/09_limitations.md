# Limitations

**Related:** [06 Security](06_security.md) · [10 Future Work](10_future_work.md) · [08 Results](08_results.md)

Oz AI is an MVP designed for demonstration, evaluation, and capstone submission. The following limitations are intentional scope boundaries or known constraints.

---

## Infrastructure and persistence

| Limitation | Detail |
|------------|--------|
| **SQLite** | Single-file database serializes writes. Suitable for demos; not for concurrent production workloads. |
| **In-process execution** | Agent pipelines run within the FastAPI process. Long runs may affect API responsiveness under load. |
| **Vite dev frontend in Docker** | Docker Compose runs the Vite development server, not a production Nginx static build. |
| **No horizontal scaling** | Single backend instance; no load balancer or worker queue. |

---

## AI and external services

| Limitation | Detail |
|------------|--------|
| **Gemini quota** | Free-tier quotas limit AI enrichment. Exhaustion triggers fallbacks automatically. |
| **Single model** | One `GOOGLE_MODEL` (default `gemini-2.5-pro`); no per-agent model routing. |
| **No ADK session checkpointing** | ADK session state is not persisted across restarts. |
| **Offline threat intelligence** | Local reputation rules only — no VirusTotal, AbuseIPDB, or commercial feeds. |
| **No external MITRE API** | ATT&CK mapping uses local rules; not auto-synced with MITRE. |

---

## Security operations integration

| Limitation | Detail |
|------------|--------|
| **No SIEM integration** | No Splunk, Sentinel, Elastic, or CrowdStrike connectors. Manual log upload only. |
| **No webhook ingestion** | Incidents created via REST or dashboard; no alert webhook receiver. |
| **No automated remediation** | Response plans are recommendations only. No host isolation or playbook execution. |
| **No rate limiting** | Ingestion endpoints lack throttling. |

---

## Human-in-the-loop and access control

| Limitation | Detail |
|------------|--------|
| **No API authentication** | All endpoints are unauthenticated. |
| **No RBAC** | No role-based access control. |
| **Approval workflow not enforced** | Human approval for response actions is documented but not implemented in API or UI. |
| **No multi-tenant isolation** | Single-tenant design. |

---

## MCP and agent wiring

| Limitation | Detail |
|------------|--------|
| **Operational MCP only** | Five tools registered. Domain tools not implemented. |
| **Direct service calls** | Agents invoke services directly, not MCP tools at runtime. |
| **No `adk eval`** | Google ADK evaluation CLI not integrated. |

---

## Evaluation and submission artifacts

| Limitation | Detail |
|------------|--------|
| **No 30-scenario library** | Benchmark scenarios exist; comprehensive labeled library not populated. |
| **Generated screenshots** | Screenshots in `docs/screenshots/` are programmatic renders, not live browser captures. |
| **No submission notebook** | Kaggle notebook not written. |
| **No demo video** | Video artifact not produced. |
| **Empty datasets directory** | `datasets/alerts/` has no synthetic alert templates. |

---

## Frontend and UX

| Limitation | Detail |
|------------|--------|
| **Polling, not WebSockets** | Investigation status uses HTTP polling. |
| **No `/about` page** | Architecture overview page not implemented. |
| **No PDF export** | Executive reports export as JSON and Markdown only. |
| **No email notifications** | No alert or report delivery via email or Slack. |

---

## Summary

These limitations reflect MVP scope. Oz AI prioritizes multi-agent coordination, Guardian safety, offline demo capability, and deployability over production enterprise features.
