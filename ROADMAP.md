# Roadmap

Oz AI development roadmap aligned with [`docs/03_TASKS.md`](docs/03_TASKS.md) and [`docs/08_MILESTONES.md`](docs/08_MILESTONES.md).

## Completed

| Sprint | Deliverables |
|--------|--------------|
| Sprint 1 | Backend API, React dashboard, Docker, incident/log CRUD |
| Sprint 2 | Google ADK runtime, MCP registry (5 tools), Coordinator, Evidence Agent |
| Sprint 3 | 6 specialist agents, Guardian, Timeline Engine, Evaluation, Investigation Runner |
| Sprint 3.5 | Documentation sync, hardening, demo assets, competition prep |
| Sprint 4 Task 1 | Open-source repository quality, architecture docs, README rewrite |

## Sprint 4 — Release hardening (in progress)

| Priority | Item | Milestone |
|----------|------|-----------|
| P0 | API bearer-token authentication | M1 |
| P0 | Response plan approval workflow (approve/reject API + UI) | M6 |
| P0 | Synthetic alert datasets (`datasets/alerts/`) | M3 |
| P1 | Docker production profile (Nginx, non-root, static frontend) | M1 |
| P1 | 30-scenario evaluation library | M8 |
| P1 | Domain MCP tools (`evidence_collector`, `threat_intel_lookup`) | M4 |
| P2 | Kaggle submission notebook | M9 |
| P2 | Demo video (≤ 3 minutes) | M9 |
| P2 | `/about` page with architecture overview | M7 |

## v0.2.0 — Security hardening

- Role-based access control (RBAC)
- Rate limiting on ingestion endpoints
- PostgreSQL migration path from SQLite
- Secret scanning in CI pipeline
- ADK session checkpointing and `adk eval`

## v0.3.0 — Enterprise integrations

- SIEM webhook ingestion (Splunk, Sentinel)
- Email/Slack notification on critical incidents
- SSO authentication (OAuth 2.0 / SAML)
- Multi-tenant incident isolation

## v1.0.0 — Production release

- Human approval gate enforced at API and agent layers
- Full MCP domain tool layer with permission enforcement
- Production Docker images with health checks and observability
- Complete evaluation suite with regression gates in CI
- Published Kaggle capstone submission package

## How to contribute

See [CONTRIBUTING.md](CONTRIBUTING.md). All work should map to a task in `docs/03_TASKS.md`.
