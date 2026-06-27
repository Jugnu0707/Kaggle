# MCP Interaction Model

Oz AI implements an in-process MCP (Model Context Protocol) tool registry. Five operational tools are registered at startup and exposed via the MCP runtime and system API.

## Tool registry

```mermaid
flowchart TB
    subgraph MCPServer["MCP Server (in-process)"]
        REG["ToolRegistry"]
        T1["health"]
        T2["list_incidents"]
        T3["incident_details"]
        T4["list_logs"]
        T5["system_info"]
    end

    subgraph Consumers["Consumers"]
        API["GET /api/v1/system/mcp"]
        RT["MCP Runtime"]
        FUTURE["Future ADK agent tool calls"]
    end

    subgraph Data["Data Access"]
        DB["SQLite via SQLAlchemy Session"]
        APP["Application state"]
    end

    REG --> T1 & T2 & T3 & T4 & T5
    API --> REG
    RT --> REG
    FUTURE -.-> REG
    T1 --> APP
    T2 & T3 & T4 --> DB
    T5 --> APP
```

## Registered tools

| Tool | Description | Input |
|------|-------------|-------|
| `health` | Application health status | None |
| `list_incidents` | Paginated incident list | `page`, `page_size` |
| `incident_details` | Single incident by ID | `incident_id` |
| `list_logs` | Uploaded log file metadata | `incident_id` (optional) |
| `system_info` | Version, database, ADK, MCP status | None |

## Runtime vs direct service calls

Today, investigation agents invoke backend **services directly** for domain logic. MCP tools provide operational introspection and a foundation for future ADK-native tool wiring.

```mermaid
sequenceDiagram
    participant Agent as Specialist Agent
    participant Service as Backend Service
    participant MCP as MCP Tool
    participant DB as Database

    Note over Agent,DB: Current path (domain agents)
    Agent->>Service: analyze(context)
    Service->>DB: read / write
    Service-->>Agent: structured result

    Note over Agent,DB: MCP path (operational tools)
    Agent->>MCP: list_incidents(page=1)
    MCP->>DB: query incidents
    MCP-->>Agent: ToolResult
```

## Implementation locations

| Component | Path |
|-----------|------|
| Registry | `mcp/registry.py` |
| Server lifecycle | `mcp/server.py` |
| Tool modules | `mcp/tools/` |
| Runtime integration | `backend/app/core/mcp_runtime.py` |
| API exposure | `backend/app/api/v1/system.py` |

## Planned expansion (Sprint 4+)

Domain MCP tools (`evidence_collector`, `threat_intel_lookup`, etc.) are documented in `docs/02_ARCHITECTURE.md` and `docs/03_TASKS.md` but not yet implemented.
