"""Unit tests for main application module.

Tests cover application setup, lifespan events, and basic functionality.
"""

import unittest

import pytest

from tests.conftest import FixtureAttrs


class TestMainApplication(FixtureAttrs, unittest.TestCase):
    """Unit tests for main application."""

    @pytest.mark.smoke
    def test_app_creates_successfully(self) -> None:
        """Test that the FastAPI application can be created."""
        self.assertIsNotNone(self.client.app)
        self.assertEqual(self.client.app.title, "Luminote API")  # type: ignore[attr-defined]
        self.assertEqual(self.client.app.version, "0.1.0")  # type: ignore[attr-defined]

    @pytest.mark.smoke
    def test_docs_endpoint_available(self) -> None:
        """Test that API docs endpoint is available."""
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)

    @pytest.mark.smoke
    def test_redoc_endpoint_available(self) -> None:
        """Test that ReDoc endpoint is available."""
        response = self.client.get("/redoc")
        self.assertEqual(response.status_code, 200)
