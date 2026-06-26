"""FastAPI application entry point for Oz AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

APP_TITLE = "Oz AI"
APP_VERSION = "0.1.0"

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning project identity and run status."""
    return {"project": "Oz AI", "status": "running"}


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    """Health check endpoint for service monitoring."""
    return {
        "status": "healthy",
        "service": "oz-ai",
        "version": APP_VERSION,
    }
