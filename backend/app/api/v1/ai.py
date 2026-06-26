"""Google AI verification API routes."""

from fastapi import APIRouter, status

from app.schemas.ai_health import AIHealthData
from app.schemas.response import APIResponse
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
