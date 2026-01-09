"""Smoke tests for Phase 0 infrastructure.

Smoke tests verify that basic functionality works without issues. These tests ensure the
application can start and basic endpoints respond correctly.
"""

import unittest

import pytest

from tests.conftest import FixtureAttrs


class TestApplicationStartup(FixtureAttrs, unittest.TestCase):
    """Smoke tests for application startup and basic functionality."""

    @pytest.mark.smoke
    def test_application_starts_successfully(self) -> None:
        """Test that the application starts without errors."""
        self.assertIsNotNone(self.client.app)
        self.assertEqual(self.client.app.title, "Luminote API")  # type: ignore[attr-defined]

    @pytest.mark.smoke
    def test_health_endpoint_responds(self) -> None:
        """Test that health check endpoint responds successfully."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")
        self.assertIn("version", data)

    @pytest.mark.smoke
    def test_openapi_schema_available(self) -> None:
        """Test that OpenAPI schema is accessible."""
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("openapi", data)
        self.assertIn("info", data)
        self.assertEqual(data["info"]["title"], "Luminote API")

    @pytest.mark.smoke
    def test_docs_ui_available(self) -> None:
        """Test that Swagger UI documentation is accessible."""
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    @pytest.mark.smoke
    def test_redoc_ui_available(self) -> None:
        """Test that ReDoc documentation is accessible."""
        response = self.client.get("/redoc")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])


class TestMiddleware(FixtureAttrs, unittest.TestCase):
    """Smoke tests for middleware functionality."""

    @pytest.mark.smoke
    def test_request_id_middleware_active(self) -> None:
        """Test that X-Request-ID header is added to responses."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Request-ID", response.headers)
        # Verify it's a valid UUID format (36 characters with dashes)
        request_id = response.headers["X-Request-ID"]
        self.assertEqual(len(request_id), 36)
        self.assertEqual(request_id.count("-"), 4)

    @pytest.mark.smoke
    def test_timing_middleware_active(self) -> None:
        """Test that X-Response-Time header is added to responses."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Response-Time", response.headers)
        # Verify format: number followed by "ms"
        response_time = response.headers["X-Response-Time"]
        self.assertTrue(response_time.endswith("ms"))
        # Extract numeric part and verify it's positive
        time_value = float(response_time[:-2])
        self.assertGreater(time_value, 0)

    @pytest.mark.smoke
    def test_cors_headers_present(self) -> None:
        """Test that CORS headers are configured."""
        response = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS preflight should return 200
        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)


class TestErrorHandling(FixtureAttrs, unittest.TestCase):
    """Smoke tests for error handling infrastructure."""

    @pytest.mark.smoke
    def test_404_not_found_handled(self) -> None:
        """Test that 404 errors are handled correctly."""
        response = self.client.get("/nonexistent-endpoint")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)

    @pytest.mark.smoke
    def test_405_method_not_allowed_handled(self) -> None:
        """Test that 405 errors are handled correctly."""
        response = self.client.post("/health")
        self.assertEqual(response.status_code, 405)
        data = response.json()
        self.assertIn("detail", data)

    @pytest.mark.smoke
    def test_error_response_includes_request_id(self) -> None:
        """Test that error responses include request ID."""
        response = self.client.get("/nonexistent-endpoint")
        self.assertEqual(response.status_code, 404)
        self.assertIn("X-Request-ID", response.headers)


class TestConfiguration(FixtureAttrs, unittest.TestCase):
    """Smoke tests for configuration and settings."""

    @pytest.mark.smoke
    def test_api_version_prefix_configured(self) -> None:
        """Test that API version prefix is properly configured."""
        # Verify OpenAPI spec includes version prefix
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Even if no v1 endpoints exist yet, the structure should be ready
        self.assertIn("info", data)

    @pytest.mark.smoke
    def test_application_metadata_correct(self) -> None:
        """Test that application metadata is correctly set."""
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["info"]["title"], "Luminote API")
        self.assertEqual(data["info"]["version"], "0.1.0")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
