"""Threat Intelligence Agent — ADK configuration and enrichment entry point."""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import Agent
from sqlalchemy.orm import Session

from agents.threat_intelligence.models import (
    ThreatIntelligenceInput,
    ThreatIntelligenceResult,
)
from agents.threat_intelligence.service import ThreatIntelligenceService
from app.core.logging import get_logger

logger = get_logger(__name__)

THREAT_INTELLIGENCE_AGENT_NAME = "threat_intelligence"
THREAT_INTELLIGENCE_AGENT_DESCRIPTION = (
    "Extracts indicators of compromise from evidence packages and produces "
    "deterministic threat intelligence reports without external lookups."
)
PROMPT_PATH = Path(__file__).with_name("prompt.md")


def load_threat_intelligence_prompt() -> str:
    """Load the versioned Threat Intelligence Agent system prompt from disk."""
    return PROMPT_PATH.read_text(encoding="utf-8")


class ThreatIntelligenceAgent:
    """Google ADK Threat Intelligence Agent — deterministic IOC extraction only."""

    def __init__(self) -> None:
        self._loaded = False
        self._adk_agent = Agent(
            name=THREAT_INTELLIGENCE_AGENT_NAME,
            description=THREAT_INTELLIGENCE_AGENT_DESCRIPTION,
            instruction=load_threat_intelligence_prompt(),
            input_schema=ThreatIntelligenceInput,
            output_schema=ThreatIntelligenceResult,
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
        """Initialize the Threat Intelligence Agent without invoking the LLM."""
        self._loaded = True
        logger.info(
            "Threat Intelligence Agent configured: name=%s description=%s",
            self.name,
            self.description,
        )

    @property
    def is_loaded(self) -> bool:
        """Return whether the Threat Intelligence Agent finished initialization."""
        return self._loaded

    def enrich(
        self,
        request: ThreatIntelligenceInput,
        db: Session,
    ) -> ThreatIntelligenceResult:
        """Extract IOCs and generate a threat intelligence report."""
        return ThreatIntelligenceService(db).enrich(request)
