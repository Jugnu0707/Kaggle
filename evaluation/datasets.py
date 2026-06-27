"""Synthetic datasets for offline agent benchmarking."""

from __future__ import annotations

from dataclasses import dataclass

BENCHMARK_AGENTS: tuple[str, ...] = (
    "Coordinator Agent",
    "Evidence Agent",
    "Threat Intelligence Agent",
    "MITRE Mapping Agent",
    "Risk Assessment Agent",
    "Response Planning Agent",
    "Executive Report Agent",
    "Guardian Agent",
    "Timeline Engine",
)


@dataclass(frozen=True)
class EvidenceScenario:
    """Sample log content for evidence collection benchmarks."""

    title: str
    log_content: str
    expected_success: bool = True


@dataclass(frozen=True)
class TextScenario:
    """Generic text input for mapping and enrichment benchmarks."""

    title: str
    text: str
    expected_success: bool = True
    expected_confidence_min: float = 70.0


EVIDENCE_SCENARIOS: tuple[EvidenceScenario, ...] = (
    EvidenceScenario(
        title="powershell_execution",
        log_content=(
            "2026-06-24T08:15:03Z ERROR process started powershell.exe -EncodedCommand ABC123\n"
            "2026-06-24T08:15:04Z WARN suspicious script execution detected\n"
        ),
    ),
    EvidenceScenario(
        title="failed_logon",
        log_content=(
            "2026-06-24T09:00:00Z EVENT=4625 failed logon for user admin\n"
            "2026-06-24T09:00:01Z EVENT=4625 failed logon for user admin\n"
        ),
    ),
)

THREAT_INTEL_SCENARIOS: tuple[TextScenario, ...] = (
    TextScenario(
        title="malicious_ip",
        text="Outbound connection to 185.234.72.19 from workstation-12",
        expected_confidence_min=60.0,
    ),
    TextScenario(
        title="benign_activity",
        text="User opened internal wiki page successfully",
        expected_confidence_min=50.0,
    ),
)

MITRE_SCENARIOS: tuple[TextScenario, ...] = (
    TextScenario(
        title="powershell_mapping",
        text="powershell.exe launched with -EncodedCommand payload",
    ),
    TextScenario(
        title="brute_force_mapping",
        text="2026-06-24T09:00:00Z EVENT=4625 failed logon for user admin",
    ),
)

GUARDIAN_SCENARIOS: tuple[dict[str, object], ...] = (
    {
        "agent": "risk",
        "response": {
            "source": "FALLBACK",
            "overall_risk": "High",
            "risk_score": 80,
            "likelihood": "Likely",
            "business_impact": "Significant business disruption",
            "confidence": 85,
            "priority": "P2",
            "summary": "Fallback risk assessment classified the incident as High.",
            "reasoning": "Incident severity is High",
        },
        "expected_success": True,
    },
    {
        "agent": "executive_report",
        "response": {
            "source": "FALLBACK",
            "title": "Executive Incident Report",
            "executive_summary": "A high-severity incident requires leadership review.",
            "business_impact": "Significant operational disruption is possible.",
            "key_findings": ["Suspicious activity detected on a critical endpoint"],
            "recommended_actions": ["Convene the incident response team"],
            "lessons_learned": ["Maintain regular executive briefings"],
            "markdown": "# Executive Incident Report",
        },
        "expected_success": True,
    },
)
