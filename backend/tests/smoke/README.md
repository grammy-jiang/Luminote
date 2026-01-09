# Smoke Tests

Smoke tests verify that basic functionality works without issues. These tests
ensure the application can start and basic endpoints respond correctly.

## Purpose

Smoke tests answer the question: **"Can the application start and handle basic
requests?"**

These are fast, focused tests that catch critical failures early:

- Application initialization
- Middleware activation
- Basic endpoint availability
- Error handling basics
- Configuration correctness

## When to Run

- **Before every commit** - Catches breaking changes early
- **After infrastructure changes** - Verifies setup is correct
- **In CI/CD pipelines** - First gate for all PRs
- **During development** - Quick feedback loop

## Writing Smoke Tests

### Naming Convention

```python
# File: test_phase{N}_{feature_area}.py
# Examples:
test_phase0_infrastructure.py
test_phase1_translation.py
test_phase2_history.py
```

### Test Structure

```python
"""Smoke tests for [feature area]."""

import unittest
import pytest
from tests.conftest import FixtureAttrs


class Test{FeatureArea}(FixtureAttrs, unittest.TestCase):
    """Smoke tests for {feature area}."""

    @pytest.mark.smoke
    def test_{what}_works(self) -> None:
        """Test that {what} works without errors."""
        # Arrange
        # Act
        # Assert - basic functionality works
```

### Guidelines

✅ **DO:**

- Test one thing per test method
- Use descriptive test names
- Keep tests fast (\< 0.1s per test)
- Test happy path only
- Verify basic responses (status codes, key fields)
- Mark with `@pytest.mark.smoke`

❌ **DON'T:**

- Test error cases (that's for e2e/unit tests)
- Test edge cases
- Make external API calls
- Test business logic details
- Write slow tests

## Current Tests

### Phase 0 Infrastructure (13 tests)

**File:** `test_phase0_infrastructure.py`

- **Application Startup** (5 tests)

  - Application creates successfully
  - Health endpoint responds
  - OpenAPI schema available
  - Documentation UIs accessible

- **Middleware** (3 tests)

  - Request ID middleware active
  - Timing middleware active
  - CORS headers present

- **Error Handling** (3 tests)

  - 404 handled
  - 405 handled
  - Error responses include request ID

- **Configuration** (2 tests)

  - API version prefix configured
  - Application metadata correct

## Running Smoke Tests

```bash
# All smoke tests
pytest tests/smoke/ -v -m smoke

# Specific test file
pytest tests/smoke/test_phase0_infrastructure.py -v

# Watch mode (requires pytest-watch)
ptw tests/smoke/ -- -m smoke
```

## Example Test

```python
@pytest.mark.smoke
def test_health_endpoint_responds(self) -> None:
    """Test that health check endpoint responds successfully."""
    response = self.client.get("/health")

    # Verify basic response
    self.assertEqual(response.status_code, 200)

    # Verify essential fields exist
    data = response.json()
    self.assertIn("status", data)
    self.assertEqual(data["status"], "ok")
```

## Future Test Areas

As you add Phase 1+ features, add smoke tests for:

### Phase 1

- **Content Extraction** - URL fetch and parse works
- **Translation Service** - Basic translation request succeeds
- **Streaming** - SSE endpoint opens and sends events

### Phase 2

- **History** - Can save and retrieve items
- **Re-translation** - Can re-translate blocks
- **Paste Mode** - Can translate pasted text

### Phase 3

- **AI Insights** - Can generate explanations
- **Verification** - Can check claims
- **Highlights** - Can save highlights

## Performance Targets

- **Individual test:** \< 0.1 seconds
- **Full smoke suite:** \< 2 seconds
- **With collection:** \< 3 seconds

If a test takes longer, consider:

- Is it doing too much? Split it.
- Is it an integration test? Move to e2e.
- Can mocking make it faster?

## Success Criteria

A good smoke test suite:

- ✅ Runs in seconds, not minutes
- ✅ Catches critical failures early
- ✅ Gives clear failure messages
- ✅ Requires no setup/teardown
- ✅ Can run in any order
- ✅ Tests actual application behavior (not mocks)

______________________________________________________________________

**Related:** See [../e2e/README.md](../e2e/README.md) for end-to-end tests
