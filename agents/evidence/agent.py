"""Evidence Agent — ADK configuration and collection entry point."""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import Agent
from sqlalchemy.orm import Session

from agents.evidence.models import EvidenceInput, EvidenceResult
from agents.evidence.service import EvidenceCollectionService
from app.core.logging import get_logger

logger = get_logger(__name__)

EVIDENCE_AGENT_NAME = "evidence"
EVIDENCE_AGENT_DESCRIPTION = (
    "Collects, validates, normalizes, and summarizes uploaded log evidence "
    "without performing threat analysis."
)
PROMPT_PATH = Path(__file__).with_name("prompt.md")


def load_evidence_prompt() -> str:
    """Load the versioned Evidence Agent system prompt from disk."""
    return PROMPT_PATH.read_text(encoding="utf-8")


class EvidenceAgent:
    """Google ADK Evidence Agent — deterministic collection, no LLM execution."""

    def __init__(self) -> None:
        self._loaded = False
        self._adk_agent = Agent(
            name=EVIDENCE_AGENT_NAME,
            description=EVIDENCE_AGENT_DESCRIPTION,
            instruction=load_evidence_prompt(),
            input_schema=EvidenceInput,
            output_schema=EvidenceResult,
        )

    @property
    def name(self) -> str:
        """Return the ADK agent name."""
        return self._adk_agent.name

    @property
    def description(self) -> str:
        """Return the ADK agent description."""
        return self._adk_agent.description

    @property
    def adk_agent(self) -> Agent:
        """Return the underlying Google ADK agent configuration."""
        return self._adk_agent

    def initialize(self) -> None:
        """Initialize the Evidence Agent without invoking the LLM."""
        self._loaded = True
        logger.info(
            "Evidence Agent configured: name=%s description=%s",
            self.name,
            self.description,
        )

    @property
    def is_loaded(self) -> bool:
        """Return whether the Evidence Agent finished initialization."""
        return self._loaded

    def collect(self, request: EvidenceInput, db: Session) -> EvidenceResult:
        """Collect and normalize evidence for an incident log file."""
        return EvidenceCollectionService(db).collect(request)
