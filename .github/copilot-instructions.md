# Copilot Onboarding Instructions — Luminote

> This file guides AI coding agents working on this repository. It consolidates
> essential information to reduce time spent exploring and help agents complete
> tasks successfully on the first try.

## Repository Overview

**Luminote** is an AI-powered two-pane translation workbench for fast, accurate
understanding of web content. The project uses **FastAPI 0.109.0 (Python
3.12+)** for the backend and **SvelteKit (Node.js 22+)** for the frontend. The
repository is in Phase 0/1 development (infrastructure and foundational
features).

**Status:** Active development, all planning completed. See
[docs/PROJECT-STATUS.md](docs/PROJECT-STATUS.md).

**Key Architecture Principle:** Two-pane reading is primary—translation is
always the persistent right pane. Never replace it with alternative content.

**Core Non-Negotiables (from AGENTS.md):**

- Do not commit secrets (API keys, tokens, customer data)
- Always run quality gates before finishing
- Use `uv run` for Python commands (not `python` directly)
- All AI operations must be user-triggered (no background calls)
- BYOK (bring your own key) — users provide API keys
- Minimize blast radius: change only what's necessary

______________________________________________________________________

## Quick Setup & Validation

### Backend (Python 3.12+)

**Initial Setup:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # macOS/Linux; Windows: .venv\Scripts\activate
pip install -e ".[dev]"    # Install editable + dev dependencies
```

**Run Server:**

```bash
luminote serve              # Runs on http://localhost:8000
```

**Quality Checks (ALWAYS run these before finishing):**

```bash
cd backend
uv run isort app/ tests/    # Fix import order
uv run black app/ tests/    # Format code
uv run ruff check app/ tests/ --no-fix  # Lint (no auto-fix)
uv run mypy app/            # Type check (strict mode)
uv run pytest -q            # Run all tests
# For coverage: uv run pytest --cov=app --cov-report=html --cov-report=term-missing
```

**Coverage Requirements (enforced by CI):**

- `app/core/` modules: **≥95%** (strictly enforced)
- All other modules: **≥85%**

### Frontend (Node.js 22+)

**Initial Setup:**

```bash
cd frontend
npm install
```

**Run Dev Server:**

```bash
npm run dev                 # Runs on http://localhost:5000
```

**Quality Checks:**

```bash
npm run lint               # ESLint check
npm run format --check     # Prettier check (or: npm run format to fix)
npm run type-check         # TypeScript type check
npm run test               # Vitest
# For coverage: npm run test:coverage
```

______________________________________________________________________

## Build & CI Validation

### What GitHub Actions Check (CI Parity)

The repository uses automated CI via GitHub Actions. Your local checks must pass
these:

**Backend CI** (triggers on `backend/` changes):

1. Install deps: `pip install -r requirements.txt && pip install -e ".[dev]"`
1. isort check: `isort --check-only app/ tests/`
1. black check: `black --check app/ tests/`
1. ruff linting: `ruff check app/ tests/ --no-fix`
1. mypy type checking: `mypy app/`
1. pytest with coverage: `pytest --cov=app --cov-report=term-missing`

**Frontend CI** (triggers on `frontend/` changes):

1. Install: `npm install`
1. SvelteKit sync: `npx svelte-kit sync`
1. ESLint: `npm run lint`
1. Prettier: `npm run format --check`
1. TypeScript: `npm run type-check`
1. Vitest coverage: `npm run test:coverage`

### Pre-commit Hooks (Optional but Recommended)

Pre-commit hooks run automatically before each commit:

```bash
pre-commit install          # Install hooks (one-time setup)
pre-commit run --all-files  # Manual run on all files
```

Hooks enforce: merge conflict detection, YAML/JSON/TOML validation, pyupgrade,
isort, black, ruff, mypy, ESLint, and Prettier.

______________________________________________________________________

## Project Structure & Key Locations

```text
Luminote/
├── backend/                          # FastAPI application
│   ├── app/
│   │   ├── main.py                   # Entry point, middleware, app factory
│   │   ├── config.py                 # Pydantic settings (env-driven)
│   │   ├── api/v1/endpoints/         # REST endpoints (/api/v1/*)
│   │   ├── core/                     # Core logic (95%+ coverage required)
│   │   │   ├── errors.py             # Custom exceptions (LuminoteException)
│   │   │   └── logging.py            # Logger setup
│   │   ├── services/                 # AI providers, integrations
│   │   ├── schemas/                  # Pydantic request/response models
│   │   └── __init__.py               # Version (app.__version__)
│   ├── tests/
│   │   ├── conftest.py               # pytest fixtures (test client)
│   │   ├── test_main.py              # Main app tests
│   │   ├── test_errors.py            # Exception handling
│   │   ├── api/                      # Endpoint tests (unit/smoke/e2e)
│   │   ├── core/                     # Core logic tests (95%+ coverage)
│   │   └── services/                 # Service integration tests
│   ├── pyproject.toml                # Package config, deps, tool settings
│   ├── requirements.txt              # Pinned dependencies
│   └── README.md                     # Backend-specific docs
│
├── frontend/                         # SvelteKit application
│   ├── src/
│   │   ├── app.html                  # Root HTML template
│   │   ├── app.css                   # Global styles
│   │   ├── routes/                   # SvelteKit page routes
│   │   ├── components/               # Reusable Svelte components
│   │   ├── stores/                   # State management (Svelte stores)
│   │   └── lib/                      # Utilities, helpers
│   ├── static/                       # Static assets
│   ├── package.json                  # Dependencies, build scripts
│   ├── tsconfig.json                 # TypeScript config
│   ├── vite.config.ts                # Vite build config
│   ├── svelte.config.js              # SvelteKit config
│   ├── tailwind.config.js            # Tailwind CSS config
│   └── README.md                     # Frontend-specific docs
│
├── docs/                             # Documentation
│   ├── adr/                          # Architecture Decision Records (5 ADRs)
│   │   ├── 001-api-endpoint-structure.md
│   │   ├── 002-streaming-translation-architecture.md
│   │   ├── 003-client-side-storage-strategy.md
│   │   ├── 004-error-handling-patterns.md
│   │   └── 005-frontend-state-management.md
│   ├── API.md                        # API endpoint documentation
│   ├── feature-specifications.md     # Feature requirements (Phase 1-3)
│   ├── atomic-features.md            # 32 atomic Phase 1 features
│   ├── github-issues-phase1.md       # Production-ready GitHub issues
│   └── PROJECT-STATUS.md             # Planning status
│
├── .github/
│   ├── workflows/                    # GitHub Actions CI
│   │   ├── backend.yml               # Backend quality checks
│   │   └── frontend.yml              # Frontend quality checks
│   └── instructions/                 # Specific module instructions
│
├── .pre-commit-config.yaml           # Pre-commit hook definitions
├── .gitignore                        # Git ignore rules
├── AGENTS.md                         # Detailed development playbook
├── ARCHITECTURE.md                   # System architecture overview
├── CONTRIBUTING.md                   # Contribution guide (601 lines)
├── README.md                         # Project overview (257 lines)
└── LICENSE                           # GPL-3.0
```

______________________________________________________________________

## Code Layout & Where to Make Changes

### Backend Layers (FastAPI)

**Add API endpoints** → `backend/app/api/v1/endpoints/` + register in
`backend/app/api/v1/__init__.py`

- See [ADR-001: API Endpoint Structure](docs/adr/001-api-endpoint-structure.md)
  for conventions
- Use `/api/v1/{resource}` naming (resource-based, not verb-based)
- Include request ID tracking from `request.state.request_id`

**Add business logic** → `backend/app/core/`

- Must achieve **95%+ test coverage**
- No HTTP handling; pure algorithms
- Raise `LuminoteException` for errors (see ADR-004)

**Add AI provider integrations** → `backend/app/services/`

- Create provider-agnostic interfaces
- Map provider errors to standard exception types
- Validate API key format before making calls

**Add request/response models** → `backend/app/schemas/`

- Use Pydantic v2 models
- Include full type hints
- Use `Optional[T]` (not `T | None`) for Python 3.12 compatibility

**Add tests** → `backend/tests/` (mirror app structure)

- Unit tests: `@pytest.mark.unit` (mocked dependencies)
- Smoke tests: `@pytest.mark.smoke` (happy path only)
- E2E tests: `@pytest.mark.e2e` (full workflow, mocked external services)

### Frontend Layers (SvelteKit + TypeScript)

**Add components** → `frontend/src/components/`

- Single-file Svelte components (`.svelte`)
- Include full TypeScript types
- Add unit tests in `*.test.ts`

**Add routes** → `frontend/src/routes/`

- SvelteKit page structure (`+page.svelte`, `+layout.svelte`)

**Add state** → `frontend/src/stores/`

- Use Svelte stores (writable, readable, derived)
- No additional state management libraries

**Add tests** → `frontend/src/**/*.test.ts`

- Use Vitest + Testing Library
- Mock external API calls (no real network requests)

______________________________________________________________________

## Configuration Files (Don't Edit Without Reason)

- `backend/pyproject.toml` — Package config and tool settings; edit only to
  change dependencies or Python version
- `backend/requirements.txt` — Pinned dependencies; keep in sync with
  `pyproject.toml`
- `frontend/package.json` — Frontend deps and scripts; change when adding
  frontend dependencies
- `.pre-commit-config.yaml` — Pre-commit hooks; update versions or add hooks
- `.github/workflows/*.yml` — CI pipeline; change only when adjusting validation
  steps
- `AGENTS.md` — Development playbook; coordinate major edits with project lead

______________________________________________________________________

## Error Handling & Logging

**Always use standard exception pattern** (see `backend/app/core/errors.py` and
ADR-004):

```python
from app.core.errors import LuminoteException

raise LuminoteException(
    code="ERROR_CODE",
    message="Human-readable message",
    status_code=400,
    details={"context": "key information"}
)
```

**Never log secrets:**

- API keys, tokens, passwords → **never**
- User data → **never**
- Request/response bodies for sensitive operations → **never**
- HTTP headers containing auth → **never**

______________________________________________________________________

## Test Organization

- Unit — marker `@pytest.mark.unit`; test single functions/classes; mocked
  dependencies
- Smoke — marker `@pytest.mark.smoke`; verify critical paths (happy path only);
  mocked dependencies
- E2E — marker `@pytest.mark.e2e`; full workflow tests; mocked external services

**Run specific test types:**

```bash
cd backend
pytest -m unit   # Unit tests only
pytest -m smoke  # Smoke tests only
pytest -m e2e    # E2E tests only
```

______________________________________________________________________

## Coverage Thresholds (CI-Enforced)

```bash
# Core modules MUST be ≥95%
backend/app/core/**/*.py ≥95%

# All other modules MUST be ≥85%
backend/app/api/**/*.py ≥85%
backend/app/services/**/*.py ≥85%
backend/app/schemas/**/*.py ≥85%
frontend/**/*.ts ≥85%
```

Generate HTML coverage report:

```bash
cd backend
uv run pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

______________________________________________________________________

## Common Commands Reference

- Run backend server: `luminote serve` (from `backend/` with `.venv` active)
- Run frontend dev server: `npm run dev` (from `frontend/`)
- Test all backend: `uv run pytest -q`
- Backend coverage: `uv run pytest --cov=app --cov-report=html`
- Backend lint/format: `uv run isort app/ && uv run black app/`
- Backend type check: `uv run mypy app/`
- Test all frontend: `npm test`
- Frontend format: `npm run format`
- Pre-commit all: `pre-commit run --all-files`

______________________________________________________________________

## Reference Documentation (Trust These First)

When working on the codebase, trust and reference these documents in order:

1. **[AGENTS.md](AGENTS.md)** — Detailed development playbook (613 lines)
1. **[ARCHITECTURE.md](ARCHITECTURE.md)** — System architecture (140 lines)
1. **[docs/adr/](docs/adr/)** — Architecture Decision Records (use-case
   specific)
1. **[docs/API.md](docs/API.md)** — Endpoint specifications
1. **[CONTRIBUTING.md](CONTRIBUTING.md)** — Full development guide (601 lines)
1. **[README.md](README.md)** — Project overview (257 lines)

**Do NOT search if you can find the answer in these files.** Trust the
documentation provided.

______________________________________________________________________

## Validation Checklist (Before Finishing)

- [ ] Code passes all quality gates: `isort`, `black`, `ruff`, `mypy` (backend)
  OR `eslint`, `prettier`, `tsc` (frontend)
- [ ] Tests pass locally and coverage meets thresholds (core ≥95%, other ≥85%)
- [ ] No secrets committed (API keys, tokens, customer data)
- [ ] Architecture principles respected (two-pane reading, BYOK, user-triggered
  AI)
- [ ] Related ADRs reviewed (if making architectural decisions)
- [ ] Changes are focused (minimal blast radius)
- [ ] Git pre-commit hooks pass (or will pass in CI)

______________________________________________________________________

**Last Updated:** January 9, 2026 **Applies to:** Luminote Phase 1 development
