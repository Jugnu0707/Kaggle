# Contributing to Oz AI

Thank you for your interest in contributing. Oz AI is an open-source enterprise incident response platform built for the Kaggle AI Agents Intensive Capstone (Agents for Business track).

## Quick links

- [Full contributing guide](.github/CONTRIBUTING.md) — branch strategy, commit conventions, PR process
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security policy](SECURITY.md)
- [Architecture](docs/02_ARCHITECTURE.md)
- [Task backlog](docs/03_TASKS.md)

## Getting started

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
cp .env.example .env
docker compose up --build
```

For local development without Docker:

```bash
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

## Development workflow

1. Pick or create a task in `docs/03_TASKS.md`
2. Branch from `main`: `feature/<task-id>-short-description`
3. Implement with tests
4. Run quality checks:

```bash
cd backend && uv run pytest
cd backend && uv run black --check app/ && uv run ruff check app/
cd frontend && npm run build
```

5. Update documentation in the same PR
6. Open a pull request using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

## Code standards

- Python 3.12+, strict type hints, Pydantic v2, Black + Ruff
- TypeScript strict mode, functional React components
- Tests adjacent to code (`tests/` subdirectories)
- No secrets in source code or logs

## Questions

Open a GitHub issue with the `question` label or refer to [`docs/01_PROJECT_BRIEF.md`](docs/01_PROJECT_BRIEF.md).
