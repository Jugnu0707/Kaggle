"""API version 1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.logs import router as logs_router
from app.api.v1.system import router as system_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router, tags=["health"])
api_v1_router.include_router(incidents_router)
api_v1_router.include_router(logs_router)
api_v1_router.include_router(system_router)
