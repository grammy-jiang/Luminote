"""
Test core error classes.

Tests cover custom exception hierarchy and error types.
"""

import pytest

from app.core.errors import (
    APIKeyError,
    ClientError,
    ExternalServiceError,
    ExtractionError,
    InvalidURLError,
    LuminoteException,
    RateLimitError,
    ServerError,
    TranslationError,
    ValidationError,
)


@pytest.mark.unit
class TestLuminoteException:
    """Test base LuminoteException class."""

    def test_exception_initialization(self) -> None:
        """Test basic exception initialization."""
        exc = LuminoteException(
            message="Test error",
            code="TEST_ERROR",
            status_code=500,
            details={"key": "value"},
        )
        assert exc.message == "Test error"
        assert exc.code == "TEST_ERROR"
        assert exc.status_code == 500
        assert exc.details == {"key": "value"}

    def test_exception_without_details(self) -> None:
        """Test exception initialization without details."""
        exc = LuminoteException(message="Error", code="ERROR", status_code=400)
        assert exc.details == {}

    def test_exception_string_representation(self) -> None:
        """Test exception string representation."""
        exc = LuminoteException(message="Test", code="TEST", status_code=500)
        assert str(exc) == "Test"


@pytest.mark.unit
class TestClientErrors:
    """Test client error classes (4xx)."""

    def test_client_error_base(self) -> None:
        """Test ClientError base class."""
        exc = ClientError(message="Client error", code="CLIENT_ERROR")
        assert exc.status_code == 400
        assert exc.message == "Client error"

    def test_invalid_url_error(self) -> None:
        """Test InvalidURLError exception."""
        exc = InvalidURLError("not-a-url")
        assert exc.status_code == 400
        assert exc.code == "INVALID_URL"
        assert "not-a-url" in exc.message
        assert exc.details["url"] == "not-a-url"

    def test_validation_error(self) -> None:
        """Test ValidationError exception."""
        exc = ValidationError("email", "Invalid format")
        assert exc.status_code == 400
        assert exc.code == "VALIDATION_ERROR"
        assert "email" in exc.message
        assert exc.details["field"] == "email"
        assert exc.details["reason"] == "Invalid format"

    def test_extraction_error(self) -> None:
        """Test ExtractionError exception."""
        exc = ExtractionError("https://example.com", "Connection timeout")
        assert exc.status_code == 422
        assert exc.code == "EXTRACTION_ERROR"
        assert "https://example.com" in exc.message
        assert exc.details["url"] == "https://example.com"
        assert exc.details["reason"] == "Connection timeout"

    def test_api_key_error(self) -> None:
        """Test APIKeyError exception."""
        exc = APIKeyError("openai", "Invalid API key format")
        assert exc.status_code == 401
        assert exc.code == "API_KEY_ERROR"
        assert "openai" in exc.message
        assert exc.details["provider"] == "openai"
        assert exc.details["reason"] == "Invalid API key format"

    def test_api_key_error_default_reason(self) -> None:
        """Test APIKeyError with default reason."""
        exc = APIKeyError("anthropic")
        assert exc.status_code == 401
        assert exc.details["reason"] == "Invalid or missing API key"

    def test_rate_limit_error_with_provider(self) -> None:
        """Test RateLimitError with provider."""
        exc = RateLimitError(60, provider="openai")
        assert exc.status_code == 429
        assert exc.code == "RATE_LIMIT_EXCEEDED"
        assert "60 seconds" in exc.message
        assert "openai" in exc.message
        assert exc.details["retry_after"] == 60
        assert exc.details["provider"] == "openai"

    def test_rate_limit_error_without_provider(self) -> None:
        """Test RateLimitError without provider."""
        exc = RateLimitError(30)
        assert exc.status_code == 429
        assert exc.code == "RATE_LIMIT_EXCEEDED"
        assert "30 seconds" in exc.message
        assert exc.details["retry_after"] == 30
        assert exc.details["provider"] is None


@pytest.mark.unit
class TestServerErrors:
    """Test server error classes (5xx)."""

    def test_server_error_base(self) -> None:
        """Test ServerError base class."""
        exc = ServerError(message="Server error", code="SERVER_ERROR")
        assert exc.status_code == 500
        assert exc.message == "Server error"

    def test_external_service_error(self) -> None:
        """Test ExternalServiceError exception."""
        exc = ExternalServiceError("database", "Connection failed")
        assert exc.status_code == 500
        assert exc.code == "EXTERNAL_SERVICE_ERROR"
        assert "database" in exc.message
        assert exc.details["service"] == "database"
        assert exc.details["reason"] == "Connection failed"

    def test_translation_error(self) -> None:
        """Test TranslationError exception."""
        exc = TranslationError("openai", "gpt-4", "API unavailable")
        assert exc.status_code == 500
        assert exc.code == "TRANSLATION_ERROR"
        assert "openai" in exc.message
        assert "gpt-4" in exc.message
        assert exc.details["provider"] == "openai"
        assert exc.details["model"] == "gpt-4"
        assert exc.details["reason"] == "API unavailable"
