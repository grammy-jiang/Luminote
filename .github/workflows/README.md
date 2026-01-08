# GitHub Actions CI/CD Workflows

This directory contains GitHub Actions workflows for Continuous Integration and Continuous Deployment.

## Workflows

### 1. Backend CI (`backend.yml`)

**Triggers:**
- Pull requests that modify `backend/**` or the workflow file itself
- Pushes to `main` branch that modify `backend/**` or the workflow file itself

**Jobs:**
- **Backend Quality Checks**: Runs linting, formatting, type checking, and tests
  - Python 3.12 setup with pip caching
  - Install dependencies from `requirements.txt` and dev dependencies
  - Run `isort --check-only` for import sorting
  - Run `black --check` for code formatting
  - Run `ruff check` for linting
  - Run `mypy` for type checking
  - Run `pytest` with coverage reporting
  - Upload coverage reports to Codecov (optional)
  - Upload coverage HTML artifacts

**Expected Duration:** ~3-5 minutes

### 2. Frontend CI (`frontend.yml`)

**Triggers:**
- Pull requests that modify `frontend/**` or the workflow file itself
- Pushes to `main` branch that modify `frontend/**` or the workflow file itself

**Jobs:**
- **Frontend Quality Checks**: Runs linting, formatting, type checking, and tests
  - Node.js 22 setup (caching disabled due to no package-lock.json)
  - Install dependencies with `npm install`
  - Run `npx svelte-kit sync` to generate `.svelte-kit` directory
  - Run `npm run lint` (ESLint)
  - Run `npm run format -- --check` (Prettier)
  - Run `npm run type-check` (TypeScript)
  - Run `npm run test:coverage` (Vitest)
  - Upload coverage reports to Codecov (optional)
  - Upload coverage artifacts

**Expected Duration:** ~2-4 minutes

### 3. Combined CI (`ci.yml`)

**Triggers:**
- All pull requests
- Pushes to `main` branch

**Jobs:**
- **Backend CI**: Same as backend.yml
- **Frontend CI**: Same as frontend.yml
- **CI Success**: Aggregates results from both backend and frontend jobs
  - Only succeeds if both backend and frontend jobs pass
  - Required status check for PRs

**Expected Duration:** ~3-5 minutes (jobs run in parallel)

## Local Testing

Before pushing, ensure all checks pass locally:

### Backend

```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run all checks (should match CI)
isort --check-only app/ tests/
black --check app/ tests/
ruff check app/ tests/ --no-fix
mypy app/
pytest --cov=app --cov-report=term-missing
```

### Frontend

```bash
cd frontend

# Run all checks (should match CI)
npm install
npx svelte-kit sync
npm run lint
npm run format -- --check
npm run type-check
npm run test:coverage
```

## Workflow Status

You can view workflow status in:
- Pull request checks tab
- Actions tab in the repository
- Repository README badges (optional)

## Coverage Reports

Coverage reports are uploaded to:
1. **Codecov** (if `CODECOV_TOKEN` secret is configured)
2. **GitHub Actions Artifacts** (available for 7 days)
   - Backend: `backend-coverage-report`
   - Frontend: `frontend-coverage-report`

To download artifacts:
1. Go to Actions → Select workflow run
2. Scroll to "Artifacts" section
3. Download the coverage report

## Path Filters

Workflows use path filters to run only when relevant files change:
- Backend workflow: Only runs when `backend/**` changes
- Frontend workflow: Only runs when `frontend/**` changes
- Combined CI workflow: Runs on all changes

This improves CI performance and reduces unnecessary workflow runs.

## Troubleshooting

### "Action Required" Status
If you see "action_required" as the workflow conclusion, it means the workflow requires approval from a repository maintainer. This is a GitHub security feature for:
- First-time contributors
- Bot accounts (like copilot-swe-agent)
- Workflows from forks

**Solution:** Repository owner needs to approve the workflow run from the Actions tab.

### Backend: Module Not Found
Ensure `pip install -e ".[dev]"` is run to install the package in editable mode.

### Frontend: Type Check Fails
Run `npx svelte-kit sync` before `npm run type-check` to generate the `.svelte-kit` directory.

### Frontend: No Lock File Warning
The project currently doesn't use `package-lock.json`. Workflows use `npm install` instead of `npm ci`.

## Configuration

### Required Secrets (Optional)
- `CODECOV_TOKEN`: For uploading coverage reports to Codecov

### Python Version
- **3.12** (matches `pyproject.toml` and local development)

### Node.js Version
- **22** (matches `package.json` and local development)

## Maintenance

When updating dependencies or tools:
1. Update local configuration files (`pyproject.toml`, `package.json`)
2. Update workflow files to match
3. Test locally before committing
4. Verify workflow runs pass in CI

## Future Improvements

- [ ] Add deployment workflows (CD)
- [ ] Add frontend npm caching (requires package-lock.json)
- [ ] Add matrix testing for multiple Python/Node versions
- [ ] Add security scanning (CodeQL, Dependabot)
- [ ] Add performance benchmarks
- [ ] Generate coverage badges
