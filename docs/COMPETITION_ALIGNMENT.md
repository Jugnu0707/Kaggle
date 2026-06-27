# Competition Alignment — Kaggle AI Agents Intensive Capstone

**Track:** Agents for Business  
**Project:** Oz AI — Enterprise Incident Response Platform

This document maps each Kaggle evaluation dimension to concrete implementation locations in the repository.

---

## Summary matrix

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Google ADK | Implemented | `agents/`, `backend/app/core/adk_runtime.py` |
| MCP tools | Implemented (5 operational) | `mcp/`, `backend/app/core/mcp_runtime.py` |
| Multi-agent architecture | Implemented (8 agents) | `agents/` |
| Business impact | Documented | `docs/01_PROJECT_BRIEF.md` |
| Security & safety | Implemented | `agents/guardian/` |
| Evaluation pipeline | Implemented | `evaluation/`, `/evaluation` UI |
| Human-in-the-loop | Documented; API pending Sprint 4 | `docs/02_ARCHITECTURE.md` |
| Deployability | Implemented | `docker-compose.yml`, `scripts/reset_demo.py` |
| Documentation | Implemented | `README.md`, `docs/` |
| Submission notebook | Planned Sprint 4 | — |
| Demo video | Planned Sprint 4 | — |

---

## Google ADK

**What judges should see:** Native Google Agent Development Kit integration with registered agent configurations and Gemini runtime.

| Artifact | Location |
|----------|----------|
| ADK runtime initialization | `backend/app/core/adk_runtime.py` |
| Agent ADK definitions | `agents/*/agent.py` |
| AI runtime registry | `backend/app/ai/runtime.py`, `backend/app/ai/registry.py` |
| Gemini provider | `backend/app/ai/provider.py` |
| Connectivity test | `GET /api/v1/ai/test` |

**Gap (Sprint 4):** ADK session checkpointing, `adk eval` integration.

---

## MCP (Model Context Protocol)

**What judges should see:** Registered MCP tool server with operational tools and API introspection.

| Artifact | Location |
|----------|----------|
| Tool registry | `mcp/registry.py` |
| Server lifecycle | `mcp/server.py` |
| Tool implementations | `mcp/tools/` |
| MCP status API | `GET /api/v1/system/mcp` |
| Architecture diagram | `docs/architecture/mcp-interaction.md` |

**Registered tools:** `health`, `list_incidents`, `incident_details`, `list_logs`, `system_info`

**Gap (Sprint 4):** Domain tools (`evidence_collector`, `threat_intel_lookup`, etc.).

---

## Multi-agent architecture

**What judges should see:** Eight specialized agents in a coordinated investigation pipeline with Guardian validation.

| Agent | Directory | API |
|-------|-----------|-----|
| Coordinator | `agents/coordinator/` | `POST /api/v1/agents/orchestrate` |
| Evidence | `agents/evidence/` | `POST /api/v1/agents/evidence` |
| Threat Intelligence | `agents/threat_intelligence/` | `POST /api/v1/agents/threat-intelligence` |
| MITRE Mapping | `agents/mitre/` | `POST /api/v1/agents/mitre` |
| Risk Assessment | `agents/risk/` | `POST /api/v1/agents/risk` |
| Response Planning | `agents/response/` | `POST /api/v1/agents/response` |
| Executive Report | `agents/executive_report/` | `POST /api/v1/agents/executive-report` |
| Guardian | `agents/guardian/` | `POST /api/v1/agents/guardian/validate` |

**Orchestration:** `POST /api/v1/investigations/run` → `InvestigationWorkflowService`

**Diagrams:** `docs/architecture/agent-workflow.md`, `docs/architecture/investigation-sequence.md`

---

## Security

**What judges should see:** Dedicated Guardian Agent with prompt injection detection, PII scanning, schema validation, and confidence thresholds.

| Capability | Location |
|------------|----------|
| Prompt injection detection | `agents/guardian/prompt_injection.py` |
| PII detection | `agents/guardian/pii_detector.py` |
| Output validation | `agents/guardian/validator.py` |
| Workflow integration | `backend/app/services/orchestration_guardian.py` |
| Audit persistence | `guardian_audits` table, `GET /incidents/{id}/guardian-audits` |
| Secrets in env only | `.env.example`, `backend/app/core/ai_config.py` |
| Sanitized replay export | `backend/app/utils/sanitize.py` |

**Gap (Sprint 4):** API authentication, response plan approval enforcement.

---

## Deployability

**What judges should see:** One-command Docker startup and offline demo mode.

| Artifact | Location |
|----------|----------|
| Docker Compose | `docker-compose.yml` |
| Backend image | `docker/Dockerfile.backend` |
| Frontend image | `docker/Dockerfile.frontend` |
| Demo reset script | `scripts/reset_demo.py` |
| Dev scripts | `scripts/dev.sh`, `scripts/dev-backend.sh`, `scripts/dev-frontend.sh` |
| Environment template | `.env.example` |

**Verify:**

```bash
docker compose up --build
python scripts/reset_demo.py
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/ai/test
```

---

## Evaluation

**What judges should see:** Structured agent evaluation with metrics API and dashboard.

| Artifact | Location |
|----------|----------|
| Evaluation engine | `evaluation/engine.py` |
| Benchmark runner | `evaluation/benchmark.py` |
| Metrics API | `GET /api/v1/evaluation` |
| Dashboard UI | `frontend/src/pages/EvaluationPage.tsx` |
| Persistence | `evaluation_metrics` table |

**Gap (Sprint 4):** 30-scenario labeled evaluation library.

---

## Documentation for reviewers

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview and quickstart |
| `docs/01_PROJECT_BRIEF.md` | Vision and competition context |
| `docs/02_ARCHITECTURE.md` | Authoritative architecture reference |
| `docs/architecture/` | Diagrams and sequence documentation |
| `docs/demo/` | Screenshot gallery |
| `docs/07_SUBMISSION_CHECKLIST.md` | Pre-submission verification |
| `ROADMAP.md` | Future milestones |
| `CHANGELOG.md` | Release history |

---

## Submission gaps (Sprint 4)

1. Kaggle submission notebook
2. Demo video (≤ 3 minutes)
3. Synthetic alert datasets in `datasets/alerts/`
4. API bearer-token authentication
5. Human approval workflow for response plans
6. Docker production profile (Nginx, non-root)

See [`07_SUBMISSION_CHECKLIST.md`](07_SUBMISSION_CHECKLIST.md) for the full checklist.
