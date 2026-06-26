"""Reusable exception types and FastAPI exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.response import APIResponse


class AppException(Exception):
    """Application-level exception with an HTTP status code."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


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


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    return _error_response(exc.message, exc.status_code)


async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Handle HTTP exceptions with the standard response envelope."""
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(message, exc.status_code)


async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle request validation errors."""
    return _error_response("Validation error", status.HTTP_422_UNPROCESSABLE_ENTITY)


async def unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """Handle unexpected server errors."""
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
