# Changelog

All notable changes to Oz AI are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Sprint 4 Task 5: Final submission package, readiness report, competition scorecard
- Sprint 4 Task 4: Submission readiness — diagrams, evidence screenshot, final checklist
- Sprint 4 Task 3: Demo video preparation (`docs/demo/` script, storyboard, FAQ)
- Sprint 4 Task 2: Kaggle submission writeup (`docs/kaggle/`)
- Sprint 4 Task 1: Professional open-source repository presentation
- `GET /api/v1/ai/test` — minimal Gemini connectivity probe
- `docs/architecture/` and `docs/diagrams/` — Mermaid diagrams
- `docs/COMPETITION_ALIGNMENT.md` — Kaggle requirement mapping
- Root community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `ROADMAP.md`
- `scripts/generate_repo_stats.py` — automated repository statistics

### Changed

- Complete README rewrite with judge quickstart, statistics, and 12 screenshots
- `.gitignore` — exclude `.cursor/` IDE metadata
- Evidence screenshot added to asset generator

## [0.1.0] — 2026-06-27

### Added

- **Sprint 1 — Foundation:** FastAPI backend, React dashboard, incident/log CRUD, Docker Compose
- **Sprint 2 — ADK & MCP:** Google ADK runtime, MCP registry (5 tools), Coordinator Agent, Evidence Agent
- **Sprint 3 — Agents & workflow:** Threat Intelligence, MITRE, Risk, Response, Executive Report, Guardian agents
- Timeline Engine with export
- Evaluation framework and dashboard
- Investigation workflow (`POST /investigations/run`) with replay and explainability
- Demo mode: `scripts/reset_demo.py` (10 incidents, 25 logs)
- 39 API operations across 35 paths
- 176 automated tests

### Security

- Guardian Agent: prompt injection detection, PII scanning, output validation
- Append-only audit logs and guardian audit persistence
- API keys via environment variables only

[Unreleased]: https://github.com/Jugnu0707/Kaggle/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Jugnu0707/Kaggle/releases/tag/v0.1.0
