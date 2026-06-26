"""MCP server startup and tool registration tests."""

from mcp.server import get_mcp_server

EXPECTED_TOOLS = [
    "health",
    "incident_details",
    "list_incidents",
    "list_logs",
    "system_info",
]


def test_mcp_server_starts_with_registered_tools() -> None:
    """MCP server is running after application startup with five tools."""
    server = get_mcp_server()

    assert server.is_running() is True
    assert server.registry.tool_count() == 5
    assert server.registry.list_tools() == EXPECTED_TOOLS


def test_mcp_start_is_idempotent() -> None:
    """Calling start again does not duplicate tool registrations."""
    server = get_mcp_server()
    initial_count = server.registry.tool_count()

    server.start()

    assert server.registry.tool_count() == initial_count
    assert server.registry.list_tools() == EXPECTED_TOOLS
