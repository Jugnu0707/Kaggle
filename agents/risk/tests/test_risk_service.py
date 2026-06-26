"""Unit tests for RiskAssessmentService AI and fallback behavior."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from google.genai import errors as genai_errors

from agents.risk.models import RiskAssessmentInput
from agents.risk.schemas import AIRiskAssessmentResponse, RiskAssessmentSource, RiskLevel
from agents.risk.service import RiskAssessmentService


@pytest.fixture
def mock_context():
    from agents.risk.schemas import IncidentContext, RiskAssessmentContext

    return RiskAssessmentContext(
        incident=IncidentContext(
            id=uuid4(),
            title="Suspicious PowerShell Execution",
            description="PowerShell launched from Word process.",
            severity="High",
            status="Investigating",
            source="Microsoft Defender",
            confidence_score=0.92,
        )
    )


def test_ai_success_returns_ai_source(db_session, mock_context) -> None:
    """Successful Gemini JSON response returns AI assessment."""
    ai_response = AIRiskAssessmentResponse(
        overall_risk=RiskLevel.HIGH,
        risk_score=82,
        likelihood="Likely",
        business_impact="Significant business disruption",
        confidence=90,
        priority="P2",
        summary="High risk due to suspicious execution chain.",
        reasoning="PowerShell and external network activity observed.",
    )

    service = RiskAssessmentService(db_session)
    with patch.object(service, "_gather_context", return_value=mock_context):
        with patch.object(service, "_call_gemini", return_value=ai_response):
            result = service.assess(RiskAssessmentInput(incident_id=mock_context.incident.id))

    assert result.source == RiskAssessmentSource.AI
    assert result.overall_risk == "High"
    assert result.priority == "P2"


def test_quota_exceeded_uses_fallback(db_session, mock_context) -> None:
    """429 quota errors trigger fallback assessment."""
    service = RiskAssessmentService(db_session)
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
            result = service.assess(RiskAssessmentInput(incident_id=mock_context.incident.id))

    assert result.source == RiskAssessmentSource.FALLBACK
    assert result.overall_risk in {"High", "Medium", "Low", "Critical"}


def test_invalid_json_uses_fallback(db_session, mock_context) -> None:
    """Invalid JSON from Gemini triggers fallback assessment."""
    service = RiskAssessmentService(db_session)
    with patch.object(service, "_gather_context", return_value=mock_context):
        with patch.object(service, "_call_gemini", return_value=None):
            result = service.assess(RiskAssessmentInput(incident_id=mock_context.incident.id))

    assert result.source == RiskAssessmentSource.FALLBACK


def test_timeout_uses_fallback(db_session, mock_context) -> None:
    """AI request timeout triggers fallback assessment."""
    service = RiskAssessmentService(db_session)

    def slow_call(*_args, **_kwargs):
        import time

        time.sleep(2)
        return None

    with patch.object(service, "_gather_context", return_value=mock_context):
        with patch.object(service, "_call_gemini", side_effect=slow_call):
            with patch("agents.risk.service.AI_REQUEST_TIMEOUT_SECONDS", 0.01):
                result = service.assess(RiskAssessmentInput(incident_id=mock_context.incident.id))

    assert result.source == RiskAssessmentSource.FALLBACK


def test_missing_api_key_uses_fallback(db_session, mock_context) -> None:
    """Missing API key triggers fallback without raising."""
    service = RiskAssessmentService(db_session)
    with patch.object(service, "_gather_context", return_value=mock_context):
        with patch("agents.risk.service.ai_settings") as mock_settings:
            mock_settings.google_api_key = ""
            mock_settings.google_model = "gemini-2.0-flash"
            result = service.assess(RiskAssessmentInput(incident_id=mock_context.incident.id))

    assert result.source == RiskAssessmentSource.FALLBACK
