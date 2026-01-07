<!-- mdformat-toc start --slug=github --maxlevel=3 --minlevel=1 -->

- [Best Practices for GitHub Copilot Custom Agents in VS Code](#best-practices-for-github-copilot-custom-agents-in-vs-code)
  - [1) What “custom agents” are (and what they’re not)](#1-what-%E2%80%9Ccustom-agents%E2%80%9D-are-and-what-they%E2%80%99re-not)
  - [2) File architecture: the “layered contract” approach](#2-file-architecture-the-%E2%80%9Clayered-contract%E2%80%9D-approach)
    - [2.1 Recommended repo layout](#21-recommended-repo-layout)
    - [2.2 Baseline contract: `.github/copilot-instructions.md`](#22-baseline-contract-githubcopilot-instructionsmd)
    - [2.3 Scoped policies: `.github/instructions/*.instructions.md`](#23-scoped-policies-githubinstructionsinstructionsmd)
    - [2.4 Agent profiles: `.github/agents/*.agent.md`](#24-agent-profiles-githubagentsagentmd)
    - [2.5 Local boundaries: `AGENTS.md` (optional)](#25-local-boundaries-agentsmd-optional)
  - [3) Instruction precedence and conflict management](#3-instruction-precedence-and-conflict-management)
    - [3.1 Three tiers exist in practice](#31-three-tiers-exist-in-practice)
    - [3.2 VS Code-specific behavior to plan for](#32-vs-code-specific-behavior-to-plan-for)
  - [4) The six essentials (quality checklist for every instruction file)](#4-the-six-essentials-quality-checklist-for-every-instruction-file)
  - [5) Tool governance: least privilege by default](#5-tool-governance-least-privilege-by-default)
    - [5.1 Why tool restriction matters](#51-why-tool-restriction-matters)
    - [5.2 Recommended tool sets by agent type](#52-recommended-tool-sets-by-agent-type)
    - [5.3 “Boundaries” rubric you should standardize](#53-%E2%80%9Cboundaries%E2%80%9D-rubric-you-should-standardize)
  - [6) Multi-agent workflows: handoffs are your SDLC control plane (VS Code)](#6-multi-agent-workflows-handoffs-are-your-sdlc-control-plane-vs-code)
    - [6.1 Recommended handoff chain (TDD-friendly)](#61-recommended-handoff-chain-tdd-friendly)
  - [7) Prompt design: reduce ambiguity, increase determinism](#7-prompt-design-reduce-ambiguity-increase-determinism)
  - [8) MCP servers in VS Code: configuration and safety](#8-mcp-servers-in-vs-code-configuration-and-safety)
    - [8.1 Configuration principles](#81-configuration-principles)
    - [8.2 Tool design principles (when you are the MCP server author)](#82-tool-design-principles-when-you-are-the-mcp-server-author)
  - [9) GitHub Copilot Coding Agent compatibility (practical notes)](#9-github-copilot-coding-agent-compatibility-practical-notes)
    - [9.1 Deterministic setup](#91-deterministic-setup)
    - [9.2 Avoid thrash in reviews](#92-avoid-thrash-in-reviews)
    - [9.3 Don’t rely on VS Code-only conveniences](#93-don%E2%80%99t-rely-on-vs-code-only-conveniences)
  - [10) Common failure modes (and how to avoid them)](#10-common-failure-modes-and-how-to-avoid-them)
  - [11) Practical templates (copy/paste starters)](#11-practical-templates-copypaste-starters)
    - [11.1 `.github/copilot-instructions.md` skeleton](#111-githubcopilot-instructionsmd-skeleton)
    - [11.2 `.github/agents/<name>.agent.md` skeleton](#112-githubagentsnameagentmd-skeleton)
  - [12) Suggested specialist roster (useful for serious projects)](#12-suggested-specialist-roster-useful-for-serious-projects)
  - [References (official + high-signal)](#references-official--high-signal)

<!-- mdformat-toc end -->

# Best Practices for GitHub Copilot Custom Agents in VS Code<a name="best-practices-for-github-copilot-custom-agents-in-vs-code"></a>

*A practical, team-ready playbook for designing repeatable agent behavior (with
compatibility notes for GitHub Copilot Coding Agent).*

______________________________________________________________________

## 1) What “custom agents” are (and what they’re not)<a name="1-what-%E2%80%9Ccustom-agents%E2%80%9D-are-and-what-they%E2%80%99re-not"></a>

Custom agents are **operational profiles**: a constrained set of instructions +
tool access that makes Copilot behave consistently for a specific job. The goal
is not personality—it’s **predictable delivery**.

Design for three realities:

1. **VS Code agent mode (interactive, local)** You select an agent profile from
   the chat UI and run a workflow with explicit steps (often via handoffs).

1. **VS Code background/cloud agents (non-interactive or remote)** Some tasks
   may run with reduced context and different tool availability.

1. **GitHub Copilot Coding Agent (remote, CI-like)** Agent execution happens in
   a GitHub-hosted environment and behaves more like a PR-producing teammate
   than an IDE assistant.

**Key implication:** your instructions and agents must be useful even when some
UI-only conveniences (like certain properties) are ignored outside VS Code.

______________________________________________________________________

## 2) File architecture: the “layered contract” approach<a name="2-file-architecture-the-%E2%80%9Clayered-contract%E2%80%9D-approach"></a>

Use a layered instruction stack instead of one giant prompt. This prevents
conflicts and keeps instructions maintainable.

### 2.1 Recommended repo layout<a name="21-recommended-repo-layout"></a>

```
.github/
  copilot-instructions.md
  instructions/
    *.instructions.md
  agents/
    *.agent.md
.vscode/
  mcp.json
.github/workflows/
  copilot-setup-steps.yml   # for GitHub Copilot Coding Agent

```

### 2.2 Baseline contract: `.github/copilot-instructions.md`<a name="22-baseline-contract-githubcopilot-instructionsmd"></a>

Put **workspace-wide rules** here:

- exact build/test/lint/type-check commands
- architecture overview and module boundaries
- coding standards (type hints, error handling expectations)
- security invariants (no secrets in logs, safe defaults)
- Definition of Done (DoD)

VS Code will apply this file automatically to all chat requests when instruction
files are enabled, and the file is also recognized by GitHub Copilot
environments.

### 2.3 Scoped policies: `.github/instructions/*.instructions.md`<a name="23-scoped-policies-githubinstructionsinstructionsmd"></a>

Use multiple smaller instruction files and apply them selectively via `applyTo`
patterns (e.g., Python rules only for `**/*.py`, test rules only for
`**/tests/**/*.py`).

This is the best way to avoid conflicts and “instruction drift” across unrelated
parts of the repo.

### 2.4 Agent profiles: `.github/agents/*.agent.md`<a name="24-agent-profiles-githubagentsagentmd"></a>

Each agent profile is a Markdown file with YAML frontmatter that defines:

- `name`, `description`
- `tools` allowlist
- `target` (optional)
- `handoffs` (VS Code UX accelerator)
- `infer` (whether it can be used as a subagent)

Store each profile as “one job, one agent.”

### 2.5 Local boundaries: `AGENTS.md` (optional)<a name="25-local-boundaries-agentsmd-optional"></a>

If you want folder-level guardrails close to the code:

- place `AGENTS.md` near risk-heavy modules (security, transports, protocol
  code)
- keep it short and specific

______________________________________________________________________

## 3) Instruction precedence and conflict management<a name="3-instruction-precedence-and-conflict-management"></a>

### 3.1 Three tiers exist in practice<a name="31-three-tiers-exist-in-practice"></a>

Across environments, instructions can come from:

- **personal/user instructions** (highest priority)
- **repository instructions** (`.github/copilot-instructions.md`,
  `.instructions.md`)
- **organization instructions** (lowest priority)

Because your repository instructions may be combined with other tiers, the
safest strategy is:

- write repo instructions as if they must coexist with unknown higher-level
  rules
- avoid redundant or contradictory statements
- prefer “hard boundaries” over stylistic preferences

### 3.2 VS Code-specific behavior to plan for<a name="32-vs-code-specific-behavior-to-plan-for"></a>

VS Code can combine multiple instruction files; when multiple types exist, **no
strict order is guaranteed**, so keep instructions non-conflicting and additive.

______________________________________________________________________

## 4) The six essentials (quality checklist for every instruction file)<a name="4-the-six-essentials-quality-checklist-for-every-instruction-file"></a>

High-performing instruction sets reliably cover:

1. **Commands**: build/test/lint/format with exact flags
1. **Testing patterns**: framework, fixtures, naming conventions
1. **Project structure**: directory map with responsibilities
1. **Code style**: conventions + at least one “golden example”
1. **Git workflow**: branch naming, commit/PR conventions
1. **Boundaries**: what to never change / ask-first / always do

If a file doesn’t add clarity in at least one of these areas, it’s usually
noise.

______________________________________________________________________

## 5) Tool governance: least privilege by default<a name="5-tool-governance-least-privilege-by-default"></a>

### 5.1 Why tool restriction matters<a name="51-why-tool-restriction-matters"></a>

Over-permissive tool access is the fastest path to unintended edits, scope
creep, and brittle changes. Treat tools like permissions.

### 5.2 Recommended tool sets by agent type<a name="52-recommended-tool-sets-by-agent-type"></a>

- **Planning / Analysis**: `read`, `search`, `fetch`
- **Implementation**: `read`, `edit`, plus terminal/shell only if needed
- **Review / Audit**: `read`, `search`
- **Docs**: `read`, `edit`
- **CI/Release**: `read`, `edit` (scoped to workflows/build config)

### 5.3 “Boundaries” rubric you should standardize<a name="53-%E2%80%9Cboundaries%E2%80%9D-rubric-you-should-standardize"></a>

Use a three-tier rubric so humans and agents interpret it consistently:

- ✅ **Allowed** (safe, routine work)
- ⚠️ **Ask first** (risky or scope-expanding changes)
- 🚫 **Never** (secrets, production configs, vendor dirs, irreversible
  operations)

Make boundaries enforceable by aligning them with tool allowlists (e.g., no
`edit` for reviewers).

______________________________________________________________________

## 6) Multi-agent workflows: handoffs are your SDLC control plane (VS Code)<a name="6-multi-agent-workflows-handoffs-are-your-sdlc-control-plane-vs-code"></a>

VS Code supports `handoffs` to move between agents. Use this to operationalize
your SDLC:

### 6.1 Recommended handoff chain (TDD-friendly)<a name="61-recommended-handoff-chain-tdd-friendly"></a>

1. **Planner** → defines contracts + acceptance criteria
1. **Test Engineer** → writes failing tests (red)
1. **Implementer** → makes tests pass (green)
1. **Security/Compliance Reviewer** → blocks unsafe defaults
1. **Docs** → ships runnable examples aligned to CI

Treat handoffs as “workflow buttons,” not automation you can’t audit. The user
stays in control.

______________________________________________________________________

## 7) Prompt design: reduce ambiguity, increase determinism<a name="7-prompt-design-reduce-ambiguity-increase-determinism"></a>

Even with great instruction files, prompts still matter. The strongest pattern
is:

- **Persona**: which agent to use and why
- **Context**: what files/modules are relevant
- **Task**: what to do (and what not to do)
- **Format**: the deliverable shape (plan, patch, checklist, etc.)

In VS Code, keep prompts shorter by pushing stable context into instruction
files.

______________________________________________________________________

## 8) MCP servers in VS Code: configuration and safety<a name="8-mcp-servers-in-vs-code-configuration-and-safety"></a>

If you use MCP tools (either consuming or building MCP servers):

### 8.1 Configuration principles<a name="81-configuration-principles"></a>

- keep secrets out of versioned files
- prefer environment variables / secure input prompts
- document how to run MCP servers locally vs CI

### 8.2 Tool design principles (when you are the MCP server author)<a name="82-tool-design-principles-when-you-are-the-mcp-server-author"></a>

- keep tools narrowly scoped (“safe primitives”), not “do anything” endpoints
- validate inputs and return typed, predictable outputs
- design error semantics to be actionable without leaking secrets

______________________________________________________________________

## 9) GitHub Copilot Coding Agent compatibility (practical notes)<a name="9-github-copilot-coding-agent-compatibility-practical-notes"></a>

If you also use GitHub’s Coding Agent, align instructions to CI reality:

### 9.1 Deterministic setup<a name="91-deterministic-setup"></a>

Provide a `copilot-setup-steps.yml` workflow so the agent can consistently
bootstrap dependencies and run checks.

### 9.2 Avoid thrash in reviews<a name="92-avoid-thrash-in-reviews"></a>

Batch review comments so the agent can process changes in one coherent pass
rather than re-running on every single comment.

### 9.3 Don’t rely on VS Code-only conveniences<a name="93-don%E2%80%99t-rely-on-vs-code-only-conveniences"></a>

Some agent profile properties may be ignored by GitHub’s Coding Agent for
compatibility. Keep the core contract in repo instruction files and keep agent
profiles valuable even without handoffs.

______________________________________________________________________

## 10) Common failure modes (and how to avoid them)<a name="10-common-failure-modes-and-how-to-avoid-them"></a>

1. **One massive instruction file** → split into layered files and scoped rules
1. **Conflicting policies** → enforce single-source-of-truth per topic
1. **Vague commands** → write copy/paste runnable commands with flags
1. **No boundaries** → add ✅/⚠️/🚫 and align tools to them
1. **Too many powerful agents** → keep a small roster of specialists
1. **Tests depend on hardware** → isolate integration tests behind explicit
   flags/markers

Treat instruction/agent files like production code: review them, refactor them,
and version them.

______________________________________________________________________

## 11) Practical templates (copy/paste starters)<a name="11-practical-templates-copypaste-starters"></a>

### 11.1 `.github/copilot-instructions.md` skeleton<a name="111-githubcopilot-instructionsmd-skeleton"></a>

```md

# Project Overview

What this project does (one paragraph).

# Tech Stack

- Python X.Y
- Key libs: ...
- Tooling: ruff, mypy/pyright, pytest, build backend

# Commands (copy/paste)

- Install: `...`
- Test: `pytest -q`
- Lint: `ruff check .`
- Type-check: `mypy .`
- Build: `python -m build`

# Project Structure

- `src/...`: ...
- `tests/...`: ...

# Code Standards

- Type hints required for public APIs
- Error handling: raise typed exceptions; no silent failure
- Logging: redact secrets; no credentials in logs

# Definition of Done

- Tests added/updated
- CI green
- Docs updated (if user-facing)
- No secrets introduced

```

### 11.2 `.github/agents/<name>.agent.md` skeleton<a name="112-githubagentsnameagentmd-skeleton"></a>

```md

---
name: example-specialist
description: One-job agent profile with explicit tools and boundaries.
tools: ["read", "search"]
target: vscode
infer: false
handoffs:
  - label: Implement
    agent: example-implementer
    prompt: "Implement the approved plan with minimal diffs."
    send: false
---

# Operating mandate

State the single responsibility and expected deliverable.

## Boundaries

✅ Allowed: ...
⚠️ Ask first: ...
🚫 Never: ...

```

______________________________________________________________________

## 12) Suggested specialist roster (useful for serious projects)<a name="12-suggested-specialist-roster-useful-for-serious-projects"></a>

A small, effective portfolio usually includes:

- Planner/Spec
- TDD Test Engineer
- Implementer
- Security Reviewer
- CI/Release Engineer
- Docs/Examples

Add domain specialists only when you have domain complexity (protocols, infra,
security-sensitive transports).

______________________________________________________________________

## References (official + high-signal)<a name="references-official--high-signal"></a>

**VS Code**

- Custom agents (agent profiles, tools, handoffs):
  https://code.visualstudio.com/docs/copilot/customization/custom-agents
- Custom instructions (`copilot-instructions.md`, `*.instructions.md`, order
  notes):
  https://code.visualstudio.com/docs/copilot/customization/custom-instructions
- MCP servers in VS Code (configuration and secrets guidance):
  https://code.visualstudio.com/docs/copilot/chat/mcp-servers
- MCP developer guide (building tools/servers):
  https://code.visualstudio.com/docs/copilot/chat/mcp-developer-guide

**GitHub Copilot**

- Creating custom agents (repo + VS Code creation paths):
  https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents
- Custom agents configuration reference (tools allowlist, compatibility notes):
  https://docs.github.com/en/copilot/reference/custom-agents-configuration

**Community / ecosystem**

- GitHub Blog: “How to write a great agents.md” (commands early, examples,
  boundaries, six areas):
  https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/
