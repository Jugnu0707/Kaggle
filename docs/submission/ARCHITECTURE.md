# Architecture Summary (Submission)

Oz AI layered architecture for Kaggle judges.

## System diagram

![Architecture](../../architecture/architecture.png)

## Mermaid diagrams (GitHub-renderable)

| Diagram | File |
|---------|------|
| System layers | [`../diagrams/system_architecture.md`](../diagrams/system_architecture.md) |
| Investigation flow | [`../diagrams/investigation_flow.md`](../diagrams/investigation_flow.md) |
| Agent sequence | [`../diagrams/agent_sequence.md`](../diagrams/agent_sequence.md) |
| Database ER | [`../diagrams/database_er.md`](../diagrams/database_er.md) |
| MCP flow | [`../diagrams/mcp_flow.md`](../diagrams/mcp_flow.md) |

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, Tailwind, Vite |
| Backend | FastAPI, SQLAlchemy, Pydantic v2, Python 3.12 |
| Agents | Google ADK + `agents/` packages |
| AI | Google Gemini (`google.genai`) |
| MCP | Custom registry — 5 tools |
| Database | SQLite — 16 tables |

## Authoritative reference

[`docs/02_ARCHITECTURE.md`](../../02_ARCHITECTURE.md)
