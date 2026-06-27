"""Unified AI runtime — ADK agents, MCP tool discovery, and Gemini provider."""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.metrics import get_runtime_metrics
from app.ai.provider import GeminiProvider
from app.ai.registry import AgentRegistry, build_default_agent_registry
from app.ai.session import ADKSession, SessionManager
from app.core.adk_runtime import get_adk_status, verify_adk_installed
from app.core.logging import get_logger
from mcp.registry import ToolResult, get_registry

logger = get_logger(__name__)

_runtime: AIRuntime | None = None


class ToolDefinitionInfo(BaseModel):
    """Serializable MCP tool metadata for discovery."""

    name: str
    description: str
    version: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class AIRuntime:
    """Coordinates ADK agent registry, MCP tool access, and Gemini provider."""

    def __init__(self) -> None:
        self._ready = False
        self.provider = GeminiProvider()
        self.agent_registry = AgentRegistry()
        self.session_manager = SessionManager()
        self._discovered_tools: list[ToolDefinitionInfo] = []

    def initialize(self) -> None:
        """Initialize the AI runtime after ADK and MCP are available."""
        if not verify_adk_installed():
            raise RuntimeError("Google ADK is not installed")

        self.agent_registry = build_default_agent_registry()
        self._discovered_tools = self._discover_tools()
        self._ready = True

        logger.info(
            "AI runtime initialized: agents=%d tools=%d adk=%s",
            self.agent_registry.agent_count(),
            len(self._discovered_tools),
            get_adk_status()["adk"],
        )

    def is_ready(self) -> bool:
        """Return whether runtime initialization completed."""
        return self._ready

    def get_status(self) -> dict[str, bool | int]:
        """Return runtime health fields for the health endpoint."""
        adk_status = get_adk_status()
        return {
            "runtime": self._ready,
            "adk": adk_status["adk"],
            "coordinator": adk_status["coordinator"],
            "registered_agents": self.agent_registry.agent_count(),
            "registered_tools": len(self._discovered_tools),
        }

    def discover_tools(self) -> list[ToolDefinitionInfo]:
        """Return registered MCP tool metadata."""
        return list(self._discovered_tools)

    def create_agent_session(self, agent_name: str) -> ADKSession:
        """Open an ADK session for agent execution."""
        return self.session_manager.create_session(agent_name)

    def close_agent_session(self, session_id: str) -> float:
        """Close an ADK session and record duration."""
        return self.session_manager.close_session(session_id)

    def invoke_tool(
        self,
        name: str,
        payload: dict[str, Any],
        db: Session,
    ) -> ToolResult[Any]:
        """Invoke an MCP tool through the runtime with latency logging."""
        started = time.perf_counter()
        result = get_registry().invoke(name, payload, db)
        latency_ms = (time.perf_counter() - started) * 1000
        get_runtime_metrics().record_tool_execution(latency_ms, result.success)
        logger.info(
            "MCP tool executed: name=%s success=%s latency_ms=%.2f",
            name,
            result.success,
            latency_ms,
        )
        return result

    def get_metrics_snapshot(self) -> dict[str, float | int]:
        """Return runtime metrics for evaluation dashboards."""
        metrics = get_runtime_metrics().snapshot()
        mean_session_ms = (
            metrics.total_adk_session_duration_ms / metrics.adk_session_count
            if metrics.adk_session_count
            else 0.0
        )
        return {
            "tool_execution_count": metrics.tool_execution_count,
            "tool_failure_count": metrics.tool_failure_count,
            "total_mcp_latency_ms": round(metrics.total_mcp_latency_ms, 2),
            "adk_session_count": metrics.adk_session_count,
            "total_adk_session_duration_ms": round(metrics.total_adk_session_duration_ms, 2),
            "mean_adk_session_duration_ms": round(mean_session_ms, 2),
        }

    def _discover_tools(self) -> list[ToolDefinitionInfo]:
        """Discover and log all registered MCP tools."""
        registry = get_registry()
        discovered: list[ToolDefinitionInfo] = []
        for name in registry.list_tools():
            tool = registry.get_tool(name)
            if tool is None:
                continue
            info = ToolDefinitionInfo(
                name=tool.name,
                description=tool.description,
                version=tool.version,
                input_schema=tool.input_schema,
                output_schema=tool.output_schema,
            )
            discovered.append(info)
            logger.info(
                "MCP tool discovered: name=%s version=%s — %s",
                tool.name,
                tool.version,
                tool.description,
            )
        return discovered


def initialize_ai_runtime() -> None:
    """Initialize the process-wide AI runtime singleton."""
    global _runtime
    runtime = AIRuntime()
    runtime.initialize()
    _runtime = runtime


def get_ai_runtime() -> AIRuntime:
    """Return the initialized AI runtime."""
    if _runtime is None or not _runtime.is_ready():
        raise RuntimeError("AI runtime is not initialized")
    return _runtime
