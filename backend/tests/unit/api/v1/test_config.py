"""Tests for config validation API endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_validate_config_success_mock_provider(client: TestClient) -> None:
    """Test successful config validation with mock provider."""
    # Arrange
    request_data = {
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert data["valid"] is True
    assert data["provider"] == "mock"
    assert data["model"] == "test-model"
    assert "capabilities" in data
    assert data["capabilities"]["streaming"] is True
    assert data["capabilities"]["max_tokens"] == 4096
    assert "details" in data

    # Check headers
    assert "X-Request-ID" in response.headers


@pytest.mark.unit
@patch("httpx.AsyncClient")
async def test_validate_config_success_openai(
    mock_client_class, client: TestClient
) -> None:
    """Test successful config validation with OpenAI provider."""
    # Mock OpenAI API response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello"}}],
        "usage": {"total_tokens": 10},
    }
    mock_response.raise_for_status = AsyncMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_client_class.return_value = mock_client_instance

    # Arrange
    request_data = {
        "provider": "openai",
        "model": "gpt-4",  # Use gpt-4 instead of gpt-4o-mini
        "api_key": "sk-test123",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is True
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-4"
    assert data["capabilities"]["streaming"] is True
    assert data["capabilities"]["max_tokens"] == 8192  # gpt-4 default


@pytest.mark.unit
@patch("httpx.AsyncClient")
async def test_validate_config_success_anthropic(
    mock_client_class, client: TestClient
) -> None:
    """Test successful config validation with Anthropic provider."""
    # Mock Anthropic API response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "content": [{"text": "Hello"}],
        "usage": {"input_tokens": 5, "output_tokens": 5},
    }
    mock_response.raise_for_status = AsyncMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_client_class.return_value = mock_client_instance

    # Arrange
    request_data = {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "api_key": "sk-ant-test123",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is True
    assert data["provider"] == "anthropic"
    assert data["model"] == "claude-3-5-sonnet-20241022"
    assert data["capabilities"]["streaming"] is True
    assert data["capabilities"]["max_tokens"] == 200000  # claude-3-5-sonnet default


@pytest.mark.unit
def test_validate_config_missing_provider(client: TestClient) -> None:
    """Test config validation with missing provider field."""
    # Arrange
    request_data = {
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "provider" in str(data)


@pytest.mark.unit
def test_validate_config_missing_model(client: TestClient) -> None:
    """Test config validation with missing model field."""
    # Arrange
    request_data = {
        "provider": "openai",
        "api_key": "test-key",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "model" in str(data)


@pytest.mark.unit
def test_validate_config_missing_api_key(client: TestClient) -> None:
    """Test config validation with missing api_key field."""
    # Arrange
    request_data = {
        "provider": "openai",
        "model": "gpt-4",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "api_key" in str(data)


@pytest.mark.unit
def test_validate_config_unsupported_provider(client: TestClient) -> None:
    """Test config validation with unsupported provider."""
    # Arrange
    request_data = {
        "provider": "unsupported-provider",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
@patch("httpx.AsyncClient")
async def test_validate_config_invalid_api_key_openai(
    mock_client_class, client: TestClient
) -> None:
    """Test config validation with invalid OpenAI API key (401)."""
    # Mock OpenAI 401 response
    import httpx

    mock_response = AsyncMock()
    mock_response.status_code = 401

    mock_error = httpx.HTTPStatusError(
        "Unauthorized", request=AsyncMock(), response=mock_response
    )

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(side_effect=mock_error)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_client_class.return_value = mock_client_instance

    # Arrange
    request_data = {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-invalid",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "API_KEY_ERROR"
    assert "openai" in data["error"].lower()


@pytest.mark.unit
@patch("httpx.AsyncClient")
async def test_validate_config_rate_limit_exceeded(
    mock_client_class, client: TestClient
) -> None:
    """Test config validation with rate limit exceeded (429)."""
    # Mock OpenAI 429 response
    import httpx

    mock_response = AsyncMock()
    mock_response.status_code = 429
    mock_response.headers = {"retry-after": "60"}

    mock_error = httpx.HTTPStatusError(
        "Too Many Requests", request=AsyncMock(), response=mock_response
    )

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(side_effect=mock_error)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_client_class.return_value = mock_client_instance

    # Arrange
    request_data = {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test123",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 429
    data = response.json()
    assert data["code"] == "RATE_LIMIT_EXCEEDED"
    assert "rate limit" in data["error"].lower()


@pytest.mark.unit
@patch("httpx.AsyncClient")
async def test_validate_config_timeout(mock_client_class, client: TestClient) -> None:
    """Test config validation with timeout after 10 seconds."""
    # Mock timeout
    import httpx

    mock_error = httpx.TimeoutException("Request timed out")

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(side_effect=mock_error)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_client_class.return_value = mock_client_instance

    # Arrange
    request_data = {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test123",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 500
    data = response.json()
    assert data["code"] == "TRANSLATION_ERROR"
    assert "timed out" in data["error"].lower()


@pytest.mark.unit
def test_validate_config_invalid_openai_key_format(client: TestClient) -> None:
    """Test config validation with invalid OpenAI key format."""
    # Arrange
    request_data = {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "invalid-key-format",  # Should start with sk-
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "API_KEY_ERROR"
    assert "format" in data["error"].lower()


@pytest.mark.unit
def test_validate_config_invalid_anthropic_key_format(client: TestClient) -> None:
    """Test config validation with invalid Anthropic key format."""
    # Arrange
    request_data = {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "api_key": "invalid-key-format",  # Should start with sk-ant-
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "API_KEY_ERROR"
    assert "format" in data["error"].lower()


@pytest.mark.unit
@patch("httpx.AsyncClient")
async def test_validate_config_minimal_cost(
    mock_client_class, client: TestClient
) -> None:
    """Test that validation uses minimal prompt to reduce cost."""
    # Mock OpenAI API response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello"}}],
        "usage": {"total_tokens": 10},
    }
    mock_response.raise_for_status = AsyncMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
    mock_client_class.return_value = mock_client_instance

    # Arrange
    request_data = {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test123",
    }

    # Act
    response = client.post("/api/v1/config/validate", json=request_data)

    # Assert
    assert response.status_code == 200

    # Verify that the API call was made with minimal settings
    mock_client_instance.post.assert_called_once()
    call_args = mock_client_instance.post.call_args

    # Check that max_tokens is minimal (5)
    request_json = call_args.kwargs["json"]
    assert request_json["max_tokens"] == 5

    # Check that timeout is 10 seconds
    assert call_args.kwargs["timeout"] == 10.0

    # Check that prompt is minimal (single word "Hi")
    messages = request_json["messages"]
    assert len(messages) == 1
    assert messages[0]["content"] == "Hi"
