"""Example unit tests demonstrating fixture usage.

These tests demonstrate how to use the mock_openai_response and sample_content fixtures.
"""

import unittest

import pytest

from tests.conftest import FixtureAttrs
from tests.utils import validate_request_id


@pytest.mark.unit
class TestFixtures(FixtureAttrs, unittest.TestCase):
    """Test fixtures and utilities."""

    def test_mock_openai_response_fixture(self) -> None:
        """Test that mock_openai_response fixture provides valid OpenAI response
        format."""
        self.assertIn("id", self.mock_openai_response)
        self.assertIn("object", self.mock_openai_response)
        self.assertEqual(self.mock_openai_response["object"], "chat.completion")
        self.assertIn("choices", self.mock_openai_response)
        self.assertGreater(len(self.mock_openai_response["choices"]), 0)
        self.assertIn("message", self.mock_openai_response["choices"][0])
        self.assertEqual(
            self.mock_openai_response["choices"][0]["message"]["role"], "assistant"
        )
        self.assertEqual(
            self.mock_openai_response["choices"][0]["message"]["content"],
            "This is a test translation.",
        )

    def test_sample_content_fixture(self) -> None:
        """Test that sample_content fixture provides valid content structure."""
        self.assertIn("title", self.sample_content)
        self.assertEqual(self.sample_content["title"], "Test Article")
        self.assertIn("content", self.sample_content)
        self.assertIn("url", self.sample_content)
        self.assertEqual(self.sample_content["url"], "https://example.com/test-article")
        self.assertIn("language", self.sample_content)
        self.assertEqual(self.sample_content["language"], "en")
        self.assertIn("word_count", self.sample_content)
        self.assertGreater(self.sample_content["word_count"], 0)

    def test_validate_request_id_with_real_response(self) -> None:
        """Test that validate_request_id utility works with actual API responses."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("x-request-id", response.headers)

        request_id = response.headers["x-request-id"]
        # Should be a valid UUID v4
        self.assertTrue(validate_request_id(request_id))

    def test_fixtures_integration(self) -> None:
        """Test using multiple fixtures together in a single test."""
        # Verify client works
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

        # Verify sample content has required fields
        self.assertIn("content", self.sample_content)
        self.assertGreater(len(self.sample_content["content"]), 0)

        # Verify mock response has expected structure
        self.assertIn("choices", self.mock_openai_response)
        self.assertGreater(len(self.mock_openai_response["choices"]), 0)

        # Validate request ID from response
        request_id = response.headers["x-request-id"]
        self.assertTrue(validate_request_id(request_id))
