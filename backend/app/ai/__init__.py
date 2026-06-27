"""AI runtime — ADK sessions, MCP tool access, and Gemini provider."""

from app.ai.metrics import get_runtime_metrics, RuntimeMetrics, RuntimeMetricsSnapshot
from app.ai.provider import GeminiProvider
from app.ai.registry import AgentRegistry, REGISTERED_AGENT_NAMES
from app.ai.runtime import AIRuntime, get_ai_runtime, initialize_ai_runtime
from app.ai.session import ADKSession, SessionManager

__all__ = [
    "ADKSession",
    "AgentRegistry",
    "AIRuntime",
    "GeminiProvider",
    "REGISTERED_AGENT_NAMES",
    "RuntimeMetrics",
    "RuntimeMetricsSnapshot",
    "SessionManager",
    "get_ai_runtime",
    "get_runtime_metrics",
    "initialize_ai_runtime",
]
