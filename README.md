# Oz AI

**Enterprise Incident Response Platform** · **v0.1.0** · **Sprint 3.5 Complete**

Kaggle — AI Agents Intensive Capstone (Agents for Business track)

Oz AI is an enterprise platform for structured incident response. It combines a FastAPI backend, React dashboard, eight specialist AI agents, Guardian safety validation, an evaluation framework, and an end-to-end investigation workflow orchestrated by the Coordinator Agent.

---

## Project status

| Sprint | Focus | Status |
|--------|-------|--------|
| Sprint 1 — Foundation | Backend API, frontend dashboard, Docker, incident/log CRUD | **Complete** |
| Sprint 2 — ADK & MCP | Google ADK setup, MCP registry (5 tools), Coordinator, Evidence Agent | **Complete** |
| Sprint 3 — Agents & workflow | Specialist agents, Guardian, Timeline Engine, Evaluation, Investigation Runner | **Complete** |
| Sprint 3.5 — Competition prep | Doc sync, ADK/MCP runtime, hardening, demo & submission assets | **Complete** |
| Sprint 4 — Release hardening | Auth, datasets, approval workflow, submission notebook | **Planned** |

### Implementation snapshot

| Area | Count / detail |
|------|----------------|
| API endpoints | **35** |
| Database tables | **15** |
| AI agents | **8** (Coordinator, Evidence, Threat Intelligence, MITRE, Risk, Response, Executive Report, Guardian) |
| MCP tools registered | **5** (`health`, `list_incidents`, `incident_details`, `list_logs`, `system_info`) |
| Frontend routes | **9** (including 404) |
| Tests | **153** collected · **100% passing** · **~93%** coverage |
| Demo incidents | **10** · **25** uploaded logs |

---

## Project overview

Oz AI helps security teams investigate incidents faster by running a coordinated multi-agent pipeline: collect evidence from uploaded logs, enrich with threat intelligence and MITRE ATT&CK mapping, assess risk, draft a response plan, generate executive reports, and validate outputs through the Guardian Agent.

Investigations are triggered explicitly via `POST /api/v1/investigations/run` or individual agent endpoints. Creating an incident does **not** automatically start the agent pipeline.

The platform is a **decision-support system**. Human approval gates for response actions are documented in the architecture but **not yet implemented** in the API or UI.

---

## Architecture

![Oz AI Architecture](docs/architecture.png)

Layered architecture documented in [`docs/02_ARCHITECTURE.md`](docs/02_ARCHITECTURE.md):

```text
Presentation (React Dashboard)
        │
        ▼
Backend (FastAPI · Services · Repositories)
        │
        ├── Agents (8 specialist agents + Timeline Engine + Evaluation Engine)
        ├── Google ADK Runtime (sessions, agent registry)
        └── MCP Runtime (5 operational tools)
        │
        ▼
Persistence (SQLite · SQLAlchemy ORM)
```

**Investigation workflow** (via `InvestigationWorkflowService`):

```text
Coordinator → Evidence → Guardian → Threat Intel → Guardian → MITRE → Guardian
  → Risk → Guardian → Response → Guardian → Executive Report → Guardian
  → Timeline Engine → Evaluation Engine
```

---

## Features

- Multi-agent incident investigation with Coordinator orchestration
- Log upload and evidence normalization
- Threat intelligence IOC extraction and reputation enrichment
- MITRE ATT&CK technique mapping
- Risk assessment and response planning
- Executive report generation
- Guardian validation between every specialist stage
- Investigation timeline reconstruction
- Agent evaluation dashboard with performance metrics
- One-click demo reset with seeded incidents and logs

---

## Folder structure

```text
Kaggle/
├── agents/                 # Agent implementations (8 agents)
├── backend/
│   ├── app/                # FastAPI application (API, services, models)
│   └── scripts/            # seed_demo_data.py, demo catalog
├── evaluation/             # Evaluation framework
├── frontend/src/           # React dashboard
├── mcp/                    # MCP registry and tools
├── scripts/                # reset_demo.py, dev.sh, generate_assets.py
├── docs/                   # Documentation and screenshots
├── storage/uploads/        # Local log file storage
├── tests/                  # Integration and agent API tests
├── docker-compose.yml
└── README.md
```

---

## Technology stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy, Pydantic v2 |
| Agents | Google ADK runtime, `google-genai` for LLM calls |
| MCP | Custom registry in `mcp/` (5 tools) |
| Database | SQLite (MVP) |
| Frontend | React 19, TypeScript, Tailwind CSS, Vite |
| Infrastructure | Docker, Docker Compose |
| Quality | pytest, pytest-cov, Ruff, Black, isort |

---

## Installation

### Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- Docker and Docker Compose (optional)

### Local setup

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
cp .env.example .env
```

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

**Dev scripts** (from repo root):

```bash
./scripts/dev.sh
./scripts/dev-backend.sh
./scripts/dev-frontend.sh
```

---

## Docker

From the repository root:

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Backend | http://localhost:8000 |
| Frontend | http://localhost:5173 |
| API docs | http://localhost:8000/docs |

```bash
curl http://localhost:8000/api/v1/health
docker compose ps
```

---

## Demo workflow

**One-click reset** (recommended for judges and demos):

```bash
python scripts/reset_demo.py
./scripts/dev.sh
```

This wipes the local database and uploads, seeds **10 incidents** with **25 logs** covering PowerShell execution, brute force, ransomware, credential dumping, suspicious outbound connections, DNS tunneling, malware download, lateral movement, privilege escalation, and data exfiltration. It runs full investigation workflows on showcase incidents and fills agent outputs so every incident detail tab has data.

**Manual demo path** (10 minutes):

1. Open **Dashboard** — review incident counts and recent activity
2. Open **Incidents** → select **Suspicious PowerShell Execution**
3. Review tabs: **Overview**, **Timeline**, **Threat Intel**, **MITRE**, **Risk**, **Response**, **Executive Report**, **Guardian**
4. Open **Evaluation** — review agent health scores and performance metrics
5. Open **Investigation Runner** on any incident → **Run New Investigation**
6. Open **Settings** — verify health, ADK runtime, and MCP tool status

Without `GOOGLE_API_KEY`, agents use deterministic fallback paths (offline demos work; live Gemini enriches AI-success paths).

---

## Environment variables

Copy `.env.example` to `.env`. Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./oz_ai.db` |
| `UPLOAD_DIR` | Log storage directory | `storage/uploads` |
| `VITE_API_URL` | Frontend API base URL | `http://localhost:8000` |
| `GOOGLE_API_KEY` | Gemini API key (optional) | *(empty)* |
| `GOOGLE_MODEL` | Gemini model | `gemini-2.5-pro` |
| `GUARDIAN_ENABLED` | Enable Guardian validation | `true` |
| `MIN_AI_CONFIDENCE` | Minimum AI confidence threshold | `70` |

Never commit `.env` files or secrets.

---

## Screenshots

| View | Image |
|------|-------|
| Dashboard | ![Dashboard](docs/screenshots/dashboard.png) |
| Incident Details | ![Incident Details](docs/screenshots/incident-details.png) |
| Threat Intelligence | ![Threat Intelligence](docs/screenshots/threat-intelligence.png) |
| MITRE Mapping | ![MITRE](docs/screenshots/mitre.png) |
| Risk Assessment | ![Risk](docs/screenshots/risk-assessment.png) |
| Response Plan | ![Response Plan](docs/screenshots/response-plan.png) |
| Executive Report | ![Executive Report](docs/screenshots/executive-report.png) |
| Guardian Audit | ![Guardian](docs/screenshots/guardian.png) |
| Timeline | ![Timeline](docs/screenshots/timeline.png) |
| Evaluation Dashboard | ![Evaluation](docs/screenshots/evaluation-dashboard.png) |
| Investigation Runner | ![Investigation Runner](docs/screenshots/investigation-runner.png) |

Architecture diagram: [`docs/architecture.png`](docs/architecture.png)

Regenerate assets: `python scripts/generate_assets.py`

---

## Testing

From `backend/`:

```bash
pip install -e ".[dev]"
python -m pytest ../tests ../evaluation/tests -v
python -m pytest --cov=app --cov=agents --cov=mcp --cov=evaluation --cov-report=term
```

Current suite: **153 tests**, **100% passing**, **~93%** line coverage.

Frontend build:

```bash
cd frontend && npm run build
```

---

## Future roadmap

### Sprint 4 — Release hardening (planned)

- API authentication and rate limiting
- Human approval workflow (response plan approve/reject)
- Synthetic datasets and alert simulator
- Docker production profile (Nginx, non-root)
- 30-scenario evaluation library and Kaggle submission notebook
- Demo video

See [`docs/03_TASKS.md`](docs/03_TASKS.md) and [`docs/08_MILESTONES.md`](docs/08_MILESTONES.md).

---

## Competition alignment

**Competition:** Kaggle — AI Agents Intensive Capstone · **Track:** Agents for Business

| Dimension | Status |
|-----------|--------|
| Multi-agent coordination | Eight agents + Coordinator orchestration |
| Google ADK | Runtime, sessions, agent registry |
| MCP tool layer | Five operational tools via AI runtime |
| Business impact | Enterprise incident response workflow |
| Security / Guardian | Validation between every specialist stage |
| Evaluation | Offline benchmarks + API dashboard |
| Deployability | `docker compose up` + `python scripts/reset_demo.py` |
| Human-in-the-loop | Documented; **not yet enforced in UI/API** |

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/01_PROJECT_BRIEF.md`](docs/01_PROJECT_BRIEF.md) | Vision, goals, technology stack |
| [`docs/02_ARCHITECTURE.md`](docs/02_ARCHITECTURE.md) | System architecture |
| [`docs/03_TASKS.md`](docs/03_TASKS.md) | Engineering backlog |
| [`docs/05_PROGRESS.md`](docs/05_PROGRESS.md) | Project journal |
| [`docs/07_SUBMISSION_CHECKLIST.md`](docs/07_SUBMISSION_CHECKLIST.md) | Pre-submission checklist |
| [`docs/08_MILESTONES.md`](docs/08_MILESTONES.md) | Sprint progress |

---

## License

MIT License. See [`LICENSE`](LICENSE).
