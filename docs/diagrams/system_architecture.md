# System Architecture

Oz AI layered architecture for the Kaggle AI Agents Capstone submission.

```mermaid
flowchart TB
    subgraph Presentation["Presentation Layer"]
        UI["React 19 Dashboard<br/>10 pages · Vite · Tailwind"]
    end

    subgraph API["API Layer"]
        FASTAPI["FastAPI REST API<br/>35 paths · 39 operations"]
    end

    subgraph Application["Application Layer"]
        SVC["Services & Repositories"]
        WF["Investigation Workflow Service"]
    end

    subgraph Intelligence["Intelligence Layer"]
        ADK["Google ADK Runtime"]
        CO["Coordinator Agent"]
        AGENTS["7 Specialist Agents"]
        GR["Guardian Agent"]
        TL["Timeline Engine"]
        EV["Evaluation Engine"]
    end

    subgraph External["External & Tool Layer"]
        GEMINI["Google Gemini API"]
        MCP["MCP Registry · 5 tools"]
    end

    subgraph Data["Persistence Layer"]
        DB["SQLite · 16 tables"]
        UP["Log Upload Storage"]
    end

    UI --> FASTAPI
    FASTAPI --> SVC
    SVC --> WF
    WF --> CO
    CO --> AGENTS
    AGENTS --> GR
    AGENTS --> ADK
    ADK --> GEMINI
    SVC --> MCP
    WF --> TL
    WF --> EV
    SVC --> DB
    FASTAPI --> UP
```

## Layer summary

| Layer | Technology | Location |
|-------|------------|----------|
| Frontend | React 19, TypeScript | `frontend/src/` |
| Backend | FastAPI, Python 3.12 | `backend/app/` |
| Agents | Google ADK | `agents/` |
| MCP | Custom registry | `mcp/` |
| AI | Gemini via `google.genai` | `backend/app/ai/` |
| Database | SQLite, SQLAlchemy | `backend/app/models/` |

## Design principles

1. Explicit investigation trigger — `POST /api/v1/investigations/run`
2. Guardian validation between every specialist stage
3. AI-first agents with deterministic fallbacks
4. Append-only audit and guardian records
