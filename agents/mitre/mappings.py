"""Local rule-based MITRE ATT&CK mapping definitions for Sprint 2."""

from __future__ import annotations

import re
from dataclasses import dataclass

from agents.mitre.models import MappedTechnique


@dataclass(frozen=True)
class MitreMappingRule:
    """Rule mapping observed evidence patterns to an ATT&CK technique."""

    rule_name: str
    technique_id: str
    technique_name: str
    tactic: str
    confidence: int
    patterns: tuple[str, ...]


MAPPING_RULES: tuple[MitreMappingRule, ...] = (
    MitreMappingRule(
        rule_name="PowerShell Execution",
        technique_id="T1059.001",
        technique_name="PowerShell",
        tactic="Execution",
        confidence=96,
        patterns=("powershell.exe", "powershell"),
    ),
    MitreMappingRule(
        rule_name="Encoded PowerShell",
        technique_id="T1027",
        technique_name="Obfuscated Files or Information",
        tactic="Defense Evasion",
        confidence=94,
        patterns=("-encodedcommand", "-enc ", "encodedcommand", "frombase64string"),
    ),
    MitreMappingRule(
        rule_name="Failed Login Attempts",
        technique_id="T1110",
        technique_name="Brute Force",
        tactic="Credential Access",
        confidence=92,
        patterns=("event=4625", "failed logon", "failed login", "bad password"),
    ),
    MitreMappingRule(
        rule_name="Credential Dump",
        technique_id="T1003",
        technique_name="OS Credential Dumping",
        tactic="Credential Access",
        confidence=95,
        patterns=("lsass.exe", "mimikatz", "sekurlsa", "credential dump"),
    ),
    MitreMappingRule(
        rule_name="Remote Service",
        technique_id="T1021",
        technique_name="Remote Services",
        tactic="Lateral Movement",
        confidence=90,
        patterns=("rdp", "remote desktop", "dest=10.", "port 3389", "port 445"),
    ),
    MitreMappingRule(
        rule_name="Ransomware Activity",
        technique_id="T1486",
        technique_name="Data Encrypted for Impact",
        tactic="Impact",
        confidence=98,
        patterns=("ransomware", "encrypt.exe", ".locked", "decrypt_instructions"),
    ),
    MitreMappingRule(
        rule_name="Network Discovery",
        technique_id="T1046",
        technique_name="Network Service Discovery",
        tactic="Discovery",
        confidence=88,
        patterns=("nmap", "network scan", "port scan", "network discovery"),
    ),
)


def map_evidence_text(text: str) -> list[MappedTechnique]:
    """Apply local mapping rules to normalized evidence text."""
    if not text.strip():
        return []

    lowered = text.lower()
    findings: dict[str, MappedTechnique] = {}

    for rule in MAPPING_RULES:
        matched_evidence: list[str] = []
        for pattern in rule.patterns:
            if pattern in lowered:
                matched_evidence.append(pattern)
                continue
            regex = re.compile(re.escape(pattern), re.IGNORECASE)
            if regex.search(text):
                matched_evidence.append(pattern)

        if not matched_evidence:
            continue

        existing = findings.get(rule.technique_id)
        technique = MappedTechnique(
            technique_id=rule.technique_id,
            technique_name=rule.technique_name,
            tactic=rule.tactic,
            confidence=rule.confidence,
            matched_evidence=sorted(set(matched_evidence)),
        )
        if existing is None or technique.confidence > existing.confidence:
            findings[rule.technique_id] = technique

    return sorted(findings.values(), key=lambda item: item.technique_id)
