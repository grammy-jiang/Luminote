# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for Luminote, following
Step 1.3 of the
[github-issue-creation-methodology.md](../github-issue-creation-methodology.md).

## Purpose

ADRs document key architectural choices so GitHub Copilot and future developers
don't have to infer patterns. Each ADR captures the context, decision, and
consequences of important architectural choices.

## ADR Format

Each ADR follows this structure:

```markdown
# ADR-XXX: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
[Why this decision is needed, what problem it solves]

## Decision
[What we decided to do]

## Consequences
[Positive and negative outcomes of this decision]

## Alternatives Considered
[Other options we evaluated and why we didn't choose them]
```

## Index of ADRs

| ADR                                              | Title                                 | Status   | Date       |
| ------------------------------------------------ | ------------------------------------- | -------- | ---------- |
| [001](001-api-endpoint-structure.md)             | API Endpoint Structure and Versioning | Accepted | 2026-01-07 |
| [002](002-streaming-translation-architecture.md) | Streaming Translation Architecture    | Accepted | 2026-01-07 |
| [003](003-client-side-storage-strategy.md)       | Client-Side Storage Strategy          | Accepted | 2026-01-07 |
| [004](004-error-handling-patterns.md)            | Error Handling and Exception Patterns | Accepted | 2026-01-07 |
| [005](005-frontend-state-management.md)          | Frontend State Management Approach    | Accepted | 2026-01-07 |

## Creating New ADRs

When making a significant architectural decision:

1. Copy the template from an existing ADR
1. Number sequentially (next available number)
1. Use kebab-case for filename: `XXX-descriptive-title.md`
1. Fill in all sections
1. Update this README index
1. Commit with descriptive message

## References

- [GitHub Issue Creation Methodology](../github-issue-creation-methodology.md)
- [Feature Specifications](../feature-specifications.md)
- [Infrastructure Requirements](../infrastructure-requirements.md)
