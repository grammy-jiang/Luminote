<!-- mdformat-toc start --slug=github --maxlevel=3 --minlevel=1 -->

- [Luminote API Reference](#luminote-api-reference)
  - [Overview](#overview)
  - [Endpoints](#endpoints)
    - [GET /health](#get-health)
    - [POST /fetch](#post-fetch)
    - [POST /extract](#post-extract)
    - [POST /translate](#post-translate)
  - [Configuration](#configuration)
  - [Error Handling](#error-handling)
  - [Rate Limiting](#rate-limiting)
  - [Security](#security)
  - [Related Documentation](#related-documentation)

<!-- mdformat-toc end -->

# Luminote API Reference<a name="luminote-api-reference"></a>

## Overview<a name="overview"></a>

The Luminote backend (FastAPI with Python 3.12+) provides a RESTful API for
content fetching, extraction, and translation. All endpoints are designed for
reliability, cost control, and consistent user experience.

**Technology Stack:**

- Backend: Python 3.12+ with FastAPI
- Package Management: `uv`
- Entry Point: `luminote serve` command

**Base URL:** `http://127.0.0.1:8000` (default development)

## Endpoints<a name="endpoints"></a>

### GET /health<a name="get-health"></a>

Health check and configuration validation.

**Purpose:** Verify API connectivity and provider configuration.

**Response:**

```json
{
  "status": "healthy",
  "provider": "openai",
  "model": "gpt-4o-mini"
}

```

**Status Codes:**

- `200` - Service healthy
- `503` - Service unavailable or misconfigured

______________________________________________________________________

### POST /fetch<a name="post-fetch"></a>

Retrieve raw content from a URL via backend proxy.

**Purpose:** Fetch web content server-side to handle CORS and provide consistent
access.

**Request:**

```json

{
  "url": "https://example.com/article"
}

```

**Response:**

```json

{
  "url": "https://example.com/article",
  "html": "<html>...</html>",
  "status_code": 200
}

```

**Status Codes:**

- `200` - Content fetched successfully
- `400` - Invalid URL
- `404` - URL not found
- `500` - Fetch failed

______________________________________________________________________

### POST /extract<a name="post-extract"></a>

Parse HTML content into reader-mode blocks.

**Purpose:** Extract structured, readable content from raw HTML.

**Request:**

```json

{
  "html": "<html>...</html>",
  "url": "https://example.com/article"
}

```

**Response:**

```json

{
  "title": "Article Title",
  "blocks": [
    {
      "id": "block-1",
      "type": "paragraph",
      "content": "First paragraph text...",
      "metadata": {}
    },
    {
      "id": "block-2",
      "type": "heading",
      "level": 2,
      "content": "Section Heading",
      "metadata": {}
    }
  ]
}

```

**Block Types:**

- `title` - Document title
- `heading` - Section heading (with `level`)
- `paragraph` - Text paragraph
- `list` - Ordered or unordered list
- `quote` - Blockquote
- `code` - Code block
- `image` - Image with caption

**Status Codes:**

- `200` - Extraction successful
- `400` - Invalid HTML
- `500` - Extraction failed

______________________________________________________________________

### POST /translate<a name="post-translate"></a>

Translate content blocks progressively using configured model.

**Purpose:** Translate extracted blocks with streaming support for progressive
rendering.

**Request:**

```json

{
  "blocks": [
    {
      "id": "block-1",
      "type": "paragraph",
      "content": "Source text..."
    }
  ],
  "target_lang": "zh",
  "source_lang": "auto"
}

```

**Response (streaming):**

```json

{
  "block_id": "block-1",
  "translation": "Translated text...",
  "status": "complete"
}

```

**Parameters:**

- `target_lang` - Target language code (required)
- `source_lang` - Source language code or "auto" for detection
- `blocks` - Array of content blocks to translate

**Status Codes:**

- `200` - Translation successful
- `400` - Invalid request
- `401` - Invalid API key
- `429` - Rate limit exceeded
- `500` - Translation failed

______________________________________________________________________

## Configuration<a name="configuration"></a>

API behavior is controlled via environment variables:

- `LUMINOTE_TARGET_LANG` - Default target language (e.g., `zh`, `en`, `ja`)
- `LUMINOTE_PROVIDER` - Provider ID (e.g., `openai`, `anthropic`)
- `LUMINOTE_MODEL` - Model name (e.g., `gpt-4o-mini`, `claude-3-5-sonnet`)
- `LUMINOTE_API_KEY` - API key for the chosen provider

See `.env.example` for full configuration options.

**Development Setup:**

```bash

cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
luminote serve  # Starts on port 8000

```

For complete setup instructions, see [../CONTRIBUTING.md](../CONTRIBUTING.md).

## Error Handling<a name="error-handling"></a>

All endpoints return consistent error responses:

```json

{
  "error": "Error message",
  "detail": "Detailed error information",
  "code": "ERROR_CODE"
}

```

**Common Error Codes:**

- `INVALID_URL` - Malformed URL
- `FETCH_FAILED` - Unable to fetch content
- `EXTRACTION_FAILED` - Unable to extract readable content
- `TRANSLATION_FAILED` - Translation service error
- `INVALID_API_KEY` - API key invalid or expired
- `RATE_LIMIT_EXCEEDED` - Provider rate limit hit

## Rate Limiting<a name="rate-limiting"></a>

Rate limits are enforced by the configured AI provider. The API does not
implement additional rate limiting at the application level in early phases.

## Security<a name="security"></a>

**BYOK (Bring Your Own Key):**

- API keys are configured server-side via environment variables
- Keys are never exposed to the frontend
- Frontend stores configuration (provider, model, language) locally but sends
  API key to backend for each request
- Backend uses provided key per request; does not store keys persistently
- Keys are sent only to the configured AI provider (OpenAI, Anthropic, etc.)

**Local Development:**

- API runs on `localhost` by default
- No authentication required for local development
- Production deployment should add authentication/authorization

**Design Principles:**

- User-controlled cost: All AI operations explicitly triggered
- Compliance-first: No automatic bypass of authentication or paywalls
- Multi-provider support: OpenAI, Anthropic, and extensible for future providers

For architecture details, see [../ARCHITECTURE.md](../ARCHITECTURE.md).

## Related Documentation<a name="related-documentation"></a>

- **Complete Design Document:**
  [feature-specifications.md](feature-specifications.md) - Full specifications
  for all phases
- **Architecture Overview:** [../ARCHITECTURE.md](../ARCHITECTURE.md) - System
  design and components
- **Development Guide:** [../CONTRIBUTING.md](../CONTRIBUTING.md) - Setup,
  standards, and workflow
- **Main Project:** [../README.md](../README.md) - Project overview and quick
  start
