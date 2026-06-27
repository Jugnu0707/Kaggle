# System Architecture

Oz AI follows a layered architecture: React dashboard → FastAPI backend → specialist agents → SQLite persistence.

## High-resolution diagram

![Oz AI System Architecture](architecture.png)

## Layer overview

```mermaid
flowchart TB
    subgraph Presentation["Presentation Layer"]
        UI["React 19 Dashboard<br/>Tailwind CSS · Vite"]
    end

    subgraph Backend["Application Layer"]
        API["FastAPI REST API<br/>39 operations · 35 paths"]
        SVC["Services & Repositories"]
        WF["Investigation Workflow"]
    end

    subgraph Intelligence["Intelligence Layer"]
        ADK["Google ADK Runtime"]
        AGENTS["8 Specialist Agents"]
        TL["Timeline Engine"]
        EV["Evaluation Engine"]
        GR["Guardian Safety Layer"]
    end

    subgraph Tools["Tool Layer"]
        MCP["MCP Registry<br/>5 operational tools"]
        GEMINI["Google Gemini API"]
    end

    subgraph Data["Persistence Layer"]
        DB["SQLite · SQLAlchemy ORM<br/>16 tables"]
        UP["Log Upload Storage"]
    end

    UI --> API
    API --> SVC
    SVC --> WF
    WF --> AGENTS
    AGENTS --> GR
    AGENTS --> ADK
    ADK --> GEMINI
    SVC --> MCP
    SVC --> TL
    SVC --> EV
    SVC --> DB
    API --> UP
```

## Design principles

1. **Explicit orchestration** — Investigations start via `POST /api/v1/investigations/run`, not on incident creation.
2. **Guardian between stages** — Every agent output is validated before the next stage proceeds.
3. **AI-first with fallback** — Agents use Gemini when available; deterministic fallbacks keep demos offline-capable.
4. **Append-only audit** — Audit and guardian records are never modified after creation.
5. **Human-in-the-loop** — Response actions require approval (API enforcement planned Sprint 4).

## Related documents

- [`agent-workflow.md`](agent-workflow.md)
- [`02_ARCHITECTURE.md`](../02_ARCHITECTURE.md)
