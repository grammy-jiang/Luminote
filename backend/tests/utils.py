"""
Test utilities for Luminote backend.

Helper functions for test data generation, mock HTTP responses, and common test operations.
"""

import uuid
from typing import Any


def generate_request_id() -> str:
    """
    Generate a valid request ID (UUID v4).

    Returns:
        A UUID v4 string
    """
    return str(uuid.uuid4())


def validate_request_id(request_id: str) -> bool:
    """
    Validate that a string is a valid UUID v4 request ID.

    Args:
        request_id: The request ID to validate

    Returns:
        True if valid UUID v4, False otherwise
    """
    try:
        uuid_obj = uuid.UUID(request_id)
        return uuid_obj.version == 4 and str(uuid_obj) == request_id
    except (ValueError, AttributeError):
        return False


def create_mock_openai_response(
    content: str,
    model: str = "gpt-4",
    role: str = "assistant",
    finish_reason: str = "stop",
) -> dict[str, Any]:
    """
    Create a mock OpenAI API response.

    Args:
        content: The response content
        model: The model name
        role: The message role
        finish_reason: The finish reason

    Returns:
        A dictionary mimicking OpenAI's response format
    """
    return {
        "id": f"chatcmpl-{generate_request_id()}",
        "object": "chat.completion",
        "created": 1234567890,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": role, "content": content},
                "finish_reason": finish_reason,
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


def create_mock_anthropic_response(
    content: str,
    model: str = "claude-3-5-sonnet-20241022",
    stop_reason: str = "end_turn",
) -> dict[str, Any]:
    """
    Create a mock Anthropic API response.

    Args:
        content: The response content
        model: The model name
        stop_reason: The stop reason

    Returns:
        A dictionary mimicking Anthropic's response format
    """
    return {
        "id": f"msg_{generate_request_id()}",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": content}],
        "model": model,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 20},
    }


def create_mock_http_response(
    status_code: int = 200,
    json_data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    text: str | None = None,
) -> dict[str, Any]:
    """
    Create a mock HTTP response for testing.

    Args:
        status_code: HTTP status code
        json_data: JSON response data
        headers: Response headers
        text: Response text (if not using json_data)

    Returns:
        A dictionary with response data
    """
    response = {"status_code": status_code, "headers": headers or {}}

    if json_data is not None:
        response["json"] = json_data
    if text is not None:
        response["text"] = text

    return response


def create_sample_content(
    title: str = "Sample Article",
    content: str = "This is sample content for testing.",
    url: str = "https://example.com/article",
    language: str = "en",
) -> dict[str, Any]:
    """
    Create sample content for testing extraction and translation.

    Args:
        title: Article title
        content: Article content
        url: Source URL
        language: Content language

    Returns:
        A dictionary with sample content data
    """
    return {
        "title": title,
        "content": content,
        "url": url,
        "language": language,
        "word_count": len(content.split()),
        "author": "Test Author",
        "published_date": "2024-01-01",
    }


def create_translation_request(
    text: str = "Hello world",
    source_lang: str = "en",
    target_lang: str = "es",
    provider: str = "openai",
    model: str = "gpt-4",
) -> dict[str, Any]:
    """
    Create a sample translation request.

    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        provider: AI provider name
        model: Model name

    Returns:
        A dictionary with translation request data
    """
    return {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "provider": provider,
        "model": model,
    }


def create_error_response(
    error: str = "An error occurred",
    code: str = "TEST_ERROR",
    status_code: int = 500,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Create a mock error response following ADR-004.

    Args:
        error: Error message
        code: Error code
        status_code: HTTP status code
        details: Additional error details
        request_id: Request ID (generates one if not provided)

    Returns:
        A dictionary with error response data
    """
    return {
        "error": error,
        "code": code,
        "status_code": status_code,
        "details": details or {},
        "request_id": request_id or generate_request_id(),
    }
