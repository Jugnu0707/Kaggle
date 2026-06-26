"""Unit tests for ExecutiveReportService AI and fallback behavior."""

from unittest.mock import patch
from uuid import uuid4

import pytest
from google.genai import errors as genai_errors

from agents.executive_report.models import ExecutiveReportInput
from agents.executive_report.schemas import (
    AIExecutiveReportResponse,
    ExecutiveReportContext,
    ExecutiveReportSource,
    IncidentContext,
    ResponsePlanContext,
    RiskAssessmentContext,
)
from agents.executive_report.service import ExecutiveReportService


@pytest.fixture
def mock_context() -> ExecutiveReportContext:
    return ExecutiveReportContext(
        incident=IncidentContext(
            id=uuid4(),
            title="Suspicious PowerShell Activity",
            description="Unusual script execution detected on a finance workstation.",
            severity="High",
            status="Investigating",
            source="Microsoft Defender",
            confidence_score=0.88,
            created_at="2026-06-26T10:00:00+00:00",
        ),
        risk_assessment=RiskAssessmentContext(
            overall_risk="High",
            risk_score=80,
            priority="P2",
            likelihood="Likely",
            business_impact="Potential disruption to finance operations",
            summary="High-risk execution activity requires leadership review.",
            reasoning="Suspicious script execution on a critical endpoint",
        ),
        response_plan=ResponsePlanContext(
            priority="P2",
            containment=["Isolate affected endpoint"],
            eradication=["Block unauthorized script execution"],
            recovery=["Validate endpoint integrity before reconnection"],
            monitoring=["Monitor for repeated script execution"],
            executive_summary="High-priority response plan prepared.",
        ),
    )


def test_ai_success_returns_ai_source(db_session, mock_context) -> None:
    """Successful Gemini JSON response returns AI executive report."""
    ai_response = AIExecutiveReportResponse(
        title="Executive Incident Report",
        executive_summary="Leadership review is required for suspicious script activity.",
        business_impact="Finance operations may face temporary disruption.",
        incident_timeline_summary="Activity was detected during the morning monitoring window.",
        key_findings=["Suspicious script execution on a finance workstation"],
        mitre_summary="Observed behavior aligns with script-based execution techniques.",
        risk_summary="Enterprise risk remains high pending containment approval.",
        recommended_actions=["Approve endpoint isolation for affected systems"],
        lessons_learned=["Review script execution controls on finance endpoints"],
    )

    service = ExecutiveReportService(db_session)
    with patch.object(service, "_gather_context", return_value=mock_context):
        with patch.object(service, "_call_gemini", return_value=ai_response):
            result = service.generate(
                ExecutiveReportInput(incident_id=mock_context.incident.id)
            )

    assert result.source == ExecutiveReportSource.AI
    assert result.title == "Executive Incident Report"
    assert "Leadership review" in result.executive_summary
    assert "## Recommended Actions" in result.markdown


def test_quota_exceeded_uses_fallback(db_session, mock_context) -> None:
    """429 quota errors trigger fallback executive report."""
    service = ExecutiveReportService(db_session)
    with patch.object(service, "_gather_context", return_value=mock_context):
        with patch.object(
            service,
            "_call_gemini",
            side_effect=genai_errors.ClientError(
                429,
                {"error": {"message": "Quota exceeded"}},
                None,
            ),
        ):
            result = service.generate(
                ExecutiveReportInput(incident_id=mock_context.incident.id)
            )

    assert result.source == ExecutiveReportSource.FALLBACK
    assert len(result.key_findings) >= 1
    assert result.markdown


def test_invalid_json_uses_fallback(db_session, mock_context) -> None:
    """Invalid JSON from Gemini triggers fallback executive report."""
    service = ExecutiveReportService(db_session)
    with patch.object(service, "_gather_context", return_value=mock_context):
        with patch.object(service, "_call_gemini", return_value=None):
            result = service.generate(
                ExecutiveReportInput(incident_id=mock_context.incident.id)
            )

    assert result.source == ExecutiveReportSource.FALLBACK
    assert result.executive_summary
