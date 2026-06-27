# Evaluation

Oz AI evaluates agent quality, system reliability, and operational performance through automated tests, AI fallback verification, performance benchmarks, reliability scenarios, and a live Evaluation Dashboard.

---

## Test coverage

| Metric | Value |
|--------|-------|
| Tests collected | **176** |
| Test locations | `tests/`, `evaluation/tests/`, `agents/*/tests/` |
| API inventory test | Validates 35 paths / 39 operations |
| E2E integration | Full analyst workflow through replay (`test_sprint3_e2e_integration.py`) |
| Reliability tests | Quota errors, AI unavailable, invalid key, missing logs (`test_reliability.py`) |
| Agent tests | Per-agent unit and service tests with labeled scenarios |

**Run tests:**

```bash
cd backend && uv run pytest
```

**Coverage:** Prior sprint hardening reported ~93% line coverage across `app`, `agents`, `mcp`, and `evaluation` packages. Regenerate with:

```bash
cd backend && uv run pytest --cov=app --cov=agents --cov=mcp --cov=evaluation --cov-report=term
```

**Test categories:**

| Category | Examples |
|----------|----------|
| API endpoints | Incidents, logs, investigations, agents, evaluation |
| Guardian | Prompt injection, PII detection, schema validation |
| Workflow | Investigation run, replay, explain, export |
| MCP | Registry, server lifecycle, tool handlers |
| AI connectivity | `GET /api/v1/ai/test` success, quota, timeout, auth |
| Database | Table initialization, expected 16 tables |

---

## AI fallback verification

Oz AI guarantees workflow continuity when Gemini is unavailable:

| Scenario | Expected behavior | Test |
|----------|-------------------|------|
| Missing `GOOGLE_API_KEY` | Agents use rule engines | Demo mode, reliability tests |
| Quota exceeded (429) | Fallback paths activate | `test_reliability.py`, agent service tests |
| Request timeout | Fallback after 30s | Agent service timeout tests |
| Invalid API key | Connectivity test returns `connected: false` | `test_ai_test.py` |
| Guardian rejection | Workflow continues with fallback signal | Orchestration guardian tests |

**Offline demo:** `python scripts/reset_demo.py` seeds 10 incidents with 25 logs and runs investigations without any API key — all agent tabs populate via fallbacks.

**Replay transparency:** Each replay step records `ai_used` and `fallback_used` flags so judges can verify AI vs. rule-engine execution per stage.

---

## Performance

Benchmarks from `scripts/sprint3_performance_benchmark.py` (in-process via FastAPI TestClient, offline fallbacks):

| Operation | Mean (ms) | Min (ms) | Max (ms) |
|-----------|-----------|----------|----------|
| Dashboard load | 3.51 | 1.61 | 7.08 |
| Incident details load | 2.63 | 1.80 | 4.05 |
| **Full investigation execution** | **36.57** | **29.01** | **50.40** |
| Agent: Evidence | 2 | 2 | 2 |
| Agent: Threat Intelligence | 1 | 1 | 1 |
| Agent: MITRE | 1 | 1 | 1 |
| Agent: Risk | 4 | 4 | 4 |
| Agent: Response | 3 | 3 | 3 |
| Agent: Executive Report | 4 | 4 | 4 |
| Agent: Timeline | 3 | 3 | 3 |
| Replay generation | 2.13 | 1.87 | 2.60 |
| Timeline generation (API) | 5.47 | 5.12 | 5.68 |
| Evaluation dashboard load | 2.08 | 1.96 | 2.29 |

**Notes:**

- In-process benchmarks exclude network latency.
- Production Gemini calls add ~2–5 seconds per AI-first agent depending on model and quota.
- Full offline investigation completes in under 50 ms in the benchmark environment.

Source: `docs/SPRINT3_PERFORMANCE_REPORT.md`

---

## Reliability

| Check | Status |
|-------|--------|
| Workflow survives Gemini quota errors | Verified |
| Workflow survives missing API key | Verified |
| No unhandled exceptions on AI test endpoint | Verified |
| Database reinitialization on startup | Verified |
| Investigation without logs returns appropriate error | Verified |
| Guardian audits persisted on every validation | Verified |
| Append-only audit trail | Enforced by application design |

**Connectivity probe:** `GET /api/v1/ai/test` — single minimal Gemini call, structured error responses for quota, auth, and timeout.

---

## Evaluation Dashboard

**Route:** `/evaluation`  
**API:** `GET /api/v1/evaluation`, `GET /api/v1/evaluation/{agent_name}`

The Evaluation Dashboard surfaces:

- Per-agent health scores
- Benchmark metrics persisted to `evaluation_metrics`
- Agent performance trends from offline evaluation runs

The Evaluation Engine runs automatically at the end of each investigation workflow, scoring outputs from the completed pipeline.

**Offline evaluation package:** `evaluation/benchmark.py` runs labeled scenarios without external dependencies. Results can be written to `evaluation/results/` (gitignored).

**Gap (Sprint 4):** 30-scenario labeled evaluation library for comprehensive regression testing.

---

## Evaluation summary

| Dimension | Result |
|-----------|--------|
| Automated tests | 176 collected |
| Full investigation (offline) | ~37 ms mean |
| AI fallback | Verified across 4 AI-first agents |
| Guardian validation | Every workflow stage |
| Live dashboard | `/evaluation` with API backing |
| Replay explainability | AI/fallback flags per step |

Oz AI demonstrates that a multi-agent incident response platform can be thoroughly tested, benchmarked, and evaluated without requiring live Gemini access — while still enriching outputs when API keys are configured.
