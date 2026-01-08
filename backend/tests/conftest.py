"""
Pytest configuration and fixtures.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import fastapi_application
from tests.utils import create_mock_openai_response, create_sample_content


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient instance
    """
    return TestClient(fastapi_application)


@pytest.fixture
def mock_openai_response() -> dict[str, Any]:
    """
    Create a mock OpenAI API response for testing.

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
    """
    Create sample content for testing extraction and translation.

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
