# Oz AI Demo Assets

Visual assets and **official Kaggle demonstration video** preparation materials for Oz AI.

## Video preparation (Sprint 4 Task 3)

| Document | Purpose |
|----------|---------|
| [demo_script.md](demo_script.md) | Full timed script (target 4:30) |
| [storyboard.md](storyboard.md) | Scene-by-scene screen, narration, duration |
| [narration.md](narration.md) | Speaking notes and delivery tips |
| [recording_checklist.md](recording_checklist.md) | Pre-flight checklist before recording |
| [demo_flow.md](demo_flow.md) | Step-by-step operator guide |
| [faq.md](faq.md) | Judge Q&A with implementation-backed answers |

**Showcase incident:** Suspicious PowerShell Execution  
**Do not record until checklist is complete.**

## Dashboard and navigation

| View | Asset | Route |
|------|-------|-------|
| Dashboard | [dashboard.png](dashboard.png) | `/` |
| Incident Details | [incident-details.png](incident-details.png) | `/incidents/:id` |
| Investigation Runner | [investigation-runner.png](investigation-runner.png) | `/incidents/:id/investigate` |

## Agent output tabs

| Agent / Feature | Asset | API |
|-----------------|-------|-----|
| Threat Intelligence | [threat-intelligence.png](threat-intelligence.png) | `GET /incidents/{id}/threat-intelligence` |
| MITRE Mapping | [mitre.png](mitre.png) | `GET /incidents/{id}/mitre` |
| Risk Assessment | [risk-assessment.png](risk-assessment.png) | `GET /incidents/{id}/risk` |
| Response Plan | [response-plan.png](response-plan.png) | `GET /incidents/{id}/response` |
| Executive Report | [executive-report.png](executive-report.png) | `GET /incidents/{id}/executive-report` |
| Guardian Audits | [guardian.png](guardian.png) | `GET /incidents/{id}/guardian-audits` |
| Timeline | [timeline.png](timeline.png) | `GET /incidents/{id}/timeline` |

## Platform views

| View | Asset | Route |
|------|-------|-------|
| Evaluation Dashboard | [evaluation-dashboard.png](evaluation-dashboard.png) | `/evaluation` |

## Demo workflow

```bash
# Reset database and seed 10 incidents with 25 logs
python scripts/reset_demo.py

# Start the stack
docker compose up --build
# or: scripts/dev.sh

# Open dashboard
open http://localhost:5173
```

## Regenerating screenshots

```bash
python scripts/generate_assets.py
cp docs/screenshots/*.png docs/demo/
```

## Related documentation

- [Architecture diagrams](../architecture/)
- [Competition alignment](../COMPETITION_ALIGNMENT.md)
- [Submission checklist](../07_SUBMISSION_CHECKLIST.md)
