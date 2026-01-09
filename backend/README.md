# Luminote Backend

This is the FastAPI backend for Luminote, an AI-powered translation and reading
comprehension tool.

## Quick Start

### Prerequisites

- **Python 3.12 or higher** (required for modern type hints)
- **uv** package manager (recommended) or pip
- **Virtual environment** tool (venv)

**Check your Python version:**

```bash
python --version  # Should be 3.12 or higher
```

**Install uv (recommended for faster installs):**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or use pip
pip install uv
```

### Setup

1. **Create a virtual environment:**

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

   **Note:** The virtual environment must be activated in each new terminal
   session.

1. **Install dependencies:**

   Using uv (recommended):

   ```bash
   uv pip install -e ".[dev]"
   ```

   Or using pip:

   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

   The `-e` flag installs the package in editable mode, allowing you to modify
   code without reinstalling.

1. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

   **Required settings in `.env`:**

   - `API_V1_PREFIX` — API path prefix (default: `/api/v1`)
   - `CORS_ORIGINS` — Allowed origins for CORS (default:
     `http://localhost:5000`)
   - `LOG_LEVEL` — Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - `DEV_HOST` — Development server host (default: `127.0.0.1`)
   - `DEV_PORT` — Development server port (default: `8000`)

1. **Start the development server:**

   ```bash
   luminote serve
   ```

   Or directly with uvicorn:

   ```bash
   uvicorn app.main:fastapi_application --reload --host 127.0.0.1 --port 8000
   ```

   The server will start at **http://localhost:8000** with auto-reload enabled.

1. **Verify the setup:**

   **Health check:**

   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:

   ```json
   {"status": "ok", "version": "0.1.0"}
   ```

   **Interactive API documentation:**

   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Development

### API Documentation

Once the server is running, you can access interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs — Interactive API testing
- **ReDoc:** http://localhost:8000/redoc — Clean API documentation

These are automatically generated from your FastAPI routes and Pydantic models.

### Code Quality

All code must pass quality checks before committing. Run these commands from the
`backend/` directory:

```bash
# Run all checks at once
isort app/ && black app/ && ruff check app/ --no-fix && mypy app/

# Or run individually:

# 1. Format imports (automatically fixes)
isort app/

# 2. Format code (automatically fixes)
black app/

# 3. Lint code (reports issues, no auto-fix)
ruff check app/ --no-fix

# 4. Type check (reports type errors)
mypy app/
```

**What each tool does:**

- **isort** — Sorts and organizes imports according to PEP 8
- **black** — Formats code to a consistent style (PEP 8 compliant)
- **ruff** — Fast linter that checks for common issues and code smells
- **mypy** — Static type checker that validates type hints

**Pre-commit hooks:**

Pre-commit hooks automatically run these checks when you commit. To install:

```bash
pip install pre-commit
pre-commit install

# Run manually on all files:
pre-commit run --all-files
```

### Testing

Run tests with pytest:

```bash
# Run all tests (fast mode)
pytest -q

# Run all tests (verbose mode)
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html to view detailed coverage

# Run specific test categories
pytest -m unit       # Unit tests only (fast, isolated)
pytest -m smoke      # Smoke tests (critical paths)
pytest -m e2e        # End-to-end tests (full workflows)

# Run specific test file
pytest tests/api/test_health.py -v

# Run specific test function
pytest tests/api/test_health.py::test_health_endpoint -v
```

**Test markers:**

Tests are categorized using pytest markers:

- `@pytest.mark.unit` — Fast unit tests with mocked dependencies
- `@pytest.mark.smoke` — Critical path tests (happy path only)
- `@pytest.mark.e2e` — End-to-end workflow tests

**Coverage requirements:**

- **Core modules** (`app/core/`): **≥95%** coverage required
- **Other modules** (`app/api/`, `app/services/`): **≥85%** coverage required

**Running tests across Python versions:**

```bash
# Install tox
pip install tox

# Run tests on all supported Python versions
tox
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

This backend follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│     API Layer (app/api/)            │  HTTP request/response handling
│     - Endpoint definitions          │
│     - Request validation            │
│     - Response formatting           │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   Service Layer (app/services/)     │  Business logic
│     - AI provider integrations      │
│     - Content extraction            │
│     - Translation orchestration     │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│    Core Layer (app/core/)           │  Core algorithms & utilities
│     - Error handling                │
│     - Logging                       │
│     - Configuration                 │
└─────────────────────────────────────┘
```

**Architecture Decision Records (ADRs):**

All significant architectural decisions are documented:

- [ADR-001: API Endpoint Structure](../docs/adr/001-api-endpoint-structure.md) —
  RESTful conventions, versioning, request tracking
- [ADR-002: Streaming Translation Architecture](../docs/adr/002-streaming-translation-architecture.md)
  — Server-Sent Events for progressive rendering
- [ADR-004: Error Handling Patterns](../docs/adr/004-error-handling-patterns.md)
  — Standard error response format and exception hierarchy

**Key principles:**

1. **RESTful API with versioning** — All endpoints under `/api/v1/` prefix
1. **Pydantic for validation** — Type-safe request/response models and settings
1. **Custom exception hierarchy** — Consistent error handling via
   `LuminoteException`
1. **Structured logging** — Request ID tracking for debugging
1. **BYOK (Bring Your Own Key)** — Users provide API keys for AI providers
1. **User-triggered AI operations only** — No automatic background AI calls

For complete architecture documentation, see
[ARCHITECTURE.md](../ARCHITECTURE.md).

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'app'"**

Solution: Install the package in editable mode:

```bash
cd backend
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**"Port 8000 already in use"**

Solution: Find and kill the process using port 8000:

```bash
# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
luminote serve --port 8001
```

**Tests failing with fixture errors**

Solution: Ensure pytest is run from the backend directory and `conftest.py`
exists:

```bash
cd backend
pytest -v
```

**Type checking errors**

Solution: Install type stubs for external libraries:

```bash
uv pip install types-requests types-urllib3
```

**Pre-commit hooks not running**

Solution: Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

For more troubleshooting tips, see
[docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md#troubleshooting).

## Development Workflow

**Quick development cycle:**

1. Make code changes
1. Run quality checks:
   `isort app/ && black app/ && ruff check app/ --no-fix && mypy app/`
1. Run tests: `pytest -q`
1. Test manually: `luminote serve` and visit http://localhost:8000/docs
1. Commit: `git commit -m "feat: your change"`

**Adding a new API endpoint:**

1. Define Pydantic schemas in `app/schemas/your_feature.py`
1. Implement business logic in `app/services/your_service.py`
1. Create the endpoint in `app/api/v1/endpoints/your_feature.py`
1. Register the router in `app/api/v1/__init__.py`
1. Add tests for all layers
1. Update API documentation if needed

For detailed workflow, see [docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for:

- Development setup and environment
- Coding standards and style guides
- Testing requirements and best practices
- Pull request process and review guidelines
- Commit message conventions

Also review [docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md) for detailed
development workflows.

## Documentation

- **[README.md](../README.md)** — Project overview
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — Contributing guidelines
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** — System architecture
- **[docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md)** — Development guide
- **[docs/API.md](../docs/API.md)** — API reference
- **[docs/adr/](../docs/adr/)** — Architecture Decision Records

## License

This project is licensed under the **GNU General Public License v3.0
(GPL-3.0)**.

See [LICENSE](../LICENSE) for details.
