"""
Test main application module.

Tests cover application setup, lifespan events, and basic functionality.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_app_creates_successfully(client: TestClient) -> None:
    """Test that the FastAPI application can be created."""
    assert client.app is not None
    assert client.app.title == "Luminote API"
    assert client.app.version == "0.1.0"


@pytest.mark.smoke
def test_health_endpoint_available(client: TestClient) -> None:
    """Test that health endpoint is available."""
    response = client.get("/health")
    assert response.status_code == 200


@pytest.mark.smoke
def test_docs_endpoint_available(client: TestClient) -> None:
    """Test that API docs endpoint is available."""
    response = client.get("/docs")
    assert response.status_code == 200


@pytest.mark.smoke
def test_redoc_endpoint_available(client: TestClient) -> None:
    """Test that ReDoc endpoint is available."""
    response = client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.unit
def test_app_has_cors_middleware(client: TestClient) -> None:
    """Test that CORS middleware is configured."""
    response = client.get("/health", headers={"Origin": "http://localhost:5000"})
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers


@pytest.mark.unit
def test_app_has_request_id_middleware(client: TestClient) -> None:
    """Test that request ID middleware is configured."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers


@pytest.mark.unit
def test_app_has_timing_middleware(client: TestClient) -> None:
    """Test that timing middleware is configured."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-response-time" in response.headers
    assert response.headers["x-response-time"].endswith("ms")
