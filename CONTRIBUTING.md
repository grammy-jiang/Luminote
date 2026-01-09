<!-- mdformat-toc start --slug=github --maxlevel=3 --minlevel=1 -->

- [Contributing to Luminote](#contributing-to-luminote)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Project Structure](#project-structure)
    - [Key Modules](#key-modules)
  - [Local Development](#local-development)
    - [Automated Setup (Recommended)](#automated-setup-recommended)
    - [Manual Setup](#manual-setup)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
    - [Pre-commit Hooks Setup](#pre-commit-hooks-setup)
  - [Development Standards](#development-standards)
    - [Python (Backend)](#python-backend)
    - [TypeScript (Frontend)](#typescript-frontend)
    - [Running Code Quality Checks](#running-code-quality-checks)
  - [Testing](#testing)
    - [Coverage Requirements](#coverage-requirements)
    - [Python Tests](#python-tests)
    - [TypeScript Tests](#typescript-tests)
  - [Building and Packaging](#building-and-packaging)
    - [Backend Package](#backend-package)
    - [Frontend Build](#frontend-build)
  - [Core Concepts](#core-concepts)
    - [Design Principles](#design-principles)
    - [Concept Model](#concept-model)
  - [Contribution Process](#contribution-process)
    - [Getting Started](#getting-started)
    - [Development Workflow](#development-workflow)
    - [Pull Request Requirements](#pull-request-requirements)
    - [Review Process](#review-process)
  - [Code of Conduct](#code-of-conduct)
    - [Our Commitment](#our-commitment)
    - [Unacceptable Behavior](#unacceptable-behavior)
    - [Enforcement](#enforcement)
  - [Support](#support)
    - [Resources](#resources)
  - [License](#license)

<!-- mdformat-toc end -->

# Contributing to Luminote<a name="contributing-to-luminote"></a>

Thank you for your interest in contributing to Luminote! This guide covers
development setup, coding standards, testing requirements, and the contribution
workflow.

## Table of Contents<a name="table-of-contents"></a>

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [Development Standards](#development-standards)
- [Testing](#testing)
- [Building and Packaging](#building-and-packaging)
- [Core Concepts](#core-concepts)
- [Contribution Process](#contribution-process)
- [Code of Conduct](#code-of-conduct)
- [Support](#support)

## Prerequisites<a name="prerequisites"></a>

Ensure you have:

- **Backend:** Python 3.12+ with `uv` for dependency management
- **Frontend:** Node.js 22+
- **APIs:** Valid API keys from OpenAI, Anthropic, or other supported providers
  (for testing)

## Project Structure<a name="project-structure"></a>

```
Luminote/
├── backend/                    # FastAPI backend package
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core business logic (95%+ coverage)
│   │   ├── models/            # Data models
│   │   └── services/          # External service integrations
│   ├── tests/                 # Test suite (unit, smoke, e2e)
│   ├── pyproject.toml         # Package configuration
│   └── requirements.txt       # Dependencies
├── frontend/                   # Svelte + TypeScript UI
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── stores/            # State management
│   │   ├── lib/               # Utilities
│   │   └── App.svelte         # Root component
│   ├── public/
│   └── package.json
└── docs/                       # Documentation
    ├── purpose_and_functionality.md
    ├── detailed-feature-specifications.md
    └── API.md

```

### Key Modules<a name="key-modules"></a>

- **`app/core/`** — Core business logic (95%+ test coverage required)
- **`app/api/`** — API endpoints and request handling
- **`app/services/`** — AI provider integrations and external services
- **`app/models/`** — Data structures and database models

## Local Development<a name="local-development"></a>

### Automated Setup (Recommended)<a name="automated-setup-recommended"></a>

The easiest way to set up your development environment is using the setup
script:

```bash
# Clone the repository
git clone https://github.com/grammy-jiang/Luminote.git
cd Luminote

# Run the setup script
./scripts/setup-dev.sh  # Linux/macOS
# OR
scripts\setup-dev.bat   # Windows
```

The script will:

- ✅ Verify Python 3.12+ and Node.js 22+ are installed
- ✅ Create backend virtual environment and install dependencies
- ✅ Install frontend dependencies
- ✅ Install pre-commit hooks
- ✅ Create `.env` files from examples
- ✅ Verify the setup by collecting tests

After setup, edit `backend/.env` to add your API keys, then start the servers.

### Manual Setup<a name="manual-setup"></a>

If you prefer manual setup or need more control:

### Backend Setup<a name="backend-setup"></a>

1. **Create and activate virtual environment:**

   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

1. **Install dependencies:**

   ```bash
   uv pip install -e ".[dev]"
   ```

1. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

1. **Start development server:**

   ```bash
   uv run luminote serve  # Runs on port 8000 using the project environment
   ```

### Frontend Setup<a name="frontend-setup"></a>

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

1. **Start development server:**

   ```bash
   npm run dev  # Serves at http://localhost:5000
   ```

### Pre-commit Hooks Setup<a name="pre-commit-hooks-setup"></a>

Pre-commit hooks automatically check your code quality before each commit. They
help catch issues early and maintain consistent code standards.

**Installation:**

```bash
# If you used the automated setup script, hooks are already installed
# Otherwise, install manually:

cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate.bat
uv pip install pre-commit
uv run pre-commit install
```

**Usage:**

```bash
# Hooks run automatically on git commit
git commit -m "your message"

# Run hooks manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-format --all-files
pre-commit run ruff --all-files
pre-commit run mypy --all-files

# Skip hooks if needed (use sparingly)
git commit --no-verify -m "your message"
```

**Configured Hooks:**

The following checks run automatically on commit:

- **Python Code Quality:**

  - `ruff` - Lint for code issues and style (with auto-fix)
  - `ruff-format` - Format code (replaces Black)
  - `pyupgrade` - Upgrade syntax for Python 3.12+
  - `docformatter` - Format docstrings
  - `mypy` - Type checking
  - `bandit` - Security vulnerability scanning

- **Configuration Files:**

  - `yamlfmt` - Format YAML files
  - `toml-sort` - Sort and format TOML files
  - `yamllint` - Lint YAML files

- **File Quality:**

  - Trailing whitespace removal
  - End-of-file fixes
  - JSON validation and formatting
  - Merge conflict detection
  - Case conflict detection

- **Shell Scripts:**

  - `shellcheck` - Shell script linting
  - `bashate` - Bash script style checking

- **Documentation:**

  - `mdformat` - Markdown formatting
  - `pymarkdown` - Markdown linting

**Performance:** Hooks complete in \<10 seconds on typical commits. First run
may be slower as it sets up hook environments.

## Development Standards<a name="development-standards"></a>

### Python (Backend)<a name="python-backend"></a>

Code must follow these standards:

- **Imports:** Format with `isort`
- **Code:** Format with `black`
- **Linting:** Check with `ruff` (no automatic formatting)
- **Type checking:** Validate with `mypy` (strict mode)
- **Standards:** Use type hints throughout and follow PEP 8

### TypeScript (Frontend)<a name="typescript-frontend"></a>

Code must follow these standards:

- **Code:** Format with `Prettier`
- **Linting:** Check with `ESLint`
- **Standards:** Use TypeScript best practices and prefer functional components

### Running Code Quality Checks<a name="running-code-quality-checks"></a>

**Python:**

```bash
cd backend

# Format imports and code
uv run isort app/ && uv run black app/

# Lint for issues
uv run ruff check app/ --no-fix

# Check type hints
uv run mypy app/

# Run all checks
uv run isort app/ && uv run black app/ && uv run ruff check app/ --no-fix && uv run mypy app/
```

**TypeScript:**

```bash

cd frontend

# Lint and format

npm run lint && npm run format

```

## Testing<a name="testing"></a>

### Coverage Requirements<a name="coverage-requirements"></a>

- **Core modules** (`app/core/`): minimum 95%
- **Other modules**: minimum 85%

Coverage below these thresholds blocks pull requests.

### Python Tests<a name="python-tests"></a>

**Run tests:**

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=app --cov-report=html

# Run specific test type
uv run pytest -m unit   # Unit tests
uv run pytest -m smoke  # Smoke tests
uv run pytest -m e2e    # End-to-end tests

# Test across all supported Python versions
uv run tox
```

**Test categories:**

- **Unit tests:** Individual functions and classes
- **Smoke tests:** Critical path verification
- **End-to-end tests:** Full workflow validation

### TypeScript Tests<a name="typescript-tests"></a>

**Run tests:**

```bash

cd frontend

# Run all tests

npm test

# Generate coverage report

npm run test:coverage

# Test across Node.js versions

npm run test:all-versions

```

Use the same test categorization as Python tests.

## Building and Packaging<a name="building-and-packaging"></a>

### Backend Package<a name="backend-package"></a>

The backend is a Python package ready for PyPI publication.

**Development installation:**

```bash

cd backend
uv pip install -e ".[dev]"

```

**Build distributions:**

```bash
cd backend
uv run python -m build
```

Creates in `backend/dist/`:

- `luminote-*.whl` — Wheel distribution
- `luminote-*.tar.gz` — Source distribution

**Run server:**

```bash
uv run luminote serve
```

The `luminote serve` command is defined as an entry point in `pyproject.toml`
under `[project.scripts]`.

**Test local build:**

```bash
uv pip install backend/dist/luminote-*.whl
uv run luminote serve
```

**Upload to PyPI (maintainers only):**

```bash
cd backend
uv run python -m twine upload dist/*
```

### Frontend Build<a name="frontend-build"></a>

**Build for production:**

```bash

cd frontend
npm run build

```

Output is in `frontend/public/build/`.

## Core Concepts<a name="core-concepts"></a>

### Design Principles<a name="design-principles"></a>

These principles guide all architecture and feature decisions:

1. **Two-pane reading is primary** — Translation always visible on the right
   pane. Never replace this with alternative content.

1. **On-demand AI, user-controlled cost** — All AI operations must be explicitly
   triggered by users. No automatic background AI calls.

1. **BYOK multi-provider** — Users bring their own API keys. Support multiple
   providers (OpenAI, Anthropic, etc.).

1. **Configurable governance** — Make prompts and terminology configurable per
   task type for consistency.

1. **All AI outputs are versioned assets** — Save every AI output with full
   provenance (model, prompt version, referenced blocks) for replay and
   regeneration.

1. **Compliance-first** — Never bypass authentication, anti-bot mechanisms, or
   paywalls automatically. All sessions are user-driven.

### Concept Model<a name="concept-model"></a>

Key abstractions throughout the codebase:

- **Document** — Extracted and cleaned content from a URL
- **Block** — Normalized content unit (paragraph, heading, list, quote, code)
- **Translation** — Block-mapped translation with version tracking
- **AI Job** — Any model request with prompt version and metadata
- **Artifact** — Saved output from an AI Job (note, link card, verification,
  etc.)

Maintain consistency by understanding these abstractions when working on the
codebase.

## Contribution Process<a name="contribution-process"></a>

### Getting Started<a name="getting-started"></a>

1. Check [GitHub Issues](https://github.com/grammy-jiang/Luminote/issues) for
   existing work
1. Comment on the issue to claim it
1. For significant changes, open a discussion first

### Development Workflow<a name="development-workflow"></a>

1. **Fork and clone:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/Luminote.git
   cd Luminote
   ```

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/short-description
   ```

   Use prefixes: `feature/`, `fix/`, `docs/`, `refactor/`, `test/`, `chore/`

1. **Make changes:**

   - Follow development standards
   - Add tests for new functionality
   - Update documentation

1. **Verify quality:**

   ```bash
   # Backend
   cd backend && uv run pytest && uv run isort app/ && uv run black app/ && \
     uv run ruff check app/ --no-fix && uv run mypy app/

   # Frontend
   cd frontend && npm test && npm run lint && npm run format
   ```

1. **Commit with conventional commits:**

   ```bash
   git commit -m "type: short description"
   ```

   Types: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

1. **Push and open a pull request:**

   ```bash
   git push origin feature/short-description
   ```

### Pull Request Requirements<a name="pull-request-requirements"></a>

Every PR must:

- Have a clear, descriptive title
- Include a description explaining **what**, **why**, and **how**
- Reference related issues
- Pass all tests (uv run pytest for Python, npm test for TypeScript)
- Meet coverage requirements (core >95%, other >85%)
- Pass code quality checks (isort, black, ruff, mypy for Python; ESLint,
  Prettier for TypeScript)
- Include screenshots for UI changes
- Update documentation if applicable

### Review Process<a name="review-process"></a>

- Reviewers request changes for clarity, consistency, or quality
- Address feedback promptly; push new commits (do not force-push)
- Keep discussions professional and focused
- Maintainers merge when all requirements are met

## Code of Conduct<a name="code-of-conduct"></a>

### Our Commitment<a name="our-commitment"></a>

We are committed to a welcoming and inclusive environment:

- Be respectful and constructive
- Welcome newcomers and help them succeed
- Focus on code and design, not personalities
- Accept responsibility for mistakes and learn from them
- Prioritize community well-being

### Unacceptable Behavior<a name="unacceptable-behavior"></a>

- Harassment, discrimination, or hate speech
- Trolling, insults, or personal attacks
- Sharing others' private information
- Professional misconduct

### Enforcement<a name="enforcement"></a>

Violations result in:

1. **First offense:** Warning and discussion
1. **Repeated violations:** Temporary repository ban
1. **Severe violations:** Permanent ban

Report concerns directly to maintainers.

## Support<a name="support"></a>

### Resources<a name="resources"></a>

- **Issues:** [GitHub Issues](https://github.com/grammy-jiang/Luminote/issues)
  for bugs and features
- **Discussions:**
  [GitHub Discussions](https://github.com/grammy-jiang/Luminote/discussions) for
  questions
- **Security:** Contact maintainers directly for vulnerabilities (do not open
  public issues)

## License<a name="license"></a>

By contributing to Luminote, you agree that your contributions will be licensed
under the [GNU General Public License v3.0 (GPL-3.0)](LICENSE).

______________________________________________________________________

**Thank you for contributing to Luminote!**
