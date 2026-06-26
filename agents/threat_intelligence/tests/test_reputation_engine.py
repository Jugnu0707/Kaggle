"""Unit tests for the offline reputation engine."""

from agents.threat_intelligence.models import IOC
from agents.threat_intelligence.reputation_engine import assess_reputation
from agents.threat_intelligence.schemas import Reputation


def test_private_ipv4_is_safe() -> None:
    assessment = assess_reputation(
        IOC(type="IPv4", value="192.168.10.25", confidence=70, source="Log")
    )
    assert assessment.reputation == Reputation.SAFE


def test_public_ipv4_is_unknown() -> None:
    assessment = assess_reputation(
        IOC(type="IPv4", value="185.234.72.19", confidence=90, source="Log")
    )
    assert assessment.reputation == Reputation.UNKNOWN


def test_suspicious_powershell_url() -> None:
    assessment = assess_reputation(
        IOC(
            type="URL",
            value="http://malicious.example.com/stage.ps1",
            confidence=85,
            source="Log",
        ),
        context_text="powershell encodedcommand",
    )
    assert assessment.reputation == Reputation.SUSPICIOUS


def test_known_ransomware_hash_is_malicious() -> None:
    assessment = assess_reputation(
        IOC(
            type="SHA256",
            value="84c82834a5d2baa474127145eea280a47288179389d56265f74838687532eda",
            confidence=95,
            source="Log",
        )
    )
    assert assessment.reputation == Reputation.MALICIOUS
