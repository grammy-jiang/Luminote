"""Template engine for translation prompts with variable substitution.

This service manages translation prompt templates with Jinja2-based variable
substitution, supporting CRUD operations and built-in templates.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from jinja2 import Environment, StrictUndefined
from jinja2.exceptions import TemplateError, UndefinedError

from app.core.errors import LuminoteException
from app.schemas.templates import Template


class TemplateEngine:
    """Template engine for managing and rendering translation prompts.

    This service provides:
    - CRUD operations for custom templates
    - Built-in templates (Professional, Casual, Academic, Business)
    - Jinja2-based variable substitution
    - Usage tracking
    - Graceful handling of missing variables
    """

    # Built-in templates
    BUILT_IN_TEMPLATES: dict[str, Template] = {}

    def __init__(self) -> None:
        """Initialize template engine with built-in templates."""
        self._templates: dict[str, Template] = {}
        self._jinja_env = Environment(undefined=StrictUndefined)
        self._initialize_built_in_templates()

    def _initialize_built_in_templates(self) -> None:
        """Initialize built-in templates."""
        built_in_defs: list[dict[str, Any]] = [
            {
                "template_id": "professional",
                "name": "Professional",
                "description": "Professional translation with formal tone and precise terminology",
                "prompt_template": """Translate the following text to {{ target_language }} using a professional tone.

{% if context %}Context: {{ context }}
{% endif %}
{% if terminology %}Terminology to use: {{ terminology }}
{% endif %}
{% if style %}Style requirements: {{ style }}
{% endif %}

Text to translate:
{{ text }}

Provide a professional, accurate translation maintaining the formal tone.""",
                "variables": {
                    "target_language": "Target language for translation",
                    "text": "Text to translate",
                    "context": "(Optional) Additional context about the content",
                    "terminology": "(Optional) Specific terminology to use",
                    "style": "(Optional) Additional style requirements",
                },
            },
            {
                "template_id": "casual",
                "name": "Casual",
                "description": "Casual translation with conversational tone",
                "prompt_template": """Translate the following text to {{ target_language }} using a casual, conversational tone.

{% if context %}Context: {{ context }}
{% endif %}
{% if terminology %}Key terms: {{ terminology }}
{% endif %}
{% if style %}Style notes: {{ style }}
{% endif %}

Text to translate:
{{ text }}

Make the translation sound natural and conversational.""",
                "variables": {
                    "target_language": "Target language for translation",
                    "text": "Text to translate",
                    "context": "(Optional) Additional context about the content",
                    "terminology": "(Optional) Key terms to include",
                    "style": "(Optional) Additional style notes",
                },
            },
            {
                "template_id": "academic",
                "name": "Academic",
                "description": "Academic translation with scholarly tone and precise terminology",
                "prompt_template": """Translate the following text to {{ target_language }} using an academic tone suitable for scholarly work.

{% if context %}Academic context: {{ context }}
{% endif %}
{% if terminology %}Technical terminology: {{ terminology }}
{% endif %}
{% if style %}Style requirements: {{ style }}
{% endif %}

Text to translate:
{{ text }}

Provide an accurate, scholarly translation with appropriate academic terminology and formal register.""",
                "variables": {
                    "target_language": "Target language for translation",
                    "text": "Text to translate",
                    "context": "(Optional) Academic or scholarly context",
                    "terminology": "(Optional) Technical or domain-specific terminology",
                    "style": "(Optional) Additional academic style requirements",
                },
            },
            {
                "template_id": "business",
                "name": "Business",
                "description": "Business translation with professional corporate tone",
                "prompt_template": """Translate the following text to {{ target_language }} using a business-appropriate tone.

{% if context %}Business context: {{ context }}
{% endif %}
{% if terminology %}Business terminology: {{ terminology }}
{% endif %}
{% if style %}Corporate style requirements: {{ style }}
{% endif %}

Text to translate:
{{ text }}

Provide a business-appropriate translation suitable for corporate communications.""",
                "variables": {
                    "target_language": "Target language for translation",
                    "text": "Text to translate",
                    "context": "(Optional) Business or corporate context",
                    "terminology": "(Optional) Business-specific terminology",
                    "style": "(Optional) Corporate style requirements",
                },
            },
        ]

        for template_def in built_in_defs:
            template = Template(
                template_id=template_def["template_id"],
                name=template_def["name"],
                description=template_def["description"],
                prompt_template=template_def["prompt_template"],
                variables=template_def["variables"],
                created_at=datetime.now(UTC),
                usage_count=0,
            )
            self.BUILT_IN_TEMPLATES[template.template_id] = template
            self._templates[template.template_id] = template

    def create_template(
        self,
        name: str,
        prompt_template: str,
        variables: dict[str, str],
        description: str = "",
    ) -> Template:
        """Create a new custom template.

        Args:
            name: Template name
            prompt_template: Jinja2 template string
            variables: Variable names mapped to descriptions
            description: Template description

        Returns:
            Created template

        Raises:
            LuminoteException: If template creation fails
        """
        # Validate Jinja2 syntax
        try:
            self._jinja_env.from_string(prompt_template)
        except TemplateError as e:
            raise LuminoteException(
                message=f"Invalid Jinja2 template syntax: {str(e)}",
                code="INVALID_TEMPLATE_SYNTAX",
                status_code=400,
                details={"syntax_error": str(e)},
            ) from e

        # Generate unique ID
        template_id = str(uuid.uuid4())

        # Create template
        template = Template(
            template_id=template_id,
            name=name,
            description=description,
            prompt_template=prompt_template,
            variables=variables,
            created_at=datetime.now(UTC),
            usage_count=0,
        )

        self._templates[template_id] = template
        return template

    def get_templates(self, include_built_in: bool = True) -> list[Template]:
        """Get all templates.

        Args:
            include_built_in: Whether to include built-in templates

        Returns:
            List of all templates
        """
        if include_built_in:
            return list(self._templates.values())
        else:
            # Return only custom templates (exclude built-in)
            return [
                t
                for t in self._templates.values()
                if t.template_id not in self.BUILT_IN_TEMPLATES
            ]

    def get_template(self, template_id: str) -> Template | None:
        """Get a specific template by ID.

        Args:
            template_id: Template identifier

        Returns:
            Template if found, None otherwise
        """
        return self._templates.get(template_id)

    def delete_template(self, template_id: str) -> bool:
        """Delete a custom template.

        Built-in templates cannot be deleted.

        Args:
            template_id: Template identifier to delete

        Returns:
            True if deleted, False if not found

        Raises:
            LuminoteException: If attempting to delete a built-in template
        """
        # Prevent deletion of built-in templates
        if template_id in self.BUILT_IN_TEMPLATES:
            raise LuminoteException(
                message=f"Cannot delete built-in template: {template_id}",
                code="CANNOT_DELETE_BUILT_IN_TEMPLATE",
                status_code=400,
                details={"template_id": template_id},
            )

        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False

    def render_template(
        self, template_id: str, variables: dict[str, str]
    ) -> tuple[str, dict[str, str]]:
        """Render a template with variable substitution.

        Handles missing variables gracefully by replacing them with empty strings.

        Args:
            template_id: Template identifier to render
            variables: Variable values for substitution

        Returns:
            Tuple of (rendered_prompt, variables_used)

        Raises:
            LuminoteException: If template not found or rendering fails
        """
        # Get template
        template = self.get_template(template_id)
        if template is None:
            raise LuminoteException(
                message=f"Template not found: {template_id}",
                code="TEMPLATE_NOT_FOUND",
                status_code=404,
                details={"template_id": template_id},
            )

        # Create a copy of variables with defaults for missing ones
        render_vars = {}
        for var_name in template.variables.keys():
            render_vars[var_name] = variables.get(var_name, "")

        # Also include any extra variables provided
        for var_name, var_value in variables.items():
            if var_name not in render_vars:
                render_vars[var_name] = var_value

        # Render template with Jinja2
        try:
            jinja_template = self._jinja_env.from_string(template.prompt_template)
            rendered = jinja_template.render(**render_vars)
        except UndefinedError as e:
            # This shouldn't happen due to our default value handling above,
            # but catch it just in case
            raise LuminoteException(
                message=f"Undefined variable in template: {str(e)}",
                code="UNDEFINED_TEMPLATE_VARIABLE",
                status_code=400,
                details={"error": str(e)},
            ) from e
        except TemplateError as e:
            raise LuminoteException(
                message=f"Template rendering failed: {str(e)}",
                code="TEMPLATE_RENDERING_FAILED",
                status_code=500,
                details={"error": str(e)},
            ) from e

        # Increment usage count
        template.usage_count += 1

        return rendered, render_vars
