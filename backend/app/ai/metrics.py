"""Thread-safe runtime metrics for MCP and ADK session tracking."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class RuntimeMetricsSnapshot:
    """Point-in-time runtime metrics."""

    tool_execution_count: int = 0
    tool_failure_count: int = 0
    total_mcp_latency_ms: float = 0.0
    adk_session_count: int = 0
    total_adk_session_duration_ms: float = 0.0


class RuntimeMetrics:
    """Accumulates MCP tool and ADK session metrics for evaluation."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tool_execution_count = 0
        self._tool_failure_count = 0
        self._total_mcp_latency_ms = 0.0
        self._adk_session_count = 0
        self._total_adk_session_duration_ms = 0.0

    def record_tool_execution(self, latency_ms: float, success: bool) -> None:
        """Record one MCP tool invocation."""
        with self._lock:
            self._tool_execution_count += 1
            self._total_mcp_latency_ms += latency_ms
            if not success:
                self._tool_failure_count += 1

    def record_session_duration(self, duration_ms: float) -> None:
        """Record one completed ADK agent session."""
        with self._lock:
            self._adk_session_count += 1
            self._total_adk_session_duration_ms += duration_ms

    def snapshot(self) -> RuntimeMetricsSnapshot:
        """Return a copy of current metrics."""
        with self._lock:
            return RuntimeMetricsSnapshot(
                tool_execution_count=self._tool_execution_count,
                tool_failure_count=self._tool_failure_count,
                total_mcp_latency_ms=self._total_mcp_latency_ms,
                adk_session_count=self._adk_session_count,
                total_adk_session_duration_ms=self._total_adk_session_duration_ms,
            )

    def reset(self) -> None:
        """Clear all metrics (used in tests)."""
        with self._lock:
            self._tool_execution_count = 0
            self._tool_failure_count = 0
            self._total_mcp_latency_ms = 0.0
            self._adk_session_count = 0
            self._total_adk_session_duration_ms = 0.0


_metrics = RuntimeMetrics()


def get_runtime_metrics() -> RuntimeMetrics:
    """Return the process-wide runtime metrics collector."""
    return _metrics
