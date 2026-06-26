"""ADK runtime initialization and status tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from agents.coordinator.agent import CoordinatorAgent

logger = get_logger(__name__)

_adk_installed = False
_coordinator_loaded = False
_coordinator: CoordinatorAgent | None = None


def verify_adk_installed() -> bool:
    """Return True when the Google ADK package imports successfully."""
    try:
        import google.adk  # noqa: F401
    except ImportError:
        return False
    return True


def initialize_adk_runtime() -> None:
    """Verify ADK imports and initialize the Coordinator Agent."""
    global _adk_installed, _coordinator_loaded, _coordinator

    if not verify_adk_installed():
        raise RuntimeError(
            "Google ADK is not installed. "
            'Install backend dependencies with: pip install -e ".[dev]"'
        )

    _adk_installed = True
    logger.info("Google ADK import verified successfully")

    from agents.coordinator.agent import CoordinatorAgent

    coordinator = CoordinatorAgent()
    coordinator.initialize()
    _coordinator = coordinator
    _coordinator_loaded = coordinator.is_loaded
    logger.info("Coordinator Agent initialized: loaded=%s", _coordinator_loaded)


def get_adk_status() -> dict[str, bool]:
    """Return current ADK and Coordinator initialization status."""
    return {"adk": _adk_installed, "coordinator": _coordinator_loaded}


def get_coordinator() -> CoordinatorAgent:
    """Return the initialized Coordinator Agent instance."""
    if _coordinator is None or not _coordinator_loaded:
        raise RuntimeError("Coordinator Agent is not initialized")
    return _coordinator
