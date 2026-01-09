---
applyTo: backend/app/services/**/*.py
excludeAgent: []
---

# Backend Services Layer Instructions

This instruction file applies to all Python files in `backend/app/services/` -
the external integrations and AI provider layer.

## Layer Responsibilities

The services layer handles:

- ✅ AI provider integrations (OpenAI, Anthropic, etc.)
- ✅ External API calls
- ✅ Provider-agnostic interfaces
- ✅ Error mapping from providers to `LuminoteException`

The services layer should **NOT**:

- ❌ Contain HTTP request handling (belongs in `app/api/`)
- ❌ Contain business logic (belongs in `app/core/`)
- ❌ Log or expose API keys

## Critical Security Rules

### API Key Handling

**NEVER log, expose, or leak API keys:**

```python
# ✅ Good - no API key in logs
logger.info("Calling translation provider", extra={"provider": "openai"})

# ❌ Bad - exposes API key
logger.info(f"Calling OpenAI with key: {api_key}")

# ❌ Bad - API key in error message
raise Exception(f"API call failed with key {api_key}")
```

### Validation Before Calls

Always validate API keys before making requests:

```python
def validate_api_key(api_key: str, provider: str) -> None:
    """Validate API key format before making calls.

    Args:
        api_key: The API key to validate.
        provider: Provider name (openai, anthropic, etc.).

    Raises:
        LuminoteException: If API key format is invalid.
    """
    if not api_key:
        raise LuminoteException(
            code="MISSING_API_KEY",
            message=f"API key required for {provider}",
            status_code=400,
        )

    # Check format without logging the key
    if provider == "openai" and not api_key.startswith("sk-"):
        raise LuminoteException(
            code="INVALID_API_KEY_FORMAT",
            message="OpenAI API key must start with 'sk-'",
            status_code=400,
        )
```

### BYOK (Bring Your Own Key)

Users provide their own API keys. **Never store keys server-side:**

```python
# ✅ Good - key passed per request
async def translate(
    content: str,
    target_language: str,
    api_key: str,  # User-provided
    provider: str = "openai",
) -> str:
    validate_api_key(api_key, provider)
    # Use api_key for this request only
    pass

# ❌ Bad - storing user keys
class TranslationService:
    def __init__(self, api_key: str):
        self.api_key = api_key  # Never store user keys
```

## Provider-Agnostic Interfaces

Create abstractions so the app isn't tied to specific providers:

```python
from typing import Protocol, AsyncIterator
from pydantic import BaseModel

class TranslationResult(BaseModel):
    """Standard translation result across all providers."""
    translated_text: str
    source_language: str
    target_language: str
    provider: str
    model: str

class TranslationProvider(Protocol):
    """Protocol for translation providers."""

    async def translate(
        self,
        content: str,
        target_language: str,
        api_key: str,
    ) -> TranslationResult:
        """Translate content to target language."""
        ...

    async def translate_stream(
        self,
        content: str,
        target_language: str,
        api_key: str,
    ) -> AsyncIterator[TranslationResult]:
        """Stream translation results."""
        ...
```

## Error Mapping

Map provider-specific errors to `LuminoteException`:

```python
import httpx
from app.core.errors import LuminoteException

async def call_openai_api(
    prompt: str,
    api_key: str,
    model: str = "gpt-4",
) -> dict:
    """Call OpenAI API with proper error handling."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        # Map OpenAI errors to LuminoteException
        status_code = e.response.status_code

        if status_code == 401:
            raise LuminoteException(
                code="INVALID_API_KEY",
                message="Invalid or expired API key",
                status_code=401,
            ) from e
        elif status_code == 429:
            raise LuminoteException(
                code="RATE_LIMIT_EXCEEDED",
                message="API rate limit exceeded",
                status_code=429,
            ) from e
        elif status_code >= 500:
            raise LuminoteException(
                code="PROVIDER_ERROR",
                message="AI provider service error",
                status_code=502,
            ) from e
        else:
            raise LuminoteException(
                code="TRANSLATION_FAILED",
                message=f"Translation failed: {e.response.text}",
                status_code=status_code,
            ) from e

    except httpx.TimeoutException as e:
        raise LuminoteException(
            code="PROVIDER_TIMEOUT",
            message="AI provider request timed out",
            status_code=504,
        ) from e

    except Exception as e:
        raise LuminoteException(
            code="UNKNOWN_ERROR",
            message=f"Unexpected error: {str(e)}",
            status_code=500,
        ) from e
```

## Streaming Responses

For streaming endpoints, use async generators:

```python
from typing import AsyncIterator

async def translate_stream(
    content_blocks: list[dict],
    target_language: str,
    api_key: str,
    provider: str = "openai",
) -> AsyncIterator[dict]:
    """Stream translation results for multiple content blocks.

    Yields:
        Translation events in SSE format:
        - {"type": "translation", "block_id": "1", "text": "..."}
        - {"type": "done"}
        - {"type": "error", "message": "..."}
    """
    try:
        for block in content_blocks:
            # Translate each block
            result = await translate_block(
                content=block["text"],
                target_language=target_language,
                api_key=api_key,
                provider=provider,
            )

            # Yield translation event
            yield {
                "type": "translation",
                "block_id": block["id"],
                "text": result.translated_text,
            }

        # Yield completion event
        yield {"type": "done"}

    except LuminoteException as e:
        # Yield error event
        yield {
            "type": "error",
            "code": e.code,
            "message": e.message,
        }
```

## Testing Services

### Mock External Calls

**Always mock external API calls** in tests:

```python
import pytest
from unittest.mock import AsyncMock, patch
from httpx import Response

@pytest.mark.unit
async def test_translate_success():
    """Test successful translation with mocked API call."""
    # Mock httpx.AsyncClient
    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response
        mock_response = Response(
            status_code=200,
            json={
                "choices": [{
                    "message": {"content": "Hola mundo"}
                }]
            },
        )
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Call service
        result = await translate(
            content="Hello world",
            target_language="es",
            api_key="test-key",
        )

        # Assert
        assert result.translated_text == "Hola mundo"

@pytest.mark.unit
async def test_translate_invalid_api_key():
    """Test error handling for invalid API key."""
    with patch("httpx.AsyncClient") as mock_client:
        # Setup 401 error
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                message="Unauthorized",
                request=...,
                response=Response(status_code=401),
            )
        )

        # Assert exception is raised and mapped correctly
        with pytest.raises(LuminoteException) as exc_info:
            await translate(
                content="Hello",
                target_language="es",
                api_key="invalid-key",
            )

        assert exc_info.value.code == "INVALID_API_KEY"
        assert exc_info.value.status_code == 401
```

### No Real API Calls

```python
# ✅ Good - mocked
@pytest.mark.unit
async def test_with_mock():
    with patch("httpx.AsyncClient"):
        result = await translate(...)

# ❌ Bad - real API call
@pytest.mark.unit
async def test_without_mock():
    result = await translate(
        content="test",
        api_key=os.getenv("OPENAI_API_KEY"),  # Real key!
    )
```

## Configuration

Use settings for provider configuration:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Provider defaults
    DEFAULT_TRANSLATION_PROVIDER: str = "openai"
    DEFAULT_TRANSLATION_MODEL: str = "gpt-4"

    # Timeouts
    PROVIDER_TIMEOUT_SECONDS: int = 30

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
```

## Code Quality

### Coverage Requirement

Services layer requires **≥85% test coverage**:

```bash
cd backend
uv run pytest --cov=app.services --cov-report=term-missing --cov-fail-under=85
```

### Type Hints

All service functions must have complete type annotations:

```python
from typing import Optional

# ✅ Good
async def translate(
    content: str,
    target_language: str,
    api_key: str,
    model: Optional[str] = None,
) -> TranslationResult:
    pass
```

## What NOT to Do

❌ **Never:**

- Log API keys, tokens, or authentication headers
- Store user API keys (always pass per-request)
- Make real API calls in tests (always mock)
- Return provider-specific error messages directly (map to LuminoteException)
- Skip validation of API keys
- Expose provider implementation details to API layer
- Use global/shared HTTP clients with stored credentials

## Before Committing

Run this checklist:

```bash
cd backend

# Format code
uv run isort app/services/
uv run black app/services/

# Lint
uv run ruff check app/services/ --no-fix

# Type check
uv run mypy app/services/

# Test with coverage
uv run pytest tests/ --cov=app.services --cov-report=term-missing --cov-fail-under=85

# Run service-specific tests
uv run pytest tests/services/ -v
```

## References

- [ARCHITECTURE.md](../../ARCHITECTURE.md) - BYOK principle
- [ADR-004: Error Handling Patterns](../../docs/adr/004-error-handling-patterns.md)
- [AGENTS.md](../../AGENTS.md) - Security boundaries
