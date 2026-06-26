"""FastAPI application entry point for Oz AI."""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.core.config import get_upload_path, settings
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
