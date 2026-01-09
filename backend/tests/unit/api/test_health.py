"""Unit tests for health check endpoint."""

import unittest

import pytest

from tests.conftest import FixtureAttrs


@pytest.mark.smoke
class TestHealthCheck(FixtureAttrs, unittest.TestCase):
    """Test health check endpoint."""

    def test_health_check(self) -> None:
        """Test health check endpoint returns correct response."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "0.1.0")
