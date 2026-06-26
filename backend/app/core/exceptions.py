"""Reusable exception types and FastAPI exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.schemas.response import APIResponse

logger = get_logger(__name__)


class AppException(Exception):
    """Application-level exception with an HTTP status code."""

    def __init__(
        self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


def _error_response(message: str, status_code: int) -> JSONResponse:
    """Build a consistent JSON error response."""
    payload = APIResponse[None](
        success=False,
        message=message,
        data=None,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(),
    )


def _format_validation_message(exc: RequestValidationError) -> str:
    """Convert validation errors into a concise human-readable message."""
    if not exc.errors():
        return "Validation error"

    first_error = exc.errors()[0]
    location = first_error.get("loc", ())
    field = location[-1] if location else "request"
    message = first_error.get("msg", "Invalid value")
    return f"Validation error: {field} — {message}"


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.exception("Application error: %s", exc.message)
    else:
        logger.warning("Application error (%s): %s", exc.status_code, exc.message)
    return _error_response(exc.message, exc.status_code)


async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Handle HTTP exceptions with the standard response envelope."""
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.error("HTTP error (%s): %s", exc.status_code, message)
    return _error_response(message, exc.status_code)


async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle request validation errors."""
    message = _format_validation_message(exc)
    logger.warning("Validation failed: %s", message)
    return _error_response(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


async def unhandled_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    """Handle unexpected server errors."""
    logger.exception("Unhandled exception: %s", exc)
    return _error_response(
        "Internal server error",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
