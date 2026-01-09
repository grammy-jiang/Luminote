"""Pytest configuration and fixtures."""

import unittest
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import fastapi_application
from tests.utils import create_mock_openai_response, create_sample_content


class FixtureAttrs:
    """Type-only mixin for injected pytest fixtures.

    These attributes are populated by the autouse fixture below for unittest.TestCase
    subclasses.
    """

    client: TestClient
    mock_openai_response: dict[str, Any]
    sample_content: dict[str, Any]


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application.

    Returns:
        TestClient instance
    """
    return TestClient(fastapi_application)


@pytest.fixture
def mock_openai_response() -> dict[str, Any]:
    """Create a mock OpenAI API response for testing.

    Returns:
        A dictionary mimicking OpenAI's response format
    """
    return create_mock_openai_response(
        content="This is a test translation.",
        model="gpt-4",
        role="assistant",
        finish_reason="stop",
    )


@pytest.fixture
def sample_content() -> dict[str, Any]:
    """Create sample content for testing extraction and translation.

    Returns:
        A dictionary with sample content data
    """
    return create_sample_content(
        title="Test Article",
        content="This is a test article with some content for testing purposes. "
        "It contains multiple sentences to simulate real content.",
        url="https://example.com/test-article",
        language="en",
    )


@pytest.fixture(autouse=True)
def _inject_unittest_fixtures(
    request: pytest.FixtureRequest,
    client: TestClient,
    mock_openai_response: dict[str, Any],
    sample_content: dict[str, Any],
) -> None:
    """Inject pytest fixtures into unittest.TestCase subclasses.

    Pytest does not pass fixtures as parameters to unittest.TestCase methods.
    Following pytest's documented pattern, this autouse fixture attaches the
    commonly used fixtures to TestCase classes so tests can access them via
    ``self`` (e.g., ``self.client``).
    """

    test_class = request.cls
    if test_class is not None and issubclass(test_class, unittest.TestCase):
        test_class.client = client
        test_class.mock_openai_response = mock_openai_response
        test_class.sample_content = sample_content
