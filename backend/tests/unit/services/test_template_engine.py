"""Tests for TemplateEngine."""

import pytest

from app.core.errors import LuminoteException
from app.services.template_engine import TemplateEngine


@pytest.mark.unit
def test_template_engine_initialization():
    """Test that template engine initializes with built-in templates."""
    engine = TemplateEngine()

    templates = engine.get_templates()
    assert len(templates) == 4

    # Verify built-in templates exist
    assert engine.get_template("professional") is not None
    assert engine.get_template("casual") is not None
    assert engine.get_template("academic") is not None
    assert engine.get_template("business") is not None


@pytest.mark.unit
def test_built_in_template_structure():
    """Test that built-in templates have proper structure."""
    engine = TemplateEngine()

    professional = engine.get_template("professional")
    assert professional is not None
    assert professional.name == "Professional"
    assert professional.description != ""
    assert professional.prompt_template != ""
    assert "target_language" in professional.variables
    assert "text" in professional.variables
    assert professional.usage_count == 0


@pytest.mark.unit
def test_create_template_success():
    """Test creating a custom template."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="Custom Template",
        description="A custom translation template",
        prompt_template="Translate {{ text }} to {{ target_language }}",
        variables={
            "text": "Text to translate",
            "target_language": "Target language",
        },
    )

    assert template.name == "Custom Template"
    assert template.description == "A custom translation template"
    assert template.template_id != ""
    assert template.usage_count == 0
    assert "text" in template.variables
    assert "target_language" in template.variables


@pytest.mark.unit
def test_create_template_with_jinja2_expressions():
    """Test creating a template with Jinja2 expressions."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="Advanced Template",
        description="Template with Jinja2 expressions",
        prompt_template="""
{% if context %}
Context: {{ context }}
{% endif %}
Translate: {{ text }}
{% for term in terms %}
- {{ term }}
{% endfor %}
""",
        variables={
            "text": "Text to translate",
            "context": "Optional context",
            "terms": "List of terms",
        },
    )

    assert template.name == "Advanced Template"
    assert "if context" in template.prompt_template
    assert "for term" in template.prompt_template


@pytest.mark.unit
def test_create_template_invalid_jinja2_syntax():
    """Test that invalid Jinja2 syntax raises exception."""
    engine = TemplateEngine()

    with pytest.raises(LuminoteException) as exc_info:
        engine.create_template(
            name="Invalid Template",
            description="Template with invalid syntax",
            prompt_template="Translate {{ text } to {{ target_language }}",  # Missing closing brace
            variables={},
        )

    assert exc_info.value.code == "INVALID_TEMPLATE_SYNTAX"
    assert exc_info.value.status_code == 400


@pytest.mark.unit
def test_get_templates_all():
    """Test getting all templates including built-in."""
    engine = TemplateEngine()

    # Create a custom template
    engine.create_template(
        name="Custom",
        prompt_template="Test {{ text }}",
        variables={"text": "Text"},
    )

    templates = engine.get_templates(include_built_in=True)
    assert len(templates) == 5  # 4 built-in + 1 custom


@pytest.mark.unit
def test_get_templates_custom_only():
    """Test getting only custom templates."""
    engine = TemplateEngine()

    # Create custom templates
    engine.create_template(
        name="Custom 1",
        prompt_template="Test {{ text }}",
        variables={"text": "Text"},
    )
    engine.create_template(
        name="Custom 2",
        prompt_template="Test {{ text }}",
        variables={"text": "Text"},
    )

    custom_templates = engine.get_templates(include_built_in=False)
    assert len(custom_templates) == 2

    # Verify they are custom templates
    custom_ids = {t.template_id for t in custom_templates}
    assert "professional" not in custom_ids
    assert "casual" not in custom_ids
    assert "academic" not in custom_ids
    assert "business" not in custom_ids


@pytest.mark.unit
def test_get_template_by_id():
    """Test getting a specific template by ID."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="Test Template",
        prompt_template="Test {{ text }}",
        variables={"text": "Text"},
    )

    retrieved = engine.get_template(template.template_id)
    assert retrieved is not None
    assert retrieved.template_id == template.template_id
    assert retrieved.name == "Test Template"


@pytest.mark.unit
def test_get_template_not_found():
    """Test getting a non-existent template returns None."""
    engine = TemplateEngine()

    result = engine.get_template("non-existent-id")
    assert result is None


@pytest.mark.unit
def test_delete_template_success():
    """Test deleting a custom template."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="To Delete",
        prompt_template="Test {{ text }}",
        variables={"text": "Text"},
    )

    # Verify it exists
    assert engine.get_template(template.template_id) is not None

    # Delete it
    result = engine.delete_template(template.template_id)
    assert result is True

    # Verify it's gone
    assert engine.get_template(template.template_id) is None


@pytest.mark.unit
def test_delete_template_not_found():
    """Test deleting a non-existent template returns False."""
    engine = TemplateEngine()

    result = engine.delete_template("non-existent-id")
    assert result is False


@pytest.mark.unit
def test_delete_built_in_template_fails():
    """Test that built-in templates cannot be deleted."""
    engine = TemplateEngine()

    with pytest.raises(LuminoteException) as exc_info:
        engine.delete_template("professional")

    assert exc_info.value.code == "CANNOT_DELETE_BUILT_IN_TEMPLATE"
    assert exc_info.value.status_code == 400

    # Verify template still exists
    assert engine.get_template("professional") is not None


@pytest.mark.unit
def test_render_template_simple():
    """Test rendering a simple template."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="Simple",
        prompt_template="Translate {{ text }} to {{ language }}",
        variables={"text": "Text", "language": "Language"},
    )

    rendered, vars_used = engine.render_template(
        template.template_id,
        {"text": "Hello world", "language": "Spanish"},
    )

    assert "Translate Hello world to Spanish" == rendered
    assert vars_used["text"] == "Hello world"
    assert vars_used["language"] == "Spanish"


@pytest.mark.unit
def test_render_template_with_conditionals():
    """Test rendering a template with Jinja2 conditionals."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="Conditional",
        prompt_template="""Translate {{ text }}
{% if context %}
Context: {{ context }}
{% endif %}""",
        variables={"text": "Text", "context": "Context"},
    )

    # Render with context
    rendered, _ = engine.render_template(
        template.template_id,
        {"text": "Hello", "context": "Greeting"},
    )
    assert "Context: Greeting" in rendered

    # Render without context
    rendered, _ = engine.render_template(
        template.template_id,
        {"text": "Hello"},
    )
    assert "Context:" not in rendered


@pytest.mark.unit
def test_render_template_missing_variables():
    """Test that missing variables are handled gracefully."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="With Optional",
        prompt_template="""Translate {{ text }}
{% if context %}Context: {{ context }}{% endif %}
{% if style %}Style: {{ style }}{% endif %}""",
        variables={
            "text": "Text to translate",
            "context": "Optional context",
            "style": "Optional style",
        },
    )

    # Render with only text (missing context and style)
    rendered, vars_used = engine.render_template(
        template.template_id,
        {"text": "Hello world"},
    )

    assert "Translate Hello world" in rendered
    assert "Context:" not in rendered
    assert "Style:" not in rendered
    assert vars_used["text"] == "Hello world"
    assert vars_used["context"] == ""  # Default empty string
    assert vars_used["style"] == ""  # Default empty string


@pytest.mark.unit
def test_render_template_not_found():
    """Test rendering a non-existent template raises exception."""
    engine = TemplateEngine()

    with pytest.raises(LuminoteException) as exc_info:
        engine.render_template("non-existent", {"text": "test"})

    assert exc_info.value.code == "TEMPLATE_NOT_FOUND"
    assert exc_info.value.status_code == 404


@pytest.mark.unit
def test_render_built_in_professional_template():
    """Test rendering the built-in professional template."""
    engine = TemplateEngine()

    rendered, vars_used = engine.render_template(
        "professional",
        {
            "target_language": "Spanish",
            "text": "Hello world",
            "context": "Formal greeting",
            "terminology": "Use 'Hola' for hello",
        },
    )

    assert "Spanish" in rendered
    assert "Hello world" in rendered
    assert "Formal greeting" in rendered
    assert "Use 'Hola' for hello" in rendered
    assert "professional" in rendered.lower() or "Professional" in rendered


@pytest.mark.unit
def test_render_built_in_casual_template():
    """Test rendering the built-in casual template."""
    engine = TemplateEngine()

    rendered, vars_used = engine.render_template(
        "casual",
        {
            "target_language": "French",
            "text": "Hey there!",
        },
    )

    assert "French" in rendered
    assert "Hey there!" in rendered
    assert "casual" in rendered.lower() or "conversational" in rendered.lower()


@pytest.mark.unit
def test_render_built_in_academic_template():
    """Test rendering the built-in academic template."""
    engine = TemplateEngine()

    rendered, vars_used = engine.render_template(
        "academic",
        {
            "target_language": "German",
            "text": "The hypothesis is supported by evidence.",
            "terminology": "Use formal academic terms",
        },
    )

    assert "German" in rendered
    assert "hypothesis" in rendered
    assert "academic" in rendered.lower() or "scholarly" in rendered.lower()


@pytest.mark.unit
def test_render_built_in_business_template():
    """Test rendering the built-in business template."""
    engine = TemplateEngine()

    rendered, vars_used = engine.render_template(
        "business",
        {
            "target_language": "Japanese",
            "text": "Please review the quarterly report.",
        },
    )

    assert "Japanese" in rendered
    assert "quarterly report" in rendered
    assert "business" in rendered.lower() or "corporate" in rendered.lower()


@pytest.mark.unit
def test_usage_count_tracking():
    """Test that usage count is incremented on each render."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="Usage Test",
        prompt_template="Test {{ text }}",
        variables={"text": "Text"},
    )

    # Initial usage count
    assert template.usage_count == 0

    # Render once
    engine.render_template(template.template_id, {"text": "Test 1"})
    assert template.usage_count == 1

    # Render again
    engine.render_template(template.template_id, {"text": "Test 2"})
    assert template.usage_count == 2

    # Render third time
    engine.render_template(template.template_id, {"text": "Test 3"})
    assert template.usage_count == 3


@pytest.mark.unit
def test_render_with_extra_variables():
    """Test rendering with extra variables not in template definition."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="Extra Vars",
        prompt_template="Text: {{ text }}, Extra: {{ extra }}",
        variables={"text": "Required text"},
    )

    # Render with extra variable not in template.variables
    rendered, vars_used = engine.render_template(
        template.template_id,
        {"text": "Hello", "extra": "Additional"},
    )

    assert "Text: Hello, Extra: Additional" == rendered
    assert vars_used["text"] == "Hello"
    assert vars_used["extra"] == "Additional"


@pytest.mark.unit
def test_render_template_multiple_variables():
    """Integration test: render with multiple variables."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="Multi-var Template",
        prompt_template="""Translate the following to {{ target_language }}:

Text: {{ text }}
{% if context %}
Context: {{ context }}
{% endif %}
{% if terminology %}
Terminology: {{ terminology }}
{% endif %}
{% if style %}
Style: {{ style }}
{% endif %}

Please provide an accurate translation.""",
        variables={
            "target_language": "Target language code",
            "text": "Text to translate",
            "context": "Additional context",
            "terminology": "Specific terms to use",
            "style": "Style requirements",
        },
    )

    rendered, vars_used = engine.render_template(
        template.template_id,
        {
            "target_language": "Spanish",
            "text": "Welcome to our application",
            "context": "Mobile app onboarding",
            "terminology": "Use 'aplicación' for application",
            "style": "Friendly and welcoming",
        },
    )

    assert "Spanish" in rendered
    assert "Welcome to our application" in rendered
    assert "Mobile app onboarding" in rendered
    assert "aplicación" in rendered
    assert "Friendly and welcoming" in rendered


@pytest.mark.unit
def test_all_built_in_templates_present():
    """Test that all 4 built-in templates are present and valid."""
    engine = TemplateEngine()

    required_templates = ["professional", "casual", "academic", "business"]

    for template_id in required_templates:
        template = engine.get_template(template_id)
        assert template is not None, f"Built-in template {template_id} not found"
        assert template.name != ""
        assert template.description != ""
        assert template.prompt_template != ""
        assert len(template.variables) > 0
        assert "target_language" in template.variables
        assert "text" in template.variables


@pytest.mark.unit
def test_template_creation_with_empty_variables():
    """Test creating a template with empty variables dict."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="No Vars",
        prompt_template="Static prompt with no variables",
        variables={},
    )

    assert template.name == "No Vars"
    assert len(template.variables) == 0

    # Should still be renderable
    rendered, vars_used = engine.render_template(template.template_id, {})
    assert rendered == "Static prompt with no variables"


@pytest.mark.unit
def test_render_template_with_complex_jinja2():
    """Test rendering template with complex Jinja2 expressions."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="Complex",
        prompt_template="""
{% for item in items.split(',') %}
- {{ item.strip() }}
{% endfor %}
Total count: {{ items.split(',') | length }}
""",
        variables={"items": "Comma-separated list"},
    )

    rendered, _ = engine.render_template(
        template.template_id,
        {"items": "apple, banana, cherry"},
    )

    assert "- apple" in rendered
    assert "- banana" in rendered
    assert "- cherry" in rendered
    assert "Total count: 3" in rendered


@pytest.mark.unit
def test_render_template_with_filters():
    """Test rendering template with Jinja2 filters."""
    engine = TemplateEngine()

    template = engine.create_template(
        name="With Filters",
        prompt_template="Uppercase: {{ text | upper }}, Length: {{ text | length }}",
        variables={"text": "Text to transform"},
    )

    rendered, _ = engine.render_template(
        template.template_id,
        {"text": "hello world"},
    )

    assert "Uppercase: HELLO WORLD" in rendered
    assert "Length: 11" in rendered


@pytest.mark.unit
def test_render_template_error_handling():
    """Test that template rendering errors are caught and handled."""
    from unittest.mock import patch

    engine = TemplateEngine()

    template = engine.create_template(
        name="Error Test",
        prompt_template="Test {{ text }}",
        variables={"text": "Test text"},
    )

    # Test TemplateError handling by mocking render to raise exception
    with patch.object(engine._jinja_env, "from_string") as mock_from_string:
        from jinja2.exceptions import TemplateError

        mock_template = mock_from_string.return_value
        mock_template.render.side_effect = TemplateError("Rendering failed")

        with pytest.raises(LuminoteException) as exc_info:
            engine.render_template(template.template_id, {"text": "test"})

        assert exc_info.value.code == "TEMPLATE_RENDERING_FAILED"
        assert exc_info.value.status_code == 500
