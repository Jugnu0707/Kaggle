"""Unit tests for the risk assessment fallback engine."""

from uuid import uuid4

from agents.evidence.models import EvidenceSummary
from agents.mitre.models import MappedTechnique
from agents.risk.fallback import assess_risk_fallback
from agents.risk.schemas import IncidentContext, RiskAssessmentContext, RiskAssessmentSource


def _context(
    *,
    severity: str = "Low",
    title: str = "Test incident",
    description: str = "Routine activity",
    techniques: list[MappedTechnique] | None = None,
) -> RiskAssessmentContext:
    return RiskAssessmentContext(
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
    )


def test_fallback_critical_for_ransomware_technique() -> None:
    """T1486 maps to Critical risk."""
    result = assess_risk_fallback(
        _context(
            techniques=[
                MappedTechnique(
                    technique_id="T1486",
                    technique_name="Data Encrypted for Impact",
                    tactic="Impact",
                    confidence=98,
                    matched_evidence=["ransomware"],
                )
            ]
        )
    )

    assert result.source == RiskAssessmentSource.FALLBACK
    assert result.overall_risk == "Critical"
    assert result.priority == "P1"
    assert 90 <= result.risk_score <= 100


def test_fallback_high_for_many_mitre_techniques() -> None:
    """More than three MITRE techniques maps to High risk."""
    techniques = [
        MappedTechnique(
            technique_id=f"T10{i}",
            technique_name=f"Technique {i}",
            tactic="Execution",
            confidence=80,
            matched_evidence=[f"pattern-{i}"],
        )
        for i in range(4)
    ]
    result = assess_risk_fallback(_context(techniques=techniques))

    assert result.overall_risk == "High"
    assert result.priority == "P2"
    assert 70 <= result.risk_score <= 89


def test_fallback_medium_for_powershell() -> None:
    """PowerShell execution maps to Medium risk."""
    result = assess_risk_fallback(
        _context(
            techniques=[
                MappedTechnique(
                    technique_id="T1059.001",
                    technique_name="PowerShell",
                    tactic="Execution",
                    confidence=85,
                    matched_evidence=["powershell.exe"],
                )
            ]
        )
    )

    assert result.overall_risk == "Medium"
    assert result.priority == "P3"


def test_fallback_low_when_no_indicators() -> None:
    """Unknown activity maps to Low risk."""
    result = assess_risk_fallback(_context())

    assert result.overall_risk == "Low"
    assert result.priority == "P4"
    assert result.risk_score <= 39
