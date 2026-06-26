"""HTTP middleware for the Oz AI backend."""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests and response status codes."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process a request and log method, path, status, and duration."""
        start = time.perf_counter()
        logger.info("Request started: %s %s", request.method, request.url.path)

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Request completed: %s %s -> %s (%.2fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
