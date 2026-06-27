"""Shared pytest helpers for agent package unit tests."""

from __future__ import annotations

from unittest.mock import MagicMock

from mcp.registry import ToolResult


def build_mock_ai_runtime(api_key: str = "test-key") -> MagicMock:
    """Build a mock AI runtime with successful MCP tool responses."""
    mock_runtime = MagicMock()
    mock_provider = MagicMock()
    mock_provider.get_api_key.return_value = api_key
    mock_provider.get_model.return_value = "gemini-2.5-pro"
    mock_provider.has_api_key.return_value = bool(api_key)
    mock_provider.generate_json.return_value = None
    mock_provider.generate_text.return_value = None
    mock_runtime.provider = mock_provider
    mock_runtime.invoke_tool.return_value = ToolResult(success=True, data={"ok": True})
    mock_runtime.discover_tools.return_value = []
    mock_runtime.create_agent_session.return_value = MagicMock(
        session_id="test-session"
    )
    mock_runtime.close_agent_session.return_value = 1.0
    return mock_runtime
