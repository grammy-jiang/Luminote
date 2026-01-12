"""Translation versioning schemas.

This module defines Pydantic models for translation version management.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VersionMetadata(BaseModel):
    """Metadata for a translation version."""

    prompt: str | None = Field(None, description="Custom prompt used for translation")
    provider: str = Field(..., description="AI provider (e.g., openai, anthropic)")
    model: str = Field(..., description="Model identifier")
    target_language: str = Field(
        ..., min_length=2, max_length=2, description="Target language code (ISO 639-1)"
    )
    source_language: str | None = Field(
        None, min_length=2, max_length=2, description="Source language code (ISO 639-1)"
    )
    custom_instructions: str | None = Field(
        None, description="Custom user instructions for translation"
    )


class TranslatedBlock(BaseModel):
    """A translated content block."""

    id: str = Field(..., description="Unique identifier for the content block")
    type: str = Field(
        ..., description="Type of content block (paragraph, heading, etc.)"
    )
    original_text: str = Field(..., description="Original text before translation")
    translated_text: str = Field(..., description="Translated text")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional block metadata"
    )


class TranslationVersion(BaseModel):
    """A version of a translated document."""

    version_id: str = Field(..., description="Unique version identifier (UUID)")
    document_url: str = Field(..., description="URL of the original document")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Version creation timestamp",
    )
    blocks: list[TranslatedBlock] = Field(
        ..., description="List of translated content blocks"
    )
    metadata: VersionMetadata = Field(..., description="Translation metadata")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
