"""Translation request and response schemas.

This module defines Pydantic models for translation API endpoints.
"""

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ContentBlock(BaseModel):
    """A single content block to be translated."""

    id: str = Field(..., description="Unique identifier for the content block")
    type: Literal["paragraph", "heading", "list", "quote", "code"] = Field(
        ..., description="Type of content block"
    )
    text: str = Field(..., min_length=1, description="Text content to translate")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional block metadata"
    )


class TranslationRequest(BaseModel):
    """Request model for translation endpoint."""

    content_blocks: list[ContentBlock] = Field(
        ..., min_length=1, description="Array of content blocks to translate"
    )
    target_language: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="Target language code (ISO 639-1)",
    )
    provider: str = Field(..., description="AI provider (e.g., openai, anthropic)")
    model: str = Field(..., description="Model identifier")
    api_key: str = Field(
        ..., min_length=1, description="User's API key for the provider"
    )

    @field_validator("target_language")
    @classmethod
    def validate_language_code(cls, v: str) -> str:
        """Validate language code format.

        Args:
            v: The language code to validate

        Returns:
            The validated language code in lowercase

        Raises:
            ValueError: If the language code is invalid
        """
        if not v.isalpha():
            raise ValueError("Language code must contain only letters")
        return v.lower()

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider name.

        Args:
            v: The provider name to validate

        Returns:
            The validated provider name in lowercase

        Raises:
            ValueError: If the provider is not supported
        """
        supported_providers = ["openai", "anthropic", "mock"]
        provider_lower = v.lower()
        if provider_lower not in supported_providers:
            raise ValueError(
                f"Provider must be one of: {', '.join(supported_providers)}"
            )
        return provider_lower


class TranslatedBlock(BaseModel):
    """A translated content block."""

    id: str = Field(..., description="Original block ID for matching")
    type: str = Field(..., description="Type of content block")
    text: str = Field(..., description="Translated text")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Translation metadata (provider, model, etc.)"
    )


class TranslationMetadata(BaseModel):
    """Metadata for translation response."""

    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Response timestamp"
    )
    processing_time: float = Field(..., description="Processing time in seconds", ge=0)


class TranslationResponse(BaseModel):
    """Response model for translation endpoint."""

    success: bool = Field(True, description="Whether the request was successful")
    data: dict[str, list[TranslatedBlock]] = Field(
        ..., description="Translation response data"
    )
    metadata: TranslationMetadata = Field(..., description="Response metadata")
