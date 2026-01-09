---
applyTo: backend/app/core/**/*.py
excludeAgent: []
---

# Backend Core Business Logic Instructions

This instruction file applies to all Python files in `backend/app/core/` - the
core business logic layer of Luminote.

## Critical Requirements

### Coverage Requirement: 95%+

Core business logic must maintain **≥95% test coverage**. This is strictly
enforced.

```bash
# Check coverage for core module
cd backend
uv run pytest --cov=app.core --cov-report=term-missing --cov-fail-under=95
```

### Architecture Principles

1. **No HTTP Dependencies**: Core modules must never import from `fastapi`,
   `starlette`, `httpx`, or any HTTP-related libraries. This layer is pure
   business logic.

1. **Pure Functions Preferred**: When possible, write pure functions without
   side effects. This makes testing easier and behavior more predictable.

1. **No External Service Calls**: Core logic should not make direct API calls or
   access external services. That belongs in the `services/` layer.

## Type Hints (Strict Mode)

All functions in core/ must have complete type annotations:

```python
from typing import Optional

# ✅ Good - complete type hints
def process_content(text: str, language: Optional[str] = None) -> dict[str, str]:
    """Process content and return structured result."""
    return {"processed": text, "language": language or "en"}

# ❌ Bad - missing type hints
def process_content(text, language=None):
    return {"processed": text, "language": language or "en"}
```

**Rules:**

- All parameters must have type annotations
- All return types must be annotated
- Use `Optional[T]` for nullable types (not `T | None` - for Python 3.12
  compatibility)
- Use `dict[str, Any]` instead of just `dict`
- Use `list[T]` instead of just `list`

## Error Handling

All exceptions in core/ must use the `LuminoteException` hierarchy defined in
`app/core/errors.py`:

```python
from app.core.errors import LuminoteException

# ✅ Good - custom exception with full context
raise LuminoteException(
    code="INVALID_CONTENT_FORMAT",
    message="Content format validation failed",
    status_code=400,
    details={
        "format": received_format,
        "supported_formats": ["html", "markdown", "plain"],
    },
)

# ❌ Bad - generic exception
raise ValueError("Invalid format")
```

**Exception structure:**

- `code`: Machine-readable error code (SCREAMING_SNAKE_CASE)
- `message`: Human-readable description
- `status_code`: HTTP status code (400 for validation, 500 for internal errors)
- `details`: Dictionary with additional context (optional)

## Testing Standards

### Test Structure

```python
import pytest
from app.core.your_module import your_function

@pytest.mark.unit
def test_your_function_success_case():
    """Test description in docstring."""
    # Arrange
    input_data = "test input"

    # Act
    result = your_function(input_data)

    # Assert
    assert result == expected_output

@pytest.mark.unit
def test_your_function_validation_error():
    """Test that validation errors are raised correctly."""
    with pytest.raises(LuminoteException) as exc_info:
        your_function(invalid_input)

    assert exc_info.value.code == "EXPECTED_ERROR_CODE"
```

### Test Markers

- `@pytest.mark.unit` - Fast tests with mocked dependencies
- `@pytest.mark.smoke` - Critical path tests (happy path only)
- `@pytest.mark.e2e` - Full workflow tests (use sparingly in core/)

### Coverage Requirements

- **Target**: ≥95% for all core/ modules
- **Focus on**: Branch coverage, not just line coverage
- **Test**: Success cases, error cases, edge cases, boundary conditions

## Code Style

### Imports

Use `isort` for import ordering:

```python
# Standard library
import json
from typing import Optional

# Third-party
from pydantic import BaseModel

# Local
from app.core.errors import LuminoteException
from app.schemas.translation import TranslationRequest
```

### Formatting

- Use `black` for code formatting (88 character line length)
- Use `ruff` for linting (no auto-fix - resolve issues manually)
- Run formatters before committing:
  ```bash
  cd backend
  uv run isort app/core/
  uv run black app/core/
  uv run ruff check app/core/ --no-fix
  ```

## Documentation

### Docstrings (Google Style)

```python
def transform_content(
    content: str,
    target_format: str,
    options: Optional[dict[str, Any]] = None,
) -> str:
    """Transform content to target format.

    Args:
        content: Input content to transform.
        target_format: Desired output format (html, markdown, plain).
        options: Optional transformation settings.

    Returns:
        Transformed content in target format.

    Raises:
        LuminoteException: If target_format is unsupported or content is invalid.

    Examples:
        >>> transform_content("<p>Hello</p>", "plain")
        'Hello'
    """
    pass
```

## What NOT to Do

❌ **Never:**

- Import from `app.api` or any HTTP layer
- Make network requests or API calls
- Access environment variables directly (use dependency injection)
- Log API keys, tokens, or user data
- Modify global state
- Use `print()` for debugging (use proper logging)
- Catch exceptions without re-raising or handling them properly

## Common Patterns

### Content Transformation

```python
from typing import Protocol

class ContentTransformer(Protocol):
    """Protocol for content transformation."""

    def transform(self, content: str) -> str:
        """Transform content."""
        ...

def apply_transformation(
    content: str,
    transformer: ContentTransformer,
) -> str:
    """Apply transformer to content with error handling."""
    try:
        result = transformer.transform(content)
        if not result:
            raise LuminoteException(
                code="EMPTY_TRANSFORMATION_RESULT",
                message="Transformation produced empty result",
                status_code=500,
            )
        return result
    except Exception as e:
        raise LuminoteException(
            code="TRANSFORMATION_FAILED",
            message=f"Content transformation failed: {str(e)}",
            status_code=500,
        ) from e
```

### Validation Functions

```python
def validate_language_code(language: str) -> None:
    """Validate language code format.

    Args:
        language: ISO 639-1 language code (e.g., 'en', 'es', 'fr').

    Raises:
        LuminoteException: If language code is invalid.
    """
    if not language or len(language) != 2:
        raise LuminoteException(
            code="INVALID_LANGUAGE_CODE",
            message="Language code must be 2-letter ISO 639-1 format",
            status_code=400,
            details={"provided": language},
        )

    if not language.isalpha() or not language.islower():
        raise LuminoteException(
            code="INVALID_LANGUAGE_CODE",
            message="Language code must be lowercase letters only",
            status_code=400,
            details={"provided": language},
        )
```

## Before Committing

Run this checklist:

```bash
cd backend

# Format code
uv run isort app/core/
uv run black app/core/

# Lint
uv run ruff check app/core/ --no-fix

# Type check
uv run mypy app/core/

# Test with coverage
uv run pytest tests/ --cov=app.core --cov-report=term-missing --cov-fail-under=95

# Run core-specific tests
uv run pytest tests/ -k "core" -v
```

All checks must pass before marking work complete.

## References

- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System architecture overview
- [ADR-004: Error Handling Patterns](../../docs/adr/004-error-handling-patterns.md)
  \- Exception handling standards
- [AGENTS.md](../../AGENTS.md) - General development guide
