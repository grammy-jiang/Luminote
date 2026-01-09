"""End-to-end tests for Phase 0 infrastructure.

E2E tests cover complete user workflows and verify the entire application stack works
together correctly. These tests simulate real user interactions.
"""

import unittest

import pytest

from app.core.errors import (
    LuminoteException,
    RateLimitError,
)
from tests.conftest import FixtureAttrs


class TestUserWorkflowHealthCheck(FixtureAttrs, unittest.TestCase):
    """E2E tests for user checking application health."""

    @pytest.mark.e2e
    def test_complete_health_check_workflow(self) -> None:
        """Test complete workflow: user checks if application is healthy.

        Workflow:
        1. User makes GET request to /health
        2. Application processes request through all middleware
        3. Response includes health status, version, and proper headers
        """
        # Step 1: User requests health check
        response = self.client.get("/health")

        # Step 2: Verify successful response
        self.assertEqual(response.status_code, 200)

        # Step 3: Verify response body
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "0.1.0")

        # Step 4: Verify middleware headers were added
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Response-Time", response.headers)

        # Step 5: Verify request ID is valid UUID format
        request_id = response.headers["X-Request-ID"]
        self.assertEqual(len(request_id), 36)
        self.assertEqual(request_id.count("-"), 4)

        # Step 6: Verify response time is reasonable (< 1000ms)
        response_time = response.headers["X-Response-Time"]
        time_value = float(response_time[:-2])
        self.assertLess(time_value, 1000.0)


class TestUserWorkflowDocumentation(FixtureAttrs, unittest.TestCase):
    """E2E tests for user accessing API documentation."""

    @pytest.mark.e2e
    def test_complete_api_documentation_workflow(self) -> None:
        """Test complete workflow: developer explores API documentation.

        Workflow:
        1. Developer navigates to /docs
        2. Documentation page loads successfully
        3. OpenAPI schema is accessible
        4. All expected endpoints are documented
        """
        # Step 1: Developer accesses Swagger UI
        docs_response = self.client.get("/docs")
        self.assertEqual(docs_response.status_code, 200)
        self.assertIn("text/html", docs_response.headers["content-type"])

        # Step 2: Developer accesses ReDoc alternative
        redoc_response = self.client.get("/redoc")
        self.assertEqual(redoc_response.status_code, 200)
        self.assertIn("text/html", redoc_response.headers["content-type"])

        # Step 3: Developer fetches OpenAPI schema
        schema_response = self.client.get("/openapi.json")
        self.assertEqual(schema_response.status_code, 200)
        schema = schema_response.json()

        # Step 4: Verify schema completeness
        self.assertIn("openapi", schema)
        self.assertIn("info", schema)
        self.assertIn("paths", schema)

        # Step 5: Verify health endpoint is documented
        self.assertIn("/health", schema["paths"])
        self.assertIn("get", schema["paths"]["/health"])


class TestUserWorkflowErrorHandling(FixtureAttrs, unittest.TestCase):
    """E2E tests for user experiencing various error conditions."""

    @pytest.mark.e2e
    def test_workflow_endpoint_not_found(self) -> None:
        """Test complete workflow: user requests non-existent endpoint.

        Workflow:
        1. User makes request to invalid endpoint
        2. Application handles 404 gracefully
        3. Error response includes proper structure and headers
        """
        # Step 1: User requests non-existent endpoint
        response = self.client.get("/api/v1/nonexistent")

        # Step 2: Verify 404 response
        self.assertEqual(response.status_code, 404)

        # Step 3: Verify error response structure
        data = response.json()
        self.assertIn("detail", data)

        # Step 4: Verify tracking headers present
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Response-Time", response.headers)

    @pytest.mark.e2e
    def test_workflow_method_not_allowed(self) -> None:
        """Test complete workflow: user uses wrong HTTP method.

        Workflow:
        1. User attempts POST on GET-only endpoint
        2. Application returns 405 Method Not Allowed
        3. Error is properly formatted
        """
        # Step 1: User attempts wrong method
        response = self.client.post("/health")

        # Step 2: Verify 405 response
        self.assertEqual(response.status_code, 405)

        # Step 3: Verify error response
        data = response.json()
        self.assertIn("detail", data)

        # Step 4: Verify headers
        self.assertIn("X-Request-ID", response.headers)


class TestUserWorkflowCORS(FixtureAttrs, unittest.TestCase):
    """E2E tests for user making cross-origin requests (frontend to backend)."""

    @pytest.mark.e2e
    def test_complete_cors_preflight_workflow(self) -> None:
        """Test complete workflow: browser makes CORS preflight request.

        Workflow:
        1. Browser sends OPTIONS preflight request
        2. Server responds with CORS headers
        3. Browser determines request is allowed
        4. Actual request proceeds
        """
        # Step 1: Browser sends preflight request
        preflight_response = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        # Step 2: Verify preflight succeeds
        self.assertEqual(preflight_response.status_code, 200)

        # Step 3: Verify CORS headers present
        self.assertIn("access-control-allow-origin", preflight_response.headers)
        self.assertIn("access-control-allow-methods", preflight_response.headers)

        # Step 4: Make actual request with Origin header
        actual_response = self.client.get(
            "/health", headers={"Origin": "http://localhost:5000"}
        )

        # Step 5: Verify actual request succeeds
        self.assertEqual(actual_response.status_code, 200)
        self.assertIn("access-control-allow-origin", actual_response.headers)

    @pytest.mark.e2e
    def test_cors_exposed_headers_workflow(self) -> None:
        """Test workflow: frontend can access custom headers.

        Workflow:
        1. Frontend makes request
        2. Backend adds custom headers (X-Request-ID, X-Response-Time)
        3. CORS exposes these headers to frontend
        4. Frontend can read the headers
        """
        # Step 1: Frontend makes request
        response = self.client.get(
            "/health", headers={"Origin": "http://localhost:5000"}
        )

        # Step 2: Verify response successful
        self.assertEqual(response.status_code, 200)

        # Step 3: Verify custom headers present
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Response-Time", response.headers)

        # Step 4: Verify CORS exposes custom headers
        # (The middleware should expose X-Request-ID and X-Response-Time)
        self.assertIn("access-control-expose-headers", response.headers)
        exposed = response.headers["access-control-expose-headers"]
        self.assertIn("X-Request-ID", exposed)
        self.assertIn("X-Response-Time", exposed)


class TestUserWorkflowCustomErrors(FixtureAttrs, unittest.TestCase):
    """E2E tests for user experiencing custom application errors."""

    @pytest.mark.e2e
    def test_workflow_luminote_exception_handling(self) -> None:
        """Test complete workflow: custom error is raised and handled.

        Workflow:
        1. Endpoint raises LuminoteException
        2. Exception handler catches it
        3. Proper error response returned with all context
        """
        # Create a test endpoint that raises LuminoteException
        from fastapi import APIRouter

        test_router = APIRouter()

        @test_router.get("/test-error")
        async def test_error_endpoint() -> None:
            raise LuminoteException(
                code="TEST_ERROR",
                message="This is a test error",
                status_code=400,
                details={"test_field": "test_value"},
            )

        # Add router to app
        self.client.app.include_router(test_router)  # type: ignore[attr-defined]

        # Step 1: User triggers error
        response = self.client.get("/test-error")

        # Step 2: Verify error response
        self.assertEqual(response.status_code, 400)
        data = response.json()

        # Step 3: Verify error structure
        self.assertEqual(data["error"], "This is a test error")
        self.assertEqual(data["code"], "TEST_ERROR")
        self.assertIn("details", data)
        self.assertEqual(data["details"]["test_field"], "test_value")

        # Step 4: Verify request tracking
        self.assertIn("request_id", data)
        self.assertIn("X-Request-ID", response.headers)
        self.assertEqual(data["request_id"], response.headers["X-Request-ID"])

    @pytest.mark.e2e
    def test_workflow_rate_limit_error_with_retry_after(self) -> None:
        """Test complete workflow: rate limit error includes Retry-After header.

        Workflow:
        1. User hits rate limit
        2. RateLimitError is raised
        3. Response includes Retry-After header
        4. User knows when to retry
        """
        # Create test endpoint that raises RateLimitError
        from fastapi import APIRouter

        test_router = APIRouter()

        @test_router.get("/test-rate-limit")
        async def test_rate_limit_endpoint() -> None:
            raise RateLimitError(retry_after=60, provider="test_provider")

        # Add router to app
        self.client.app.include_router(test_router)  # type: ignore[attr-defined]

        # Step 1: User hits rate limit
        response = self.client.get("/test-rate-limit")

        # Step 2: Verify 429 status
        self.assertEqual(response.status_code, 429)

        # Step 3: Verify Retry-After header
        self.assertIn("Retry-After", response.headers)
        self.assertEqual(response.headers["Retry-After"], "60")

        # Step 4: Verify error response
        data = response.json()
        self.assertEqual(data["code"], "RATE_LIMIT_EXCEEDED")
        self.assertIn("retry_after", data["details"])
        self.assertEqual(data["details"]["retry_after"], 60)


class TestUserWorkflowValidation(FixtureAttrs, unittest.TestCase):
    """E2E tests for user submitting invalid data."""

    @pytest.mark.e2e
    def test_workflow_pydantic_validation_error(self) -> None:
        """Test complete workflow: user submits invalid request data.

        Workflow:
        1. User submits request with validation errors
        2. Pydantic validates and rejects
        3. Validation exception handler formats errors
        4. User receives clear error messages
        """
        # Create test endpoint with Pydantic validation
        from fastapi import APIRouter
        from pydantic import BaseModel, Field

        test_router = APIRouter()

        class TestRequest(BaseModel):
            name: str = Field(..., min_length=3)
            age: int = Field(..., ge=0, le=150)

        @test_router.post("/test-validation")
        async def test_validation_endpoint(data: TestRequest) -> dict[str, str]:
            return {"status": "ok"}

        # Add router to app
        self.client.app.include_router(test_router)  # type: ignore[attr-defined]

        # Step 1: User submits invalid data (missing required fields)
        response = self.client.post("/test-validation", json={})

        # Step 2: Verify 422 validation error
        self.assertEqual(response.status_code, 422)

        # Step 3: Verify error structure
        data = response.json()
        self.assertEqual(data["code"], "VALIDATION_ERROR")
        self.assertEqual(data["error"], "Validation failed")

        # Step 4: Verify detailed error information
        self.assertIn("details", data)
        self.assertIn("errors", data["details"])
        errors = data["details"]["errors"]
        self.assertGreater(len(errors), 0)

        # Step 5: Verify tracking headers
        self.assertIn("request_id", data)
        self.assertIn("X-Request-ID", response.headers)


class TestIntegrationMiddlewareStack(FixtureAttrs, unittest.TestCase):
    """E2E tests for complete middleware stack integration."""

    @pytest.mark.e2e
    def test_middleware_execution_order(self) -> None:
        """Test that middleware executes in correct order.

        Workflow:
        1. Request enters middleware stack
        2. Request ID added (executes first)
        3. Timing started
        4. Request processed
        5. Response generated
        6. Timing completed and header added
        7. Request ID header added
        """
        # Make request
        response = self.client.get("/health")

        # Verify all middleware effects are present
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Response-Time", response.headers)

        # Verify both middleware added their headers
        request_id = response.headers["X-Request-ID"]
        self.assertEqual(len(request_id), 36)  # Valid UUID

        response_time = response.headers["X-Response-Time"]
        self.assertTrue(response_time.endswith("ms"))

    @pytest.mark.e2e
    def test_complete_request_lifecycle(self) -> None:
        """Test complete request lifecycle through all layers.

        Workflow:
        1. Request received
        2. CORS headers processed
        3. Request ID middleware adds tracking
        4. Timing middleware starts timer
        5. Endpoint handler executes
        6. Response generated
        7. Timing middleware adds duration
        8. Request ID middleware adds tracking header
        9. CORS headers added to response
        10. Response returned to client
        """
        # Step 1-9: Make request with CORS headers
        response = self.client.get(
            "/health",
            headers={
                "Origin": "http://localhost:5000",
                "Content-Type": "application/json",
            },
        )

        # Step 10: Verify complete response
        # Success status
        self.assertEqual(response.status_code, 200)

        # Body
        data = response.json()
        self.assertEqual(data["status"], "ok")

        # CORS headers
        self.assertIn("access-control-allow-origin", response.headers)

        # Middleware headers
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Response-Time", response.headers)

        # Verify all components working together
        self.assertTrue(len(response.headers["X-Request-ID"]) == 36)
        self.assertTrue(response.headers["X-Response-Time"].endswith("ms"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
