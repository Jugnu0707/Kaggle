"""Generic API response schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard envelope for all API responses."""

    model_config = ConfigDict(from_attributes=True)

    success: bool
    message: str
    data: T | None = None
