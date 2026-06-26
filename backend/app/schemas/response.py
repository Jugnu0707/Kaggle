"""Generic API response schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard envelope for all API responses."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(description="Whether the request completed successfully")
    message: str = Field(description="Human-readable status message")
    data: T | None = Field(default=None, description="Response payload when successful")

    @classmethod
    def example(cls, data: Any, message: str = "Success") -> dict[str, Any]:
        """Build an OpenAPI-friendly example payload."""
        return {"success": True, "message": message, "data": data}
