# Copilot Onboarding Instructions — Luminote

> This file guides AI coding agents. Trust these instructions and only search if
> information is incomplete or in error.

## Repository Overview

**What:** AI-powered two-pane translation workbench for understanding web
content. **Languages:** Python 3.12+ (FastAPI 0.109.0 backend), TypeScript +
Svelte (SvelteKit frontend) **Status:** Active Phase 0/1 development. See
[docs/PROJECT-STATUS.md](docs/PROJECT-STATUS.md). **Key Principle:** Two-pane
reading primary—translation always visible right pane.

**Non-Negotiables:**

- No secrets (API keys, tokens) ever committed
- Always run quality gates before finishing
- Use `uv run` for Python (not `python` directly)
- All AI ops user-triggered (never automatic)
- BYOK: users provide API keys
- Minimal blast radius

## Quick Start Commands

### Automated Setup (Recommended)

```bash
# Clone and setup in one go
git clone https://github.com/grammy-jiang/Luminote.git
cd Luminote
./scripts/setup-dev.sh     # Linux/macOS
# OR
scripts\setup-dev.bat      # Windows
```

The setup script:

- Verifies Python 3.12+ and Node.js 22+ installed
- Creates backend venv and installs dependencies
- Installs frontend dependencies
- Installs pre-commit hooks (auto-enforces on commits)
- Creates .env files from examples
- Validates setup by collecting tests

### Backend (Python 3.12+)

```bash
cd backend
uv venv                    # Create venv (or: python -m venv .venv)
source .venv/bin/activate # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"  # Install with uv or: pip install -e ".[dev]"
uv run luminote serve      # http://localhost:8000
```

**Quality checks (MUST pass before finishing):**

```bash
cd backend
uv run isort app/ tests/ && uv run black app/ tests/
uv run ruff check app/ tests/ --no-fix && uv run mypy app/
uv run pytest -q                    # Add: --cov=app for coverage
```

**Coverage required:** `app/core/` ≥95%, others ≥85%

### Frontend (Node.js 22+)

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5000
npm run lint && npm run format && npm run type-check && npm test
```

______________________________________________________________________

## Project Structure

```text
backend/app/               core/ (95%+ coverage)  api/v1/endpoints/
backend/tests/             conftest.py, test files (mirror app/)
frontend/src/              components/, stores/, routes/, lib/
docs/adr/                  5 Architecture Decision Records
.github/workflows/         backend.yml, frontend.yml (CI checks)
.github/instructions/      Layer-specific rules
```

______________________________________________________________________

## Build & CI Validation

**GitHub Actions checks (replicate locally):**

**Backend:** (triggers on `backend/` changes)

1. `pip install -r requirements.txt && pip install -e ".[dev]"`
1. `isort --check-only app/ tests/`
1. `black --check app/ tests/`
1. `ruff check app/ tests/ --no-fix`
1. `mypy app/` (strict mode)
1. `pytest --cov=app --cov-report=term-missing`

**Frontend:** (triggers on `frontend/` changes)

1. `npm install`
1. `npx svelte-kit sync`
1. `npm run lint` (ESLint)
1. `npm run format --check` (Prettier)
1. `npm run type-check` (TypeScript)
1. `npm run test:coverage` (Vitest)

**Optional:** Pre-commit hooks auto-enforce checks:

```bash
pre-commit install          # One-time setup
pre-commit run --all-files  # Manual run
```

______________________________________________________________________

## Code Layout & Where to Change

**Backend Layers:**

- **API Layer** (`app/api/v1/endpoints/`): HTTP only, delegate to core/services
- **Core Layer** (`app/core/`): Business logic, pure functions, 95%+ coverage
  required
- **Services** (`app/services/`): AI provider integrations, external APIs
- **Schemas** (`app/schemas/`): Pydantic models (use Optional\[T\] not T|None
  for Py3.12)
- **Tests** (`backend/tests/`): Mirror app structure, use pytest markers: @unit,
  @smoke, @e2e

**Frontend Layers:**

- **Components** (`src/lib/components/`): Svelte single-file components with
  TypeScript
- **Routes** (`src/routes/`): SvelteKit pages (+page.svelte, +layout.svelte)
- **Stores** (`src/lib/stores/`): Svelte stores (no extra frameworks)
- **Tests** (`src/**/*.test.ts`): Vitest + Testing Library (mock all APIs)

## Error Handling & Logging

**Use standard exception pattern** (see `backend/app/core/errors.py` and
[ADR-004](docs/adr/004-error-handling-patterns.md)):

```python
from app.core.errors import LuminoteException
raise LuminoteException(code="ERROR_CODE", message="...", status_code=400, details={...})
```

**Never log:** API keys, tokens, passwords, user data, auth headers

**Test markers:** Use `@pytest.mark.unit`, `@pytest.mark.smoke`,
`@pytest.mark.e2e`

## Design Principles (NEVER violate)

1. **Two-pane reading is primary** — Translation always visible right pane
   (never replace)
1. **On-demand AI, user-controlled cost** — All AI ops explicitly user-triggered
   (no background calls)
1. **BYOK multi-provider** — Users provide API keys; support OpenAI, Anthropic,
   etc.
1. **Configurable governance** — Make prompts, terminology configurable per task
   type
1. **All AI outputs are versioned assets** — Save with full provenance (model,
   prompt, blocks)
1. **Compliance-first** — Never bypass auth, anti-bot, paywalls automatically

## Data Model Concepts

Understand these core abstractions when working on code:

- **Document** — Extracted & cleaned content from URL
- **Block** — Normalized unit (paragraph, heading, list, quote, code, image)
- **Translation** — Block-mapped translation with version tracking
- **AI Job** — Model request with prompt version & metadata
- **Artifact** — Saved AI Job output (note, link card, verification, etc.)

______________________________________________________________________

## Configuration Files (Edit only when necessary)

- `backend/pyproject.toml` — Dependencies, Python version, tool config
- `backend/requirements.txt` — Keep in sync with pyproject.toml
- `frontend/package.json` — Frontend dependencies and scripts
- `.pre-commit-config.yaml` — Pre-commit hooks config
- `.github/workflows/*.yml` — CI pipeline steps (modify with care)
- `AGENTS.md` — Development playbook (coordinate major edits)

______________________________________________________________________

## Reference Documentation (Trust these first, search only if incomplete)

1. **[AGENTS.md](AGENTS.md)** — Development playbook (613 lines)
1. **[ARCHITECTURE.md](ARCHITECTURE.md)** — System architecture (140 lines)
1. **[docs/adr/](docs/adr/)** — Architecture Decision Records (5 files)
1. **[docs/API.md](docs/API.md)** — API specifications
1. **[CONTRIBUTING.md](CONTRIBUTING.md)** — Full setup guide (601 lines)
1. **[README.md](README.md)** — Project overview (257 lines)

______________________________________________________________________

## Validation Checklist (Before Finishing)

- [ ] Code passes quality gates: `isort`, `black`, `ruff`, `mypy` (backend) OR
  `eslint`, `prettier`, `tsc` (frontend)
- [ ] Tests pass with coverage ≥95% (core), ≥85% (other)
- [ ] No secrets committed (API keys, tokens, internal URLs)
- [ ] Architecture respected: two-pane reading, BYOK, user-triggered AI
- [ ] ADRs reviewed (if making architectural decisions)
- [ ] Changes focused with minimal blast radius
- [ ] Pre-commit hooks pass locally

______________________________________________________________________

**Last Updated:** January 9, 2026 | **Applies to:** Luminote Phase 1 development
