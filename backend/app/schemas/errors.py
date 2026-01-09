"""Error response schemas for standardized API responses.

This module defines Pydantic models for error responses following ADR-004.
"""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information for a specific field or issue."""

    error: str = Field(..., description="Error message")
    message: str = Field(..., description="Detailed error description")
    field: str | None = Field(None, description="Field name if validation error")


class ErrorResponse(BaseModel):
    """Standard error response format with request tracking."""

    error: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Additional error context"
    )
    request_id: str = Field(..., description="Unique request identifier for tracing")


class SuccessResponse(BaseModel):
    """Standard success response format."""

    message: str = Field(..., description="Success message")
    data: dict[str, Any] | None = Field(None, description="Response data")
    request_id: str = Field(..., description="Unique request identifier for tracing")
