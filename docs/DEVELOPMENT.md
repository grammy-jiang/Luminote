# Development Guide

This guide provides comprehensive information for developers working on Luminote.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Code Review Process](#code-review-process)
- [Testing Guidelines](#testing-guidelines)
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)

## Architecture Overview

### System Architecture

Luminote follows a client-server architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                          │
│  (SvelteKit + TypeScript + Tailwind CSS)            │
│                                                      │
│  • Dual-pane layout (source + translation)          │
│  • State management via Svelte stores               │
│  • Client-side configuration storage                │
│  • Progressive rendering                            │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/REST API
                   │ (JSON, Server-Sent Events)
┌──────────────────▼──────────────────────────────────┐
│                    Backend                           │
│           (FastAPI + Python 3.12+)                  │
│                                                      │
│  • RESTful API endpoints (/api/v1/*)                │
│  • Content extraction and normalization             │
│  • AI provider integrations (BYOK)                  │
│  • Streaming translation orchestration              │
└──────────────────┬──────────────────────────────────┘
                   │ API calls
┌──────────────────▼──────────────────────────────────┐
│              AI Providers                            │
│  (OpenAI, Anthropic, etc.)                          │
│                                                      │
│  • Translation services                              │
│  • Text analysis (future)                           │
│  • User-provided API keys (BYOK)                    │
└──────────────────────────────────────────────────────┘
```

### Core Design Principles

These principles guide all architectural decisions and feature development:

1. **Two-pane reading is primary** — The translation pane is always visible on the right. Never replace it with alternative content.

2. **On-demand AI, user-controlled cost** — All AI operations must be explicitly triggered by users. No automatic background AI calls.

3. **BYOK multi-provider** — Users bring their own API keys. Support multiple providers (OpenAI, Anthropic, etc.).

4. **Configurable governance** — Prompts and terminology are configurable per task type for consistency.

5. **All AI outputs are versioned assets** — Every AI output is saved with full provenance (model, prompt version, referenced blocks) for replay and regeneration.

6. **Compliance-first** — Never bypass authentication, anti-bot mechanisms, or paywalls automatically. All sessions are user-driven.

### Key Abstractions

Understanding these core concepts is essential for working with the codebase:

- **Document** — Extracted and cleaned content from a URL
- **Block** — Normalized content unit (paragraph, heading, list, quote, code, image)
- **Translation** — Block-mapped translation with version tracking
- **AI Job** — Any model request with prompt version and metadata
- **Artifact** — Saved output from an AI Job (note, link card, verification, etc.)

### Technology Stack

**Backend:**
- **Runtime:** Python 3.12+ (required for modern type hints and performance)
- **Framework:** FastAPI (async-first, automatic OpenAPI docs)
- **Validation:** Pydantic v2 (data models and settings)
- **Server:** Uvicorn (ASGI server with auto-reload in dev)
- **Package management:** uv (fast Python package installer)

**Frontend:**
- **Runtime:** Node.js 22+ (LTS with latest ECMAScript support)
- **Framework:** SvelteKit 2.0 (SSR-capable, file-based routing)
- **Language:** TypeScript (strict mode for type safety)
- **Styling:** Tailwind CSS 3.4 (utility-first CSS)
- **Build tool:** Vite 5 (fast HMR and optimized builds)
- **Testing:** Vitest (Vite-native test runner)

**Code Quality:**
- **Python:** isort, black, ruff, mypy, pytest
- **TypeScript:** ESLint, Prettier, TypeScript compiler
- **Pre-commit hooks:** Automated checks on every commit

### API Design

All backend APIs follow RESTful conventions with versioning:

- **Base path:** `/api/v1/`
- **Health check:** `/health` (no version prefix)
- **Resource-based naming:** `/api/v1/translations`, not `/api/v1/translate`
- **Request IDs:** Every request gets a unique `X-Request-ID` for tracing
- **Error format:** Consistent JSON error responses (see ADR-004)
- **Streaming:** Server-Sent Events (SSE) for progressive rendering (see ADR-002)

For detailed API specifications, see [docs/API.md](API.md).

### Architecture Decision Records (ADRs)

All significant architectural decisions are documented in [docs/adr/](adr/):

- [ADR-001: API Endpoint Structure](adr/001-api-endpoint-structure.md) — RESTful API conventions, request tracking
- [ADR-002: Streaming Translation Architecture](adr/002-streaming-translation-architecture.md) — SSE for progressive rendering
- [ADR-003: Client-Side Storage Strategy](adr/003-client-side-storage-strategy.md) — Local storage for settings
- [ADR-004: Error Handling Patterns](adr/004-error-handling-patterns.md) — Standard error response format
- [ADR-005: Frontend State Management](adr/005-frontend-state-management.md) — Svelte stores architecture

## Development Workflow

### Setting Up Your Environment

**Prerequisites:**
- Python 3.12 or higher
- Node.js 22 or higher
- Git
- A code editor (VS Code recommended)

**Quick setup (automated):**

```bash
# Clone the repository
git clone https://github.com/grammy-jiang/Luminote.git
cd Luminote

# Run the setup script
./scripts/setup-dev.sh  # Linux/macOS
# OR
scripts\setup-dev.bat   # Windows
```

The setup script will:
1. Verify Python 3.12+ and Node.js 22+ are installed
2. Create backend virtual environment and install dependencies
3. Install frontend dependencies
4. Install pre-commit hooks
5. Create `.env` files from examples
6. Verify the setup by collecting tests

**Manual setup:**

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed manual setup instructions.

### Daily Development Cycle

**1. Start development servers:**

Terminal 1 (Backend):
```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
luminote serve
# Backend runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
# Frontend runs at http://localhost:5000
```

**2. Make changes:**

- Create a feature branch: `git checkout -b feature/your-feature-name`
- Write code following the project's coding standards
- Add tests for new functionality
- Update documentation if needed

**3. Run quality checks:**

Backend:
```bash
cd backend
isort app/
black app/
ruff check app/ --no-fix
mypy app/
pytest
```

Frontend:
```bash
cd frontend
npm run lint
npm run format
npm run type-check
npm test
```

**4. Commit changes:**

Pre-commit hooks will run automatically. If they fail, fix the issues and try again.

```bash
git add .
git commit -m "feat: your feature description"
```

**5. Push and create a pull request:**

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

### Working with Backend Code

**Project structure:**

```
backend/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── api/
│   │   └── v1/              # API version 1
│   │       ├── __init__.py  # Router registration
│   │       └── endpoints/   # API endpoint modules
│   ├── core/
│   │   ├── errors.py        # Custom exceptions (≥95% coverage)
│   │   └── logging.py       # Logging configuration
│   ├── services/            # Business logic and AI integrations
│   └── schemas/             # Pydantic models for validation
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── api/                 # API endpoint tests
│   ├── services/            # Service layer tests
│   └── core/                # Core logic tests (≥95% coverage)
└── pyproject.toml           # Package config and tool settings
```

**Adding a new API endpoint:**

1. Create Pydantic schemas in `app/schemas/your_feature.py`
2. Implement business logic in `app/services/your_service.py`
3. Create the endpoint in `app/api/v1/endpoints/your_feature.py`
4. Register the router in `app/api/v1/__init__.py`
5. Add tests for schemas, service, and endpoint
6. Update API documentation if needed

**Running specific tests:**

```bash
# Run all tests
pytest

# Run specific test file
pytest backend/tests/api/test_health.py -v

# Run specific test function
pytest backend/tests/api/test_health.py::test_health_endpoint -v

# Run by marker
pytest -m unit      # Unit tests only
pytest -m smoke     # Smoke tests only
pytest -m e2e       # End-to-end tests only

# Run with coverage
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser to view coverage report
```

**Debugging:**

Use Python's built-in debugger or your IDE's debugger:

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

### Working with Frontend Code

**Project structure:**

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/     # Reusable Svelte components
│   │   ├── stores/         # Svelte stores for state management
│   │   ├── utils/          # Utility functions
│   │   └── *.test.ts       # Test files co-located with code
│   ├── routes/             # SvelteKit pages and layouts
│   │   ├── +layout.svelte  # Root layout
│   │   └── +page.svelte    # Home page
│   ├── app.html            # HTML template
│   └── app.css             # Global styles (Tailwind)
├── static/                 # Static assets (images, etc.)
└── [config files]          # Various configuration files
```

**Path aliases:**

Use these aliases in your imports:

```typescript
import { myStore } from '$stores/myStore';
import Button from '$components/Button.svelte';
import { formatDate } from '$utils/date';
```

**Creating a new component:**

1. Create component file: `src/lib/components/YourComponent.svelte`
2. Write the component with TypeScript: `<script lang="ts">`
3. Add tests: `src/lib/components/YourComponent.test.ts`
4. Update tests to ≥85% coverage
5. Use the component in your pages

**Running tests:**

```bash
# Run all tests
npm test

# Watch mode (runs on file changes)
npm run test:watch

# With coverage report
npm run test:coverage
# Open coverage/index.html in browser to view report

# Run specific test file
npm test -- YourComponent.test.ts
```

**Debugging:**

Use browser DevTools or VS Code debugger:

1. Start dev server: `npm run dev`
2. Open http://localhost:5000 in browser
3. Open DevTools (F12)
4. Add `debugger;` statement in code or use browser breakpoints

### Configuration Management

**Backend configuration:**

Edit `backend/.env` to configure the backend:

```bash
# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=Luminote

# CORS Configuration (comma-separated list)
CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Development server configuration
DEV_HOST=127.0.0.1
DEV_PORT=8000
DEV_RELOAD=true
```

Configuration is loaded via Pydantic Settings (`app/config.py`) and cached for performance.

**Frontend configuration:**

Frontend uses environment variables and runtime configuration. API endpoints and settings will be configurable in Phase 1.

## Branching Strategy

### Branch Types

Luminote uses a simplified Git Flow with the following branch types:

- **`main`** — Production-ready code. Always stable and deployable.
- **`develop`** — Integration branch for features. Default branch for development.
- **Feature branches** — For new features: `feature/short-description`
- **Fix branches** — For bug fixes: `fix/short-description`
- **Docs branches** — For documentation: `docs/short-description`
- **Refactor branches** — For code refactoring: `refactor/short-description`
- **Test branches** — For test additions: `test/short-description`
- **Chore branches** — For maintenance: `chore/short-description`

### Branch Naming Convention

Use descriptive, kebab-case names:

```
feature/dual-pane-layout
fix/translation-streaming-error
docs/api-documentation
refactor/error-handling
test/add-translation-tests
chore/update-dependencies
```

### Workflow

**1. Starting new work:**

```bash
# Update your local main/develop branch
git checkout develop
git pull origin develop

# Create a new feature branch
git checkout -b feature/your-feature-name
```

**2. During development:**

```bash
# Commit frequently with clear messages
git add .
git commit -m "feat: add dual-pane layout component"

# Keep your branch up to date
git fetch origin
git rebase origin/develop  # Or merge if you prefer
```

**3. Ready for review:**

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a pull request on GitHub
# Request reviews from team members
```

**4. After merge:**

```bash
# Delete local branch
git branch -d feature/your-feature-name

# Delete remote branch
git push origin --delete feature/your-feature-name

# Update local branches
git checkout develop
git pull origin develop
```

### Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <short summary>

[optional body]

[optional footer]
```

**Types:**
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `refactor:` — Code refactoring (no behavior change)
- `test:` — Adding or updating tests
- `chore:` — Maintenance tasks (dependencies, config, etc.)
- `perf:` — Performance improvements
- `ci:` — CI/CD changes

**Examples:**

```
feat: add streaming translation endpoint

Implements Server-Sent Events for progressive rendering of translations.
Follows ADR-002 for streaming architecture.

Closes #25
```

```
fix: handle network timeout in extraction service

Previously, network timeouts would cause unhandled exceptions.
Now properly catches and returns user-friendly error messages.

Fixes #42
```

## Code Review Process

### Pull Request Requirements

Every pull request must meet these requirements before merge:

**✅ Code Quality:**
- All quality checks pass (isort, black, ruff, mypy for Python; ESLint, Prettier, TypeScript for frontend)
- No new linter warnings or errors
- Code follows project conventions and patterns

**✅ Testing:**
- All existing tests pass
- New tests added for new functionality
- Coverage requirements met (core ≥95%, other ≥85%)
- Tests are meaningful and not just for coverage

**✅ Documentation:**
- Code is well-commented where necessary
- API changes documented in docs/API.md
- README updated if needed
- Architecture decisions recorded in ADRs (if significant)

**✅ Functionality:**
- Feature works as expected
- No breaking changes (or clearly documented if necessary)
- Edge cases handled
- Error messages are clear and actionable

**✅ PR Description:**
- Clear title describing the change
- Description explains **what**, **why**, and **how**
- References related issues (e.g., "Closes #25")
- Screenshots/videos for UI changes
- Breaking changes highlighted

### Review Process

**1. Author submits PR:**
- Fill out the PR template completely
- Self-review your changes first
- Ensure all CI checks pass
- Request reviewers (at least 1-2 people)

**2. Reviewers provide feedback:**
- Review within 1-2 business days
- Focus on code quality, design, and maintainability
- Ask questions if unclear
- Provide constructive, specific feedback
- Approve when satisfied

**3. Author addresses feedback:**
- Respond to all comments
- Make requested changes
- Push new commits (do not force-push during review)
- Re-request review when ready

**4. Merge:**
- Maintainer merges when all requirements met
- Use "Squash and merge" for clean history
- Delete branch after merge

### Review Guidelines

**For reviewers:**

✅ **Do:**
- Be respectful and constructive
- Explain the "why" behind suggestions
- Acknowledge good work
- Focus on code, not the person
- Use GitHub's suggestion feature for minor changes

❌ **Don't:**
- Nitpick on personal style preferences
- Block PRs on minor issues
- Review your own code (get external review)
- Rush reviews to meet deadlines

**For authors:**

✅ **Do:**
- Respond to all comments (even if just "Done" or "Fixed")
- Ask questions if feedback is unclear
- Be open to suggestions
- Thank reviewers for their time

❌ **Don't:**
- Take feedback personally
- Argue without understanding the concern
- Mark conversations as resolved before reviewer agrees
- Force-push during active review

### Common Review Topics

**Code structure:**
- Is the code in the right module/layer?
- Are abstractions appropriate?
- Is the code DRY (Don't Repeat Yourself)?
- Are there better patterns available?

**Error handling:**
- Are errors caught and handled appropriately?
- Are error messages clear and actionable?
- Is logging appropriate?
- Are edge cases covered?

**Testing:**
- Are tests meaningful and comprehensive?
- Do tests cover edge cases?
- Are tests maintainable?
- Is mocking appropriate?

**Performance:**
- Are there obvious performance issues?
- Is the code efficient?
- Are there unnecessary database/API calls?
- Is caching appropriate?

**Security:**
- Are inputs validated?
- Are secrets handled securely?
- Is authentication/authorization correct?
- Are there injection risks?

## Testing Guidelines

### Testing Philosophy

Luminote follows a comprehensive testing strategy to ensure code quality and reliability:

1. **Test behavior, not implementation** — Focus on what the code does, not how it does it
2. **Write tests first (TDD encouraged)** — Clarifies requirements and design
3. **Keep tests simple and readable** — Tests are documentation
4. **Mock external dependencies** — No real API calls, network requests, or database writes
5. **Aim for high coverage** — But don't sacrifice quality for numbers

### Test Categories

**Unit Tests** (mark with `@pytest.mark.unit`):
- Test individual functions and classes in isolation
- Fast execution (<1ms per test)
- Mock all dependencies
- Focus on edge cases and error conditions

**Smoke Tests** (mark with `@pytest.mark.smoke`):
- Test critical paths with happy path data
- Verify core functionality works end-to-end
- Run before every deployment
- Should complete in <10 seconds total

**End-to-End Tests** (mark with `@pytest.mark.e2e`):
- Test complete workflows across multiple components
- Mock external services but not internal components
- Verify integration between layers
- Can be slower but should still complete in reasonable time

### Coverage Requirements

Coverage thresholds are enforced in CI:

- **Core modules** (`app/core/`): **≥95%** (strictly enforced)
- **API modules** (`app/api/`): **≥85%**
- **Service modules** (`app/services/`): **≥85%**
- **Frontend code**: **≥85%**

To check coverage:

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS
# or xdg-open htmlcov/index.html  # Linux
# or start htmlcov/index.html  # Windows

# Frontend
cd frontend
npm run test:coverage
open coverage/index.html  # macOS
```

### Writing Good Tests

**Backend (Python):**

```python
import pytest
from fastapi.testclient import TestClient

# Unit test example
@pytest.mark.unit
def test_parse_url_valid():
    """Test URL parsing with valid input."""
    url = "https://example.com/page"
    result = parse_url(url)
    assert result.scheme == "https"
    assert result.netloc == "example.com"
    assert result.path == "/page"

# Smoke test example
@pytest.mark.smoke
def test_health_endpoint(client: TestClient):
    """Test health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# E2E test example
@pytest.mark.e2e
def test_translation_workflow(client: TestClient, mock_openai):
    """Test complete translation workflow."""
    # Mock AI provider
    mock_openai.create_completion.return_value = {
        "choices": [{"text": "translated content"}]
    }
    
    # Make request
    response = client.post("/api/v1/translate", json={
        "text": "hello world",
        "target_lang": "es"
    })
    
    # Verify response
    assert response.status_code == 200
    assert "translated content" in response.json()["text"]
```

**Frontend (TypeScript):**

```typescript
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import Button from './Button.svelte';

describe('Button component', () => {
  it('renders with correct text', () => {
    render(Button, { props: { text: 'Click me' } });
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick handler when clicked', async () => {
    const onClick = vi.fn();
    const { component } = render(Button, { 
      props: { text: 'Click me', onClick } 
    });
    
    await fireEvent.click(screen.getByText('Click me'));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it('is disabled when disabled prop is true', () => {
    render(Button, { props: { text: 'Click me', disabled: true } });
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});
```

### Test Fixtures and Mocking

**Backend fixtures (in `conftest.py`):**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import fastapi_application

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(fastapi_application)

@pytest.fixture
def mock_settings():
    """Mock application settings."""
    return Settings(
        API_V1_PREFIX="/api/v1",
        LOG_LEVEL="DEBUG"
    )

@pytest.fixture
def sample_blocks():
    """Sample content blocks for testing."""
    return [
        {"type": "heading", "content": "Title"},
        {"type": "paragraph", "content": "Content"}
    ]
```

**Mocking external services:**

```python
# Use unittest.mock or pytest-mock
from unittest.mock import patch, MagicMock

@pytest.mark.unit
@patch('app.services.openai_client.OpenAI')
def test_translation_service(mock_openai):
    """Test translation service with mocked OpenAI."""
    # Setup mock
    mock_openai.return_value.completions.create.return_value = {
        "choices": [{"text": "translated"}]
    }
    
    # Test your code
    service = TranslationService(api_key="test-key")
    result = service.translate("hello", target_lang="es")
    
    # Verify
    assert result == "translated"
    mock_openai.return_value.completions.create.assert_called_once()
```

### Running Tests in CI

All tests run automatically on every pull request. You can also run them locally to verify before pushing:

```bash
# Backend - run all checks
cd backend
isort app/ && black app/ && ruff check app/ --no-fix && mypy app/ && pytest

# Frontend - run all checks
cd frontend
npm run lint && npm run format && npm run type-check && npm test
```

## Troubleshooting

### Common Backend Issues

#### Import errors or module not found

**Symptom:**
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
```bash
cd backend
source .venv/bin/activate  # Activate virtual environment
uv pip install -e ".[dev]"  # Install in editable mode
```

#### Port 8000 already in use

**Symptom:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use a different port
luminote serve --port 8001
```

#### Tests failing with fixture errors

**Symptom:**
```
fixture 'client' not found
```

**Solution:**
- Ensure you're running pytest from the backend directory
- Check that `conftest.py` exists and defines the fixture
- Make sure `__init__.py` files exist in test directories

#### Type checking errors with mypy

**Symptom:**
```
error: Cannot find implementation or library stub for module
```

**Solution:**
```bash
# Install type stubs
uv pip install types-requests types-urllib3

# Or ignore specific modules in pyproject.toml
[tool.mypy]
ignore_missing_imports = true
```

### Common Frontend Issues

#### Port 5000 already in use

**Symptom:**
```
Port 5000 is in use
```

**Solution:**
```bash
# Find and kill process using port 5000
lsof -i :5000  # macOS/Linux
kill -9 <PID>

# On Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

#### Node modules not found

**Symptom:**
```
Cannot find module '@sveltejs/kit'
```

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### TypeScript errors after update

**Symptom:**
```
Type error: Property 'xyz' does not exist on type...
```

**Solution:**
```bash
# Check types
npm run type-check

# Clear cache and rebuild
rm -rf .svelte-kit node_modules
npm install
npm run build
```

#### Vite build fails

**Symptom:**
```
✘ [ERROR] Build failed
```

**Solution:**
```bash
# Clear cache
rm -rf .svelte-kit

# Check for syntax errors
npm run type-check

# Rebuild
npm run build
```

### Git and Version Control Issues

#### Pre-commit hooks failing

**Symptom:**
```
pre-commit hook failed
```

**Solution:**
```bash
# Run hooks manually to see details
pre-commit run --all-files

# Fix reported issues, then commit again
git add .
git commit -m "your message"

# Skip hooks if absolutely necessary (use sparingly!)
git commit --no-verify -m "your message"
```

#### Merge conflicts

**Symptom:**
```
CONFLICT (content): Merge conflict in file.py
```

**Solution:**
```bash
# Update your branch
git fetch origin
git merge origin/develop

# Resolve conflicts in your editor
# Look for <<<<<<< HEAD markers

# After resolving, mark as resolved
git add resolved-file.py
git commit -m "resolve merge conflicts"
```

#### Accidentally committed to main

**Symptom:**
You committed directly to main instead of a feature branch.

**Solution:**
```bash
# Create a new branch from current state
git branch feature/your-feature

# Reset main to match origin
git checkout main
git reset --hard origin/main

# Continue work on feature branch
git checkout feature/your-feature
```

### Environment and Configuration Issues

#### Environment variables not loading

**Symptom:**
Settings have default values instead of your .env values.

**Solution:**
```bash
# Check .env file exists
ls backend/.env

# Check file is not empty
cat backend/.env

# Ensure no spaces around = in .env
# ✅ CORRECT: LOG_LEVEL=DEBUG
# ❌ WRONG: LOG_LEVEL = DEBUG

# Restart the server to pick up changes
```

#### Different behavior in development vs production

**Symptom:**
Code works locally but fails in CI or production.

**Solution:**
- Check Python/Node.js versions match (Python 3.12+, Node.js 22+)
- Ensure all dependencies are in requirements.txt or package.json
- Check environment-specific configurations
- Review CI logs for specific errors
- Test with production-like settings locally

### Performance Issues

#### Slow tests

**Symptom:**
Test suite takes several minutes to run.

**Solution:**
```bash
# Run only fast tests
pytest -m unit

# Use pytest-xdist for parallel execution
pip install pytest-xdist
pytest -n auto

# Profile slow tests
pytest --durations=10
```

#### Slow development server

**Symptom:**
Backend or frontend server is slow to respond.

**Solution:**
- Check for infinite loops or blocking operations
- Review logs for excessive logging
- Ensure dev database is not too large (if applicable)
- Check system resources (CPU, memory, disk)
- Disable debugging tools if running

### Getting Help

If you're still stuck after trying these solutions:

1. **Search existing issues:** Check [GitHub Issues](https://github.com/grammy-jiang/Luminote/issues) for similar problems
2. **Check documentation:** Review [CONTRIBUTING.md](../CONTRIBUTING.md) and [ARCHITECTURE.md](../ARCHITECTURE.md)
3. **Ask in discussions:** Post in [GitHub Discussions](https://github.com/grammy-jiang/Luminote/discussions)
4. **Provide context:** Include error messages, logs, steps to reproduce, and what you've tried

## Additional Resources

### Project Documentation

- **[README.md](../README.md)** — Project overview and quick start
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — Contributing guidelines and setup
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** — System architecture and design
- **[docs/API.md](API.md)** — API reference and specifications
- **[docs/adr/](adr/)** — Architecture Decision Records

### Backend Resources

- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** — Backend framework
- **[Pydantic Documentation](https://docs.pydantic.dev/)** — Data validation
- **[Pytest Documentation](https://docs.pytest.org/)** — Testing framework
- **[Python Type Hints](https://docs.python.org/3/library/typing.html)** — Type annotations

### Frontend Resources

- **[SvelteKit Documentation](https://kit.svelte.dev/docs)** — Frontend framework
- **[Svelte Documentation](https://svelte.dev/docs)** — Component framework
- **[TypeScript Documentation](https://www.typescriptlang.org/docs)** — Type system
- **[Tailwind CSS Documentation](https://tailwindcss.com/docs)** — Styling
- **[Vitest Documentation](https://vitest.dev)** — Testing framework

### Code Quality Tools

- **[Ruff](https://docs.astral.sh/ruff/)** — Fast Python linter
- **[Black](https://black.readthedocs.io/)** — Python code formatter
- **[mypy](https://mypy.readthedocs.io/)** — Static type checker
- **[ESLint](https://eslint.org/docs/latest/)** — JavaScript/TypeScript linter
- **[Prettier](https://prettier.io/docs/en/)** — Code formatter

### Learning Resources

- **[Python 3.12 What's New](https://docs.python.org/3/whatsnew/3.12.html)** — Latest Python features
- **[TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)** — TypeScript guide
- **[REST API Best Practices](https://restfulapi.net/)** — API design
- **[Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)** — Branching model

### Community and Support

- **[GitHub Issues](https://github.com/grammy-jiang/Luminote/issues)** — Bug reports and feature requests
- **[GitHub Discussions](https://github.com/grammy-jiang/Luminote/discussions)** — Questions and discussions
- **[Pull Requests](https://github.com/grammy-jiang/Luminote/pulls)** — Code contributions

---

**Last Updated:** January 8, 2026

This guide is maintained by the Luminote development team. Contributions and improvements are welcome!
