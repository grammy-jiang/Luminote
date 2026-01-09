"""Test error handling and response standardization.

Tests cover exception handlers and request ID tracking.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.errors import (
    APIKeyError,
    ExtractionError,
    InvalidURLError,
    RateLimitError,
    TranslationError,
)
from app.main import fastapi_application


@pytest.mark.e2e
class TestExceptionHandlers:
    """Test exception handler middleware."""

    def test_404_includes_request_id(self, client: TestClient) -> None:
        """Test 404 error includes request ID."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        # FastAPI default 404 doesn't go through our handler, but should have request ID
        assert "X-Request-ID" in response.headers

    def test_health_check_includes_request_id(self, client: TestClient) -> None:
        """Test successful response includes request ID in header."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        # Verify it's a valid UUID
        request_id = response.headers["X-Request-ID"]
        uuid.UUID(request_id)  # Should not raise

    def test_validation_error_response(self, client: TestClient) -> None:
        """Test validation error returns proper format."""
        # Create a temporary test endpoint that will fail validation
        from pydantic import BaseModel

        class TestRequest(BaseModel):
            email: str

        @fastapi_application.post("/test-validation")
        async def test_endpoint(data: TestRequest) -> dict[str, str]:
            return {"status": "ok"}

        # Send invalid data
        response = client.post("/test-validation", json={"email": 123})
        assert response.status_code == 422

        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == "VALIDATION_ERROR"
        assert "request_id" in data
        assert "details" in data
        assert "errors" in data["details"]
        assert "X-Request-ID" in response.headers

    def test_custom_exception_handler(self, client: TestClient) -> None:
        """Test custom exception handler returns proper format."""

        @fastapi_application.get("/test-custom-error")
        async def test_error_endpoint() -> dict[str, str]:
            raise InvalidURLError("not-a-valid-url")

        response = client.get("/test-custom-error")
        assert response.status_code == 400

        data = response.json()
        assert data["code"] == "INVALID_URL"
        assert "not-a-valid-url" in data["error"]
        assert "request_id" in data
        assert "details" in data
        assert data["details"]["url"] == "not-a-valid-url"
        assert "X-Request-ID" in response.headers

    def test_rate_limit_error_handler(self, client: TestClient) -> None:
        """Test rate limit error handler."""

        @fastapi_application.get("/test-rate-limit")
        async def test_rate_limit_endpoint() -> dict[str, str]:
            raise RateLimitError(60, provider="openai")

        response = client.get("/test-rate-limit")
        assert response.status_code == 429

        data = response.json()
        assert data["code"] == "RATE_LIMIT_EXCEEDED"
        assert "60 seconds" in data["error"]
        assert data["details"]["retry_after"] == 60
        assert data["details"]["provider"] == "openai"
        assert "request_id" in data
        assert "X-Request-ID" in response.headers
        # Verify Retry-After header is included per RFC 7231
        assert "Retry-After" in response.headers
        assert response.headers["Retry-After"] == "60"

    def test_api_key_error_handler(self, client: TestClient) -> None:
        """Test API key error handler."""

        @fastapi_application.get("/test-api-key-error")
        async def test_api_key_endpoint() -> dict[str, str]:
            raise APIKeyError("anthropic", "Invalid key format")

        response = client.get("/test-api-key-error")
        assert response.status_code == 401

        data = response.json()
        assert data["code"] == "API_KEY_ERROR"
        assert "anthropic" in data["error"]
        assert data["details"]["provider"] == "anthropic"
        assert "request_id" in data

    def test_translation_error_handler(self, client: TestClient) -> None:
        """Test translation error handler."""

        @fastapi_application.get("/test-translation-error")
        async def test_translation_endpoint() -> dict[str, str]:
            raise TranslationError("openai", "gpt-4", "Service unavailable")

        response = client.get("/test-translation-error")
        assert response.status_code == 500

        data = response.json()
        assert data["code"] == "TRANSLATION_ERROR"
        assert "openai" in data["error"]
        assert "gpt-4" in data["error"]
        assert data["details"]["provider"] == "openai"
        assert data["details"]["model"] == "gpt-4"
        assert "request_id" in data

    def test_extraction_error_handler(self, client: TestClient) -> None:
        """Test extraction error handler."""

        @fastapi_application.get("/test-extraction-error")
        async def test_extraction_endpoint() -> dict[str, str]:
            raise ExtractionError("https://example.com", "Timeout")

        response = client.get("/test-extraction-error")
        assert response.status_code == 422

        data = response.json()
        assert data["code"] == "EXTRACTION_ERROR"
        assert "https://example.com" in data["error"]
        assert data["details"]["url"] == "https://example.com"
        assert "request_id" in data


@pytest.mark.unit
class TestRequestIDMiddleware:
    """Test request ID middleware."""

    def test_request_id_is_uuid(self, client: TestClient) -> None:
        """Test request ID is a valid UUID."""
        response = client.get("/health")
        request_id = response.headers["X-Request-ID"]
        # Should not raise ValueError
        uuid.UUID(request_id)

    def test_request_id_unique_per_request(self, client: TestClient) -> None:
        """Test each request gets a unique ID."""
        response1 = client.get("/health")
        response2 = client.get("/health")

        id1 = response1.headers["X-Request-ID"]
        id2 = response2.headers["X-Request-ID"]

        assert id1 != id2

    def test_request_id_in_error_response(self, client: TestClient) -> None:
        """Test request ID appears in both header and error body."""

        @fastapi_application.get("/test-request-id-error")
        async def test_endpoint() -> dict[str, str]:
            raise InvalidURLError("test")

        response = client.get("/test-request-id-error")

        header_id = response.headers["X-Request-ID"]
        body_id = response.json()["request_id"]

        # Both should exist and match
        assert header_id == body_id
        uuid.UUID(header_id)  # Should be valid UUID
