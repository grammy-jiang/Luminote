---
applyTo: '**/tests/**/*.py'
excludeAgent: []
---

# Test Files Instructions

This instruction file applies to all Python test files in `tests/` directories -
the test suite for backend code.

## Testing Philosophy

Tests are first-class code that:

- Document expected behavior
- Enable confident refactoring
- Catch regressions early
- Serve as usage examples

**Quality matters**: Write tests you'd want to maintain.

## Test Markers

Use pytest markers to categorize tests (defined in `pyproject.toml`):

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    """Fast test with mocked dependencies."""
    pass

@pytest.mark.smoke
def test_critical_path():
    """Critical path verification (happy path only)."""
    pass

@pytest.mark.e2e
def test_full_workflow():
    """End-to-end test with (mocked) external services."""
    pass
```

**Run specific markers:**

```bash
cd backend

# Run only unit tests (fast)
uv run pytest -m unit

# Run smoke tests (critical paths)
uv run pytest -m smoke

# Run end-to-end tests
uv run pytest -m e2e
```

## Test Structure

### Arrange-Act-Assert Pattern

```python
@pytest.mark.unit
def test_content_transformation():
    """Test content transformation with valid input."""
    # Arrange - set up test data
    input_content = "<p>Hello world</p>"
    expected_output = "Hello world"

    # Act - execute the code under test
    result = transform_html_to_text(input_content)

    # Assert - verify the outcome
    assert result == expected_output
```

### Descriptive Names

Test names should describe **what** is being tested and **what** should happen:

```python
# ✅ Good - clear intent
def test_translation_request_validation_fails_for_empty_content():
    pass

def test_translation_service_raises_exception_for_invalid_api_key():
    pass

# ❌ Bad - unclear
def test_translation():
    pass

def test_validate():
    pass
```

### Docstrings

Add docstrings to explain **why** the test exists:

```python
@pytest.mark.unit
def test_language_code_validation_rejects_three_letter_codes():
    """Test that language validation rejects ISO 639-2 codes.

    We only support ISO 639-1 (2-letter codes) to keep the API simple
    and consistent. This test ensures we reject longer formats.
    """
    with pytest.raises(LuminoteException) as exc_info:
        validate_language_code("eng")  # ISO 639-2

    assert exc_info.value.code == "INVALID_LANGUAGE_CODE"
```

## Mocking External Services

### Always Mock External Calls

**Never make real API calls** in tests:

```python
import pytest
from unittest.mock import AsyncMock, patch
import httpx

@pytest.mark.unit
async def test_openai_translation_success():
    """Test successful OpenAI translation with mocked API."""
    # Mock the HTTP client
    with patch("httpx.AsyncClient") as mock_client:
        # Set up mock response
        mock_response = httpx.Response(
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

        # Call the service
        result = await translate_with_openai(
            content="Hello world",
            target_language="es",
            api_key="test-key",
        )

        # Verify result
        assert result.translated_text == "Hola mundo"
```

### httpx_mock for HTTP Calls

Use `httpx_mock` fixture for cleaner HTTP mocking:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.unit
async def test_api_call_with_httpx_mock(httpx_mock):
    """Test API call using httpx_mock fixture."""
    # Register mock response
    httpx_mock.add_response(
        method="POST",
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{"message": {"content": "Translated text"}}]
        },
    )

    # Make the call
    async with AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json={"prompt": "test"},
        )

    assert response.status_code == 200
```

## Testing FastAPI Endpoints

### Use TestClient Fixture

The `client` fixture is defined in `conftest.py`:

```python
from fastapi.testclient import TestClient

@pytest.mark.unit
def test_health_check_endpoint(client: TestClient):
    """Test health check returns 200."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.unit
def test_translation_endpoint_validation(client: TestClient):
    """Test translation endpoint validates request data."""
    # Invalid request - missing required fields
    response = client.post(
        "/api/v1/translations",
        json={"content": ""},  # Empty content - invalid
    )

    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()
```

### Testing Error Responses

```python
@pytest.mark.unit
def test_translation_endpoint_handles_invalid_language(client: TestClient):
    """Test error handling for invalid language code."""
    response = client.post(
        "/api/v1/translations",
        json={
            "content": "Hello world",
            "target_language": "xxx",  # Invalid code
            "provider": "openai",
        },
    )

    assert response.status_code == 400
    error_data = response.json()
    assert error_data["code"] == "INVALID_LANGUAGE"
    assert "request_id" in error_data
```

## Fixtures

### Reusable Test Data

Define fixtures in `conftest.py`:

```python
import pytest

@pytest.fixture
def sample_translation_request():
    """Sample translation request for testing."""
    return {
        "content": "Hello world",
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
    }

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [{
            "message": {
                "content": "Hola mundo"
            }
        }],
        "model": "gpt-4",
    }
```

**Use in tests:**

```python
@pytest.mark.unit
def test_with_fixtures(sample_translation_request, mock_openai_response):
    """Test using fixtures."""
    assert sample_translation_request["content"] == "Hello world"
    assert mock_openai_response["choices"][0]["message"]["content"] == "Hola mundo"
```

### Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default - new instance per test
def temp_data():
    return {"value": 1}

@pytest.fixture(scope="module")  # Shared across module
def expensive_setup():
    # Expensive operation
    return setup_data()

@pytest.fixture(scope="session")  # Shared across entire test session
def global_config():
    return load_config()
```

## Coverage Requirements

### Overall Coverage

- **Core modules** (`app/core/`): **≥95%**
- **API layer** (`app/api/`): **≥85%**
- **Services layer** (`app/services/`): **≥85%**

### Check Coverage

```bash
cd backend

# Run with coverage report
uv run pytest --cov=app --cov-report=term-missing

# HTML coverage report (open in browser)
uv run pytest --cov=app --cov-report=html
# Open backend/htmlcov/index.html

# Fail if coverage is below threshold
uv run pytest --cov=app --cov-fail-under=85
```

### Focus on Branch Coverage

```python
# ✅ Good - test both branches
def test_validation_success():
    """Test validation with valid input."""
    result = validate(valid_input)
    assert result is True

def test_validation_failure():
    """Test validation with invalid input."""
    result = validate(invalid_input)
    assert result is False

# ❌ Bad - only one branch tested
def test_validation():
    result = validate(valid_input)
    assert result is True
    # Missing: invalid input test
```

## Parametrized Tests

Use `@pytest.mark.parametrize` for multiple similar test cases:

```python
import pytest

@pytest.mark.parametrize(
    "language_code,expected_valid",
    [
        ("en", True),
        ("es", True),
        ("fr", True),
        ("", False),
        ("eng", False),  # 3 letters - invalid
        ("E", False),    # 1 letter - invalid
        ("EN", False),   # uppercase - invalid
        ("e1", False),   # contains digit - invalid
    ],
)
@pytest.mark.unit
def test_language_code_validation(language_code, expected_valid):
    """Test language code validation with various inputs."""
    if expected_valid:
        # Should not raise
        validate_language_code(language_code)
    else:
        # Should raise
        with pytest.raises(LuminoteException):
            validate_language_code(language_code)
```

## Async Tests

Mark async tests with `@pytest.mark.asyncio`:

```python
import pytest

@pytest.mark.asyncio
@pytest.mark.unit
async def test_async_translation():
    """Test async translation function."""
    result = await translate_async(
        content="Hello",
        target_language="es",
    )
    assert result is not None
```

## Testing Exceptions

### Verify Exception Type and Message

```python
import pytest
from app.core.errors import LuminoteException

@pytest.mark.unit
def test_raises_specific_exception():
    """Test that specific exception is raised."""
    with pytest.raises(LuminoteException) as exc_info:
        dangerous_operation()

    # Verify exception details
    assert exc_info.value.code == "EXPECTED_ERROR_CODE"
    assert exc_info.value.status_code == 400
    assert "expected phrase" in exc_info.value.message.lower()
```

## What NOT to Do

❌ **Never:**

- Make real API calls (always mock)
- Use real API keys (use `"test-key"` or similar)
- Test implementation details (test behavior, not internal structure)
- Write tests that depend on execution order
- Use `sleep()` or `time.sleep()` (use `freezegun` for time-based tests)
- Modify global state without cleanup
- Create tests that require manual setup
- Skip writing tests for error cases

## Common Patterns

### Testing Time-Dependent Code

```python
from freezegun import freeze_time
from datetime import datetime

@pytest.mark.unit
@freeze_time("2024-01-15 12:00:00")
def test_timestamp_generation():
    """Test timestamp generation with frozen time."""
    result = generate_timestamp()
    expected = datetime(2024, 1, 15, 12, 0, 0)
    assert result == expected
```

### Testing Logging

```python
import logging

@pytest.mark.unit
def test_error_logging(caplog):
    """Test that errors are logged correctly."""
    with caplog.at_level(logging.ERROR):
        process_with_error()

    assert "Expected error message" in caplog.text
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
```

### Testing File Operations

```python
from pathlib import Path

@pytest.mark.unit
def test_file_processing(tmp_path: Path):
    """Test file processing with temporary directory."""
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Process file
    result = process_file(str(test_file))

    # Verify
    assert result.success is True
```

## Before Committing

Run this checklist:

```bash
cd backend

# Run all tests
uv run pytest -v

# Check coverage
uv run pytest --cov=app --cov-report=term-missing

# Run specific test categories
uv run pytest -m unit -v
uv run pytest -m smoke -v

# Ensure no tests are skipped unintentionally
uv run pytest --strict-markers
```

## References

- [pytest documentation](https://docs.pytest.org/)
- [AGENTS.md](../../AGENTS.md) - Testing requirements
- `backend/tests/conftest.py` - Shared fixtures and configuration
