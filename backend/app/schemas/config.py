"""Config validation request and response schemas.

This module defines Pydantic models for config validation API endpoints.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ConfigValidationRequest(BaseModel):
    """Request model for config validation endpoint."""

    provider: str = Field(..., description="AI provider (e.g., openai, anthropic)")
    model: str = Field(..., description="Model identifier")
    api_key: str = Field(
        ..., min_length=1, description="User's API key for the provider"
    )

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


class ModelCapabilities(BaseModel):
    """Model capabilities information."""

    streaming: bool = Field(..., description="Whether model supports streaming")
    max_tokens: int = Field(..., description="Maximum tokens supported by model", ge=0)


class ConfigValidationResponse(BaseModel):
    """Response model for config validation endpoint."""

    valid: bool = Field(..., description="Whether the configuration is valid")
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model identifier")
    capabilities: ModelCapabilities = Field(..., description="Model capabilities")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Additional validation details"
    )
