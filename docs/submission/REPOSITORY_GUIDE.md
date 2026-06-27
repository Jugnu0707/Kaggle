# Repository Guide (Submission)

How to clone, configure, develop, and test Oz AI.

## Clone

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
```

**Public repository:** https://github.com/Jugnu0707/Kaggle

## Configure

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | No | Default `sqlite:///./oz_ai.db` |
| `UPLOAD_DIR` | No | Default `storage/uploads` |
| `GOOGLE_API_KEY` | No | Empty = offline fallbacks |
| `GOOGLE_MODEL` | No | Default `gemini-2.5-pro` |
| `VITE_API_URL` | No | Default `http://localhost:8000` |
| `GUARDIAN_ENABLED` | No | Default `true` |

Never commit `.env`.

## Docker (recommended for judges)

```bash
docker compose up --build
python scripts/reset_demo.py   # use: cd backend && uv run python ../scripts/reset_demo.py
```

## Local development

```bash
# Backend
cd backend && uv sync
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

Or: `./scripts/dev.sh`

## Tests

```bash
cd backend && uv run pytest
cd frontend && npm run build
```

176 tests collected across `tests/`, `evaluation/tests/`, `agents/*/tests/`.

## Repository statistics

```bash
python scripts/generate_repo_stats.py
```

## Key directories

| Path | Contents |
|------|----------|
| `agents/` | 8 ADK agent implementations |
| `backend/app/` | FastAPI application |
| `frontend/src/` | React dashboard |
| `mcp/` | MCP registry and tools |
| `evaluation/` | Benchmark framework |
| `docs/` | Documentation hub |
| `docs/kaggle/` | Competition writeup |
| `docs/submission/` | This submission package |
| `docs/demo/` | Video prep materials |

## Community files

| File | Purpose |
|------|---------|
| `LICENSE` | MIT |
| `CONTRIBUTING.md` | Contribution guide |
| `CHANGELOG.md` | Release history |
| `ROADMAP.md` | Future milestones |
| `SECURITY.md` | Vulnerability reporting |
| `CODE_OF_CONDUCT.md` | Community standards |

## Regenerate assets

```bash
cd backend && uv run python ../scripts/generate_assets.py   # screenshots
python scripts/generate_repo_stats.py                        # statistics
```
