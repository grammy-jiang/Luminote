---
applyTo: backend/app/api/**/*.py
excludeAgent: []
---

# Backend API Layer Instructions

This instruction file applies to all Python files in `backend/app/api/` - the
HTTP request/response handling layer.

## Layer Responsibilities

The API layer is **HTTP-only**. It should:

- ✅ Handle HTTP requests and responses
- ✅ Validate request data using Pydantic schemas
- ✅ Call business logic from `app/core/` or `app/services/`
- ✅ Format responses using standard envelope
- ✅ Add request context (request IDs, timing)

The API layer should **NOT**:

- ❌ Contain business logic (belongs in `app/core/`)
- ❌ Make direct AI provider calls (belongs in `app/services/`)
- ❌ Process or transform data (belongs in `app/core/`)

## ADR-001 Compliance: API Endpoint Structure

All API endpoints must follow
[ADR-001](../../docs/adr/001-api-endpoint-structure.md):

### Request ID Tracking

Every request must have a unique ID for tracing:

```python
from fastapi import Request

@router.post("/api/v1/translations")
async def create_translation(
    request: Request,
    translation_request: TranslationRequest,
):
    # Access request ID from middleware
    request_id = request.state.request_id

    # Use request_id in logging and error responses
    logger.info(f"Processing translation", extra={"request_id": request_id})
```

The request ID is automatically added by the request ID middleware in `main.py`.

### API Versioning

All endpoints must use `/api/v1/` prefix:

```python
# ✅ Good - versioned endpoint
@router.post("/api/v1/translations")
async def create_translation(...):
    pass

# ❌ Bad - no version prefix
@router.post("/translations")
async def create_translation(...):
    pass
```

**Exception:** Health check endpoint at `/health` (no version prefix).

### Resource-Based Naming

Use plural resource names:

```python
# ✅ Good - resource-based
@router.post("/api/v1/translations")  # POST creates a translation
@router.get("/api/v1/translations/{id}")  # GET retrieves a translation

# ❌ Bad - action-based
@router.post("/api/v1/translate")
@router.get("/api/v1/get-translation")
```

## Request/Response Patterns

### Request Validation (Pydantic)

```python
from pydantic import BaseModel, Field
from fastapi import APIRouter, Request

router = APIRouter()

# Define request schema in app/schemas/
class TranslationRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    target_language: str = Field(..., pattern="^[a-z]{2}$")
    provider: str = Field(default="openai")

@router.post("/api/v1/translations")
async def create_translation(
    request: Request,
    translation_request: TranslationRequest,
):
    # Pydantic automatically validates the request
    # If validation fails, FastAPI returns 422 automatically
    pass
```

### Response Envelope

Use consistent response structure:

```python
from fastapi import Response

@router.post("/api/v1/translations")
async def create_translation(
    request: Request,
    response: Response,
    translation_request: TranslationRequest,
):
    try:
        # Call business logic
        result = await translation_service.translate(
            content=translation_request.content,
            target_language=translation_request.target_language,
        )

        # Add timing header (done by middleware)
        # Add request ID to response
        response.headers["X-Request-ID"] = request.state.request_id

        # Return structured response
        return {
            "status": "success",
            "data": result,
            "request_id": request.state.request_id,
        }

    except LuminoteException as e:
        # Exception handler in main.py will format this
        raise
```

## Error Handling

Errors are handled by the centralized exception handler in `main.py`. Just raise
`LuminoteException`:

```python
from app.core.errors import LuminoteException

@router.post("/api/v1/translations")
async def create_translation(
    request: Request,
    translation_request: TranslationRequest,
):
    # Validation error
    if not is_valid_language(translation_request.target_language):
        raise LuminoteException(
            code="INVALID_LANGUAGE",
            message=f"Unsupported language: {translation_request.target_language}",
            status_code=400,
            details={
                "language": translation_request.target_language,
                "supported": ["en", "es", "fr", "de"],
            },
        )

    # The exception handler will automatically add request_id
    # and return a properly formatted error response
```

## Streaming Responses (SSE)

For streaming endpoints (like progressive translation), use Server-Sent Events:

```python
from fastapi.responses import StreamingResponse
import json

@router.post("/api/v1/translations/stream")
async def stream_translation(
    request: Request,
    translation_request: TranslationRequest,
):
    async def event_generator():
        try:
            async for chunk in translation_service.translate_stream(...):
                # Send data event
                yield f"data: {json.dumps(chunk.dict())}\n\n"

            # Send completion event
            yield "event: done\ndata: {}\n\n"

        except Exception as e:
            # Send error event
            error_data = {
                "error": str(e),
                "code": "TRANSLATION_ERROR",
                "request_id": request.state.request_id,
            }
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Request-ID": request.state.request_id,
        },
    )
```

See
[ADR-002: Streaming Translation Architecture](../../docs/adr/002-streaming-translation-architecture.md)
for full details.

## Dependency Injection

Use FastAPI's dependency injection for shared logic:

```python
from fastapi import Depends
from app.core.config import Settings, get_settings

@router.post("/api/v1/translations")
async def create_translation(
    translation_request: TranslationRequest,
    settings: Settings = Depends(get_settings),  # Injected
):
    # Use settings
    max_length = settings.MAX_CONTENT_LENGTH
    pass
```

## Testing API Endpoints

Use the FastAPI test client:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.unit
def test_create_translation_success():
    """Test successful translation creation."""
    response = client.post(
        "/api/v1/translations",
        json={
            "content": "Hello world",
            "target_language": "es",
            "provider": "openai",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "data" in response.json()
    assert "request_id" in response.json()

@pytest.mark.unit
def test_create_translation_validation_error():
    """Test validation error handling."""
    response = client.post(
        "/api/v1/translations",
        json={
            "content": "",  # Invalid - too short
            "target_language": "es",
        },
    )

    assert response.status_code == 422  # Validation error
```

## Middleware Order

Middleware executes in **reverse order** of definition in `main.py`:

1. **Request ID middleware** (first to execute) - Adds X-Request-ID
1. **Timing middleware** (last to execute) - Adds X-Response-Time
1. **CORS middleware** - Handles cross-origin requests

When adding new middleware, consider the execution order.

## CORS Configuration

CORS is configured in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # From .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Never hardcode CORS origins** - always use configuration.

## Code Quality

### Coverage Requirement

API layer requires **≥85% test coverage**:

```bash
cd backend
uv run pytest --cov=app.api --cov-report=term-missing --cov-fail-under=85
```

### Type Hints

All API endpoints must have type annotations:

```python
from typing import Optional
from fastapi import Request

# ✅ Good - complete type hints
@router.post("/api/v1/translations")
async def create_translation(
    request: Request,
    translation_request: TranslationRequest,
) -> dict[str, Any]:
    pass

# ❌ Bad - missing return type
@router.post("/api/v1/translations")
async def create_translation(request, translation_request):
    pass
```

## What NOT to Do

❌ **Never:**

- Put business logic in API endpoints (extract to `core/` or `services/`)
- Make direct database calls (use repository pattern)
- Log API keys, tokens, or user data
- Return raw exceptions to users (use LuminoteException)
- Skip request validation (always use Pydantic)
- Hardcode configuration values (use Settings)
- Return different response formats from similar endpoints

## Before Committing

Run this checklist:

```bash
cd backend

# Format code
uv run isort app/api/
uv run black app/api/

# Lint
uv run ruff check app/api/ --no-fix

# Type check
uv run mypy app/api/

# Test with coverage
uv run pytest tests/ --cov=app.api --cov-report=term-missing --cov-fail-under=85

# Run API-specific tests
uv run pytest tests/api/ -v
```

## References

- [ADR-001: API Endpoint Structure](../../docs/adr/001-api-endpoint-structure.md)
- [ADR-002: Streaming Translation Architecture](../../docs/adr/002-streaming-translation-architecture.md)
- [ADR-004: Error Handling Patterns](../../docs/adr/004-error-handling-patterns.md)
- [AGENTS.md](../../AGENTS.md) - General development guide
