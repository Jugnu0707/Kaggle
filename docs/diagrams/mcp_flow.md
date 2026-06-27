# MCP Flow

Model Context Protocol tool registry and interaction model.

```mermaid
flowchart LR
    subgraph Startup["Application Startup"]
        INIT["mcp/server.py start()"]
        LOAD["import mcp.tools"]
        REG["ToolRegistry.register()"]
    end

    subgraph Tools["Registered MCP Tools"]
        T1["health"]
        T2["list_incidents"]
        T3["incident_details"]
        T4["list_logs"]
        T5["system_info"]
    end

    subgraph Consumers["Consumers"]
        API["GET /api/v1/system/mcp"]
        RT["MCP Runtime"]
        UI["Settings Page"]
    end

    subgraph Data["Data Sources"]
        DB["SQLite via SQLAlchemy"]
        APP["Application State"]
    end

    INIT --> LOAD --> REG
    REG --> T1 & T2 & T3 & T4 & T5
    API --> REG
    RT --> REG
    UI --> API
    T1 --> APP
    T2 & T3 & T4 --> DB
    T5 --> APP
```

## Tool catalog

| Tool | Description | Handler |
|------|-------------|---------|
| `health` | Application health status | `mcp/tools/health.py` |
| `list_incidents` | Paginated incident list | `mcp/tools/incidents.py` |
| `incident_details` | Single incident by ID | `mcp/tools/incidents.py` |
| `list_logs` | Log file metadata | `mcp/tools/logs.py` |
| `system_info` | Version, ADK, MCP status | `mcp/tools/system.py` |

## Runtime vs agent calls

```mermaid
sequenceDiagram
    participant Agent as Specialist Agent
    participant Service as Backend Service
    participant MCP as MCP Tool
    participant DB as Database

    Note over Agent,DB: Current: direct service invocation
    Agent->>Service: analyze(context)
    Service->>DB: read / write
    Service-->>Agent: structured result

    Note over Agent,DB: MCP: operational introspection
    Agent->>MCP: list_incidents(page=1)
    MCP->>DB: query
    MCP-->>Agent: ToolResult
```

## Implementation

| Component | Path |
|-----------|------|
| Registry | `mcp/registry.py` |
| Server | `mcp/server.py` |
| Runtime | `backend/app/core/mcp_runtime.py` |
| API | `backend/app/api/v1/system.py` |

Five tools registered at startup. Domain tools (`evidence_collector`, `threat_intel_lookup`) are planned for future sprints.
