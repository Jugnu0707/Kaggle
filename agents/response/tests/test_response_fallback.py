"""Unit tests for the response planning fallback engine."""

from uuid import uuid4

from agents.evidence.models import EvidenceSummary
from agents.mitre.models import MappedTechnique
from agents.response.fallback import plan_response_fallback
from agents.response.schemas import (
    IncidentContext,
    ResponsePlanningContext,
    ResponsePlanSource,
    RiskAssessmentContext,
)


def _context(
    *,
    severity: str = "Low",
    title: str = "Test incident",
    description: str = "Routine activity",
    techniques: list[MappedTechnique] | None = None,
    risk_priority: str = "P4",
) -> ResponsePlanningContext:
    return ResponsePlanningContext(
        incident=IncidentContext(
            id=uuid4(),
            title=title,
            description=description,
            severity=severity,
            status="Investigating",
            source="Test Source",
            confidence_score=0.5,
        ),
        evidence_summaries=[
            EvidenceSummary(
                file_type="application_log",
                total_entries=1,
                time_range="2026-06-26T10:00:00 to 2026-06-26T11:00:00",
                possible_log_source="Generic application log",
                data_quality_observations=["Sample entries are available for review"],
            )
        ],
        mitre_techniques=techniques or [],
        risk_assessment=RiskAssessmentContext(
            overall_risk="Low",
            risk_score=20,
            priority=risk_priority,
            summary="Low risk incident",
            reasoning="No elevated indicators",
        ),
    )


def test_fallback_ransomware_playbook() -> None:
    """Ransomware maps to isolation and backup recovery actions."""
    result = plan_response_fallback(
        _context(
            severity="Critical",
            title="Ransomware detected",
            techniques=[
                MappedTechnique(
                    technique_id="T1486",
                    technique_name="Data Encrypted for Impact",
                    tactic="Impact",
                    confidence=98,
                    matched_evidence=["encryption"],
                )
            ],
            risk_priority="P1",
        )
    )

    assert result.source == ResponsePlanSource.FALLBACK
    assert result.priority == "P1"
    assert any("Isolate" in action for action in result.containment)
    assert any("backup" in action.lower() for action in result.recovery)


def test_fallback_powershell_playbook() -> None:
    """PowerShell execution maps to endpoint isolation and script blocking."""
    result = plan_response_fallback(
        _context(
            techniques=[
                MappedTechnique(
                    technique_id="T1059.001",
                    technique_name="PowerShell",
                    tactic="Execution",
                    confidence=85,
                    matched_evidence=["powershell.exe"],
                )
            ],
            risk_priority="P3",
        )
    )

    assert result.priority == "P3"
    assert any("PowerShell" in action for action in result.eradication)
    assert any("parent process" in action.lower() for action in result.monitoring)


def test_fallback_failed_login_playbook() -> None:
    """Failed login maps to IP blocking and MFA recommendations."""
    result = plan_response_fallback(
        _context(
            techniques=[
                MappedTechnique(
                    technique_id="T1110",
                    technique_name="Brute Force",
                    tactic="Credential Access",
                    confidence=80,
                    matched_evidence=["failed login"],
                )
            ],
            risk_priority="P3",
        )
    )

    assert any("Block source IP" in action for action in result.containment)
    assert any("multi-factor" in action.lower() for action in result.eradication)


def test_fallback_generic_when_no_indicators() -> None:
    """Unknown activity maps to generic response recommendations."""
    result = plan_response_fallback(_context())

    assert result.source == ResponsePlanSource.FALLBACK
    assert len(result.containment) >= 1
    assert len(result.monitoring) >= 1
    assert "recommendations only" in result.executive_summary.lower()
