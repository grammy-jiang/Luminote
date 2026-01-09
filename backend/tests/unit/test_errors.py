"""Unit tests for error handling and response standardization.

Tests cover exception handlers and request ID tracking.
"""

import unittest
import uuid

import pytest

from app.core.errors import (
    APIKeyError,
    ExtractionError,
    InvalidURLError,
    RateLimitError,
    TranslationError,
)
from app.main import fastapi_application
from tests.conftest import FixtureAttrs


@pytest.mark.e2e
class TestExceptionHandlers(FixtureAttrs, unittest.TestCase):
    """Test exception handler middleware."""

    def test_404_includes_request_id(self) -> None:
        """Test 404 error includes request ID."""
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        # FastAPI default 404 doesn't go through our handler, but should have request ID
        self.assertIn("X-Request-ID", response.headers)

    def test_health_check_includes_request_id(self) -> None:
        """Test successful response includes request ID in header."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Request-ID", response.headers)
        # Verify it's a valid UUID
        request_id = response.headers["X-Request-ID"]
        uuid.UUID(request_id)  # Should not raise

    def test_validation_error_response(self) -> None:
        """Test validation error returns proper format."""
        # Create a temporary test endpoint that will fail validation
        from pydantic import BaseModel

        class TestRequest(BaseModel):
            email: str

        @fastapi_application.post("/test-validation")
        async def test_endpoint(data: TestRequest) -> dict[str, str]:
            return {"status": "ok"}

        # Send invalid data
        response = self.client.post("/test-validation", json={"email": 123})
        self.assertEqual(response.status_code, 422)

        data = response.json()
        self.assertIn("error", data)
        self.assertIn("code", data)
        self.assertEqual(data["code"], "VALIDATION_ERROR")
        self.assertIn("request_id", data)
        self.assertIn("details", data)
        self.assertIn("errors", data["details"])
        self.assertIn("X-Request-ID", response.headers)

    def test_custom_exception_handler(self) -> None:
        """Test custom exception handler returns proper format."""

        @fastapi_application.get("/test-custom-error")
        async def test_error_endpoint() -> dict[str, str]:
            raise InvalidURLError("not-a-valid-url")

        response = self.client.get("/test-custom-error")
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertEqual(data["code"], "INVALID_URL")
        self.assertIn("not-a-valid-url", data["error"])
        self.assertIn("request_id", data)
        self.assertIn("details", data)
        self.assertEqual(data["details"]["url"], "not-a-valid-url")
        self.assertIn("X-Request-ID", response.headers)

    def test_rate_limit_error_handler(self) -> None:
        """Test rate limit error handler."""

        @fastapi_application.get("/test-rate-limit")
        async def test_rate_limit_endpoint() -> dict[str, str]:
            raise RateLimitError(60, provider="openai")

        response = self.client.get("/test-rate-limit")
        self.assertEqual(response.status_code, 429)

        data = response.json()
        self.assertEqual(data["code"], "RATE_LIMIT_EXCEEDED")
        self.assertIn("60 seconds", data["error"])
        self.assertEqual(data["details"]["retry_after"], 60)
        self.assertEqual(data["details"]["provider"], "openai")
        self.assertIn("request_id", data)
        self.assertIn("X-Request-ID", response.headers)
        # Verify Retry-After header is included per RFC 7231
        self.assertIn("Retry-After", response.headers)
        self.assertEqual(response.headers["Retry-After"], "60")

    def test_api_key_error_handler(self) -> None:
        """Test API key error handler."""

        @fastapi_application.get("/test-api-key-error")
        async def test_api_key_endpoint() -> dict[str, str]:
            raise APIKeyError("anthropic", "Invalid key format")

        response = self.client.get("/test-api-key-error")
        self.assertEqual(response.status_code, 401)

        data = response.json()
        self.assertEqual(data["code"], "API_KEY_ERROR")
        self.assertIn("anthropic", data["error"])
        self.assertEqual(data["details"]["provider"], "anthropic")
        self.assertIn("request_id", data)

    def test_translation_error_handler(self) -> None:
        """Test translation error handler."""

        @fastapi_application.get("/test-translation-error")
        async def test_translation_endpoint() -> dict[str, str]:
            raise TranslationError("openai", "gpt-4", "Service unavailable")

        response = self.client.get("/test-translation-error")
        self.assertEqual(response.status_code, 500)

        data = response.json()
        self.assertEqual(data["code"], "TRANSLATION_ERROR")
        self.assertIn("openai", data["error"])
        self.assertIn("gpt-4", data["error"])
        self.assertEqual(data["details"]["provider"], "openai")
        self.assertEqual(data["details"]["model"], "gpt-4")
        self.assertIn("request_id", data)

    def test_extraction_error_handler(self) -> None:
        """Test extraction error handler."""

        @fastapi_application.get("/test-extraction-error")
        async def test_extraction_endpoint() -> dict[str, str]:
            raise ExtractionError("https://example.com", "Timeout")

        response = self.client.get("/test-extraction-error")
        self.assertEqual(response.status_code, 422)

        data = response.json()
        self.assertEqual(data["code"], "EXTRACTION_ERROR")
        self.assertIn("https://example.com", data["error"])
        self.assertEqual(data["details"]["url"], "https://example.com")
        self.assertIn("request_id", data)


@pytest.mark.unit
class TestRequestIDMiddleware(FixtureAttrs, unittest.TestCase):
    """Test request ID middleware."""

    def test_request_id_is_uuid(self) -> None:
        """Test request ID is a valid UUID."""
        response = self.client.get("/health")
        request_id = response.headers["X-Request-ID"]
        # Should not raise ValueError
        uuid.UUID(request_id)

    def test_request_id_unique_per_request(self) -> None:
        """Test each request gets a unique ID."""
        response1 = self.client.get("/health")
        response2 = self.client.get("/health")

        id1 = response1.headers["X-Request-ID"]
        id2 = response2.headers["X-Request-ID"]

        self.assertNotEqual(id1, id2)

    def test_request_id_in_error_response(self) -> None:
        """Test request ID appears in both header and error body."""

        @fastapi_application.get("/test-request-id-error")
        async def test_endpoint() -> dict[str, str]:
            raise InvalidURLError("test")

        response = self.client.get("/test-request-id-error")

        header_id = response.headers["X-Request-ID"]
        body_id = response.json()["request_id"]

        # Both should exist and match
        self.assertEqual(header_id, body_id)
        uuid.UUID(header_id)  # Should be valid UUID
