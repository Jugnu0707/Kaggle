# Roadmap

Oz AI development roadmap aligned with [`docs/03_TASKS.md`](docs/03_TASKS.md) and [`docs/08_MILESTONES.md`](docs/08_MILESTONES.md).

## Completed

| Sprint | Deliverables |
|--------|--------------|
| Sprint 1 | Backend API, React dashboard, Docker, incident/log CRUD |
| Sprint 2 | Google ADK runtime, MCP registry (5 tools), Coordinator, Evidence Agent |
| Sprint 3 | 6 specialist agents, Guardian, Timeline Engine, Evaluation, Investigation Runner |
| Sprint 3.5 | Documentation sync, hardening, demo assets, competition prep |
| Sprint 4 Tasks 1–4 | README, Kaggle writeup, demo prep, submission verification |

## Sprint 4 — Submission packaging (in progress)

| Priority | Item | Status |
|----------|------|--------|
| P0 | Record demo video | Script ready — `docs/demo/demo_script.md` |
| P0 | Kaggle submission notebook | Pending |
| P0 | Upload demo video URL | Pending |
| P1 | API bearer-token authentication | Planned (M1) |
| P1 | Response plan approval workflow | Planned (M6) |
| P2 | Live browser screenshots | Optional |

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
