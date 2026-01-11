"""Tests for OpenAI translation provider."""

import os
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.core.errors import (
    APIKeyError,
    InsufficientPermissionsError,
    ProviderTimeoutError,
    QuotaExceededError,
    RateLimitError,
    TranslationError,
)
from app.services.providers.openai_provider import OpenAIProvider


@pytest.mark.unit
async def test_openai_provider_name():
    """Test that provider returns correct name."""
    provider = OpenAIProvider()
    assert provider.get_provider_name() == "openai"


@pytest.mark.unit
async def test_openai_translate_success():
    """Test successful translation with OpenAI."""
    provider = OpenAIProvider()

    # Mock response
    mock_response_data = {
        "choices": [{"message": {"content": "Hola mundo"}}],
        "usage": {"total_tokens": 30},
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        # Create a proper httpx.Response with a request
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=200, json=mock_response_data, request=mock_request
        )
        mock_post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.post = mock_post

        result = await provider.translate(
            text="Hello world",
            target_language="es",
            model="gpt-4",
            api_key="sk-test-key",
        )

        assert result.translated_text == "Hola mundo"
        assert result.tokens_used == 30
        assert result.model == "gpt-4"
        assert result.provider == "openai"

        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args.kwargs["headers"]["Authorization"] == "Bearer sk-test-key"
        assert call_args.kwargs["json"]["model"] == "gpt-4"


@pytest.mark.unit
async def test_openai_translate_invalid_api_key_format():
    """Test that invalid API key format raises APIKeyError."""
    provider = OpenAIProvider()

    with pytest.raises(APIKeyError) as exc_info:
        await provider.translate(
            text="Hello", target_language="es", model="gpt-4", api_key="invalid-key"
        )

    assert exc_info.value.code == "API_KEY_ERROR"
    assert "openai" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_translate_empty_api_key():
    """Test that empty API key raises APIKeyError."""
    provider = OpenAIProvider()

    with pytest.raises(APIKeyError) as exc_info:
        await provider.translate(
            text="Hello", target_language="es", model="gpt-4", api_key=""
        )

    assert exc_info.value.code == "API_KEY_ERROR"


@pytest.mark.unit
async def test_openai_translate_401_error():
    """Test handling of 401 authentication error."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Unauthorized",
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
            response=httpx.Response(
                status_code=401, json={"error": {"message": "Invalid API key"}}
            ),
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(APIKeyError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-invalid"
            )

        assert exc_info.value.code == "API_KEY_ERROR"
        assert "openai" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_translate_429_rate_limit():
    """Test handling of 429 rate limit error."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
            response=httpx.Response(
                status_code=429, json={"error": {"message": "Rate limit exceeded"}}
            ),
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(RateLimitError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"
        assert exc_info.value.details["provider"] == "openai"


@pytest.mark.unit
async def test_openai_translate_500_server_error():
    """Test handling of 500 server error."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Internal Server Error",
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
            response=httpx.Response(status_code=500),
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(TranslationError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "TRANSLATION_ERROR"
        assert "openai" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_translate_400_bad_request():
    """Test handling of 400 bad request error."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=400,
            json={"error": {"message": "Invalid model specified"}},
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Bad Request",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(TranslationError) as exc_info:
            await provider.translate(
                text="Hello",
                target_language="es",
                model="invalid-model",
                api_key="sk-test",
            )

        assert exc_info.value.code == "TRANSLATION_ERROR"
        assert "invalid model" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_translate_400_error_json_parse_failure():
    """Test 400 error with JSON parse failure in error extraction."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        from unittest.mock import Mock

        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.request = mock_request
        # Mock json() to raise exception
        mock_response.json.side_effect = Exception("JSON parse error")

        mock_post.side_effect = httpx.HTTPStatusError(
            message="Bad Request",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(TranslationError) as exc_info:
            await provider.translate(
                text="Hello",
                target_language="es",
                model="gpt-4",
                api_key="sk-test",
            )

        assert exc_info.value.code == "TRANSLATION_ERROR"


@pytest.mark.unit
async def test_openai_translate_429_error_json_parse_attempt():
    """Test 429 error attempts to parse JSON for retry info."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        from unittest.mock import Mock

        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.request = mock_request
        mock_response.headers = {}  # Add empty headers dict
        # Return valid JSON with retry info structure
        mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}

        mock_post.side_effect = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(RateLimitError):
            await provider.translate(
                text="Hello",
                target_language="es",
                model="gpt-4",
                api_key="sk-test",
            )


@pytest.mark.unit
async def test_openai_translate_timeout():
    """Test handling of timeout error."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.TimeoutException("Request timed out")
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(ProviderTimeoutError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "PROVIDER_TIMEOUT"
        assert exc_info.value.status_code == 504
        assert "timed out" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_translate_unexpected_response_format():
    """Test handling of unexpected API response format."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        # Missing 'choices' key
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=200, json={"usage": {"total_tokens": 30}}, request=mock_request
        )
        mock_post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(TranslationError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "TRANSLATION_ERROR"
        assert "format" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_translate_402_quota_exceeded():
    """Test handling of 402 payment required / quota exceeded error."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=402,
            json={"error": {"message": "You have exceeded your quota"}},
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Payment Required",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(QuotaExceededError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "QUOTA_EXCEEDED"
        assert exc_info.value.status_code == 402
        assert "openai" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_translate_403_forbidden():
    """Test handling of 403 forbidden / insufficient permissions error."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=403,
            json={"error": {"message": "Insufficient permissions"}},
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Forbidden",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(InsufficientPermissionsError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "INSUFFICIENT_PERMISSIONS"
        assert exc_info.value.status_code == 403
        assert "openai" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_translate_429_with_retry_after_header():
    """Test that retry_after is extracted from response headers."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=429,
            headers={"retry-after": "120"},
            json={"error": {"message": "Rate limit exceeded"}},
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(RateLimitError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"
        assert exc_info.value.details["retry_after"] == 120
        assert exc_info.value.details["provider"] == "openai"


@pytest.mark.unit
async def test_openai_translate_429_quota_in_message():
    """Test 429 with quota message is treated as QuotaExceededError."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=429,
            json={
                "error": {
                    "type": "insufficient_quota",
                    "message": "You have insufficient quota for this request",
                }
            },
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(QuotaExceededError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "QUOTA_EXCEEDED"
        assert "insufficient quota" in exc_info.value.message.lower()


# Tests for validate() method error handling


@pytest.mark.unit
async def test_openai_validate_success():
    """Test successful API key validation."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=200,
            json={
                "choices": [{"message": {"content": "Hello"}}],
                "usage": {"total_tokens": 5},
            },
            request=mock_request,
        )
        mock_post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.post = mock_post

        result = await provider.validate(model="gpt-4", api_key="sk-test-key")

        assert result.valid is True
        assert result.provider == "openai"
        assert result.model == "gpt-4"
        assert result.capabilities.streaming is True
        assert result.capabilities.max_tokens == 8192


@pytest.mark.unit
async def test_openai_validate_invalid_api_key_format():
    """Test that invalid API key format raises APIKeyError during validation."""
    provider = OpenAIProvider()

    with pytest.raises(APIKeyError) as exc_info:
        await provider.validate(model="gpt-4", api_key="invalid-key")

    assert exc_info.value.code == "API_KEY_ERROR"
    assert "openai" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_validate_401_error():
    """Test handling of 401 authentication error during validation."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Unauthorized",
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
            response=httpx.Response(
                status_code=401, json={"error": {"message": "Invalid API key"}}
            ),
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(APIKeyError) as exc_info:
            await provider.validate(model="gpt-4", api_key="sk-invalid")

        assert exc_info.value.code == "API_KEY_ERROR"
        assert "openai" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_openai_validate_402_quota_exceeded():
    """Test handling of 402 quota exceeded error during validation."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=402,
            json={"error": {"message": "You have exceeded your quota"}},
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Payment Required",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(QuotaExceededError) as exc_info:
            await provider.validate(model="gpt-4", api_key="sk-test")

        assert exc_info.value.code == "QUOTA_EXCEEDED"
        assert exc_info.value.status_code == 402


@pytest.mark.unit
async def test_openai_validate_403_forbidden():
    """Test handling of 403 forbidden error during validation."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=403,
            json={"error": {"message": "Insufficient permissions"}},
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Forbidden",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(InsufficientPermissionsError) as exc_info:
            await provider.validate(model="gpt-4", api_key="sk-test")

        assert exc_info.value.code == "INSUFFICIENT_PERMISSIONS"
        assert exc_info.value.status_code == 403


@pytest.mark.unit
async def test_openai_validate_429_rate_limit():
    """Test handling of 429 rate limit error during validation."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=429,
            headers={"retry-after": "90"},
            json={"error": {"message": "Rate limit exceeded"}},
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(RateLimitError) as exc_info:
            await provider.validate(model="gpt-4", api_key="sk-test")

        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"
        assert exc_info.value.details["retry_after"] == 90


@pytest.mark.unit
async def test_openai_validate_timeout():
    """Test handling of timeout error during validation."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.TimeoutException("Request timed out")
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(ProviderTimeoutError) as exc_info:
            await provider.validate(model="gpt-4", api_key="sk-test")

        assert exc_info.value.code == "PROVIDER_TIMEOUT"
        assert exc_info.value.status_code == 504


@pytest.mark.unit
async def test_openai_validate_402_json_parse_failure():
    """Test validate 402 error with JSON parse failure."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        from unittest.mock import Mock

        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 402
        mock_response.request = mock_request
        # Mock json() to raise exception
        mock_response.json.side_effect = Exception("JSON parse error")

        mock_post.side_effect = httpx.HTTPStatusError(
            message="Payment Required",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(QuotaExceededError) as exc_info:
            await provider.validate(model="gpt-4", api_key="sk-test")

        assert exc_info.value.code == "QUOTA_EXCEEDED"


@pytest.mark.unit
async def test_openai_validate_403_json_parse_failure():
    """Test validate 403 error with JSON parse failure."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        from unittest.mock import Mock

        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.request = mock_request
        # Mock json() to raise exception
        mock_response.json.side_effect = Exception("JSON parse error")

        mock_post.side_effect = httpx.HTTPStatusError(
            message="Forbidden",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(InsufficientPermissionsError) as exc_info:
            await provider.validate(model="gpt-4", api_key="sk-test")

        assert exc_info.value.code == "INSUFFICIENT_PERMISSIONS"


@pytest.mark.unit
async def test_openai_validate_429_invalid_retry_after():
    """Test validate 429 with invalid retry-after header."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=429,
            headers={"retry-after": "not-valid"},
            json={"error": {"message": "Rate limit exceeded"}},
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(RateLimitError) as exc_info:
            await provider.validate(model="gpt-4", api_key="sk-test")

        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"
        assert exc_info.value.details["retry_after"] == 60  # Default


@pytest.mark.unit
async def test_openai_translate_402_json_parse_failure():
    """Test 402 error with JSON parse failure."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        from unittest.mock import Mock

        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 402
        mock_response.request = mock_request
        # Mock json() to raise exception
        mock_response.json.side_effect = Exception("JSON parse error")

        mock_post.side_effect = httpx.HTTPStatusError(
            message="Payment Required",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(QuotaExceededError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "QUOTA_EXCEEDED"
        assert "API quota exceeded" in exc_info.value.message


@pytest.mark.unit
async def test_openai_translate_403_json_parse_failure():
    """Test 403 error with JSON parse failure."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        from unittest.mock import Mock

        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.request = mock_request
        # Mock json() to raise exception
        mock_response.json.side_effect = Exception("JSON parse error")

        mock_post.side_effect = httpx.HTTPStatusError(
            message="Forbidden",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(InsufficientPermissionsError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "INSUFFICIENT_PERMISSIONS"
        assert "Insufficient permissions" in exc_info.value.message


@pytest.mark.unit
async def test_openai_translate_429_invalid_retry_after_header():
    """Test 429 with invalid retry-after header value."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = httpx.Response(
            status_code=429,
            headers={"retry-after": "invalid"},  # Invalid integer
            json={"error": {"message": "Rate limit exceeded"}},
            request=mock_request,
        )
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(RateLimitError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"
        # Should fall back to default 60 seconds
        assert exc_info.value.details["retry_after"] == 60


@pytest.mark.unit
async def test_openai_translate_429_json_parse_error():
    """Test 429 with JSON parse error falls back to rate limit."""
    provider = OpenAIProvider()

    with patch("httpx.AsyncClient") as mock_client:
        from unittest.mock import Mock

        mock_post = AsyncMock()
        mock_request = httpx.Request(
            "POST", "https://api.openai.com/v1/chat/completions"
        )
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.request = mock_request
        mock_response.headers = {}
        # Mock json() to raise exception
        mock_response.json.side_effect = Exception("JSON parse error")

        mock_post.side_effect = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=mock_request,
            response=mock_response,
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(RateLimitError) as exc_info:
            await provider.translate(
                text="Hello", target_language="es", model="gpt-4", api_key="sk-test"
            )

        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="No OPENAI_API_KEY set")
async def test_openai_real_translation():
    """Integration test with real OpenAI API (requires API key)."""
    provider = OpenAIProvider()
    api_key = os.getenv("OPENAI_API_KEY", "")

    result = await provider.translate(
        text="Hello, world!",
        target_language="es",
        model="gpt-4o-mini",
        api_key=api_key,
    )

    assert result.translated_text
    assert result.tokens_used > 0
    assert result.model == "gpt-4o-mini"
    assert result.provider == "openai"
    # Check translation is not the same as input (actually translated)
    assert result.translated_text.lower() != "hello, world!"
