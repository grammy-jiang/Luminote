# Luminote Error Codes Reference

This document provides a complete reference of all error codes returned by the
Luminote API, following
[ADR-004: Error Handling Patterns](../../docs/adr/004-error-handling-patterns.md).

## Error Response Format

All API errors follow this standard format:

```json
{
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "details": {
    "field": "value",
    "additional_context": "..."
  },
  "request_id": "uuid-v4-string"
}
```

### Response Headers

- `X-Request-ID`: Unique request identifier (UUID v4)
- `X-Response-Time`: Response time in milliseconds
- `Retry-After`: (Rate limit errors only) Seconds to wait before retrying

## Error Code Taxonomy

### Client Errors (4xx)

Errors caused by invalid client requests. Users can fix these by modifying their
request.

#### INVALID_URL

**Status Code:** 400 Bad Request

**Description:** The provided URL format is invalid or malformed.

**User Action:** Check the URL format and ensure it starts with `http://` or
`https://`.

**Example:**

```json
{
  "error": "Invalid URL format: not-a-valid-url",
  "code": "INVALID_URL",
  "details": {
    "url": "not-a-valid-url"
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### VALIDATION_ERROR

**Status Code:** 422 Unprocessable Entity

**Description:** Request data failed Pydantic validation. One or more required
fields are missing or have invalid values.

**User Action:** Review the error details and correct the specified fields.

**Example:**

```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "errors": [
      {
        "field": "body.target_language",
        "message": "field required"
      }
    ]
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### EXTRACTION_ERROR

**Status Code:** 422 Unprocessable Entity

**Description:** Content extraction from the URL failed. The page may be
inaccessible, require authentication, or have no extractable content.

**User Action:** Verify the URL is accessible and contains readable content.
Consider copying and pasting text instead.

**Example:**

```json
{
  "error": "Failed to extract content from https://example.com: Connection timeout",
  "code": "EXTRACTION_ERROR",
  "details": {
    "url": "https://example.com",
    "reason": "Connection timeout"
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### API_KEY_ERROR

**Status Code:** 401 Unauthorized

**Description:** API key validation or authentication failed. The key may be
invalid, expired, or have incorrect format.

**User Action:** Verify your API key is correct and active with the provider.

**Example:**

```json
{
  "error": "API key error for openai: Invalid or missing API key",
  "code": "API_KEY_ERROR",
  "details": {
    "provider": "openai",
    "reason": "Invalid or missing API key"
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### RATE_LIMIT_EXCEEDED

**Status Code:** 429 Too Many Requests

**Description:** Rate limit has been exceeded. Too many requests sent in a given
time period.

**User Action:** Wait for the specified retry_after period before making another
request.

**Response Headers:** `Retry-After: {seconds}`

**Example:**

```json
{
  "error": "Rate limit exceeded. Retry after 60 seconds. (Provider: openai)",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "retry_after": 60,
    "provider": "openai"
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Server Errors (5xx)

Errors caused by server-side issues or external service failures. These are
typically temporary and users should retry.

#### EXTERNAL_SERVICE_ERROR

**Status Code:** 500 Internal Server Error

**Description:** An external service (AI provider, web scraping service) failed
or returned an error.

**User Action:** Try again in a few moments. If the issue persists, the external
service may be experiencing downtime.

**Example:**

```json
{
  "error": "External service 'openai' error: API unavailable",
  "code": "EXTERNAL_SERVICE_ERROR",
  "details": {
    "service": "openai",
    "reason": "API unavailable"
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### URL_FETCH_ERROR

**Status Code:** 502 Bad Gateway (unreachable) or 504 Gateway Timeout (timeout)

**Description:** Failed to fetch content from the specified URL due to network
error, unreachable host, or timeout.

**User Action:** Verify the URL is correct and accessible. Check if the site is
down or blocking automated access.

**Example:**

```json
{
  "error": "Failed to fetch URL https://example.com: Connection timeout",
  "code": "URL_FETCH_ERROR",
  "details": {
    "url": "https://example.com",
    "reason": "Connection timeout"
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### TRANSLATION_ERROR

**Status Code:** 500 Internal Server Error

**Description:** Translation request failed. This may be due to provider API
errors, invalid model specifications, or content processing issues.

**User Action:** Try again. If the issue persists, verify your API key and model
settings.

**Example:**

```json
{
  "error": "Translation failed using openai/gpt-4: Service unavailable",
  "code": "TRANSLATION_ERROR",
  "details": {
    "provider": "openai",
    "model": "gpt-4",
    "reason": "Service unavailable"
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### PROVIDER_TIMEOUT

**Status Code:** 504 Gateway Timeout

**Description:** The AI provider request exceeded the timeout limit and was
cancelled.

**User Action:** Try again with a shorter content or different model. Provider
may be experiencing high load.

**Example:**

```json
{
  "error": "Provider openai request timed out for model gpt-4: Request timed out",
  "code": "PROVIDER_TIMEOUT",
  "details": {
    "provider": "openai",
    "model": "gpt-4",
    "reason": "Request timed out"
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### INTERNAL_ERROR

**Status Code:** 500 Internal Server Error

**Description:** An unexpected error occurred that was not explicitly handled.
This indicates a bug or unexpected condition.

**User Action:** Report this error with the request_id to the development team.

**Example:**

```json
{
  "error": "An unexpected error occurred",
  "code": "INTERNAL_ERROR",
  "details": {},
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## Error Code Summary Table

| Code                     | Status  | Category | Retryable | User Action                |
| ------------------------ | ------- | -------- | --------- | -------------------------- |
| `INVALID_URL`            | 400     | Client   | No        | Fix URL format             |
| `VALIDATION_ERROR`       | 422     | Client   | No        | Fix request data           |
| `EXTRACTION_ERROR`       | 422     | Client   | Maybe     | Check URL accessibility    |
| `API_KEY_ERROR`          | 401     | Client   | No        | Verify API key             |
| `RATE_LIMIT_EXCEEDED`    | 429     | Client   | Yes       | Wait and retry             |
| `EXTERNAL_SERVICE_ERROR` | 500     | Server   | Yes       | Retry later                |
| `URL_FETCH_ERROR`        | 502/504 | Server   | Yes       | Check URL/retry            |
| `TRANSLATION_ERROR`      | 500     | Server   | Yes       | Retry                      |
| `PROVIDER_TIMEOUT`       | 504     | Server   | Yes       | Retry with shorter content |
| `INTERNAL_ERROR`         | 500     | Server   | Yes       | Report to developers       |

## HTTP Status Code Mapping

### 400 Bad Request

- `INVALID_URL`: Malformed URL

### 401 Unauthorized

- `API_KEY_ERROR`: Invalid or missing API key

### 422 Unprocessable Entity

- `VALIDATION_ERROR`: Request validation failed
- `EXTRACTION_ERROR`: Content extraction failed

### 429 Too Many Requests

- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded

### 500 Internal Server Error

- `EXTERNAL_SERVICE_ERROR`: External service failure
- `TRANSLATION_ERROR`: Translation failed
- `INTERNAL_ERROR`: Unexpected error

### 502 Bad Gateway

- `URL_FETCH_ERROR`: Cannot reach URL

### 504 Gateway Timeout

- `URL_FETCH_ERROR`: URL fetch timeout
- `PROVIDER_TIMEOUT`: AI provider timeout

## Usage Examples

### Frontend Error Handling

```typescript
async function handleAPICall() {
  try {
    const response = await fetch('/api/v1/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com' })
    });

    if (!response.ok) {
      const error = await response.json();

      // Handle specific error codes
      switch (error.code) {
        case 'INVALID_URL':
          showError('Please enter a valid URL');
          break;
        case 'RATE_LIMIT_EXCEEDED':
          const retryAfter = error.details.retry_after;
          showError(`Rate limit exceeded. Please wait ${retryAfter} seconds.`);
          break;
        case 'API_KEY_ERROR':
          showError('Invalid API key. Please check your settings.');
          break;
        default:
          showError(`Error: ${error.error}`);
      }

      // Log request ID for debugging
      console.error(`Request ID: ${error.request_id}`);
    }
  } catch (err) {
    showError('Network error. Please check your connection.');
  }
}
```

### Backend Exception Raising

```python
from app.core.errors import InvalidURLError, RateLimitError

# Validate URL
if not url.startswith(('http://', 'https://')):
    raise InvalidURLError(url)

# Check rate limit
if requests_count > limit:
    raise RateLimitError(retry_after=60, provider="openai")
```

## Debugging with Request IDs

Every error response includes a `request_id` field that uniquely identifies the
request. This ID appears in:

1. **Response header**: `X-Request-ID`
1. **Response body**: `request_id` field
1. **Server logs**: All log entries for that request

To debug an error:

1. Copy the `request_id` from the error response
1. Search server logs for that request ID
1. Review the full request context and stack trace

## Related Documentation

- [ADR-004: Error Handling Patterns](../../docs/adr/004-error-handling-patterns.md)
- [Backend API Layer Instructions](../../.github/instructions/backend-api.instructions.md)
- [Backend Core Instructions](../../.github/instructions/backend-core.instructions.md)

## Changelog

- **2026-01-11**: Initial version documenting all error codes
