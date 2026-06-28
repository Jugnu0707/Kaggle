# Oz AI — Notebook Image Mapping

Maps Kaggle notebook `images/` placeholders to repository files.

Copy files into your Kaggle notebook `images/` directory before publishing.

---

## Mapping table

| Notebook path | Recommended source | Fallback | Notebook section |
|---------------|-------------------|----------|------------------|
| `images/dashboard.png` | `demo/output/screenshots/dashboard.png` | `docs/screenshots/dashboard.png` | §9 |
| `images/incidents.png` | `demo/output/screenshots/incidents.png` | Capture `/incidents` | §9 |
| `images/incident-detail.png` | `demo/output/screenshots/overview.png` | `docs/screenshots/incident-details.png` | §9 |
| `images/threat-intelligence.png` | `demo/output/screenshots/threat_intelligence.png` | `docs/screenshots/threat-intelligence.png` | §9 |
| `images/mitre.png` | `demo/output/screenshots/mitre.png` | `docs/screenshots/mitre.png` | §9 |
| `images/risk-assessment.png` | `demo/output/screenshots/risk.png` | `docs/screenshots/risk-assessment.png` | §9 |
| `images/response-plan.png` | `demo/output/screenshots/response.png` | `docs/screenshots/response-plan.png` | §9 |
| `images/executive-report.png` | `demo/output/screenshots/executive_report.png` | `docs/screenshots/executive-report.png` | §9 |
| `images/guardian.png` | `demo/output/screenshots/guardian.png` | `docs/screenshots/guardian.png` | §9 |
| `images/timeline.png` | `demo/output/screenshots/timeline.png` | `docs/screenshots/timeline.png` | §9 |
| `images/replay.png` | `demo/output/screenshots/replay.png` | Capture `/investigations/{runId}/replay` | §9 |
| `images/evaluation.png` | `demo/output/screenshots/evaluation.png` | `docs/screenshots/evaluation-dashboard.png` | §9 |
| `images/settings.png` | `demo/output/screenshots/settings.png` | Capture `/settings` | §9 |
| `images/reports.png` | **Capture manually** `/reports` | — | §9 |
| `images/log-upload.png` | **Capture manually** `/logs` | — | §9 |

---

## Optional supplementary images

| Notebook path | Source | Purpose |
|---------------|--------|---------|
| `images/investigation-runner.png` | `docs/screenshots/investigation-runner.png` | Pipeline execution UI |
| `images/evidence.png` | `docs/screenshots/evidence.png` | Evidence tab (if cited separately) |
| `images/architecture.png` | `docs/architecture.png` | Architecture diagram |

---

## Markdown snippets (copy into notebook)

```markdown
![Dashboard](images/dashboard.png)
![Incident List](images/incidents.png)
![Incident Detail](images/incident-detail.png)
![Threat Intelligence](images/threat-intelligence.png)
![MITRE ATT&CK](images/mitre.png)
![Risk Assessment](images/risk-assessment.png)
![Response Plan](images/response-plan.png)
![Executive Report](images/executive-report.png)
![Guardian Audit](images/guardian.png)
![Timeline](images/timeline.png)
![Investigation Replay](images/replay.png)
![Evaluation Dashboard](images/evaluation.png)
![Reports](images/reports.png)
![Settings](images/settings.png)
![Log Upload](images/log-upload.png)
```

---

## Authenticity note

- **`demo/output/screenshots/`** — live browser captures from `scripts/record_demo.py` (1920×1080).
- **`docs/screenshots/`** — stylized PIL renders from `scripts/generate_assets.py` (1440×900).

Prefer live captures for the Kaggle notebook when available.

---

## Demo video

| Asset | Path |
|-------|------|
| Local recording | `demo/output/demo.mp4` |
| Kaggle upload | Upload separately; link in notebook §16 |

---

## Copy commands (from repo root)

```bash
mkdir -p kaggle_images
cp demo/output/screenshots/dashboard.png kaggle_images/dashboard.png
cp demo/output/screenshots/incidents.png kaggle_images/incidents.png
cp demo/output/screenshots/overview.png kaggle_images/incident-detail.png
cp demo/output/screenshots/threat_intelligence.png kaggle_images/threat-intelligence.png
cp demo/output/screenshots/mitre.png kaggle_images/mitre.png
cp demo/output/screenshots/risk.png kaggle_images/risk-assessment.png
cp demo/output/screenshots/response.png kaggle_images/response-plan.png
cp demo/output/screenshots/executive_report.png kaggle_images/executive-report.png
cp demo/output/screenshots/guardian.png kaggle_images/guardian.png
cp demo/output/screenshots/timeline.png kaggle_images/timeline.png
cp demo/output/screenshots/replay.png kaggle_images/replay.png
cp demo/output/screenshots/evaluation.png kaggle_images/evaluation.png
cp demo/output/screenshots/settings.png kaggle_images/settings.png
# Manually add reports.png and log-upload.png after capturing /reports and /logs
```

Rename `kaggle_images/` to `images/` in the Kaggle notebook file browser.
