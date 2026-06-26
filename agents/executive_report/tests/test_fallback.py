"""Unit tests for the executive report fallback engine."""

from uuid import uuid4

from agents.evidence.models import EvidenceSummary
from agents.executive_report.fallback import generate_executive_report_fallback
from agents.executive_report.schemas import (
    ExecutiveReportContext,
    ExecutiveReportSource,
    IncidentContext,
    ResponsePlanContext,
    RiskAssessmentContext,
)
from agents.mitre.models import MappedTechnique


def _context(
    *,
    severity: str = "High",
    title: str = "Ransomware Activity Detected",
    description: str = "Encryption activity observed on finance endpoints.",
) -> ExecutiveReportContext:
    return ExecutiveReportContext(
        incident=IncidentContext(
            id=uuid4(),
            title=title,
            description=description,
            severity=severity,
            status="Investigating",
            source="EDR Platform",
            confidence_score=0.9,
            created_at="2026-06-26T08:00:00+00:00",
        ),
        evidence_summaries=[
            EvidenceSummary(
                file_type="application_log",
                total_entries=12,
                time_range="2026-06-26T08:00:00 to 2026-06-26T09:00:00",
                possible_log_source="Endpoint telemetry",
                data_quality_observations=["Timestamps detected in log entries"],
            )
        ],
        mitre_techniques=[
            MappedTechnique(
                technique_id="T1486",
                technique_name="Data Encrypted for Impact",
                tactic="Impact",
                confidence=95,
                matched_evidence=["encryption"],
            )
        ],
        risk_assessment=RiskAssessmentContext(
            overall_risk="Critical",
            risk_score=92,
            priority="P1",
            likelihood="Very Likely",
            business_impact="Severe operational disruption across finance systems",
            summary="Critical ransomware indicators require immediate leadership review.",
            reasoning="Encryption activity on critical endpoints",
        ),
        response_plan=ResponsePlanContext(
            priority="P1",
            containment=["Isolate affected host from the network"],
            eradication=["Remove ransomware binaries"],
            recovery=["Restore from verified backups"],
            monitoring=["Monitor for re-encryption"],
            executive_summary="Critical containment plan prepared.",
        ),
        suspicious_indicator_count=2,
    )


def test_fallback_generates_complete_report() -> None:
    """Fallback returns structured JSON and Markdown without raw logs."""
    result = generate_executive_report_fallback(_context())

    assert result.source == ExecutiveReportSource.FALLBACK
    assert result.title == "Executive Incident Report"
    assert result.executive_summary
    assert result.business_impact
    assert len(result.key_findings) >= 1
    assert len(result.recommended_actions) >= 1
    assert len(result.lessons_learned) >= 1
    assert "# Executive Incident Report" in result.markdown
    assert "powershell.exe" not in result.markdown.lower()


def test_fallback_uses_business_language() -> None:
    """Fallback report avoids raw technical log content."""
    result = generate_executive_report_fallback(_context())

    assert "ransomware" in result.executive_summary.lower() or "critical" in result.executive_summary.lower()
    assert "Attack activity aligns with" in result.markdown
