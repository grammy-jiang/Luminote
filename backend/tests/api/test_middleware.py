"""
Test CORS and timing middleware.
"""

import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient


@pytest.mark.unit
def test_cors_headers_present(client: TestClient) -> None:
    """Test CORS headers are present in response."""
    response = client.get("/health", headers={"Origin": "http://localhost:5000"})

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:5000"
    assert "access-control-allow-credentials" in response.headers
    assert response.headers["access-control-allow-credentials"] == "true"


@pytest.mark.unit
def test_cors_preflight_request(client: TestClient) -> None:
    """Test CORS preflight OPTIONS request works correctly."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:5000"
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers
    assert "access-control-allow-credentials" in response.headers


@pytest.mark.unit
def test_cors_invalid_origin(client: TestClient) -> None:
    """Test CORS headers not present for invalid origin."""
    response = client.get("/health", headers={"Origin": "http://malicious.com"})

    assert response.status_code == 200
    # CORS middleware should not set allow-origin for invalid origins
    # Note: The header won't be present if origin is not allowed
    assert (
        "access-control-allow-origin" not in response.headers
        or response.headers["access-control-allow-origin"] != "http://malicious.com"
    )


@pytest.mark.unit
def test_timing_header_present(client: TestClient) -> None:
    """Test X-Response-Time header is present in all responses."""
    response = client.get("/health")

    assert response.status_code == 200
    assert "x-response-time" in response.headers
    # Should be in format like "1.23ms"
    assert response.headers["x-response-time"].endswith("ms")


@pytest.mark.unit
def test_request_id_header_present(client: TestClient) -> None:
    """Test X-Request-ID header is present in all responses."""
    response = client.get("/health")

    assert response.status_code == 200
    assert "x-request-id" in response.headers
    # Should be a valid UUID format (36 characters with hyphens)
    assert len(response.headers["x-request-id"]) == 36


@pytest.mark.unit
def test_slow_request_logging(client: TestClient) -> None:
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
        response = client.get("/slow-test")

        assert response.status_code == 200
        # Verify logger.warning was called for slow request
        mock_logger.assert_called_once()
        call_args = mock_logger.call_args
        assert "Slow request detected" in call_args[0][0]
        assert "extra" in call_args[1]
        assert "duration_ms" in call_args[1]["extra"]
        # Verify the logged duration is >= 1000ms (threshold for slow requests)
        duration_str = call_args[1]["extra"]["duration_ms"]
        duration_value = float(duration_str)
        assert (
            duration_value >= 1000.0
        ), f"Duration {duration_value}ms should be >= 1000ms"


@pytest.mark.unit
def test_custom_headers_present(client: TestClient) -> None:
    """Test that X-Request-ID and X-Response-Time headers are present."""
    # Make a GET request with an Origin header to exercise CORS middleware
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:5000"},
    )

    assert response.status_code == 200
    # These headers must be present so that they can be exposed to browsers via CORS
    assert "x-request-id" in response.headers
    assert "x-response-time" in response.headers
