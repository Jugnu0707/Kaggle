# Oz AI — Screenshot Checklist

**Purpose:** Define every screenshot required for the Kaggle notebook and verify availability.

---

## Resolution standards

| Source | Resolution | Authenticity |
|--------|------------|--------------|
| `docs/screenshots/` | 1440×900 | PIL-generated renders (`scripts/generate_assets.py`) |
| `demo/output/screenshots/` | 1920×1080 | Live Playwright captures (`scripts/record_demo.py`) |

**Recommendation:** Upload live captures from `demo/output/screenshots/` to Kaggle where available. Use `docs/screenshots/` only when no live capture exists.

---

## Required screenshots

### 1. Dashboard

| Field | Value |
|-------|-------|
| **Title** | Security Operations Dashboard |
| **Purpose** | Show incident volume and recent activity |
| **When to capture** | After `scripts/reset_demo.py`, navigate to `/` |
| **Expected data** | Total Incidents, Critical/High counts, Recent Incidents table |
| **Framing** | Full page including sidebar |
| **Zoom** | 100% |
| **Notebook section** | §5 Solution Overview, §10 Screenshots |
| **Repo file** | `docs/screenshots/dashboard.png` ✓ |
| **Live capture** | `demo/output/screenshots/dashboard.png` ✓ |

### 2. Incident List

| Field | Value |
|-------|-------|
| **Title** | Incidents |
| **Purpose** | Show seeded demo incidents including PowerShell showcase |
| **When to capture** | `/incidents` with demo data loaded |
| **Expected data** | Suspicious PowerShell Execution (High), 10 incidents |
| **Framing** | Table centered, sidebar visible |
| **Notebook section** | §10 Screenshots |
| **Repo file** | **Missing** in `docs/screenshots/` |
| **Live capture** | `demo/output/screenshots/incidents.png` ✓ |

### 3. Incident Detail

| Field | Value |
|-------|-------|
| **Title** | Incident Detail — Overview |
| **Purpose** | Show incident metadata and description |
| **When to capture** | Click Suspicious PowerShell Execution |
| **Expected data** | Severity, status, description, evidence count |
| **Repo file** | `docs/screenshots/incident-details.png` ✓ |
| **Live capture** | `demo/output/screenshots/overview.png` ✓ |

### 4. Threat Intelligence

| Field | Value |
|-------|-------|
| **Title** | Threat Intelligence tab |
| **Purpose** | IOC enrichment results |
| **Expected data** | IOC table, reputation indicators |
| **Repo file** | `docs/screenshots/threat-intelligence.png` ✓ |
| **Live capture** | `demo/output/screenshots/threat_intelligence.png` ✓ |

### 5. MITRE ATT&CK

| Field | Value |
|-------|-------|
| **Title** | MITRE ATT&CK tab |
| **Expected data** | Technique IDs (e.g. T1059.001) |
| **Repo file** | `docs/screenshots/mitre.png` ✓ |
| **Live capture** | `demo/output/screenshots/mitre.png` ✓ |

### 6. Risk Assessment

| Field | Value |
|-------|-------|
| **Title** | Risk Assessment tab |
| **Expected data** | Overall risk, confidence, severity |
| **Repo file** | `docs/screenshots/risk-assessment.png` ✓ |
| **Live capture** | `demo/output/screenshots/risk.png` ✓ |

### 7. Response Plan

| Field | Value |
|-------|-------|
| **Title** | Response Plan tab |
| **Expected data** | Containment, eradication, recovery steps |
| **Repo file** | `docs/screenshots/response-plan.png` ✓ |
| **Live capture** | `demo/output/screenshots/response.png` ✓ |

### 8. Executive Report

| Field | Value |
|-------|-------|
| **Title** | Executive Report tab |
| **Expected data** | Management summary, recommendations |
| **Repo file** | `docs/screenshots/executive-report.png` ✓ |
| **Live capture** | `demo/output/screenshots/executive_report.png` ✓ |

### 9. Guardian Audit

| Field | Value |
|-------|-------|
| **Title** | Guardian Audit tab |
| **Expected data** | Validation records, confidence, PII/secret flags |
| **Repo file** | `docs/screenshots/guardian.png` ✓ |
| **Live capture** | `demo/output/screenshots/guardian.png` ✓ |

### 10. Timeline

| Field | Value |
|-------|-------|
| **Title** | Investigation Timeline |
| **Expected data** | Chronological events |
| **Repo file** | `docs/screenshots/timeline.png` ✓ |
| **Live capture** | `demo/output/screenshots/timeline.png` ✓ |

### 11. Investigation Runner

| Field | Value |
|-------|-------|
| **Title** | Investigation Runner |
| **Purpose** | Show pipeline execution UI |
| **Repo file** | `docs/screenshots/investigation-runner.png` ✓ |
| **Live capture** | Capture during `record_demo.py` Scene 5 (not saved separately) |

### 12. Replay

| Field | Value |
|-------|-------|
| **Title** | Investigation Replay |
| **Expected data** | Step list, AI/Fallback badges, timing |
| **Repo file** | **Missing** in `docs/screenshots/` |
| **Live capture** | `demo/output/screenshots/replay.png` ✓ |

### 13. Evaluation

| Field | Value |
|-------|-------|
| **Title** | Evaluation Dashboard |
| **Expected data** | Overall health score, per-agent metrics |
| **Repo file** | `docs/screenshots/evaluation-dashboard.png` ✓ |
| **Live capture** | `demo/output/screenshots/evaluation.png` ✓ |

### 14. Reports

| Field | Value |
|-------|-------|
| **Title** | Reports |
| **Expected data** | Incident list linking to executive report tabs |
| **Repo file** | **Missing** |
| **Live capture** | **Missing** — capture `/reports` after demo seed |
| **Action** | Run app, open Reports, screenshot before submission |

### 15. Settings

| Field | Value |
|-------|-------|
| **Title** | System Settings |
| **Expected data** | ADK status, MCP tools, database health |
| **Repo file** | **Missing** in `docs/screenshots/` |
| **Live capture** | `demo/output/screenshots/settings.png` ✓ |

### 16. Log Upload

| Field | Value |
|-------|-------|
| **Title** | Log Uploads |
| **Expected data** | Upload form, uploaded log list |
| **Repo file** | **Missing** |
| **Live capture** | **Missing** — capture `/logs` after demo seed |
| **Action** | Run app, open Log Uploads, screenshot before submission |

---

## Capture workflow

```bash
./scripts/dev.sh
backend/.venv/bin/python scripts/reset_demo.py
backend/.venv/bin/python scripts/record_demo.py   # produces demo/output/screenshots/*.png
```

Manual captures still needed:

1. `/reports` → save as `images/reports.png`
2. `/logs` → save as `images/log-upload.png`

---

## Pre-submission checklist

- [ ] All 16 screenshots captured at 1920×1080 or consistent aspect ratio
- [ ] No API keys visible in any screenshot
- [ ] Demo incident "Suspicious PowerShell Execution" visible where applicable
- [ ] Files copied to Kaggle notebook `images/` directory per `NOTEBOOK_IMAGES.md`
