# Luminote Backend

This is the FastAPI backend for Luminote, an AI-powered translation and reading comprehension tool.

## Quick Start

### Prerequisites

- Python 3.12 or higher
- pip or uv package manager

### Setup

1. **Create a virtual environment:**

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**

   Using uv (recommended):
   ```bash
   uv pip install -e ".[dev]"
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

3. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start the development server:**

   ```bash
   luminote serve
   ```

   Or directly:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Test the health check:**

   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {"status": "ok", "version": "0.1.0"}
   ```

## Development

### API Documentation

Once the server is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Code Quality

Run all quality checks before committing:

```bash
# Format imports
isort app/

# Format code
black app/

# Lint code
ruff check app/ --no-fix

# Type check
mypy app/
```

### Testing

Run tests with pytest:

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test categories
pytest -m unit
pytest -m smoke
pytest -m e2e
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── api/
│   │   └── v1/              # API version 1
│   │       ├── __init__.py
│   │       └── endpoints/   # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── errors.py        # Custom exceptions
│   │   └── logging.py       # Logging configuration
│   ├── services/            # Business logic
│   │   └── __init__.py
│   └── schemas/             # Pydantic models
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── api/
│   ├── services/
│   └── core/
├── pyproject.toml           # Project metadata and tool config
├── requirements.txt         # Production dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Architecture

This backend follows the architecture defined in:
- [ADR-001: API Endpoint Structure](../docs/adr/001-api-endpoint-structure.md)
- [ADR-004: Error Handling Patterns](../docs/adr/004-error-handling-patterns.md)

Key principles:
- RESTful API with versioning (`/api/v1/`)
- Pydantic for data validation and settings
- Custom exception hierarchy for error handling
- Structured logging
- BYOK (Bring Your Own Key) for AI providers
- User-triggered AI operations only

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

## License

GPL-3.0 - See [LICENSE](../LICENSE) for details.
