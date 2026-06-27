"""Offline fallback enrichment for extracted IOCs."""

from __future__ import annotations

from agents.threat_intelligence.models import IOC, ThreatIntelligenceFinding
from agents.threat_intelligence.reputation_engine import assess_reputation
from agents.threat_intelligence.schemas import ThreatIntelligenceSource


def enrich_ioc_fallback(
    ioc: IOC, *, context_text: str = ""
) -> ThreatIntelligenceFinding:
    """Enrich a single IOC using offline reputation rules only."""
    assessment = assess_reputation(ioc, context_text=context_text)
    analyst_notes = (
        f"Offline enrichment applied to {ioc.type} indicator from {ioc.source}. "
        "No external threat intelligence provider was consulted."
    )
    if assessment.reputation.value == "Malicious":
        analyst_notes += " Treat as high-priority for containment review."
    elif assessment.reputation.value == "Suspicious":
        analyst_notes += " Correlate with surrounding evidence before escalation."

    return ThreatIntelligenceFinding(
        indicator=ioc.value,
        indicator_type=ioc.type,
        reputation=assessment.reputation.value,
        confidence=assessment.confidence,
        source=ThreatIntelligenceSource.FALLBACK,
        description=assessment.description,
        analyst_notes=analyst_notes,
    )
