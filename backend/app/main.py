"""FastAPI application entry point for Oz AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.schemas.response import APIResponse

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(application)
    application.include_router(api_v1_router)

    @application.get("/")
    async def root() -> APIResponse[dict[str, str]]:
        """Root endpoint returning project identity and run status."""
        return APIResponse(
            success=True,
            message="Running",
            data={"project": settings.app_name, "status": "running"},
        )

    logger.info("Application started: %s v%s", settings.app_name, settings.app_version)
    return application


app = create_app()
