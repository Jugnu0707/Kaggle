"""MITRE Mapping Agent — ADK configuration and mapping entry point."""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import Agent
from sqlalchemy.orm import Session

from agents.mitre.models import MitreMappingInput, MitreMappingResult
from agents.mitre.service import MitreMappingService
from app.core.logging import get_logger

logger = get_logger(__name__)

MITRE_AGENT_NAME = "mitre_mapping"
MITRE_AGENT_DESCRIPTION = (
    "Maps normalized evidence to MITRE ATT&CK techniques using local rule-based "
    "matching without external APIs or LLM reasoning."
)
PROMPT_PATH = Path(__file__).with_name("prompt.md")


def load_mitre_prompt() -> str:
    """Load the versioned MITRE Mapping Agent system prompt from disk."""
    return PROMPT_PATH.read_text(encoding="utf-8")


class MitreMappingAgent:
    """Google ADK MITRE Mapping Agent — deterministic mapping only."""

    def __init__(self) -> None:
        self._loaded = False
        self._adk_agent = Agent(
            name=MITRE_AGENT_NAME,
            description=MITRE_AGENT_DESCRIPTION,
            instruction=load_mitre_prompt(),
            input_schema=MitreMappingInput,
            output_schema=MitreMappingResult,
        )

    @property
    def name(self) -> str:
        return self._adk_agent.name

    @property
    def description(self) -> str:
        return self._adk_agent.description

    @property
    def adk_agent(self) -> Agent:
        return self._adk_agent

    def initialize(self) -> None:
        self._loaded = True
        logger.info(
            "MITRE Mapping Agent configured: name=%s description=%s",
            self.name,
            self.description,
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def map_incident(self, request: MitreMappingInput, db: Session) -> MitreMappingResult:
        return MitreMappingService(db).map_incident(request)
