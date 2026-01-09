# Operational Metrics for Copilot Agent PRs

> This document defines how to track and measure GitHub Copilot agent
> performance in the Luminote repository, enabling data-driven improvements to
> agent workflows, instructions, and task design.

______________________________________________________________________

## Overview

GitHub Copilot coding agents are powerful but require **continuous evaluation**
to ensure they remain productive and maintain code quality. This document
defines:

- **Key metrics** to track
- **Collection methods** (automated and manual)
- **Review cadence** (when to analyze results)
- **Actions** to take based on findings

**Goal:** Make agent usage predictable, safe, and aligned with Luminote's
development standards.

______________________________________________________________________

## 1. Core Metrics

### 1.1 PR Volume and Merge Rate

**What to measure:**

| Metric           | Definition                          | Target      |
| ---------------- | ----------------------------------- | ----------- |
| **Agent PRs/mo** | PRs created by agents               | Track trend |
| **Merge rate**   | % agent PRs merged w/o revisions    | ≥75%        |
| **Avg review**   | Days from PR open to merge          | \<2 days    |
| **Revisions**    | Avg "request changes" → new commits | ≤1 per PR   |

**Collection method:**

- Use GitHub Actions to query PRs with label `agent-generated` via GitHub REST
  API
- Calculate: `merged_prs / total_agent_prs`
- Log every Monday in a spreadsheet or GitHub Discussion

**Example query** (GitHub REST API):

```bash
curl -s "https://api.github.com/repos/grammy-jiang/Luminote/pulls\
?state=closed&labels=agent-generated" \
  | jq '[.[] | {number, merged_at, created_at, review_comments}]'
```

______________________________________________________________________

### 1.2 Code Quality Metrics

**What to measure:**

| Metric               | Definition                             | Target      |
| -------------------- | -------------------------------------- | ----------- |
| **Test coverage**    | % of new code covered by tests         | ≥95% (core) |
| **CI pass rate**     | % of PRs that pass CI on first attempt | ≥90%        |
| **Lint/type errors** | # of errors caught in review (not CI)  | 0           |
| **Failed tests**     | # of tests that fail after merge       | 0           |

**Collection method:**

- Extract from CI logs (GitHub Actions: `.github/workflows/backend.yml`,
  `.github/workflows/frontend.yml`)
- Parse test output: `grep "coverage:" backend/pytest-output.txt`
- Log CI status: green ✅ vs red ❌ for each agent PR

**Tracking template** (spreadsheet row):

```text
PR #123 | Task: "Add extract endpoint" | Coverage: 89% |
CI: ✅ | Lint: 0 errors | Tests: ✅
```

______________________________________________________________________

### 1.3 Issue Resolution Metrics

**What to measure:**

| Metric                 | Definition                            | Target |
| ---------------------- | ------------------------------------- | ------ |
| **Issue closure rate** | % of issues that result in PR → merge | ≥80%   |
| **Acceptance met**     | % of PRs addressing all criteria      | ≥90%   |
| **Scope creep**        | # of PRs that modify unrelated files  | ≤5%    |
| **Rework rate**        | % of agent PRs requiring follow-up    | ≤10%   |

**Collection method:**

- Review each agent PR against its source issue
- Checklist: "Does this PR solve the original problem completely?"
- Log pass/fail in GitHub Project board or spreadsheet
- Track follow-up issues opened with label `agent-followup`

**Example**:

```text
Issue #42: "Add translation API endpoint"
├─ PR #99: ✅ Acceptance criteria met (all 5 checkboxes)
├─ PR #99: ❌ Minor: Added validation logic not requested
├─ PR #99: ✅ Merged after 1 review round
└─ Result: ISSUE CLOSED (no rework needed)
```

______________________________________________________________________

### 1.4 Development Velocity Metrics

**What to measure:**

| Metric            | Definition                      | Target      |
| ----------------- | ------------------------------- | ----------- |
| **Time to PR**    | Hours from assign to PR open    | \<4 hours   |
| **Time to merge** | Hours from PR open to merge     | \<24 hours  |
| **Cost/PR**       | GH Actions minutes per agent PR | Track trend |
| **Throughput**    | Features completed/sprint       | Increases   |

**Collection method:**

- GitHub Actions logs: `run_duration` from workflow summary
- Spreadsheet: track assignment → PR → merge timestamps
- GitHub API: query PR `created_at`, `merged_at` timestamps

**Example**:

```bash
# Extract from GitHub Actions logs
grep "Job completed in" .github/workflows/logs.txt

# Or query via API
curl "https://api.github.com/repos/grammy-jiang/Luminote/pulls/99" \
  | jq '{created_at, merged_at, review_comments}'
```

______________________________________________________________________

## 2. Quality Checkpoints

### 2.1 Weekly Review (Every Monday)

**Cadence:** Check on every agent PR merged in the past 7 days

**Checklist:**

- [ ] Merge rate ≥75%?
- [ ] CI pass rate ≥90%?
- [ ] No 0 lint errors in agent PRs?
- [ ] Acceptance criteria met in ≥90% of PRs?
- [ ] No unexpected regressions in main branch tests?

**Action if criteria not met:**

1. Identify the failing PR(s)
1. Root cause: instruction issue? task design issue? environment issue?
1. Log findings in `#agent-feedback` channel (or GitHub Discussion)
1. Decide: update instructions, tighten task scoping, or investigate CI

**Example Log Entry:**

```markdown
## Weekly Review — 2026-01-13

✅ Merge rate: 76% (16/21 PRs merged)
✅ CI pass rate: 95%
⚠️ Lint errors: 1 agent PR had unused import (caught in review, not CI)
✅ Acceptance criteria: 94% met
🔴 Regression: Backend test `test_extract_html` failed post-merge (Issue #150)

**Action:** Investigate why agent didn't catch regression in test suite.
```

______________________________________________________________________

### 2.2 Monthly Review (First Monday of Month)

**Cadence:** Comprehensive analysis of all agent activity

**Metrics to extract:**

1. **Merge rate trend** (last 3 months)
1. **Code quality trend** (test coverage, lint errors)
1. **Issue resolution rate** (% of agent tasks completed)
1. **Velocity trend** (PRs per week)
1. **Developer feedback** (from code review comments)

**Template:**

```markdown
## Monthly Agent Performance Review — January 2026

### Summary
- Total agent PRs: 21
- Merged: 16 (76%)
- Rejected: 2 (did not meet criteria)
- Pending review: 3

### Quality Metrics
- Avg test coverage: 87% (target: ≥85%) ✅
- CI pass rate: 94% (target: ≥90%) ✅
- Rework rate: 5% (target: ≤10%) ✅
- Scope creep: 4% (target: ≤5%) ✅

### Top Agent Issues Completed
1. #12 - Translation API endpoint ✅
2. #23 - Error handling standardization ✅
3. #31 - Test coverage for core/ modules ✅

### Blockers / Improvements Needed
- Task #45: Agent struggled with complex requirement scoping
  - **Root cause:** Issue description was ambiguous
  - **Fix:** Better use of acceptance criteria templates

- PR #89: Lint errors missed in agent PR
  - **Root cause:** CI pre-flight incomplete
  - **Fix:** Verify copilot-setup-steps.yml runs all checks

### Recommendations for Next Sprint
1. Refine issue templates to reduce ambiguity (3 examples to improve)
2. Add lint check to copilot-setup-steps.yml pre-flight
3. Experiment with test-specialist agent on 5 test-focused issues
```

______________________________________________________________________

### 2.3 Quarterly Review (Every 3 Months)

**Cadence:** Strategic assessment

**Questions to answer:**

1. **Is agent usage aligned with Luminote's goals?**

   - Are agents handling the right types of tasks?
   - Could we use agents for additional tasks?

1. **What has improved? What needs fixing?**

   - Compare Q1 merge rate to Q2, Q3, Q4
   - Track instruction evolution (what changed in AGENTS.md,
     copilot-instructions.md?)
   - Are security/compliance standards being maintained?

1. **Is there developer consensus?**

   - Survey: "How would you rate agent PRs on quality/clarity?"
   - "What % of agent PRs require meaningful rework?"
   - "Should we expand agent usage?"

1. **Financial & resource impact:**

   - GitHub Actions minutes used by agents per month
   - Estimated developer hours saved (PRs completed by agents vs. manual)
   - Cost-benefit: "Is this worth continuing?"

**Deliverable:** Quarterly report with recommendations

______________________________________________________________________

## 3. Sampling & Code Review

### 3.1 Systematic Code Review Sampling

**Goal:** Catch patterns of issues that CI doesn't catch

**Frequency:** Sample 3–5 agent PRs per week (randomly selected)

**Checklist for each PR:**

```markdown
### Code Review Sample: PR #XYZ

- [ ] Architecture patterns followed (layered structure respected)
- [ ] Comments are clear and helpful (not obvious, not missing)
- [ ] Error handling matches ADR-004 pattern
- [ ] Logging doesn't expose secrets
- [ ] No hardcoded values or credentials
- [ ] Edge cases considered (empty inputs, nulls, timeouts)
- [ ] Naming is descriptive (functions, variables, classes)
- [ ] Performance concerns? (N+1 queries, unnecessary loops, etc.)

**Verdict:** ✅ Good / ⚠️ Minor issues / 🔴 Significant concerns
```

### 3.2 Metrics from Code Review Sampling

Track patterns across sampled PRs:

```text
Week of 2026-01-13: 5 PRs sampled
- Architecture issues: 0
- Error handling issues: 1 (PR #105: missing validation)
- Naming issues: 2 (PRs #101, #103)
- Security issues: 0
- Performance issues: 0

Pattern: Agent needs reminder about input validation
(possibly instruction update?)
```

______________________________________________________________________

## 4. Automated Tracking (GitHub Actions)

### 4.1 Collect Agent PR Metrics Automatically

**Workflow:** `.github/workflows/agent-metrics.yml` (to be created)

```yaml
name: Collect Agent PR Metrics
on:
  pull_request:
    types: [closed]

jobs:
  log-metrics:
    if: contains(github.event.pull_request.labels.*.name, 'agent-generated')
    runs-on: ubuntu-latest
    steps:
      - name: Log Agent PR Metrics
        run: |
          PR_NUMBER=${{ github.event.pull_request.number }}
          PR_TITLE="${{ github.event.pull_request.title }}"
          MERGED=${{ github.event.pull_request.merged }}
          REVIEW_COMMENTS=${{ github.event.pull_request.review_comments }}

          echo "Agent PR #$PR_NUMBER: $PR_TITLE"
          echo "Merged: $MERGED"
          echo "Review comments: $REVIEW_COMMENTS"
          # Log to GitHub Discussions or append to metrics file
```

**Manual Alternative:** Weekly spreadsheet entry (faster to implement)

______________________________________________________________________

## 5. Reporting & Dashboard

### 5.1 Where to Store Data

**Option A (Simple):** GitHub Discussions

- Create discussion: "📊 Agent Metrics"
- Monthly comment with table of metrics

**Option B (Advanced):** GitHub Project Board

- Columns: Week, Merge Rate, CI Pass Rate, Avg Review Time, Notes
- Updated manually or via GitHub Actions

**Option C (Most Advanced):** External Dashboard

- Export metrics to CSV
- Use Looker, Grafana, or Google Sheets for visualization
- Share read-only link with team

### 5.2 Sample Dashboard View

```text
Luminote Agent Performance Dashboard
====================================

Last 30 Days:
- Total PRs: 21
- Merge rate: 76% 📈 (was 70% in Dec)
- CI pass rate: 94% ✅
- Avg review time: 1.2 days ⏱️
- Coverage avg: 87% (target 85%) ✅

Recent Trends:
[Line graph: merge rate over 12 months]
[Bar graph: coverage by module]
[Table: top blockers / improvements]
```

______________________________________________________________________

## 6. Action Plan Based on Metrics

### 6.1 If Merge Rate Drops Below 70%

**Possible causes:**

- Instructions are stale or conflicting
- Task descriptions are ambiguous
- Agent hit a new edge case in codebase

**Action:**

1. Sample 5 rejected PRs
1. Identify common reason (code quality? scope? architecture?)
1. Update relevant instruction file
1. Re-run test on new issues
1. Document lesson learned

**Example:**

```text
2026-01-15: Merge rate dropped to 60%.
Root cause: Agent missing context about new async/await pattern.
Fix: Added example to backend-api.instructions.md.
Result: Next 5 PRs merged. Merge rate recovered to 80%.
```

______________________________________________________________________

### 6.2 If Coverage Falls Below 85%

**Possible causes:**

- Task doesn't emphasize test coverage
- Test-specialist agent not assigned
- Edge cases aren't in acceptance criteria

**Action:**

1. Review last 3 PRs with low coverage
1. Identify which areas lacked tests
1. Update issue template to explicitly call out "coverage minimum"
1. For future: assign test-specialist agent on coverage-critical tasks

______________________________________________________________________

### 6.3 If Rework Rate Exceeds 10%

**Possible causes:**

- Issue acceptance criteria unclear
- Agent not following established patterns
- Task too complex for current instruction set

**Action:**

1. Sample the rework PRs
1. Identify: Was it architectural? stylistic? missing requirements?
1. Create a follow-up session with clarified requirements
1. Document pattern to avoid in future issues

______________________________________________________________________

## 7. Tools & Scripts

### 7.1 Query Agent PRs from GitHub API

```bash
#!/bin/bash
# scripts/agent-metrics.sh — Extract metrics for agent PRs

REPO="grammy-jiang/Luminote"
LABEL="agent-generated"

# Get all closed agent PRs from last 30 days
curl -s "https://api.github.com/repos/$REPO/pulls\
?state=closed&labels=$LABEL&per_page=100" \
  | jq '.[] | select(.merged_at > now - 2592000) | {
      number,
      title,
      merged: .merged_at != null,
      review_comments,
      created_at,
      merged_at
    }' > agent-prs-30days.json

# Calculate stats
jq -s 'length' agent-prs-30days.json  # Total PRs
jq -s '[.[] | select(.merged == true)] | length' agent-prs-30days.json  # Merged
```

### 7.2 Track Metrics in Spreadsheet

Use Google Sheets or Excel with this template:

```text
Date       | PR # | Title                | Status   | Coverage
2026-01-08 | 99   | Add extract endpoint | ✅ Merged| 91%
2026-01-09 | 101  | Refactor error layer | ⏳ Review| 88%
```

______________________________________________________________________

## 8. Review Schedule

| Cadence               | Owner            | Deliverable         |
| --------------------- | ---------------- | ------------------- |
| **Weekly** (Monday)   | Tech Lead        | Quick metrics check |
| **Monthly** (1st Mon) | Tech Lead        | Detailed report     |
| **Quarterly**         | Tech Lead + Team | Strategic review    |
| **Ad-hoc**            | Tech Lead        | Root cause analysis |

______________________________________________________________________

## 9. Feedback Loop

### 9.1 Continuous Improvement Cycle

```text
Metrics Collected
     ↓
Weekly Review (quality check)
     ↓
Issues Found? → Root Cause Analysis
     ↓
Update Instructions / Task Design
     ↓
Monitor Next Set of PRs
     ↓
Monthly Review (trends)
     ↓
Quarterly Strategy Review (scale decision)
```

### 9.2 When to Escalate

**Flag for team discussion if:**

- Merge rate drops >20% week-over-week
- CI pass rate falls below 85%
- 2+ security/compliance issues found in sampled PRs
- Rework rate exceeds 15%
- Developer feedback is consistently negative

**Example Escalation:**

```text
🚨 Alert: Agent CI pass rate dropped to 78% (from 94%)
Root cause: Pre-commit hooks not running in
copilot-setup-steps.yml
Action: Emergency fix to workflow + manual re-run of
recent failing PRs
Status: Resolved; monitoring next 10 agent PRs
```

______________________________________________________________________

## 10. Success Criteria

**Luminote's agent program is successful if:**

✅ Merge rate ≥75% (agent PRs are production-ready on first attempt) ✅ CI pass
rate ≥90% (quality gates are working) ✅ Test coverage ≥85% baseline, ≥95% for
core modules ✅ Review time \<2 days (PRs don't languish) ✅ Rework rate ≤10%
(instructions are clear and complete) ✅ Zero security/compliance issues in agent
PRs ✅ Developer satisfaction ≥8/10 (team endorses agent usage)

______________________________________________________________________

## Appendix: Example Monthly Report

```markdown
# Agent Performance Report — January 2026

## Executive Summary
Agent productivity trending positive. 76% merge rate, 94% CI pass rate.
Recommend continuing current program with minor instruction updates.

## Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Agent PRs | 21 | — | ✅ |
| Merge rate | 76% | ≥75% | ✅ |
| CI pass rate | 94% | ≥90% | ✅ |
| Test coverage | 87% | ≥85% | ✅ |
| Rework rate | 5% | ≤10% | ✅ |

## Top Tasks Completed
1. PR #99: Translation API endpoint (Issue #12)
2. PR #105: Error handling standardization (Issue #23)
3. PR #112: Core module tests (Issue #31)

## Issues & Resolutions
- **Issue:** One PR (PR #101) had unused imports
  - **Root cause:** Lint check incomplete in pre-flight
  - **Fix:** Updated copilot-setup-steps.yml

## Recommendations
1. Continue current agent usage
2. Try test-specialist agent on 5 test-only issues next month
3. Refine 2 issue templates (examples: #15, #28)

## Next Review
February 3, 2026
```

______________________________________________________________________

**Last Updated:** January 9, 2026 **Owner:** Tech Lead / DevOps **Related:**
[copilot-instructions.md](../copilot-instructions.md),
[AGENTS.md](../../AGENTS.md)
