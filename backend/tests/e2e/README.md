# End-to-End Tests

End-to-end tests cover complete user workflows and verify the entire application
stack works together correctly. These tests simulate real user interactions from
start to finish.

## Purpose

E2E tests answer the question: **"Can users complete their tasks
successfully?"**

These tests verify complete workflows:

- User interaction flows
- Multiple system components working together
- Request/response cycles
- Error handling workflows
- Cross-cutting concerns (CORS, auth, etc.)

## When to Run

- **Before pull requests** - Ensures features work end-to-end
- **After feature changes** - Verifies workflows still work
- **Before releases** - Final verification
- **Periodically in CI** - Catches integration issues

## Writing E2E Tests

### Naming Convention

```python
# File: test_phase{N}_{workflow_area}.py
# Examples:
test_phase0_workflows.py
test_phase1_translation_workflows.py
test_phase2_history_workflows.py
```

### Test Structure

```python
"""End-to-end tests for [workflow area]."""

import unittest
import pytest
from tests.conftest import FixtureAttrs


class TestUserWorkflow{Feature}(FixtureAttrs, unittest.TestCase):
    """E2E tests for user [doing something]."""

    @pytest.mark.e2e
    def test_complete_{workflow}_workflow(self) -> None:
        """Test complete workflow: user [does what].

        Workflow:
        1. User [does step 1]
        2. Application [processes]
        3. User sees [result]
        4. User [does step 2]
        5. Workflow completes successfully
        """
        # Step 1: User action
        response = self.client.post("/api/v1/endpoint", json={...})

        # Step 2: Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Step 3: Verify workflow state
        self.assertEqual(data["status"], "complete")

        # Step 4-N: Continue workflow...
```

### Guidelines

✅ **DO:**

- Document workflow steps in docstring
- Test complete user journeys
- Verify all side effects
- Test both happy and error paths
- Use realistic data
- Mark with `@pytest.mark.e2e`
- Test cross-cutting concerns

❌ **DON'T:**

- Test implementation details
- Make real external API calls (mock them)
- Write tests that depend on each other
- Test only one component
- Repeat what unit tests cover

## Current Tests

### Phase 0 Workflows (11 tests)

**File:** `test_phase0_workflows.py`

- **Health Check Workflow** (1 test)

  - User checks application health
  - Verifies request → middleware → response cycle

- **Documentation Workflow** (1 test)

  - Developer explores API documentation
  - Swagger UI → ReDoc → OpenAPI schema

- **Error Handling Workflows** (2 tests)

  - User encounters 404 error
  - User uses wrong HTTP method

- **CORS Workflows** (2 tests)

  - Browser makes CORS preflight request
  - Frontend reads custom headers

- **Custom Error Workflows** (2 tests)

  - Custom exception raised and handled
  - Rate limit error with Retry-After header

- **Validation Workflow** (1 test)

  - User submits invalid data
  - Validation errors formatted correctly

- **Middleware Stack Integration** (2 tests)

  - Middleware executes in correct order
  - Complete request lifecycle through all layers

## Running E2E Tests

```bash
# All e2e tests
pytest tests/e2e/ -v -m e2e

# Specific test file
pytest tests/e2e/test_phase0_workflows.py -v

# Specific workflow
pytest tests/e2e/test_phase0_workflows.py::TestUserWorkflowHealthCheck -v
```

## Example Test

```python
@pytest.mark.e2e
def test_complete_translation_workflow(self) -> None:
    """Test complete workflow: user translates a web page.

    Workflow:
    1. User submits URL for translation
    2. Backend fetches and extracts content
    3. Backend streams translation back
    4. User sees progressive translation
    5. Translation completes successfully
    """
    # Step 1: User submits translation request
    response = self.client.post(
        "/api/v1/translate",
        json={
            "url": "https://example.com/article",
            "target_lang": "zh"
        }
    )

    # Step 2: Verify translation started
    self.assertEqual(response.status_code, 200)

    # Step 3: Verify response structure
    data = response.json()
    self.assertIn("blocks", data)
    self.assertGreater(len(data["blocks"]), 0)

    # Step 4: Verify each block translated
    for block in data["blocks"]:
        self.assertIn("translation", block)
        self.assertIn("status", block)
        self.assertEqual(block["status"], "complete")
```

## Future Test Areas

As you add Phase 1+ features, add e2e tests for:

### Phase 1

#### Translation Workflow

1. User enters URL
1. Content extracted
1. Translation streams back
1. User sees result

#### Error Recovery Workflow

1. Translation fails
1. User sees error message
1. User retries
1. Success

#### Block Synchronization Workflow

1. User hovers over source block
1. Translation block highlights
1. User clicks
1. Scroll synchronizes

### Phase 2

#### History Workflow

1. User translates page
1. Page saved to history
1. User accesses history
1. Can re-open translation

#### Re-translation Workflow

1. User selects block
1. User requests re-translation
1. New translation generated
1. User can compare versions

### Phase 3

#### Verification Workflow

1. User requests verification
1. Claims extracted
1. Verification checks run
1. Results displayed with evidence

#### Multi-model Workflow

1. User enables multi-model
1. Multiple models process content
1. Results compared
1. Best result selected

## Test Data

Use realistic data that represents actual usage:

```python
# Good: Realistic URL
url = "https://blog.example.com/2026/01/tech-article"

# Bad: Fake/test URL
url = "http://test.com"

# Good: Realistic content
content = "This is a comprehensive article about..."

# Bad: Minimal content
content = "test"
```

## Mocking External Services

E2E tests should mock external services to:

- Avoid network calls (faster tests)
- Ensure deterministic results
- Test error conditions
- Avoid rate limits

```python
from unittest.mock import patch

@patch('app.services.openai_client.translate')
def test_translation_workflow(self, mock_translate):
    mock_translate.return_value = {"translation": "..."}
    # Test proceeds with mocked response
```

## Performance Targets

- **Individual test:** \< 1 second
- **Full e2e suite:** \< 10 seconds
- **With setup/teardown:** \< 15 seconds

E2E tests can be slower than unit tests, but should still be reasonably fast.

## Success Criteria

A good e2e test suite:

- ✅ Tests complete user journeys
- ✅ Verifies integration between components
- ✅ Gives clear failure messages with workflow context
- ✅ Mocks external dependencies
- ✅ Can run in any order
- ✅ Covers both success and failure paths
- ✅ Represents realistic usage

______________________________________________________________________

**Related:** See [../smoke/README.md](../smoke/README.md) for smoke tests
