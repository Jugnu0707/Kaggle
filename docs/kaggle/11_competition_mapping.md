# Competition Mapping

**Related:** [08 Results](08_results.md) · [COMPETITION_ALIGNMENT.md](../COMPETITION_ALIGNMENT.md) · [12 Submission Notes](12_submission_notes.md)

**Competition:** Kaggle AI Agents Intensive Capstone  
**Track:** Agents for Business  
**Project:** Oz AI — Enterprise Incident Response Platform

---

## Requirement matrix

| Requirement | Status | Implementation | Evidence |
|-------------|--------|----------------|----------|
| **Multi-agent system** | Implemented | 8 specialist agents in coordinated pipeline | `agents/`, `POST /api/v1/investigations/run` |
| **Google ADK** | Implemented | ADK runtime, agent configs, registry | `backend/app/core/adk_runtime.py`, `agents/*/agent.py` |
| **MCP** | Implemented | 5 operational tools, registry, introspection | `mcp/`, `GET /api/v1/system/mcp` |
| **Agent skills / specialization** | Implemented | Single mission per agent with typed schemas | [05 AI Agents](05_ai_agents.md) |
| **Security & safety** | Implemented | Guardian validation between stages | `agents/guardian/`, [06 Security](06_security.md) |
| **Business impact** | Documented | Enterprise incident response / MTTR reduction | [01 Problem Statement](01_problem_statement.md) |
| **Evaluation** | Implemented | Engine, health scores, dashboard, 176 tests | `evaluation/`, `/evaluation` |
| **Deployability** | Implemented | Docker Compose, demo reset, offline mode | `docker-compose.yml`, `scripts/reset_demo.py` |
| **Documentation** | Implemented | README, architecture, kaggle writeup | `README.md`, `docs/` |
| **Human-in-the-loop** | Documented | Approval workflow planned; not enforced | [09 Limitations](09_limitations.md) |
| **Innovation** | Implemented | Guardian gates, replay explainability, offline fallbacks | Investigation Replay, `ai_used`/`fallback_used` flags |
| **User experience** | Implemented | 10-page React dashboard | `frontend/src/pages/` |

---

## Google ADK

| Artifact | Location |
|----------|----------|
| ADK runtime initialization | `backend/app/core/adk_runtime.py` |
| Agent ADK definitions | `agents/*/agent.py` |
| AI runtime registry | `backend/app/ai/runtime.py`, `registry.py` |
| Gemini provider | `backend/app/ai/provider.py` |
| Connectivity test | `GET /api/v1/ai/test` |
| Versioned prompts | `agents/*/prompt.md` |

**Gap:** ADK session checkpointing, `adk eval` not implemented.

---

## MCP

| Artifact | Location |
|----------|----------|
| Tool registry | `mcp/registry.py` |
| Server lifecycle | `mcp/server.py` |
| Tool implementations | `mcp/tools/` |
| MCP status API | `GET /api/v1/system/mcp` |

**Tools:** `health`, `list_incidents`, `incident_details`, `list_logs`, `system_info`

**Gap:** Domain tools not implemented; agents call services directly.

---

## Multi-agent architecture

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

**Orchestration:** `InvestigationWorkflowService` via `POST /api/v1/investigations/run`

---

## Security

| Capability | Location |
|------------|----------|
| Prompt injection detection | `agents/guardian/prompt_injection.py` |
| PII detection and masking | `agents/guardian/pii_detector.py` |
| Secret detection and masking | `agents/guardian/secret_detector.py` |
| Schema validation | `agents/guardian/validator.py` |
| Workflow integration | `backend/app/services/orchestration_guardian.py` |
| Audit persistence | `guardian_audits` table |

**Gap:** API authentication, approval enforcement not implemented.

---

## Deployability

| Artifact | Location |
|----------|----------|
| Docker Compose | `docker-compose.yml` |
| Backend image | `docker/Dockerfile.backend` |
| Frontend image | `docker/Dockerfile.frontend` |
| Demo reset | `scripts/reset_demo.py` |
| Environment template | `.env.example` |

**Judge commands:**

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle && cp .env.example .env
docker compose up --build
python scripts/reset_demo.py
```

---

## Evaluation

| Artifact | Location |
|----------|----------|
| Evaluation engine | `evaluation/engine.py` |
| Benchmark runner | `evaluation/benchmark.py` |
| Health scorer | `evaluation/scorer.py` |
| Metrics API | `GET /api/v1/evaluation` |
| Dashboard UI | `/evaluation` |
| Automated tests | 176 collected |

**Gap:** 30-scenario labeled library not populated.

---

## Submission gaps

| Item | Status |
|------|--------|
| Kaggle submission notebook | Pending |
| Demo video | Pending |
| API authentication | Planned |
| Human approval workflow | Planned |
| Domain MCP tools | Planned |

See [12 Submission Notes](12_submission_notes.md).
