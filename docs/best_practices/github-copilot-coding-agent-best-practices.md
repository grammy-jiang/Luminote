<!-- mdformat-toc start --slug=github --maxlevel=3 --minlevel=1 -->

- [GitHub Copilot Coding Agent – Best Practices for High-Quality, Autonomous Work](#github-copilot-coding-agent-%E2%80%93-best-practices-for-high-quality-autonomous-work)
  - [1. Objective & Scope](#1-objective--scope)
  - [2. Mental Model: What the Agent Is (and Isn't)](#2-mental-model-what-the-agent-is-and-isnt)
  - [3. The Configuration File Hierarchy](#3-the-configuration-file-hierarchy)
  - [4. Writing Effective Instructions](#4-writing-effective-instructions)
  - [5. Pre-Warming the Environment](#5-pre-warming-the-environment)
  - [6. Designing Tasks the Agent Can Complete](#6-designing-tasks-the-agent-can-complete)
  - [7. Optimizing Issue and Prompt Structure](#7-optimizing-issue-and-prompt-structure)
  - [8. Constraining Blast Radius](#8-constraining-blast-radius)
  - [9. Embedding the Agent in CI and Team Process](#9-embedding-the-agent-in-ci-and-team-process)
  - [10. Security Considerations](#10-security-considerations)
  - [11. Common Anti-Patterns](#11-common-anti-patterns)
  - [12. Operational Checklist](#12-operational-checklist)
  - [13. Summary](#13-summary)
  - [14. Quick Reference](#14-quick-reference)
  - [References](#references)

<!-- mdformat-toc end -->

# GitHub Copilot Coding Agent – Best Practices for High-Quality, Autonomous Work<a name="github-copilot-coding-agent-%E2%80%93-best-practices-for-high-quality-autonomous-work"></a>

______________________________________________________________________

## 1. Objective & Scope<a name="1-objective--scope"></a>

**English**

This document defines best practices for using the GitHub Copilot **coding
agent** to maximize **high-quality, useful work** in each session. The goal is
to get reviewable, production-ready PRs merged safely—not to generate large
volumes of edits or artificially extend agent runtime.

Key assumptions:

- Copilot coding agent runs inside **GitHub Actions** and is designed for
  **short, autonomous tasks** that end with a pull request, not for multi-hour
  batch jobs.
- Session duration is **finite and not configurable** from the repository. Treat
  each run as "tens of minutes to complete a well-scoped change," not a
  multi-hour pipeline.
- Long-running work (heavy tests, data pipelines, builds) should be handled by
  **standard CI workflows** triggered by the agent's PR, not by the agent
  itself.

______________________________________________________________________

## 2. Mental Model: What the Agent Is (and Isn't)<a name="2-mental-model-what-the-agent-is-and-isnt"></a>

**English**

Think of Copilot coding agent as:

- A **temporary contractor**: you give it a well-written ticket, it does focused
  work, opens a PR, and exits.
- Not a daemon, not a job scheduler, and not a replacement for CI.

The agent operates in an ephemeral development environment powered by GitHub
Actions. When you assign an issue to Copilot or mention `@copilot` in a PR
comment, the agent evaluates the task, explores your repository, makes changes,
executes automated tests and linters, then opens a pull request with its work.

Entry points include: assigning issues directly to "Copilot," mentioning
`@copilot` in pull request comments, using the agents panel at
`github.com/copilot/agents`, delegating tasks via VS Code's GitHub Pull Requests
extension, or using the `/delegate` command in GitHub CLI.

Position the agent around: **small, well-scoped issues, clear acceptance
criteria, and quick PR turnaround**.

______________________________________________________________________

## 3. The Configuration File Hierarchy<a name="3-the-configuration-file-hierarchy"></a>

**English**

Understanding the instruction file hierarchy is fundamental to controlling agent
behavior. Files are processed in a specific priority order, with more specific
instructions taking precedence.

**Repository-wide instructions** live in `/.github/copilot-instructions.md` and
apply to all tasks. This file should tell Copilot:

- How to **build** the project
- How to **run tests**
- Coding conventions, frameworks, and "don't" rules
- The **quality bar / definition of done** for code changes (required tests,
  lint/type checks, documentation updates, review expectations)

**Path-specific instructions** use YAML frontmatter in
`/.github/instructions/**/*.instructions.md` files to target specific file
patterns:

```yaml
---
applyTo: "app/models/**/*.rb"
excludeAgent: "code-review"
---

# These instructions apply only to Ruby model files

```

**Agent instruction files** (`**/AGENTS.md`, `/CLAUDE.md`, `/GEMINI.md`) provide
compatibility with multiple AI coding tools. The `AGENTS.md` format is
particularly powerful because the nearest file in the directory tree takes
precedence, allowing fine-grained control over different parts of your codebase.

**Custom agent profiles** in `.github/agents/CUSTOM-AGENT-NAME.md` create
specialized agents for specific workflows—a test specialist, documentation
writer, or security reviewer, each with distinct instructions and permissions.

______________________________________________________________________

## 4. Writing Effective Instructions<a name="4-writing-effective-instructions"></a>

**English**

GitHub's analysis of over 2,500 repositories reveals that effective instruction
files share five critical elements: a clear role definition, executable commands
listed early, concrete code examples, explicit boundaries, and complete tech
stack specifications with versions.

**Put executable commands early.** The agent needs to know how to build, test,
and validate your project immediately:

```markdown

## Available Commands

- `make build` - Build the project
- `make test` - Run unit tests
- `make fmt` - Format code before committing
- `make ci` - Full CI check (build, lint, test)

```

**One real code snippet beats three paragraphs.** Instead of describing your
error handling philosophy, show it:

```python

# Error handling pattern for this project

async def fetch_user(user_id: str) -> User:
    try:
        response = await client.get(f"/users/{user_id}")
        response.raise_for_status()
        return User.model_validate(response.json())
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch user {user_id}: {e.response.status_code}")
        raise UserNotFoundError(user_id) from e

```

**Define three-tier boundaries** using "always do," "ask first," and "never do"
rules:

- ✅ **Always**: Run `make fmt` before commits, write unit tests for new
  functions
- ⚠️ **Ask first**: Adding new dependencies, modifying database schemas
- 🚫 **Never**: Modify production configuration, remove existing tests, change
  authentication logic

**Provide fast, focused test commands**—not just "run the full suite":

```markdown

## Fast Validation Commands

- `pytest tests/service_x -q` - Quick tests for service_x only
- `npm test -- --testPathPattern=auth` - Auth module tests only

```

______________________________________________________________________

## 5. Pre-Warming the Environment<a name="5-pre-warming-the-environment"></a>

**English**

A major source of wasted agent time is repeated environment setup (checkout,
dependency install, tooling). Use a dedicated workflow:
`.github/workflows/copilot-setup-steps.yml`.

This workflow is referenced by Copilot when running the coding agent and should
contain the **stable, reusable setup steps** for your repo so that each agent
run starts from a pre-warmed environment instead of re-installing everything
from scratch:

- Runs in GitHub Actions **before** the agent starts
- Lets you:
  - Install system packages
  - Restore dependencies (pip, npm, NuGet, etc.)
  - Perform an initial successful build or smoke test

Example:

```yaml

# .github/workflows/copilot-setup-steps.yml

name: Copilot Setup Steps

on:
  push:
    paths:
      - .github/workflows/copilot-setup-steps.yml

jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest
    timeout-minutes: 45

    permissions:
      contents: read

    steps:
      - uses: actions/checkout@v5

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Verify build works
        run: make build

      - name: Verify tests can run
        run: make test --dry-run

```

______________________________________________________________________

## 6. Designing Tasks the Agent Can Complete<a name="6-designing-tasks-the-agent-can-complete"></a>

**English**

When you assign an issue to `@copilot`, the **issue is the prompt**. For high
efficiency and high-quality output:

**Scope tightly.** One agent task = one logical change:

- ✅ Implement a specific feature flag
- ✅ Refactor a single module / component
- ✅ Add tests for a clearly defined surface area
- ❌ "Modernize the whole repo"
- ❌ "Improve performance everywhere"

**Right-size tasks for a single agent session.** Aim for changes that mostly
touch one service, module, or well-defined slice of the repo. A good rule of
thumb: modifications reviewable by a human in 15–30 minutes. If a task naturally
splits into multiple PRs, create multiple issues and let the agent handle them
iteratively.

**Write issue templates for agents.** Include at minimum:

- **Context** – what this code does in business terms
- **Change request** – what should be different after the agent finishes
- **Acceptance criteria** – what we will check to decide if the PR is acceptable
- **How to build & test** – commands, test suites, environment notes
- **Files to modify** – explicit list of files the agent should touch
- **Do not change** – files, packages, or behaviors that must be preserved
- **Known edge cases & pitfalls** – prevent the agent from re-introducing
  historical bugs

**Make success measurable.** Tie acceptance criteria to concrete checks:
specific test commands, linters, or smoke flows ("this endpoint still returns
200 for this payload"). Call out what must **not** break (critical paths, SLAs,
or user journeys).

**Reference existing design docs / ADRs.** Link to design docs, architecture
diagrams, or ADRs so the agent does not have to infer architecture from scratch.

**Include visual context when relevant.** The agent supports vision models and
can work from screenshots, mockups, or diagrams.

Example issue structure:

```markdown

## Problem

The user profile API returns 500 when accessing /api/users/{id} for users without profile photos.

## Context

This endpoint is called ~10K times/day. The photo field was added in v2.3 but older users don't have it populated.

## Acceptance Criteria

- [ ] API returns default avatar URL when user has no photo
- [ ] Add unit tests covering the edge case
- [ ] Update API documentation in /docs/api.md
- [ ] Endpoint returns 200 for test user ID `test-user-no-photo`

## Files to Modify

- `src/api/routes/users.py` - Add fallback logic
- `tests/api/test_users.py` - Add test cases
- `docs/api.md` - Update response schema

## Do Not Change

- Authentication middleware
- Database schema

## How to Test

- `pytest tests/api/test_users.py -v`
- `curl localhost:8000/api/users/test-user-no-photo` should return 200

```

______________________________________________________________________

## 7. Optimizing Issue and Prompt Structure<a name="7-optimizing-issue-and-prompt-structure"></a>

**English**

Small structural tweaks in issues can significantly improve outcomes:

**Ask for a plan first.** Request that the agent write a short numbered plan
before implementing. This improves alignment and makes review easier:

```markdown

Before making changes, please:
1. Write a numbered plan of the changes you'll make
2. List any assumptions you're making
3. Then implement the plan

```

**Use explicit follow-up prompts** when the agent stops with TODOs. The comment
`@copilot Please replace the TODO with a full implementation` often pushes past
cautious stopping points.

**Batch PR comments using "Start a review"** rather than adding individual
comments. Submitting all feedback at once triggers more comprehensive work than
piecemeal requests.

**Reference earlier goals in follow-up comments.** When the agent loses focus
during a long PR thread, explicitly reminding it of the original objectives
helps it regain context.

______________________________________________________________________

## 8. Constraining Blast Radius<a name="8-constraining-blast-radius"></a>

**English**

Use explicit constraints to keep changes focused and safe:

- Tell the agent to **work only in specific paths** (for example
  `src/service_x/` and `tests/service_x/`), especially in monorepos.
- Ask the agent to avoid repo-wide reformatting or large search/replace that
  creates noisy diffs.
- For infrastructure, schema, or data changes, split work into: "agent prepares
  code + tests" and "human-run pipeline applies change".

Create **specialized custom agents** for recurring quality concerns. A test
specialist agent with focused instructions produces better results than asking
the general agent to also write tests:

```markdown

---
name: test-agent
description: QA specialist for comprehensive testing
---
You are a QA software engineer. You:
- Write tests following existing patterns in /tests/
- Run tests and iterate on failures
- Never modify source code or remove failing tests
- Use table-driven tests when testing multiple inputs

```

______________________________________________________________________

## 9. Embedding the Agent in CI and Team Process<a name="9-embedding-the-agent-in-ci-and-team-process"></a>

**English**

Integrate the agent into existing review and governance instead of bypassing it:

- Use `CODEOWNERS` so agent PRs automatically request review from the right
  maintainers.
- Keep **required checks strict** for agent PRs (tests, lint, type checks,
  security scans); do not weaken gates for automation.
- Disallow direct bot pushes to main: agents open PRs, humans review and merge.
- In higher-risk repos, require agent changes to pass through **staging / canary
  environments** before promotion.
- Track simple metrics (agent PR count, merge rate, average review changes, CI
  failure rate), periodically sample merged agent PRs and recurring review
  feedback, and use them to refine instructions, templates, and
  `copilot-instructions`.

**Start small and calibrate.** Use labels like `good-first-agent-task`,
`agent-refactor`, `agent-tests-only` to identify agent-suitable issues. Start
with tasks whose success is easily verified by local tests and small file sets.

______________________________________________________________________

## 10. Security Considerations<a name="10-security-considerations"></a>

**English**

While Copilot includes built-in security protections (CodeQL analysis, secret
scanning, dependency checking against GitHub's Advisory Database), treat
AI-generated commands and changes as **untrusted until reviewed**.

**Built-in protections:**

- The agent operates with read-only repository access
- Can only push to branches prefixed with `copilot/`
- Cannot approve or merge its own PRs
- Firewall-controlled internet access

**Additional guardrails you should implement:**

- Review shell commands proposed or executed by the agent
- Avoid giving the agent access to secrets it does not strictly need
- Keep destructive operations (infra changes, data deletions) behind separate,
  human-initiated workflows
- Never assign tasks involving authentication changes, secrets handling, or PII
  processing
- Configure branch protection rules that apply to Copilot branches
- Implement pre-commit hooks for additional secrets scanning

**Important note:** Research indicates AI code review may miss critical
vulnerabilities including SQL injection, XSS, and insecure deserialization.
These built-in tools supplement but don't replace dedicated security practices.
Always review generated code with security awareness before merging.

______________________________________________________________________

## 11. Common Anti-Patterns<a name="11-common-anti-patterns"></a>

**English**

1. **Massive, ambiguous tickets**

   - "Refactor the whole service so it's cleaner."
   - "Fix all performance issues in this repo."

   These cause the agent to burn its limited runtime thrashing around with no
   clear success condition.

1. **Letting the agent own long-running pipelines**

   Trying to have the agent run full multi-hour test suites or data jobs
   directly is inefficient. CI is built for that.

1. **Skipping setup steps**

   Re-installing dependencies and tools from scratch on every agent run
   drastically cuts into useful time.

1. **Blindly merging agent PRs**

   Copilot is powerful, but not infallible. Always review, run tests, and treat
   it as a junior dev who works fast but can be wrong.

1. **No explicit quality expectations**

   Simply writing "add tests" produces inconsistent results. Specify framework,
   coverage expectations, and patterns to follow.

1. **Missing dependency pre-installation**

   Several factors cause the agent to stop before completing a task. Missing
   dependencies trigger trial-and-error loops that exhaust resources.

______________________________________________________________________

## 12. Operational Checklist<a name="12-operational-checklist"></a>

**Before using the agent at scale**

**Repository Setup:**

- [ ] Add `.github/copilot-instructions.md` with build/test instructions, coding
  conventions, and quality expectations
- [ ] Add `.github/workflows/copilot-setup-steps.yml` to pre-warm dependencies
  and tools
- [ ] Configure path-specific instructions for complex areas of the codebase
- [ ] Decide which stacks warrant **custom agents** and set them up

**Issue Management:**

- [ ] Create issue templates specifically optimized as prompts for `@copilot`
- [ ] Define labels to identify agent-suitable tasks (`good-first-agent-task`,
  `agent-refactor`, etc.)
- [ ] Document the standard issue structure (Context, Change Request, Acceptance
  Criteria, Files to Modify, Do Not Change, How to Test)

**Quality and Security:**

- [ ] Configure CI workflows that run on PRs from the agent with full checks
- [ ] Verify `CODEOWNERS` will assign appropriate reviewers to agent PRs
- [ ] Document the **quality expectations for agent PRs** (tests to run, review
  rules, when to request design review)
- [ ] Document security guardrails around secrets and dangerous commands

**Ongoing Operations:**

- [ ] Track metrics (PR count, merge rate, CI failure rate)
- [ ] Schedule periodic review of merged agent PRs
- [ ] Establish process for updating instructions based on feedback

______________________________________________________________________

## 13. Summary<a name="13-summary"></a>

**English**

Use GitHub Copilot coding agent as a high-speed, short-lived coding assistant
that produces high-quality, reviewable PRs:

- Give it **well-scoped issues** with clear acceptance criteria and explicit
  file lists
- Provide a **pre-warmed environment** via `copilot-setup-steps.yml`
- Set **clear quality expectations** (tests, architecture, style) in repository
  instructions
- Maintain **strong CI and review guardrails**—same standards as human-authored
  code
- **Chain multiple focused sessions** rather than expecting multi-hour
  autonomous work

Do not expect it to behave like a long-running background worker. The gap
between mediocre and excellent results comes down to preparation:
well-structured instruction files, clearly written issues, pre-configured
environments, and explicit quality requirements.

The most successful teams use Copilot Agent for work it handles well (bug fixes,
test coverage, documentation, incremental features) while reserving complex
architectural decisions and security-critical code for human developers.

______________________________________________________________________

## 14. Quick Reference<a name="14-quick-reference"></a>

| Aspect          | Best Practice                                                           |
| --------------- | ----------------------------------------------------------------------- |
| Task scope      | One logical change, reviewable in 15-30 min                             |
| Issue structure | Context + Change + Acceptance + Files + Do Not Change + Test            |
| Instructions    | Commands first, code examples, three-tier boundaries                    |
| Environment     | Pre-warm with `copilot-setup-steps.yml`                                 |
| Quality gates   | Same as human code: tests, lint, security scans                         |
| Security        | No secrets access, review all commands, human-initiated destructive ops |
| Iteration       | Multiple focused sessions, not one long run                             |

______________________________________________________________________

## References<a name="references"></a>

- [GitHub Docs – About GitHub Copilot coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)
- [GitHub Docs – Best practices for using Copilot to work on tasks](https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks)
- [GitHub Docs – Repository-wide custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [GitHub Docs – Preinstalling tools in Copilot's environment](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)
- [GitHub Blog – How to write a great agents.md: Lessons from over 2,500 repositories](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)
- [GitHub Blog – Assigning and completing issues with coding agent](https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/)
- [GitHub Blog – GitHub Copilot coding agent 101](https://github.blog/ai-and-ml/github-copilot/github-copilot-coding-agent-101-getting-started-with-agentic-workflows-on-github/)
