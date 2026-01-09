"""Test main application module.

Tests cover application setup, lifespan events, and basic functionality.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_app_creates_successfully(client: TestClient) -> None:
    """Test that the FastAPI application can be created."""
    assert client.app is not None
    assert client.app.title == "Luminote API"  # type: ignore[attr-defined]
    assert client.app.version == "0.1.0"  # type: ignore[attr-defined]


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
