# Oz AI Evaluation Framework

Self-contained evaluation harness for measuring agent quality, reliability, and performance without external monitoring tools.

## Responsibilities

- Measure accuracy, latency, reliability, fallback usage, success rate, and execution statistics
- Calculate weighted health scores per agent
- Generate JSON and Markdown evaluation reports
- Persist metrics to the `evaluation_metrics` database table

## Components

| Module | Purpose |
|--------|---------|
| `engine.py` | Orchestrates benchmarks, scoring, and report generation |
| `metrics.py` | Execution metric models and aggregation |
| `scorer.py` | Health score calculation (Availability 30%, Reliability 30%, Performance 20%, Accuracy 20%) |
| `benchmark.py` | Offline benchmarks for all nine agent stages |
| `report_generator.py` | JSON and Markdown report export |
| `datasets.py` | Synthetic benchmark scenarios |

## Benchmarked Agents

1. Coordinator Agent
2. Evidence Agent
3. Threat Intelligence Agent
4. MITRE Mapping Agent
5. Risk Assessment Agent
6. Response Planning Agent
7. Executive Report Agent
8. Guardian Agent
9. Timeline Engine

## API

- `GET /api/v1/evaluation` — overall score and per-agent summary
- `GET /api/v1/evaluation/{agent_name}` — detailed agent statistics

## Reports

Reports are written to `evaluation/results/` as:

- `evaluation_report_<timestamp>.json`
- `evaluation_report_<timestamp>.md`

## Constraints

- No Prometheus, Grafana, or external monitoring dependencies
- Works independently of Google AI availability (benchmarks use offline paths)
- Does not modify approved architecture layers

## Running Tests

```bash
cd backend && pytest ../evaluation/tests -v
```
