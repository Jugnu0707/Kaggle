# Oz AI — Submission & Demo Checklist

**Competition:** Kaggle AI Agents Intensive Capstone · Agents for Business  
**Repository:** https://github.com/Jugnu0707/Kaggle  
**Last updated:** RC2 Task 5

Status: **Complete** · **Pending** · **Verify before submit**

---

## GitHub repository

| Item | Status | Verification |
|------|--------|--------------|
| Repository public | Verify | https://github.com/Jugnu0707/Kaggle accessible without login |
| README complete | Complete | Architecture, quickstart, stats, demo workflow |
| LICENSE (MIT) | Complete | `LICENSE` present |
| CONTRIBUTING, SECURITY, CODE_OF_CONDUCT | Complete | Root community files |
| No secrets in git | Verify | `.env` gitignored; run `git log -p -- .env` — no commits |
| `.env.example` present | Complete | No real API keys in template |

---

## Documentation

| Item | Status | Path |
|------|--------|------|
| Kaggle writeup (assembled) | Complete | `docs/kaggle/FINAL_WRITEUP.md` |
| Kaggle source docs (01–12) | Complete | `docs/kaggle/0*.md`, `1*.md` |
| Architecture docs | Complete | `docs/architecture/01–10` |
| Competition mapping | Complete | `docs/kaggle/11_competition_mapping.md` |
| Demo script (final) | Complete | `docs/demo/FINAL_DEMO_SCRIPT.md` |
| Storyboard (final) | Complete | `docs/demo/FINAL_STORYBOARD.md` |
| Recording guide (final) | Complete | `docs/demo/FINAL_RECORDING_GUIDE.md` |
| Judge FAQ | Complete | `docs/demo/JUDGE_FAQ.md` |

---

## Screenshots

| Item | Status | Path |
|------|--------|------|
| Dashboard | Complete | `docs/screenshots/dashboard.png` |
| Incident details | Complete | `docs/screenshots/incident-details.png` |
| Threat Intelligence | Complete | `docs/screenshots/threat-intelligence.png` |
| MITRE | Complete | `docs/screenshots/mitre.png` |
| Risk Assessment | Complete | `docs/screenshots/risk-assessment.png` |
| Response Plan | Complete | `docs/screenshots/response-plan.png` |
| Executive Report | Complete | `docs/screenshots/executive-report.png` |
| Guardian | Complete | `docs/screenshots/guardian.png` |
| Timeline | Complete | `docs/screenshots/timeline.png` |
| Evaluation Dashboard | Complete | `docs/screenshots/evaluation-dashboard.png` |
| Investigation Runner | Complete | `docs/screenshots/investigation-runner.png` |
| Evidence view | Partial | No dedicated Evidence tab — use Overview + `/logs` |
| Settings page | Pending | Live browser capture recommended |
| Investigation Replay | Pending | Live browser capture recommended |
| Reports page | Pending | Live browser capture recommended |
| Log Upload page | Pending | Live browser capture recommended |

Note: existing screenshots are programmatic renders, not live browser captures.

---

## Demo video

| Item | Status | Action |
|------|--------|--------|
| Demo script finalized | Complete | `docs/demo/FINAL_DEMO_SCRIPT.md` |
| Storyboard finalized | Complete | `docs/demo/FINAL_STORYBOARD.md` |
| Recording guide finalized | Complete | `docs/demo/FINAL_RECORDING_GUIDE.md` |
| Environment rehearsed | Pending | Run pre-flight commands in recording guide |
| Video recorded | Pending | Target 4 min, max 5 min |
| Video edited and exported | Pending | 1080p H.264 |
| Video uploaded | Pending | YouTube (unlisted) or Vimeo |
| Video URL ready for submission | Pending | Add to Kaggle notebook |

---

## Kaggle writeup

| Item | Status | Action |
|------|--------|--------|
| Source content prepared | Complete | `docs/kaggle/01–12` |
| Assembled writeup | Complete | `docs/kaggle/FINAL_WRITEUP.md` (~2,276 words) |
| Kaggle notebook created | Pending | Copy/adapt writeup into notebook cells |
| Notebook published | Pending | Kaggle workspace |

---

## Demo verification

Run before recording and before submission:

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
cp .env.example .env
docker compose up --build          # or ./scripts/dev.sh
python scripts/reset_demo.py
```

| Check | Expected | Command |
|-------|----------|---------|
| Health | 200 | `curl localhost:8000/api/v1/health` |
| MCP tools | 5 | `curl localhost:8000/api/v1/system/mcp` |
| Demo incident | Visible | Open `/incidents` — **Suspicious PowerShell Execution** |
| Agent tabs populated | All tabs have data | Open incident — Threat Intel through Guardian |
| Evaluation dashboard | Health scores | Open `/evaluation` |
| Settings | ADK + MCP status | Open `/settings` |
| Offline demo | Works without key | Unset `GOOGLE_API_KEY`, re-run `reset_demo.py` |
| Tests pass | 176 collected | `cd backend && uv run pytest` |
| No secrets exposed | Clean | Do not commit `.env` |

---

## Docker verification

| Item | Status | Verification |
|------|--------|--------------|
| `docker compose up --build` succeeds | Verify | Both containers healthy |
| Backend port 8000 | Complete | `oz-ai-backend` |
| Frontend port 5173 | Complete | `oz-ai-frontend` |
| Volumes persist data | Complete | `oz-ai-data`, `oz-ai-uploads` |
| Backend healthcheck | Complete | curl in Dockerfile healthcheck |

---

## Technical requirements (competition)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Google ADK | Complete | `agents/*/agent.py`, ADK runtime |
| MCP | Complete | 5 tools, `GET /api/v1/system/mcp` |
| Multi-agent (8) | Complete | Investigation workflow |
| Security / Guardian | Complete | Between-stage validation |
| Deployability | Complete | Docker + demo reset |
| Evaluation | Complete | Engine + dashboard + 176 tests |
| Business impact | Complete | Enterprise incident response |

---

## Remaining before submission

- [ ] Record demo video (≤ 5 minutes)
- [ ] Upload video and capture URL
- [ ] Create Kaggle submission notebook from `FINAL_WRITEUP.md`
- [ ] Capture 4 live screenshots (Settings, Replay, Reports, Log Upload)
- [ ] Verify GitHub repository is public
- [ ] Final offline demo test on clean machine
- [ ] Regenerate repo stats: `python scripts/generate_repo_stats.py`
- [ ] Confirm no `.env` or API keys in repository history

---

## Pre-submission sign-off

| Role | Check | Date |
|------|-------|------|
| Demo reset works offline | ☐ | |
| Docker stack starts clean | ☐ | |
| Video ≤ 5:00 uploaded | ☐ | |
| Notebook published | ☐ | |
| Repo URL + video URL in submission form | ☐ | |
| No secrets in repo | ☐ | |

---

## Related documents

- [FINAL_DEMO_SCRIPT.md](FINAL_DEMO_SCRIPT.md)
- [FINAL_RECORDING_GUIDE.md](FINAL_RECORDING_GUIDE.md)
- [JUDGE_FAQ.md](JUDGE_FAQ.md)
- [docs/kaggle/final_checklist.md](../kaggle/final_checklist.md)
- [docs/kaggle/12_submission_notes.md](../kaggle/12_submission_notes.md)
