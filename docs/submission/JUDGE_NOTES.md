# Judge Notes (Submission)

Quick reference for Kaggle and Google engineer reviewers.

## What Oz AI is

Multi-agent **enterprise incident response** platform — eight Google ADK specialist agents, Guardian safety layer, MCP tools, investigation workflow with replay and evaluation. **Agents for Business** track.

## 60-second verdict

| Question | Answer |
|----------|--------|
| Does it use Google ADK? | Yes — 8 agents, runtime init, Settings page |
| Does it use MCP? | Yes — 5 operational tools, `/api/v1/system/mcp` |
| Multi-agent? | Yes — Coordinator + 7 specialists + Guardian |
| Security? | Guardian between stages; no auto-remediation |
| Deployable? | `docker compose up` + `reset_demo.py` |
| Works offline? | Yes — rule-engine fallbacks |

## Fastest path to value (10 min)

```bash
git clone https://github.com/Jugnu0707/Kaggle.git && cd Kaggle
cp .env.example .env && docker compose up --build
cd backend && uv run python ../scripts/reset_demo.py
```

Open http://localhost:5173 → **Suspicious PowerShell Execution** → all tabs → `/evaluation` → `/settings`

## Key URLs

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | Dashboard |
| http://localhost:8000/docs | OpenAPI / Swagger |
| http://localhost:8000/api/v1/ai/test | Gemini connectivity |
| http://localhost:8000/api/v1/system/mcp | MCP tool list |

## Statistics (verified)

39 API operations · 8 agents · 5 MCP tools · 16 tables · 10 pages · 176 tests · ~29K LOC

## What to look for

1. **Not a chatbot** — structured pipeline with persisted outputs per agent
2. **Guardian gates** — not trusting LLM self-policing
3. **Replay explainability** — `ai_used` / `fallback_used` per step
4. **Executive report** — leadership language, no raw logs
5. **Evaluation dashboard** — agent health metrics

## Known gaps (honest)

- No API auth yet
- No human approval UI yet
- No SIEM connectors
- Submission notebook + video pending
- SQLite (demo), not production Postgres

## FAQ

See [`../demo/faq.md`](../demo/faq.md) for ADK, MCP, fallback, Guardian, SQLite, SIEM, scaling.

## Documentation map

| Doc | Purpose |
|-----|---------|
| `README.md` | Project overview |
| `docs/submission/FINAL_WRITEUP.md` | Competition narrative |
| `docs/kaggle/` | Detailed writeup sections |
| `docs/diagrams/` | Mermaid architecture |
| `docs/kaggle/final_checklist.md` | Requirement checklist |

## Contact

MIT License · GitHub Issues for questions · Security: `SECURITY.md`
