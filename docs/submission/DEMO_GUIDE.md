# Demo Guide (Submission)

Step-by-step guide for Kaggle judges to run the Oz AI demonstration.

## Prerequisites

- Docker and Docker Compose
- Git
- Optional: `GOOGLE_API_KEY` for live Gemini enrichment

## Setup (5 minutes)

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
cp .env.example .env
# Optional: set GOOGLE_API_KEY in .env
docker compose up --build
```

In a second terminal (after containers are healthy):

```bash
cd Kaggle
cd backend && uv run python ../scripts/reset_demo.py
# or from repo root if uv installed: cd backend && uv run python ../scripts/reset_demo.py
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:5173 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |

## Showcase incident

**Suspicious PowerShell Execution** — High severity, 3 logs, full agent outputs pre-populated after `reset_demo.py`.

## Demonstration flow

| Step | Action | What to show |
|------|--------|--------------|
| 1 | Open Dashboard (`/`) | Incident counts, recent activity |
| 2 | Incidents → PowerShell incident | Title, severity, description |
| 3 | Overview tab | Evidence context, log count |
| 4 | Threat Intelligence tab | IOCs, reputation badges |
| 5 | MITRE tab | T1059.001 PowerShell, confidence |
| 6 | Risk tab | Risk level, score, narrative |
| 7 | Response tab | Containment, eradication, recovery |
| 8 | Executive Report tab | Leadership summary (no raw logs) |
| 9 | Guardian Audit tab | Per-agent validation records |
| 10 | Timeline tab | Chronological events |
| 11 | Evaluation (`/evaluation`) | Agent health scores |
| 12 | Settings (`/settings`) | Health, ADK loaded, 5 MCP tools |

## Run new investigation

1. Open incident → **Investigate** (`/incidents/:id/investigate`)
2. Click **Run New Investigation**
3. Wait for completion (polls status)
4. Open **Investigation Replay** — step list, AI/Fallback badges, export

## Offline fallback demo

```bash
# Clear GOOGLE_API_KEY in .env
cd backend && uv run python ../scripts/reset_demo.py
```

All tabs still populate. Replay shows `fallback_used: true` on AI-first stages.

## API smoke test

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/ai/test
curl http://localhost:8000/api/v1/system/mcp
```

## Video script

See [`../demo/demo_script.md`](../demo/demo_script.md) (target 4:30).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Empty incident tabs | Run `reset_demo.py` |
| Backend not reachable | `docker compose ps`, check port 8000 |
| AI test fails | Set `GOOGLE_API_KEY` or expect `connected: false` |
| Slow reset | Stop duplicate backend processes holding SQLite lock |
