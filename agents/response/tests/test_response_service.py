"""Unit tests for ResponsePlanningService AI and fallback behavior."""

from unittest.mock import patch
from uuid import uuid4

import pytest
from agents.conftest import build_mock_ai_runtime
from agents.response.models import ResponsePlanInput
from agents.response.schemas import AIResponsePlanResponse, ResponsePlanSource
from agents.response.service import ResponsePlanningService
from google.genai import errors as genai_errors


@pytest.fixture
def mock_context():
    from agents.response.schemas import (
        IncidentContext,
        ResponsePlanningContext,
        RiskAssessmentContext,
    )

    return ResponsePlanningContext(
        incident=IncidentContext(
            id=uuid4(),
            title="Suspicious PowerShell Execution",
            description="PowerShell launched from Word process.",
            severity="High",
            status="Investigating",
            source="Microsoft Defender",
            confidence_score=0.92,
        ),
        risk_assessment=RiskAssessmentContext(
            overall_risk="High",
            risk_score=80,
            priority="P2",
            summary="High risk execution chain",
            reasoning="PowerShell with suspicious parent process",
        ),
    )


def test_ai_success_returns_ai_source(
    db_session, mock_context, mock_ai_runtime
) -> None:
    """Successful Gemini JSON response returns AI response plan."""
    ai_response = AIResponsePlanResponse(
        priority="P2",
        containment=["Isolate affected endpoint"],
        eradication=["Block unauthorized PowerShell execution"],
        recovery=["Validate endpoint integrity before reconnection"],
        monitoring=["Monitor for repeated script execution"],
        executive_summary="High-priority response plan for suspicious PowerShell activity.",
    )

    service = ResponsePlanningService(db_session)
    mock_runtime = build_mock_ai_runtime()
    with patch("agents.response.service.get_ai_runtime", return_value=mock_runtime):
        with patch.object(service, "_gather_context", return_value=mock_context):
            with patch.object(service, "_call_gemini", return_value=ai_response):
                result = service.plan(
                    ResponsePlanInput(incident_id=mock_context.incident.id)
                )

    assert result.source == ResponsePlanSource.AI
    assert result.priority == "P2"
    assert "Isolate affected endpoint" in result.containment


def test_quota_exceeded_uses_fallback(
    db_session, mock_context, mock_ai_runtime
) -> None:
    """429 quota errors trigger fallback response plan."""
    service = ResponsePlanningService(db_session)
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
            result = service.plan(
                ResponsePlanInput(incident_id=mock_context.incident.id)
            )

    assert result.source == ResponsePlanSource.FALLBACK
    assert result.priority == "P2"


def test_invalid_json_uses_fallback(db_session, mock_context, mock_ai_runtime) -> None:
    """Invalid JSON from Gemini triggers fallback response plan."""
    service = ResponsePlanningService(db_session)
    with patch.object(service, "_gather_context", return_value=mock_context):
        with patch.object(service, "_call_gemini", return_value=None):
            result = service.plan(
                ResponsePlanInput(incident_id=mock_context.incident.id)
            )

    assert result.source == ResponsePlanSource.FALLBACK


def test_timeout_uses_fallback(db_session, mock_context, mock_ai_runtime) -> None:
    """AI request timeout triggers fallback response plan."""
    service = ResponsePlanningService(db_session)

    def slow_call(*_args, **_kwargs):
        import time

        time.sleep(2)
        return None

    with patch.object(service, "_gather_context", return_value=mock_context):
        with patch.object(service, "_call_gemini", side_effect=slow_call):
            with patch("agents.response.service.AI_REQUEST_TIMEOUT_SECONDS", 0.01):
                result = service.plan(
                    ResponsePlanInput(incident_id=mock_context.incident.id)
                )

    assert result.source == ResponsePlanSource.FALLBACK


def test_missing_api_key_uses_fallback(
    db_session, mock_context, mock_ai_runtime
) -> None:
    """Missing API key triggers fallback without raising."""
    mock_ai_runtime.provider.get_api_key.return_value = ""
    mock_ai_runtime.provider.has_api_key.return_value = False

    service = ResponsePlanningService(db_session)
    with patch.object(service, "_gather_context", return_value=mock_context):
        result = service.plan(ResponsePlanInput(incident_id=mock_context.incident.id))

    assert result.source == ResponsePlanSource.FALLBACK
