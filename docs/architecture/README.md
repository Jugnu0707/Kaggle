# Architecture Documentation Index

Professional architecture documentation for Oz AI v0.1.0.

**Authoritative reference:** [`docs/02_ARCHITECTURE.md`](../02_ARCHITECTURE.md)

---

## Documents

| # | Document | Description |
|---|----------|-------------|
| 01 | [System Overview](01_system_overview.md) | Purpose, scope, components, workflow |
| 02 | [Component Diagram](02_component_diagram.md) | Mermaid component architecture |
| 03 | [Sequence Diagram](03_sequence_diagram.md) | Upload → investigate → report flow |
| 04 | [Agent Workflow](04_agent_workflow.md) | All agents: purpose, I/O, APIs |
| 05 | [Database Design](05_database_design.md) | ER diagram and relationships |
| 06 | [MCP Architecture](06_mcp_architecture.md) | Tool registry, discovery, invocation |
| 07 | [ADK Runtime](07_adk_runtime.md) | ADK init, sessions, Gemini, fallbacks |
| 08 | [Security Architecture](08_security_architecture.md) | Guardian, masking, audit trail |
| 09 | [Deployment](09_deployment.md) | Docker topology, ports, volumes |
| 10 | [Decision Records](10_decision_records.md) | Architectural decision summaries |

---

## Reading Paths

### For judges and evaluators

1. [System Overview](01_system_overview.md)
2. [Sequence Diagram](03_sequence_diagram.md)
3. [Agent Workflow](04_agent_workflow.md)
4. [Deployment](09_deployment.md)

### For developers

1. [Component Diagram](02_component_diagram.md)
2. [Database Design](05_database_design.md)
3. [MCP Architecture](06_mcp_architecture.md)
4. [ADK Runtime](07_adk_runtime.md)
5. [Decision Records](10_decision_records.md)

### For security reviewers

1. [Security Architecture](08_security_architecture.md)
2. [Agent Workflow](04_agent_workflow.md) — Guardian section
3. [Decision Records](10_decision_records.md) — Rule-based Guardian

---

## Diagram Index

All diagrams use Mermaid and render on GitHub without external image dependencies.

| Diagram | Location | Type |
|---------|----------|------|
| Component architecture | [02_component_diagram.md](02_component_diagram.md) | `flowchart TD` |
| Investigation sequence | [03_sequence_diagram.md](03_sequence_diagram.md) | `sequenceDiagram` |
| Entity relationships | [05_database_design.md](05_database_design.md) | `erDiagram` |
| MCP lifecycle | [06_mcp_architecture.md](06_mcp_architecture.md) | `flowchart LR` |
| ADK startup | [07_adk_runtime.md](07_adk_runtime.md) | `flowchart TD` |
| Fallback strategy | [07_adk_runtime.md](07_adk_runtime.md) | `flowchart TD` |
| Guardian pipeline | [08_security_architecture.md](08_security_architecture.md) | `flowchart TD` |
| Deployment topology | [09_deployment.md](09_deployment.md) | `flowchart TD` |
| ADK session lifecycle | [07_adk_runtime.md](07_adk_runtime.md) | `stateDiagram-v2` |

---

## Legacy Documents

Earlier architecture files remain for reference. Prefer the numbered documents above.

| Legacy File | Superseded By |
|-------------|---------------|
| [system-architecture.md](system-architecture.md) | [01_system_overview.md](01_system_overview.md), [02_component_diagram.md](02_component_diagram.md) |
| [agent-workflow.md](agent-workflow.md) | [04_agent_workflow.md](04_agent_workflow.md) |
| [investigation-sequence.md](investigation-sequence.md) | [03_sequence_diagram.md](03_sequence_diagram.md) |
| [database-er.md](database-er.md) | [05_database_design.md](05_database_design.md) |
| [mcp-interaction.md](mcp-interaction.md) | [06_mcp_architecture.md](06_mcp_architecture.md) |
| [architecture.png](architecture.png) | Mermaid diagrams in numbered docs |

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [`docs/02_ARCHITECTURE.md`](../02_ARCHITECTURE.md) | Authoritative architecture reference |
| [`docs/04_DECISIONS.md`](../04_DECISIONS.md) | Full ADR text |
| [`docs/kaggle/ai_agents.md`](../kaggle/ai_agents.md) | Agent detail for competition |
| [`docs/kaggle/limitations.md`](../kaggle/limitations.md) | Known limitations |
| [`docs/kaggle/architecture.md`](../kaggle/architecture.md) | Competition architecture summary |
| [`docs/diagrams/`](../diagrams/) | Additional Mermaid diagrams |

---

## Regenerating Assets

```bash
python scripts/generate_assets.py      # architecture.png + UI screenshots
python scripts/generate_repo_stats.py  # repository statistics
```
