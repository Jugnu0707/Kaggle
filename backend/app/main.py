"""FastAPI application entry point for Oz AI."""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.core.adk_runtime import initialize_adk_runtime
from app.core.config import get_upload_path, settings
from app.core.evidence_runtime import initialize_evidence_runtime
from app.core.mcp_runtime import initialize_mcp_runtime
from app.core.mitre_runtime import initialize_mitre_runtime
from app.core.guardian_runtime import initialize_guardian_runtime
from app.core.executive_report_runtime import initialize_executive_report_runtime
from app.core.response_runtime import initialize_response_runtime
from app.core.risk_runtime import initialize_risk_runtime
from app.core.threat_intelligence_runtime import initialize_threat_intelligence_runtime
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.openapi import OPENAPI_TAGS
from app.db.database import init_db
from app.schemas.response import APIResponse

logger = get_logger(__name__)

root_router = APIRouter(tags=["root"])


@root_router.get(
    "/",
    response_model=APIResponse[dict[str, str]],
    summary="Application root",
    description="Return the application identity and runtime status.",
    responses={200: {"description": "Application is running"}},
)
async def root() -> APIResponse[dict[str, str]]:
    """Root endpoint returning project identity and run status."""
    return APIResponse(
        success=True,
        message="Running",
        data={"project": settings.app_name, "status": "running"},
    )


@asynccontextmanager
async def lifespan(_application: FastAPI):
    """Initialize application resources on startup."""
    init_db()
    get_upload_path()
    initialize_adk_runtime()
    initialize_evidence_runtime()
    initialize_threat_intelligence_runtime()
    initialize_mitre_runtime()
    initialize_risk_runtime()
    initialize_response_runtime()
    initialize_executive_report_runtime()
    initialize_guardian_runtime()
    initialize_mcp_runtime()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Oz AI REST API for enterprise incident management, log uploads, "
            "and operational dashboard metrics."
        ),
        contact={"name": "Oz AI Engineering"},
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )

    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(application)
    application.include_router(root_router)
    application.include_router(api_v1_router)

    logger.info("Application started: %s v%s", settings.app_name, settings.app_version)
    return application


app = create_app()
