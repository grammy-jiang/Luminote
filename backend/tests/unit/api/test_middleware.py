"""Unit tests for CORS and timing middleware."""

import unittest
from unittest.mock import patch

import pytest

from tests.conftest import FixtureAttrs


@pytest.mark.unit
class TestCORSMiddleware(FixtureAttrs, unittest.TestCase):
    """Test CORS middleware."""

    def test_cors_headers_present(self) -> None:
        """Test CORS headers are present in response."""
        response = self.client.get(
            "/health", headers={"Origin": "http://localhost:5000"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)
        self.assertEqual(
            response.headers["access-control-allow-origin"], "http://localhost:5000"
        )
        self.assertIn("access-control-allow-credentials", response.headers)
        self.assertEqual(response.headers["access-control-allow-credentials"], "true")

    def test_cors_preflight_request(self) -> None:
        """Test CORS preflight OPTIONS request works correctly."""
        response = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)
        self.assertEqual(
            response.headers["access-control-allow-origin"], "http://localhost:5000"
        )
        self.assertIn("access-control-allow-methods", response.headers)
        self.assertIn("access-control-allow-headers", response.headers)
        self.assertIn("access-control-allow-credentials", response.headers)

    def test_cors_invalid_origin(self) -> None:
        """Test CORS headers not present for invalid origin."""
        response = self.client.get(
            "/health", headers={"Origin": "http://malicious.com"}
        )

        self.assertEqual(response.status_code, 200)
        # CORS middleware should not set allow-origin for invalid origins
        # Note: The header won't be present if origin is not allowed
        self.assertTrue(
            "access-control-allow-origin" not in response.headers
            or response.headers["access-control-allow-origin"] != "http://malicious.com"
        )


@pytest.mark.unit
class TestTimingMiddleware(FixtureAttrs, unittest.TestCase):
    """Test timing middleware."""

    def test_timing_header_present(self) -> None:
        """Test X-Response-Time header is present in all responses."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertIn("x-response-time", response.headers)
        # Should be in format like "1.23ms"
        self.assertTrue(response.headers["x-response-time"].endswith("ms"))

    def test_request_id_header_present(self) -> None:
        """Test X-Request-ID header is present in all responses."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertIn("x-request-id", response.headers)
        # Should be a valid UUID format (36 characters with hyphens)
        self.assertEqual(len(response.headers["x-request-id"]), 36)

    def test_slow_request_logging(self) -> None:
        """Test that slow requests (>1s) are logged."""
        import asyncio

        # Create a test endpoint that sleeps (note: this endpoint persists on the
        # shared application, but is necessary for testing timing behavior)
        from app.main import fastapi_application

        @fastapi_application.get("/slow-test")
        async def slow_endpoint() -> dict[str, str]:
            await asyncio.sleep(1.1)  # Sleep for >1s
            return {"status": "slow"}

        with patch("app.main.logger.warning") as mock_logger:
            # Make request to slow endpoint
            response = self.client.get("/slow-test")

            self.assertEqual(response.status_code, 200)
            # Verify logger.warning was called for slow request
            mock_logger.assert_called_once()
            call_args = mock_logger.call_args
            self.assertIn("Slow request detected", call_args[0][0])
            self.assertIn("extra", call_args[1])
            self.assertIn("duration_ms", call_args[1]["extra"])
            # Verify the logged duration is >= 1000ms (threshold for slow requests)
            duration_str = call_args[1]["extra"]["duration_ms"]
            duration_value = float(duration_str)
            self.assertGreaterEqual(
                duration_value,
                1000.0,
                f"Duration {duration_value}ms should be >= 1000ms",
            )

    def test_custom_headers_present(self) -> None:
        """Test that X-Request-ID and X-Response-Time headers are present."""
        # Make a GET request with an Origin header to exercise CORS middleware
        response = self.client.get(
            "/health",
            headers={"Origin": "http://localhost:5000"},
        )

        self.assertEqual(response.status_code, 200)
        # These headers must be present so that they can be exposed to browsers via CORS
        self.assertIn("x-request-id", response.headers)
        self.assertIn("x-response-time", response.headers)
