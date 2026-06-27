# Sprint 3 Performance Report

**Generated:** 2026-06-27T03:43:49.112042+00:00

| Operation | Mean (ms) | Min (ms) | Max (ms) |
|-----------|-----------|----------|----------|
| Dashboard load | 3.51 | 1.61 | 7.08 |
| Incident details load | 2.63 | 1.8 | 4.05 |
| Full investigation execution | 36.57 | 29.01 | 50.4 |
| Agent: Coordinator Agent | 0 | 0 | 0 |
| Agent: Evidence | 2 | 2 | 2 |
| Agent: Threat Intelligence | 1 | 1 | 1 |
| Agent: MITRE | 1 | 1 | 1 |
| Agent: Risk | 4 | 4 | 4 |
| Agent: Response | 3 | 3 | 3 |
| Agent: Executive Report | 4 | 4 | 4 |
| Agent: Timeline | 3 | 3 | 3 |
| Agent: Evaluation | 0 | 0 | 0 |
| Replay generation | 2.13 | 1.87 | 2.6 |
| Timeline generation (API) | 5.47 | 5.12 | 5.68 |
| Evaluation dashboard load | 2.08 | 1.96 | 2.29 |

## Notes

- Benchmarks run in-process via FastAPI TestClient (no network overhead).
- Investigation timing includes full Coordinator workflow with offline fallbacks.
- Production timings vary with hardware, Gemini API latency, and dataset size.
