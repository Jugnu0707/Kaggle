"""Google AI verification API routes."""

from fastapi import APIRouter, status

from app.schemas.ai_health import AIHealthData
from app.schemas.ai_test import AITestResponse
from app.schemas.response import APIResponse
from app.services.ai_test_service import AITestService
from app.services.gemini_service import GeminiService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get(
    "/health",
    response_model=APIResponse[AIHealthData],
    status_code=status.HTTP_200_OK,
    summary="Verify Google AI Studio connectivity",
    description=(
        "Send a minimal prompt to the configured Gemini model to verify that "
        "GOOGLE_API_KEY and GOOGLE_MODEL are valid. This endpoint performs API "
        "verification only and does not invoke agent reasoning."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Connectivity check completed",
            "content": {
                "application/json": {
                    "examples": {
                        "connected": {
                            "summary": "Gemini API reachable",
                            "value": {
                                "success": True,
                                "message": "Google AI connectivity verified",
                                "data": {
                                    "connected": True,
                                    "model": "gemini-2.5-pro",
                                    "response": "Oz AI Ready",
                                },
                            },
                        },
                        "disconnected": {
                            "summary": "Gemini API unavailable or misconfigured",
                            "value": {
                                "success": False,
                                "message": "Google AI connectivity check failed",
                                "data": {
                                    "connected": False,
                                    "error": "GOOGLE_API_KEY is not configured",
                                },
                            },
                        },
                    }
                }
            },
        },
    },
)
def ai_health_check() -> APIResponse[AIHealthData]:
    """Verify Google AI Studio API key and model connectivity."""
    result = GeminiService().health_check()
    data = AIHealthData(
        connected=result.connected,
        model=result.model,
        response=result.response,
        error=result.error,
    )

    if result.connected:
        return APIResponse(
            success=True,
            message="Google AI connectivity verified",
            data=data,
        )

    return APIResponse(
        success=False,
        message="Google AI connectivity check failed",
        data=data,
    )


@router.get(
    "/test",
    response_model=AITestResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Test Google Gemini API connectivity",
    description=(
        "Send a single minimal prompt to the configured Gemini model to verify "
        "that GOOGLE_API_KEY and GOOGLE_MODEL work. Uses one API call with a "
        "one-word expected response to minimize token usage. Does not invoke "
        "agents, MCP, or investigation workflows."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Connectivity probe completed",
            "content": {
                "application/json": {
                    "examples": {
                        "connected": {
                            "summary": "Gemini API reachable",
                            "value": {
                                "connected": True,
                                "provider": "Google Gemini",
                                "model": "gemini-2.5-pro",
                                "response": "READY",
                                "latency_ms": 123,
                            },
                        },
                        "quota_exceeded": {
                            "summary": "Gemini quota exceeded",
                            "value": {
                                "connected": False,
                                "reason": "Quota exceeded",
                            },
                        },
                        "invalid_key": {
                            "summary": "Invalid or missing API key",
                            "value": {
                                "connected": False,
                                "reason": "Invalid API key",
                            },
                        },
                        "timeout": {
                            "summary": "Gemini request timed out",
                            "value": {
                                "connected": False,
                                "reason": "Timeout",
                            },
                        },
                    }
                }
            },
        },
    },
)
def ai_connectivity_test() -> AITestResponse:
    """Verify Gemini API key and model with a minimal token probe."""
    result = AITestService().test_connectivity()
    return AITestResponse(
        connected=result.connected,
        provider=result.provider,
        model=result.model,
        response=result.response,
        latency_ms=result.latency_ms,
        reason=result.reason,
    )
