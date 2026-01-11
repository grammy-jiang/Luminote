"""Unit tests for core error classes.

Tests cover custom exception hierarchy and error types.
"""

import unittest

import pytest

from app.core.errors import (
    APIKeyError,
    ClientError,
    ExternalServiceError,
    ExtractionError,
    InvalidURLError,
    LuminoteException,
    ProviderTimeoutError,
    RateLimitError,
    ServerError,
    TranslationError,
    URLFetchError,
    ValidationError,
)


@pytest.mark.unit
class TestLuminoteException(unittest.TestCase):
    """Test base LuminoteException class."""

    def test_exception_initialization(self) -> None:
        """Test basic exception initialization."""
        exc = LuminoteException(
            message="Test error",
            code="TEST_ERROR",
            status_code=500,
            details={"key": "value"},
        )
        self.assertEqual(exc.message, "Test error")
        self.assertEqual(exc.code, "TEST_ERROR")
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.details, {"key": "value"})

    def test_exception_without_details(self) -> None:
        """Test exception initialization without details."""
        exc = LuminoteException(message="Error", code="ERROR", status_code=400)
        self.assertEqual(exc.details, {})

    def test_exception_string_representation(self) -> None:
        """Test exception string representation."""
        exc = LuminoteException(message="Test", code="TEST", status_code=500)
        self.assertEqual(str(exc), "Test")


@pytest.mark.unit
class TestClientErrors(unittest.TestCase):
    """Test client error classes (4xx)."""

    def test_client_error_base(self) -> None:
        """Test ClientError base class."""
        exc = ClientError(message="Client error", code="CLIENT_ERROR")
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.message, "Client error")

    def test_invalid_url_error(self) -> None:
        """Test InvalidURLError exception."""
        exc = InvalidURLError("not-a-url")
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.code, "INVALID_URL")
        self.assertIn("not-a-url", exc.message)
        self.assertEqual(exc.details["url"], "not-a-url")

    def test_validation_error(self) -> None:
        """Test ValidationError exception."""
        exc = ValidationError("email", "Invalid format")
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.code, "VALIDATION_ERROR")
        self.assertIn("email", exc.message)
        self.assertEqual(exc.details["field"], "email")
        self.assertEqual(exc.details["reason"], "Invalid format")

    def test_extraction_error(self) -> None:
        """Test ExtractionError exception."""
        exc = ExtractionError("https://example.com", "Connection timeout")
        self.assertEqual(exc.status_code, 422)
        self.assertEqual(exc.code, "EXTRACTION_ERROR")
        self.assertIn("https://example.com", exc.message)
        self.assertEqual(exc.details["url"], "https://example.com")
        self.assertEqual(exc.details["reason"], "Connection timeout")

    def test_api_key_error(self) -> None:
        """Test APIKeyError exception."""
        exc = APIKeyError("openai", "Invalid API key format")
        self.assertEqual(exc.status_code, 401)
        self.assertEqual(exc.code, "API_KEY_ERROR")
        self.assertIn("openai", exc.message)
        self.assertEqual(exc.details["provider"], "openai")
        self.assertEqual(exc.details["reason"], "Invalid API key format")

    def test_api_key_error_default_reason(self) -> None:
        """Test APIKeyError with default reason."""
        exc = APIKeyError("anthropic")
        self.assertEqual(exc.status_code, 401)
        self.assertEqual(exc.details["reason"], "Invalid or missing API key")

    def test_rate_limit_error_with_provider(self) -> None:
        """Test RateLimitError with provider."""
        exc = RateLimitError(60, provider="openai")
        self.assertEqual(exc.status_code, 429)
        self.assertEqual(exc.code, "RATE_LIMIT_EXCEEDED")
        self.assertIn("60 seconds", exc.message)
        self.assertIn("openai", exc.message)
        self.assertEqual(exc.details["retry_after"], 60)
        self.assertEqual(exc.details["provider"], "openai")

    def test_rate_limit_error_without_provider(self) -> None:
        """Test RateLimitError without provider."""
        exc = RateLimitError(30)
        self.assertEqual(exc.status_code, 429)
        self.assertEqual(exc.code, "RATE_LIMIT_EXCEEDED")
        self.assertIn("30 seconds", exc.message)
        self.assertEqual(exc.details["retry_after"], 30)
        self.assertIsNone(exc.details["provider"])


@pytest.mark.unit
class TestServerErrors(unittest.TestCase):
    """Test server error classes (5xx)."""

    def test_server_error_base(self) -> None:
        """Test ServerError base class."""
        exc = ServerError(message="Server error", code="SERVER_ERROR")
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.message, "Server error")

    def test_external_service_error(self) -> None:
        """Test ExternalServiceError exception."""
        exc = ExternalServiceError("database", "Connection failed")
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.code, "EXTERNAL_SERVICE_ERROR")
        self.assertIn("database", exc.message)
        self.assertEqual(exc.details["service"], "database")
        self.assertEqual(exc.details["reason"], "Connection failed")

    def test_translation_error(self) -> None:
        """Test TranslationError exception."""
        exc = TranslationError("openai", "gpt-4", "API unavailable")
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.code, "TRANSLATION_ERROR")
        self.assertIn("openai", exc.message)
        self.assertIn("gpt-4", exc.message)
        self.assertEqual(exc.details["provider"], "openai")
        self.assertEqual(exc.details["model"], "gpt-4")
        self.assertEqual(exc.details["reason"], "API unavailable")

    def test_url_fetch_error_default_status(self) -> None:
        """Test URLFetchError with default status code."""
        exc = URLFetchError("https://example.com", "Connection refused")
        self.assertEqual(exc.status_code, 502)
        self.assertEqual(exc.code, "URL_FETCH_ERROR")
        self.assertIn("https://example.com", exc.message)
        self.assertEqual(exc.details["url"], "https://example.com")
        self.assertEqual(exc.details["reason"], "Connection refused")

    def test_url_fetch_error_custom_status(self) -> None:
        """Test URLFetchError with custom status code."""
        exc = URLFetchError("https://example.com", "Timeout", status_code=504)
        self.assertEqual(exc.status_code, 504)
        self.assertEqual(exc.code, "URL_FETCH_ERROR")

    def test_provider_timeout_error(self) -> None:
        """Test ProviderTimeoutError exception."""
        exc = ProviderTimeoutError("openai", "gpt-4", "Request exceeded 30s limit")
        self.assertEqual(exc.status_code, 504)
        self.assertEqual(exc.code, "PROVIDER_TIMEOUT")
        self.assertIn("openai", exc.message)
        self.assertIn("gpt-4", exc.message)
        self.assertEqual(exc.details["provider"], "openai")
        self.assertEqual(exc.details["model"], "gpt-4")
        self.assertEqual(exc.details["reason"], "Request exceeded 30s limit")

    def test_provider_timeout_error_default_reason(self) -> None:
        """Test ProviderTimeoutError with default reason."""
        exc = ProviderTimeoutError("anthropic", "claude-3")
        self.assertEqual(exc.status_code, 504)
        self.assertEqual(exc.code, "PROVIDER_TIMEOUT")
        self.assertEqual(exc.details["reason"], "Request timed out")
