"""Template schemas for translation prompts.

This module defines Pydantic models for template management.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class TemplateVariable(BaseModel):
    """A variable definition for a template."""

    name: str = Field(..., description="Variable name (e.g., 'context', 'terminology')")
    description: str = Field(..., description="Description of the variable's purpose")


class Template(BaseModel):
    """A translation prompt template with variable substitution."""

    template_id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template description")
    prompt_template: str = Field(
        ..., description="Prompt template with Jinja2 placeholders"
    )
    variables: dict[str, str] = Field(
        default_factory=dict,
        description="Variable names mapped to their descriptions",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Template creation timestamp",
    )
    usage_count: int = Field(
        default=0, ge=0, description="Number of times template has been used"
    )


class CreateTemplateRequest(BaseModel):
    """Request to create a new template."""

    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str = Field(
        default="", max_length=500, description="Template description"
    )
    prompt_template: str = Field(
        ..., min_length=1, description="Prompt template with Jinja2 placeholders"
    )
    variables: dict[str, str] = Field(
        default_factory=dict,
        description="Variable names mapped to their descriptions",
    )


class RenderTemplateRequest(BaseModel):
    """Request to render a template with variables."""

    template_id: str = Field(..., description="Template identifier to render")
    variables: dict[str, str] = Field(
        default_factory=dict, description="Variable values for substitution"
    )


class RenderTemplateResponse(BaseModel):
    """Response containing rendered template."""

    rendered_prompt: str = Field(..., description="Rendered prompt with substitutions")
    template_id: str = Field(..., description="Template that was used")
    variables_used: dict[str, str] = Field(
        ..., description="Variables that were substituted"
    )
