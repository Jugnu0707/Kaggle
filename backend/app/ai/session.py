"""ADK session lifecycle tracking for agent runtime execution."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.ai.metrics import get_runtime_metrics
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ADKSession:
    """Represents one agent execution session in the ADK runtime."""

    session_id: str
    agent_name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _started_at: float = field(default_factory=time.perf_counter)

    def elapsed_ms(self) -> float:
        """Return elapsed session time in milliseconds."""
        return (time.perf_counter() - self._started_at) * 1000


class SessionManager:
    """Creates and closes ADK sessions with duration logging."""

    def __init__(self) -> None:
        self._sessions: dict[str, ADKSession] = {}

    def create_session(self, agent_name: str) -> ADKSession:
        """Create a new ADK session for an agent execution."""
        session = ADKSession(session_id=str(uuid.uuid4()), agent_name=agent_name)
        self._sessions[session.session_id] = session
        logger.info(
            "ADK session created: session_id=%s agent=%s",
            session.session_id,
            agent_name,
        )
        return session

    def close_session(self, session_id: str) -> float:
        """Close a session, record duration metrics, and return elapsed ms."""
        session = self._sessions.pop(session_id, None)
        if session is None:
            return 0.0
        duration_ms = session.elapsed_ms()
        get_runtime_metrics().record_session_duration(duration_ms)
        logger.info(
            "ADK session closed: session_id=%s agent=%s duration_ms=%.2f",
            session_id,
            session.agent_name,
            duration_ms,
        )
        return duration_ms

    def active_session_count(self) -> int:
        """Return the number of open sessions."""
        return len(self._sessions)
