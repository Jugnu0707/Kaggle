"""MCP runtime initialization and status tracking."""

from __future__ import annotations

from mcp.server import get_mcp_server

from app.core.logging import get_logger

logger = get_logger(__name__)

_mcp_running = False


def initialize_mcp_runtime() -> None:
    """Start the MCP server and verify tool registration."""
    global _mcp_running

    server = get_mcp_server()
    server.start()

    if not server.is_running():
        raise RuntimeError("MCP server failed to start")

    if server.registry.tool_count() == 0:
        raise RuntimeError("MCP server started but no tools were registered")

    _mcp_running = True
    logger.info(
        "MCP runtime initialized: running=%s, tools=%s",
        _mcp_running,
        server.registry.list_tools(),
    )


def get_mcp_status() -> dict[str, bool | int | list[str]]:
    """Return current MCP server status for API responses."""
    server = get_mcp_server()
    return {
        "mcp": server.is_running() and _mcp_running,
        "tool_count": server.registry.tool_count(),
        "tools": server.registry.list_tools(),
    }


def is_mcp_running() -> bool:
    """Return whether MCP runtime initialization completed successfully."""
    return _mcp_running and get_mcp_server().is_running()
