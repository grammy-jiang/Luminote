"""Content extraction schemas.

This module defines Pydantic models for content extraction.
"""

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ContentBlock(BaseModel):
    """A single content block extracted from a document.

    This is the extraction version that supports image blocks. For translation, the type
    must be one of the non-image types.
    """

    id: str = Field(..., description="Unique identifier for the content block")
    type: Literal["paragraph", "heading", "list", "quote", "code", "image"] = Field(
        ..., description="Type of content block"
    )
    text: str = Field(default="", description="Text content of the block")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional block metadata"
    )


class ExtractedContent(BaseModel):
    """Extracted and structured content from a URL."""

    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Document title")
    author: str | None = Field(None, description="Author name if available")
    date_published: str | None = Field(
        None, description="Publication date if available"
    )
    content_blocks: list[ContentBlock] = Field(
        ..., description="List of structured content blocks"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional extraction metadata"
    )
    extraction_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when extraction occurred",
    )


class ExtractionRequest(BaseModel):
    """Request model for content extraction."""

    url: str = Field(
        ...,
        description="URL to extract content from",
        min_length=1,
        examples=["https://example.com/article"],
    )


class ExtractionMetadata(BaseModel):
    """Metadata for extraction response."""

    request_id: str = Field(..., description="Unique request identifier for tracing")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Response timestamp",
    )
    processing_time: float = Field(
        ..., description="Processing time in seconds", ge=0.0
    )


class ExtractionResponseData(BaseModel):
    """Data payload for extraction response."""

    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Document title")
    author: str | None = Field(None, description="Author name if available")
    date_published: str | None = Field(
        None, description="Publication date if available"
    )
    content_blocks: list[ContentBlock] = Field(
        ..., description="List of structured content blocks"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional extraction metadata"
    )


class ExtractionResponse(BaseModel):
    """Response model for content extraction following ADR-001 envelope."""

    success: bool = Field(True, description="Indicates if the request was successful")
    data: ExtractionResponseData = Field(..., description="Extraction result data")
    metadata: ExtractionMetadata = Field(..., description="Response metadata")
