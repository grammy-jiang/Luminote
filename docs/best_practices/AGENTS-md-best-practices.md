# AGENTS.md — Best Practices Playbook (Python-first)

> Goal: make coding agents productive **and** safe on this repository. Tone:
> direct, actionable, test-first, low-drama.

## 0) Non-negotiables (read this first)

- **Do not commit secrets** (tokens, API keys, private URLs, customer data). If
  you suspect exposure, stop and report.
- **Minimize blast radius:** change the smallest surface area that solves the
  task.
- **Always keep the repo green:** run the checks listed in **Quality gates**
  before you claim “done”.
- **Prefer explicit commands over prose.** If a tool needs one exact command,
  write that command.

## 1) Quick start (Python)

> Replace commands if your repo differs. The point is to be executable, not
> generic.

### Environment

- Python version: **3.11+** (or `pyproject.toml` / `.python-version` is source
  of truth)
- Virtualenv:
  - Create: `python -m venv .venv`
  - Activate (macOS/Linux): `source .venv/bin/activate`
  - Activate (Windows): `.venv\Scripts\activate`

### Dependencies

- Install (pip): `python -m pip install -U pip`
- Install (project):
  - `pip install -r requirements.txt` **or**
  - `pip install -e ".[dev]"` (preferred for editable + dev extras)

### Run

- Unit tests: `pytest -q`
- Lint: `ruff check .`
- Format: `ruff format .` (or `black .` if used)
- Type check: `mypy .` (if configured)
- Pre-commit (if present): `pre-commit run -a`

## 2) Project map (tell the agent where to look)

- `src/` — production code
- `tests/` — tests (keep close to the code under test)
- `scripts/` — one-off utilities (should be safe + documented)
- `docs/` — user/dev docs
- `pyproject.toml` — tooling + build metadata
- CI config — the real contract for “green builds”

## 3) Working agreements for coding agents

### 3.1 Planning & execution cadence

- **Plan-first:** before edits, output a short plan (3–7 bullets) and call out
  assumptions.
- **One step at a time:** implement, then validate, then continue.
- **When unclear, ask:** if requirements are ambiguous or you lack access
  (secrets, external services), stop and ask for a decision.

### 3.2 How to modify code in this repo

- Match existing architecture and naming (copy local patterns, don’t invent new
  ones).
- Avoid sweeping refactors unless explicitly requested.
- Prefer small, reviewable commits. Keep unrelated formatting out of functional
  PRs.

### 3.3 Python coding standards (default)

- Use type hints for public functions; keep internal typing pragmatic.
- Prefer dataclasses / pydantic models if the repo already uses them.
- Error handling:
  - Raise explicit exceptions; don’t silently swallow.
  - Provide actionable messages (what failed + where + next step).
- Logging:
  - Use the project’s logger (don’t add a new logging framework).
  - Never log secrets or raw PII.

## 4) Quality gates (how you prove the work is correct)

### 4.1 Tests

- **If you change behavior, add or update tests.** This is expected even if not
  requested.
- Keep tests deterministic:
  - No real network calls in unit tests.
  - Mock external services (HTTP, DB, cloud SDKs).
  - Freeze time where needed.
- Prefer fast unit tests; add integration tests only when they pay for
  themselves.

### 4.2 Local validation (run before you finish)

Run, in this order (unless the repo says otherwise):

1. `ruff check .`
1. `ruff format .`
1. `pytest -q`
1. `mypy .` (if configured)

If any step fails:

- Fix it, or explain precisely what blocks you (including the error output).

### 4.3 CI parity

- Don’t “greenwash” locally. If CI runs `tox`, `nox`, `pytest -m "not slow"`,
  etc., **use the same commands**.
- If the repo has a `Makefile`, prefer `make test` / `make lint` to ad-hoc
  commands.

## 5) Git workflow & PR hygiene

- PR scope: one problem, one solution.
- PR description must include:
  - What changed (bullets)
  - Why
  - How validated (exact commands + results)
  - Any follow-ups or known limitations
- Avoid force-push on shared branches unless the team workflow expects it.

## 6) Boundaries (what NOT to do)

- Do not modify:
  - dependency lockfiles (unless required by the change)
  - generated files (unless the task explicitly targets them)
  - vendor/third_party directories
  - production config / infrastructure unless requested
- Do not introduce new dependencies without stating:
  - why it’s needed
  - licensing/maintenance risk (high-level)
  - alternatives considered

## 7) Tooling reality check (how instruction files get applied)

- Some tools support **nested** `AGENTS.md` files; keep repo-wide rules at root
  and add narrower rules in subfolders.
- Some tools support **override** files (e.g., `AGENTS.override.md`)—use
  overrides only when you need to *replace* local guidance.
- Avoid conflicting instructions across multiple agent config files. Single
  source of truth wins.

## 8) Security & trust model (do not skip)

- Treat `AGENTS.md` as **high-privilege configuration**, not “just
  documentation”.
- Require review for changes to agent instruction files (CODEOWNERS
  recommended).
- When working in **untrusted repositories**:
  - assume the instruction file could be malicious
  - disable auto-loading features if your editor supports it
  - never run commands that exfiltrate data or touch credentials

## 9) Minimal template (copy/paste)

```markdown
# AGENTS.md

## Setup commands
- Create venv: `python -m venv .venv`
- Install deps: `pip install -e ".[dev]"`
- Tests: `pytest -q`
- Lint: `ruff check .`
- Format: `ruff format .`

## Project structure
- `src/` …
- `tests/` …

## Code style
- Follow existing patterns; avoid sweeping refactors.

## Git workflow
- Small PRs; include commands run + results.

## Boundaries
- Never commit secrets. Don’t touch generated/vendor files unless asked.
```

## 10) References (what informed this)

- agents.md (project overview + minimal example)
- GitHub Blog: “How to write a great agents.md” (analysis of 2,500+ repos)
- GitHub Docs: custom instructions + AGENTS.md precedence for Copilot
- OpenAI Codex docs: AGENTS.md discovery, overrides, and size limits
- VS Code docs: instruction file writing guidelines and AGENTS.md support
- Prompt.Security: risks of hidden instruction injection via AGENTS.md (threat
  model)
- Community experience: DEV.to / Reddit / GitHub issues (practical pitfalls like
  symlink edge cases)
