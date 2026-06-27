# Oz AI Architecture Documentation

This directory contains architecture diagrams and sequence documentation for Oz AI. The authoritative system reference remains [`docs/02_ARCHITECTURE.md`](../../02_ARCHITECTURE.md).

## Contents

| Document | Description |
|----------|-------------|
| [architecture.png](architecture.png) | High-resolution system architecture diagram |
| [system-architecture.md](system-architecture.md) | Layered architecture overview |
| [agent-workflow.md](agent-workflow.md) | Multi-agent investigation pipeline |
| [mcp-interaction.md](mcp-interaction.md) | MCP tool registry and interactions |
| [database-er.md](database-er.md) | Database entity-relationship diagram |
| [investigation-sequence.md](investigation-sequence.md) | End-to-end investigation sequence |

## Regenerating assets

```bash
python scripts/generate_assets.py   # architecture.png + UI screenshots
python scripts/generate_repo_stats.py  # repository statistics
```
