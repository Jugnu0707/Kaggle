# Evaluation

**Related:** [04 Implementation](04_implementation.md) · [08 Results](08_results.md) · [09 Limitations](09_limitations.md)

Oz AI evaluates agent quality, system reliability, and operational performance through automated tests, fallback verification, performance benchmarks, and a live Evaluation Dashboard.

---

## Evaluation Engine

Location: `evaluation/engine.py`

Runs automatically at the end of each investigation workflow. Collects execution metrics from completed pipeline stages and persists results to the `evaluation_metrics` table.

Supporting modules:

| Module | Purpose |
|--------|---------|
| `evaluation/benchmark.py` | Offline agent benchmarks with labeled scenarios |
| `evaluation/metrics.py` | Execution metric dataclasses and aggregation |
| `evaluation/scorer.py` | Health score calculation |
| `evaluation/report_generator.py` | Evaluation report generation |

---

## Health Score

Location: `evaluation/scorer.py`

Weighted composite score (0–100) per agent:

| Component | Weight | Measures |
|-----------|--------|----------|
| Availability | 30% | Success rate without hard failures |
| Reliability | 30% | Consistent success, low retry pressure |
| Performance | 20% | Mean execution time vs. 5 s target |
| Accuracy | 20% | Benchmark confidence or success rate |

Performance degrades linearly between 5 s (score 100) and 15 s (score 0).

---

## Replay

Location: `backend/app/models/investigation_replay.py`, `investigation_replay_service.py`

Each investigation run persists step records to `investigation_replays`:

| Field | Purpose |
|-------|---------|
| `step_number` | Ordered stage index |
| `agent_name` | Executed agent or engine |
| `duration_ms` | Stage latency |
| `ai_used` | Whether Gemini was used |
| `fallback_used` | Whether fallback path executed |
| `input_summary` / `output_summary` | Sanitized summaries |

**APIs:**

- `GET /api/v1/investigations/{run_id}/replay`
- `GET /api/v1/investigations/{run_id}/explain`
- `GET /api/v1/investigations/{run_id}/replay/export`

**UI:** Investigation Replay page at `/investigations/:runId/replay`

---

## Metrics

### Persisted metrics (`evaluation_metrics`)

| Field | Description |
|-------|-------------|
| `agent_name` | Agent identifier |
| `execution_time_ms` | Stage duration |
| `ai_used` | Gemini usage flag |
| `fallback_used` | Fallback usage flag |
| `success` | Execution success |
| `confidence` | Optional confidence score |

### API

- `GET /api/v1/evaluation` — all agent health scores
- `GET /api/v1/evaluation/{agent_name}` — single agent detail

### UI

Evaluation dashboard at `/evaluation` (`EvaluationPage.tsx`)

---

## Testing

### Repository statistics (verified)

| Metric | Count |
|--------|-------|
| Automated tests | 176 |
| API paths | 35 |
| API operations | 39 |
| AI agents | 8 |
| MCP tools | 5 |
| Database tables | 16 |
| Frontend pages | 10 |

Regenerate: `python scripts/generate_repo_stats.py`

### Test coverage

| Category | Examples |
|----------|----------|
| API endpoints | Incidents, logs, investigations, agents, evaluation |
| Guardian | Prompt injection, PII detection, schema validation |
| Workflow | Investigation run, replay, explain, export |
| MCP | Registry, server lifecycle, tool handlers |
| AI connectivity | `GET /api/v1/ai/test` success, quota, timeout, auth |
| Database | Table initialization, 16 expected tables |
| Agent services | Per-agent unit tests in `agents/*/tests/` |

```bash
cd backend && uv run pytest
```

Prior sprint hardening reported ~93% line coverage across `app`, `agents`, `mcp`, and `evaluation` packages. Regenerate with:

```bash
cd backend && uv run pytest --cov=app --cov=agents --cov=mcp --cov=evaluation --cov-report=term
```

### AI fallback verification

| Scenario | Expected behavior |
|----------|-------------------|
| Missing `GOOGLE_API_KEY` | Agents use rule engines |
| Quota exceeded (429) | Fallback paths activate |
| Request timeout | Fallback after timeout |
| Invalid API key | `connected: false` on AI test |
| Guardian rejection | Workflow continues with fallback |

Offline demo: `python scripts/reset_demo.py` — ten incidents, twenty-five logs, no API key required.

### Performance benchmarks

From `scripts/sprint3_performance_benchmark.py` (in-process TestClient, offline fallbacks). Source: `docs/SPRINT3_PERFORMANCE_REPORT.md`

| Operation | Mean (ms) |
|-----------|-----------|
| Full investigation execution | 36.57 |
| Dashboard load | 3.51 |
| Evaluation dashboard load | 2.08 |

Notes: benchmarks exclude network latency. Gemini calls add seconds per AI-first agent in production. Offline full investigation completes under 50 ms in the benchmark environment.

---

## Evaluation gaps

| Gap | Detail |
|-----|--------|
| 30-scenario library | Benchmark scenarios exist; comprehensive labeled library not populated |
| `adk eval` | Google ADK evaluation CLI not integrated |
| CI regression gates | Health score thresholds not enforced in CI |

See [09 Limitations](09_limitations.md).
