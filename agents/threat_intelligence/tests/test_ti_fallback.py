"""Unit tests for threat intelligence fallback enrichment."""

from agents.threat_intelligence.fallback import enrich_ioc_fallback
from agents.threat_intelligence.models import IOC
from agents.threat_intelligence.schemas import ThreatIntelligenceSource


def test_fallback_enriches_public_ip() -> None:
    finding = enrich_ioc_fallback(
        IOC(type="IPv4", value="185.234.72.19", confidence=90, source="Application Log")
    )
    assert finding.source == ThreatIntelligenceSource.FALLBACK
    assert finding.reputation == "Unknown"
    assert finding.description
    assert "Offline enrichment" in finding.analyst_notes
