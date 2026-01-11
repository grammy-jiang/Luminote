"""Tests for Anthropic translation provider."""

import os
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.core.errors import (
    APIKeyError,
    ProviderTimeoutError,
    RateLimitError,
    TranslationError,
)
from app.services.providers.anthropic_provider import AnthropicProvider


@pytest.mark.unit
async def test_anthropic_provider_name():
    """Test that provider returns correct name."""
    provider = AnthropicProvider()
    assert provider.get_provider_name() == "anthropic"


@pytest.mark.unit
async def test_anthropic_translate_success():
    """Test successful translation with Anthropic."""
    provider = AnthropicProvider()

    # Mock response
    mock_response_data = {
        "content": [{"type": "text", "text": "Hola mundo"}],
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        mock_response = httpx.Response(
            status_code=200, json=mock_response_data, request=mock_request
        )
        mock_post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.post = mock_post

        result = await provider.translate(
            text="Hello world",
            target_language="es",
            model="claude-3-5-sonnet-20241022",
            api_key="sk-ant-test-key",
        )

        assert result.translated_text == "Hola mundo"
        assert result.tokens_used == 15  # 10 + 5
        assert result.model == "claude-3-5-sonnet-20241022"
        assert result.provider == "anthropic"

        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args.kwargs["headers"]["x-api-key"] == "sk-ant-test-key"
        assert call_args.kwargs["json"]["model"] == "claude-3-5-sonnet-20241022"


@pytest.mark.unit
async def test_anthropic_translate_invalid_api_key_format():
    """Test that invalid API key format raises APIKeyError."""
    provider = AnthropicProvider()

    with pytest.raises(APIKeyError) as exc_info:
        await provider.translate(
            text="Hello",
            target_language="es",
            model="claude-3-5-sonnet-20241022",
            api_key="invalid-key",
        )

    assert exc_info.value.code == "API_KEY_ERROR"
    assert "anthropic" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_anthropic_translate_empty_api_key():
    """Test that empty API key raises APIKeyError."""
    provider = AnthropicProvider()

    with pytest.raises(APIKeyError) as exc_info:
        await provider.translate(
            text="Hello",
            target_language="es",
            model="claude-3-5-sonnet-20241022",
            api_key="",
        )

    assert exc_info.value.code == "API_KEY_ERROR"


@pytest.mark.unit
async def test_anthropic_translate_401_error():
    """Test handling of 401 authentication error."""
    provider = AnthropicProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Unauthorized",
            request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"),
            response=httpx.Response(
                status_code=401, json={"error": {"message": "Invalid API key"}}
            ),
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(APIKeyError) as exc_info:
            await provider.translate(
                text="Hello",
                target_language="es",
                model="claude-3-5-sonnet-20241022",
                api_key="sk-ant-invalid",
            )

        assert exc_info.value.code == "API_KEY_ERROR"
        assert "anthropic" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_anthropic_translate_429_rate_limit():
    """Test handling of 429 rate limit error."""
    provider = AnthropicProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"),
            response=httpx.Response(
                status_code=429,
                headers={"retry-after": "30"},
                json={"error": {"message": "Rate limit exceeded"}},
            ),
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(RateLimitError) as exc_info:
            await provider.translate(
                text="Hello",
                target_language="es",
                model="claude-3-5-sonnet-20241022",
                api_key="sk-ant-test",
            )

        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"
        assert exc_info.value.details["provider"] == "anthropic"
        assert exc_info.value.details["retry_after"] == 30


@pytest.mark.unit
async def test_anthropic_translate_500_server_error():
    """Test handling of 500 server error."""
    provider = AnthropicProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.HTTPStatusError(
            message="Internal Server Error",
            request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"),
            response=httpx.Response(status_code=500),
        )
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(TranslationError) as exc_info:
            await provider.translate(
                text="Hello",
                target_language="es",
                model="claude-3-5-sonnet-20241022",
                api_key="sk-ant-test",
            )

        assert exc_info.value.code == "TRANSLATION_ERROR"
        assert "anthropic" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_anthropic_translate_400_bad_request():
    """Test handling of 400 bad request error."""
    provider = AnthropicProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
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
                api_key="sk-ant-test",
            )

        assert exc_info.value.code == "TRANSLATION_ERROR"
        assert "invalid model" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_anthropic_translate_400_error_json_parse_failure():
    """Test 400 error with JSON parse failure in error extraction."""
    provider = AnthropicProvider()

    with patch("httpx.AsyncClient") as mock_client:
        from unittest.mock import Mock

        mock_post = AsyncMock()
        mock_request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
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
                model="claude-3-5-sonnet-20241022",
                api_key="sk-ant-test",
            )

        assert exc_info.value.code == "TRANSLATION_ERROR"


@pytest.mark.unit
async def test_anthropic_translate_timeout():
    """Test handling of timeout error."""
    provider = AnthropicProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_post.side_effect = httpx.TimeoutException("Request timed out")
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(ProviderTimeoutError) as exc_info:
            await provider.translate(
                text="Hello",
                target_language="es",
                model="claude-3-5-sonnet-20241022",
                api_key="sk-ant-test",
            )

        assert exc_info.value.code == "PROVIDER_TIMEOUT"
        assert exc_info.value.status_code == 504
        assert "timed out" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_anthropic_translate_unexpected_response_format():
    """Test handling of unexpected API response format."""
    provider = AnthropicProvider()

    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        # Missing 'content' key
        mock_request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        mock_response = httpx.Response(
            status_code=200,
            json={"usage": {"input_tokens": 10, "output_tokens": 5}},
            request=mock_request,
        )
        mock_post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(TranslationError) as exc_info:
            await provider.translate(
                text="Hello",
                target_language="es",
                model="claude-3-5-sonnet-20241022",
                api_key="sk-ant-test",
            )

        assert exc_info.value.code == "TRANSLATION_ERROR"
        assert "format" in exc_info.value.message.lower()
        assert "response format" in exc_info.value.message.lower()


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="No ANTHROPIC_API_KEY set"
)
async def test_anthropic_real_translation():
    """Integration test with real Anthropic API (requires API key)."""
    provider = AnthropicProvider()
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    result = await provider.translate(
        text="Hello, world!",
        target_language="es",
        model="claude-3-5-sonnet-20241022",
        api_key=api_key,
    )

    assert result.translated_text
    assert result.tokens_used > 0
    assert result.model == "claude-3-5-sonnet-20241022"
    assert result.provider == "anthropic"
    # Check translation is not the same as input (actually translated)
    assert result.translated_text.lower() != "hello, world!"
