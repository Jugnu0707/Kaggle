"""Offline deterministic reputation engine for extracted IOCs."""

from __future__ import annotations

import ipaddress

from agents.threat_intelligence.ioc_extractor import is_private_ipv4
from agents.threat_intelligence.models import IOC
from agents.threat_intelligence.schemas import Reputation, ReputationAssessment

# Sample ransomware hashes for offline matching (expandable without API calls).
KNOWN_RANSOMWARE_HASHES: dict[str, str] = {
    "84c82834a5d2baa474127145eea280a47288179389d56265f74838687532eda": "WannaCry sample",
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": "Observed in evidence",
}

SUSPICIOUS_URL_TOKENS = (
    "powershell",
    ".ps1",
    "payload",
    "malicious",
    "stage",
    "download",
    "-enc",
)


def assess_reputation(ioc: IOC, *, context_text: str = "") -> ReputationAssessment:
    """Assign offline reputation and baseline confidence to an extracted IOC."""
    ioc_type = ioc.type
    value = ioc.value
    lowered = value.lower()
    context = context_text.lower()

    if ioc_type in {"SHA256", "SHA1", "MD5"} and lowered in KNOWN_RANSOMWARE_HASHES:
        label = KNOWN_RANSOMWARE_HASHES[lowered]
        return ReputationAssessment(
            reputation=Reputation.MALICIOUS,
            confidence=95,
            description=f"Known ransomware-related hash ({label})",
        )

    if ioc_type == "IPv4":
        if is_private_ipv4(value):
            return ReputationAssessment(
                reputation=Reputation.SAFE,
                confidence=75,
                description="RFC1918 or private IPv4 address observed in evidence",
            )
        return ReputationAssessment(
            reputation=Reputation.UNKNOWN,
            confidence=85,
            description="Public IPv4 address requires analyst review",
        )

    if ioc_type == "IPv6":
        try:
            address = ipaddress.ip_address(value)
            if address.is_private or address.is_loopback:
                return ReputationAssessment(
                    reputation=Reputation.INFORMATIONAL,
                    confidence=70,
                    description="Private or link-local IPv6 address observed in evidence",
                )
        except ValueError:
            pass
        return ReputationAssessment(
            reputation=Reputation.UNKNOWN,
            confidence=80,
            description="Public IPv6 address requires analyst review",
        )

    if ioc_type == "URL":
        if (
            any(token in lowered for token in SUSPICIOUS_URL_TOKENS)
            or "powershell" in context
        ):
            return ReputationAssessment(
                reputation=Reputation.SUSPICIOUS,
                confidence=88,
                description="URL associated with suspicious script or download activity",
            )
        return ReputationAssessment(
            reputation=Reputation.UNKNOWN,
            confidence=75,
            description="URL indicator extracted from evidence for analyst review",
        )

    if ioc_type == "Domain":
        if lowered.endswith(".local") or lowered.endswith(".internal"):
            return ReputationAssessment(
                reputation=Reputation.INFORMATIONAL,
                confidence=70,
                description="Internal domain name observed in evidence",
            )
        if any(token in lowered for token in ("malicious", "evil", "bad")):
            return ReputationAssessment(
                reputation=Reputation.SUSPICIOUS,
                confidence=82,
                description="Domain name contains suspicious naming patterns",
            )
        return ReputationAssessment(
            reputation=Reputation.UNKNOWN,
            confidence=78,
            description="Domain indicator extracted from evidence",
        )

    if ioc_type == "Email":
        return ReputationAssessment(
            reputation=Reputation.INFORMATIONAL,
            confidence=72,
            description="Email address observed in evidence context",
        )

    if ioc_type == "Hostname":
        return ReputationAssessment(
            reputation=Reputation.INFORMATIONAL,
            confidence=70,
            description="Internal hostname observed in evidence",
        )

    if ioc_type == "WindowsUsername":
        return ReputationAssessment(
            reputation=Reputation.INFORMATIONAL,
            confidence=68,
            description="Windows account reference observed in evidence",
        )

    return ReputationAssessment(
        reputation=Reputation.UNKNOWN,
        confidence=60,
        description="Indicator extracted from evidence for analyst review",
    )
