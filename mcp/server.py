"""MCP server lifecycle management."""

from __future__ import annotations

from app.core.logging import get_logger
from mcp.registry import ToolRegistry, get_registry

logger = get_logger(__name__)


class MCPServer:
    """In-process MCP server that registers and exposes tools to future agents."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry
        self._running = False

    def start(self) -> None:
        """Load tool modules, register tools, and mark the server as running."""
        if self._running:
            logger.info(
                "MCP server already running with %d tools",
                self.registry.tool_count(),
            )
            return

        import mcp.tools  # noqa: F401

        for name in self.registry.list_tools():
            tool = self.registry.get_tool(name)
            if tool is not None:
                logger.info("Registered MCP tool: %s — %s", name, tool.description)

        self._running = True
        logger.info(
            "MCP server started with %d registered tools",
            self.registry.tool_count(),
        )

    def is_running(self) -> bool:
        """Return whether the MCP server has started successfully."""
        return self._running


_server: MCPServer | None = None


def get_mcp_server() -> MCPServer:
    """Return the singleton MCP server instance."""
    global _server
    if _server is None:
        _server = MCPServer(get_registry())
    return _server
