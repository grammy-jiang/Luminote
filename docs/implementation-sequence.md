# Implementation Sequence (Step 2.3)

This document defines the implementation order for Luminote's Phase 1 features
following Step 2.3 of the
[github-issue-creation-methodology.md](github-issue-creation-methodology.md).

## Overview

**Total Phase 1 Effort:** ~14 hours (32 atomic features) **Timeline:** 8 weeks
**Batching Strategy:** Dependency-based, not feature-based **Team Capacity:**
Optimized for single developer or Copilot assignment

______________________________________________________________________

## Phase 0: Infrastructure Setup (Week 1)

**Status:** Not detailed here - see
[infrastructure-requirements.md](infrastructure-requirements.md)

### Critical Prerequisites

All Phase 1 work blocked until:

- [ ] Backend project initialized (FastAPI, project structure)
- [ ] Frontend project initialized (SvelteKit, build tools)
- [ ] Development environment (Docker, pre-commit hooks)
- [ ] CI/CD pipeline basic setup
- [ ] Testing frameworks configured (Pytest, Vitest)

**Estimated Time:** 4-6 hours (Phase 0 infrastructure issues) **Blocking:** All
Phase 1 work

______________________________________________________________________

## Phase 1 Implementation Batches

### Batch 1.1: Backend Core Foundation (Week 2-3)

**Issues:** 1.1, 1.2, 1.3, 1.4 **Estimated Time:** 2.5 hours **Rationale:** All
frontend features depend on these backend services

#### Issue 1.1: Create Translation API Endpoint

- **Type:** Backend Feature
- **Depends On:** Phase 0 infrastructure
- **Blocks:** 1.2, 1.11, 1.10, Feature 4 error handling
- **Time:** 30 min
- **Layer:** Backend + Testing + Documentation
- **Files:** `backend/app/api/v1/endpoints/translate.py`

**Acceptance Criteria:**

- ✅ POST `/api/v1/translate` endpoint exists
- ✅ Accepts JSON: `{content_blocks, target_language, provider, model, api_key}`
- ✅ Returns translated blocks with IDs
- ✅ Validates input (400), handles errors (4xx/5xx)
- ✅ Request ID in responses
- ✅ Pytest unit tests included

**Testing:** Unit tests with mocked providers, error case coverage
**Documentation:** Endpoint docs, request/response schema

______________________________________________________________________

#### Issue 1.2: Implement Translation Service

- **Type:** Backend Feature
- **Depends On:** Phase 0, Issue 1.1
- **Blocks:** 1.10, 1.11, translation workflow
- **Time:** 45 min
- **Layer:** Backend + Testing
- **Files:** `backend/app/services/translation_service.py`,
  `backend/app/services/providers/`

**Acceptance Criteria:**

- ✅ `TranslationService` class with abstract provider interface
- ✅ Supports OpenAI, Anthropic (extensible)
- ✅ Translates single block, multiple blocks
- ✅ Token usage tracking
- ✅ Provider-specific error handling
- ✅ No API key exposure in errors
- ✅ Unit tests with mocked providers

**Testing:** Test each provider abstraction, error cases **Documentation:**
Service architecture notes

______________________________________________________________________

#### Issue 1.3: Implement Content Extraction Service

- **Type:** Backend Feature
- **Depends On:** Phase 0 infrastructure
- **Blocks:** 1.4, 2.2-2.5, Feature 2 extraction workflow
- **Time:** 45 min
- **Layer:** Backend + Testing
- **Files:** `backend/app/services/extraction_service.py`

**Acceptance Criteria:**

- ✅ `ExtractionService.extract(url: str) -> ExtractedContent`
- ✅ Uses Mozilla Readability library
- ✅ Returns title, author, date, content blocks
- ✅ Block types: paragraph, heading, list, code, image, blockquote
- ✅ Network error handling, timeout (30s)
- ✅ Mock URL tests, integration tests
- ✅ Unit tests for content parsing

**Testing:** Mock HTTP responses, real URL tests, error cases **Documentation:**
Supported content types, limitations

______________________________________________________________________

#### Issue 1.4: Add Content Extraction Endpoint

- **Type:** Backend Feature
- **Depends On:** Issue 1.3
- **Blocks:** Frontend extraction workflow, 2.5 caching
- **Time:** 20 min
- **Layer:** Backend + Testing + Documentation
- **Files:** `backend/app/api/v1/endpoints/extract.py`

**Acceptance Criteria:**

- ✅ POST `/api/v1/extract` accepts `{url: string}`
- ✅ Returns `ExtractedContent` with blocks
- ✅ Validates URL format (400)
- ✅ Handles unreachable host (502)
- ✅ Handles extraction failure (422)
- ✅ Includes metadata (title, author, date)
- ✅ Tests for each error case

**Testing:** Unit tests for URL validation, error handling **Documentation:**
Endpoint docs, error codes

______________________________________________________________________

### Batch 1.2: Backend Configuration (Week 3)

**Issues:** 3.1, 4.1 **Estimated Time:** 1.25 hours **Rationale:** Configuration
validation needed for settings UI, error format needed for all error handling

#### Issue 3.1: Create Configuration Validation Endpoint

- **Type:** Backend Feature
- **Depends On:** Issues 1.1, 1.2, Phase 0
- **Blocks:** Frontend config UI (3.3-3.4), all translations
- **Time:** 30 min
- **Layer:** Backend + Testing + Documentation
- **Files:** `backend/app/api/v1/endpoints/config.py`

**Acceptance Criteria:**

- ✅ POST `/api/v1/config/validate` accepts `{provider, model, api_key}`
- ✅ Validates key format before API call
- ✅ Makes test API call to provider
- ✅ Returns success/error with clear message
- ✅ Never exposes API key in errors
- ✅ Timeout protection (10 seconds)
- ✅ Unit and integration tests

**Testing:** Mock providers, error cases, real provider testing
**Documentation:** Configuration format reference

______________________________________________________________________

#### Issue 4.1: Standardize Error Response Format

- **Type:** Backend Feature
- **Depends On:** Phase 0, existing errors
- **Blocks:** All error handling, Frontend error UI
- **Time:** 20 min
- **Layer:** Backend + Testing + Documentation
- **Files:** `backend/app/exceptions.py`, middleware updates

**Acceptance Criteria:**

- ✅ All errors follow standard format: `{error, code, details, request_id}`
- ✅ HTTP status codes match error types
- ✅ Request IDs included in all responses
- ✅ No sensitive data in error messages
- ✅ User-friendly error messages
- ✅ Documented error codes reference
- ✅ Tests for error formatting

**Testing:** Test error format for all endpoints **Documentation:** Error codes
reference table, developer guide

______________________________________________________________________

### Batch 1.3: Backend Error Handling (Week 4)

**Issues:** 4.2, 4.3, 2.2-2.5 **Estimated Time:** 2.5 hours **Rationale:**
Robust error handling before feature expansion, content type support increases
extraction service value

#### Issue 4.2: Handle URL Fetch Errors

- **Type:** Backend Feature (Enhancement)
- **Depends On:** Issues 1.3, 1.4, 4.1
- **Blocks:** Production readiness
- **Time:** 25 min
- **Layer:** Backend + Testing
- **Files:** `backend/app/services/extraction_service.py`

**Acceptance Criteria:**

- ✅ Invalid URL format → 400
- ✅ Host unreachable → 502
- ✅ Request timeout → 504
- ✅ Access denied → 403
- ✅ Server error → 500
- ✅ Clear error messages for users
- ✅ Logged for debugging
- ✅ Unit tests for each case

**Testing:** Mock each error condition, integration tests **Documentation:**
Error messages guide

______________________________________________________________________

#### Issue 4.3: Handle API Key Errors

- **Type:** Backend Feature (Enhancement)
- **Depends On:** Issues 1.1, 1.2, 4.1
- **Blocks:** Production readiness
- **Time:** 20 min
- **Layer:** Backend + Testing
- **Files:** `backend/app/services/providers/`

**Acceptance Criteria:**

- ✅ Invalid key format → 400
- ✅ Unauthorized key → 401
- ✅ Quota exceeded → 429/402
- ✅ Rate limited → 429 (with retry info)
- ✅ Provider specific errors mapped
- ✅ Actionable recovery steps
- ✅ Unit tests with mocked providers

**Testing:** Mock each provider's error responses **Documentation:** Rate limit
handling guide

______________________________________________________________________

#### Issue 2.2: Add News Article Content Support

- **Type:** Backend Feature (Enhancement)
- **Depends On:** Issue 1.3
- **Blocks:** Content type expansion
- **Time:** 30 min
- **Layer:** Backend + Testing + Documentation
- **Files:** `backend/app/services/extraction_service.py`

**Acceptance Criteria:**

- ✅ Detects and extracts headlines
- ✅ Extracts byline and author
- ✅ Preserves publication date
- ✅ Extracts pull quotes
- ✅ Handles image captions
- ✅ Unit tests with 3 real articles
- ✅ Integration tests with news sites

**Testing:** Real article examples, content extraction tests **Documentation:**
News content type guide

______________________________________________________________________

#### Issue 2.3: Add Blog Post Content Support

- **Type:** Backend Feature (Enhancement)
- **Depends On:** Issue 1.3
- **Blocks:** Content type expansion
- **Time:** 25 min
- **Layer:** Backend + Testing + Documentation
- **Files:** `backend/app/services/extraction_service.py`

**Acceptance Criteria:**

- ✅ Extracts title and author
- ✅ Gets publication date
- ✅ Filters comments section
- ✅ Handles sidebar content gracefully
- ✅ Unit tests with 3 blog posts
- ✅ Integration tests with popular blogs

**Testing:** Real blog examples, content extraction tests **Documentation:**
Blog content type guide

______________________________________________________________________

#### Issue 2.4: Add Technical Documentation Support

- **Type:** Backend Feature (Enhancement)
- **Depends On:** Issue 1.3
- **Blocks:** Content type expansion
- **Time:** 30 min
- **Layer:** Backend + Testing + Documentation
- **Files:** `backend/app/services/extraction_service.py`

**Acceptance Criteria:**

- ✅ Preserves heading hierarchy
- ✅ Preserves code blocks with formatting
- ✅ Identifies and marks examples
- ✅ Preserves reference links
- ✅ Removes line numbers from code
- ✅ Unit tests with technical docs
- ✅ Integration tests with doc sites

**Testing:** Real documentation examples **Documentation:** Technical doc type
guide

______________________________________________________________________

#### Issue 2.5: Implement Content Caching (24h TTL)

- **Type:** Backend Feature (Enhancement)
- **Depends On:** Issue 1.4
- **Blocks:** Performance optimization
- **Time:** 30 min
- **Layer:** Backend + Testing
- **Files:** `backend/app/services/caching_service.py`

**Acceptance Criteria:**

- ✅ Caches extracted content for 24 hours
- ✅ Uses URL as cache key
- ✅ Compresses cached content
- ✅ Automatic cleanup of expired entries
- ✅ Storage quota checked
- ✅ Cache hit vs miss logged
- ✅ Unit tests for cache logic
- ✅ Performance improvement tests

**Testing:** Cache logic tests, TTL expiry tests **Documentation:** Caching
strategy notes

______________________________________________________________________

### Batch 1.4: Streaming Translation Backend (Week 4)

**Issues:** 1.10 **Estimated Time:** 40 min **Rationale:** Enables progressive
rendering on frontend, critical for UX

#### Issue 1.10: Create Streaming Translation Endpoint

- **Type:** Backend Feature
- **Depends On:** Issues 1.1, 1.2, Phase 0
- **Blocks:** Frontend 1.11 progressive rendering
- **Time:** 40 min
- **Layer:** Backend + Testing + Documentation
- **Files:** `backend/app/api/v1/endpoints/translate.py`

**Acceptance Criteria:**

- ✅ POST `/api/v1/translate/stream` returns Server-Sent Events
- ✅ Sends block translations as they complete
- ✅ Proper SSE format: `data: {...}`
- ✅ Final event: completion marker
- ✅ Error event on failure
- ✅ Headers prevent proxy buffering
- ✅ Handles connection interruption gracefully
- ✅ Unit tests with mocked provider
- ✅ Integration tests with real streaming

**Testing:** SSE parsing tests, streaming error tests **Documentation:**
Streaming API docs, client example

______________________________________________________________________

### Batch 2.1: Frontend Foundation (Week 5)

**Issues:** 1.5, 1.6, 1.7, 3.2, 3.3 **Estimated Time:** 2.5 hours **Rationale:**
Build layout foundation first, then enhance

#### Issue 1.5: Create Dual-Pane Layout Component

- **Type:** Frontend Component
- **Depends On:** Phase 0 infrastructure
- **Blocks:** All pane display, resizing, interaction features
- **Time:** 30 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/DualPaneLayout.svelte`

**Acceptance Criteria:**

- ✅ Two-column layout (50/50 split by default)
- ✅ Left and right pane slots
- ✅ Responsive: stacks on mobile
- ✅ Maintains scroll position per pane
- ✅ TypeScript types defined
- ✅ Component tests with vitest

**Testing:** Component snapshot tests, responsive tests **Documentation:**
Component API docs

______________________________________________________________________

#### Issue 1.6: Add Draggable Divider for Pane Resizing

- **Type:** Frontend Component (Enhancement)
- **Depends On:** Issue 1.5
- **Blocks:** Advanced layout control
- **Time:** 30 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/DualPaneLayout.svelte`

**Acceptance Criteria:**

- ✅ Draggable divider between panes
- ✅ Drag adjusts pane widths
- ✅ Minimum width enforcement (20%)
- ✅ Widths persisted to localStorage
- ✅ Cursor changes on hover
- ✅ Touch device support
- ✅ Keyboard shortcuts (arrow keys)
- ✅ No visual jumping during drag

**Testing:** Drag interaction tests, localStorage tests **Documentation:**
Keyboard shortcuts reference

______________________________________________________________________

#### Issue 1.7: Add Skeleton Loading States

- **Type:** Frontend Component
- **Depends On:** Issue 1.5
- **Blocks:** Progressive rendering UI
- **Time:** 25 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/SkeletonLoader.svelte`

**Acceptance Criteria:**

- ✅ Animated shimmer placeholder
- ✅ Shows multiple block placeholders
- ✅ Different heights for variety
- ✅ Works in both panes
- ✅ Accessible (not marked interactive)
- ✅ Component tests

**Testing:** Animation tests, accessibility tests **Documentation:** Component
usage guide

______________________________________________________________________

#### Issue 3.2: Create Configuration Store with Persistence

- **Type:** Frontend Store
- **Depends On:** Phase 0 infrastructure
- **Blocks:** Config panel, settings page
- **Time:** 25 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/stores/config.ts`

**Acceptance Criteria:**

- ✅ Svelte store: provider, model, target_language, api_key
- ✅ API key stored in memory only (never localStorage)
- ✅ Config persisted to localStorage
- ✅ Load from localStorage on startup
- ✅ Reset to defaults method
- ✅ TypeScript types
- ✅ Store tests with localStorage mock

**Testing:** Store logic tests, localStorage tests **Documentation:** Store API
documentation

______________________________________________________________________

#### Issue 3.3: Create Configuration Panel Component

- **Type:** Frontend Component
- **Depends On:** Issue 3.2
- **Blocks:** Settings workflow
- **Time:** 35 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/ConfigPanel.svelte`

**Acceptance Criteria:**

- ✅ Provider dropdown (OpenAI, Anthropic, etc.)
- ✅ Model selector (updates per provider)
- ✅ API key input (password field)
- ✅ Target language selector
- ✅ Test connection button
- ✅ Save and reset buttons
- ✅ Success/error messages
- ✅ Component tests with mocked stores

**Testing:** User interaction tests, form validation tests **Documentation:**
Component usage guide

______________________________________________________________________

### Batch 2.2: Frontend Pane Display (Week 5-6)

**Issues:** 1.8, 1.9, 3.4 **Estimated Time:** 1.5 hours **Rationale:** Display
layers needed before content integration

#### Issue 1.8: Create Source Pane Display Component

- **Type:** Frontend Component
- **Depends On:** Issue 1.5
- **Blocks:** Content display, synchronization
- **Time:** 30 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/SourcePane.svelte`

**Acceptance Criteria:**

- ✅ Renders extracted content blocks
- ✅ Heading hierarchy visualization (H1-H6)
- ✅ Code block syntax highlighting
- ✅ Images with lazy loading
- ✅ Lists (ul/ol) formatted
- ✅ Blockquotes styled
- ✅ Links preserved (footnote style)
- ✅ Responsive typography
- ✅ Component tests for each block type

**Testing:** Block type rendering tests, accessibility tests **Documentation:**
Supported content types reference

______________________________________________________________________

#### Issue 1.9: Create Translation Pane Display Component

- **Type:** Frontend Component
- **Depends On:** Issue 1.5
- **Blocks:** Translated content display
- **Time:** 20 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/TranslationPane.svelte`

**Acceptance Criteria:**

- ✅ Renders translated blocks
- ✅ Same structure as source
- ✅ Optimized line height (1.6-1.8)
- ✅ Readable font sizing
- ✅ RTL text support
- ✅ Component tests

**Testing:** Block rendering tests, typography tests **Documentation:**
Component usage guide

______________________________________________________________________

#### Issue 3.4: Create Settings Page/Route

- **Type:** Frontend Page
- **Depends On:** Issue 3.3
- **Blocks:** User settings workflow
- **Time:** 25 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/routes/settings/+page.svelte`

**Acceptance Criteria:**

- ✅ Route at `/settings`
- ✅ Config panel displayed
- ✅ Export configuration button (no API key)
- ✅ Clear data button with confirmation
- ✅ Version information shown
- ✅ Page tests with mocked stores

**Testing:** Navigation tests, button action tests **Documentation:** User guide
for settings

______________________________________________________________________

### Batch 2.3: Frontend Integration (Week 6-7)

**Issues:** 1.11, 1.12, 1.13, 1.14, 5.1 **Estimated Time:** 2 hours
**Rationale:** Connect frontend to backend, implement core interactions

#### Issue 1.11: Implement Progressive Block Rendering

- **Type:** Frontend Feature
- **Depends On:** Issues 1.5, 1.8, 1.9, Backend 1.10
- **Blocks:** Streaming translation workflow
- **Time:** 35 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/utils/streaming.ts`

**Acceptance Criteria:**

- ✅ Connects to `/api/v1/translate/stream`
- ✅ Parses SSE events correctly
- ✅ Updates UI for each block in real-time
- ✅ Shows loading state for pending blocks
- ✅ Handles stream errors gracefully
- ✅ Disconnects cleanly
- ✅ Works with variable translation speed
- ✅ Unit tests for event parsing

**Testing:** SSE parsing tests, error handling tests **Documentation:**
Streaming client implementation guide

______________________________________________________________________

#### Issue 1.12: Add Block-Level Hover Highlighting

- **Type:** Frontend Feature
- **Depends On:** Issues 1.8, 1.9
- **Blocks:** Synchronization interaction
- **Time:** 25 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/SourcePane.svelte`,
  `TranslationPane.svelte`

**Acceptance Criteria:**

- ✅ Hover source block → highlight in translation
- ✅ Hover translation → highlight in source
- ✅ Distinct but not harsh highlight color
- ✅ Debounced (50ms) to avoid flashing
- ✅ Works with keyboard focus
- ✅ Accurate block ID mapping
- ✅ Component tests with hover simulation

**Testing:** Interaction tests, animation tests **Documentation:** Interaction
behavior docs

______________________________________________________________________

#### Issue 1.13: Add Block-Level Click Navigation

- **Type:** Frontend Feature
- **Depends On:** Issue 1.12
- **Blocks:** Full synchronization
- **Time:** 20 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/DualPaneLayout.svelte`

**Acceptance Criteria:**

- ✅ Click source block → scroll translation to match
- ✅ Click translation → scroll source to match
- ✅ Smooth scroll animation (300ms)
- ✅ Scroll anchor preserved
- ✅ Works on both panes
- ✅ Component tests

**Testing:** Scroll behavior tests, edge case tests **Documentation:**
Navigation behavior docs

______________________________________________________________________

#### Issue 1.14: Add Keyboard Navigation

- **Type:** Frontend Feature
- **Depends On:** Issue 1.13
- **Blocks:** Accessibility
- **Time:** 25 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/DualPaneLayout.svelte`

**Acceptance Criteria:**

- ✅ Arrow Up/Down: Navigate blocks
- ✅ Tab: Switch panes
- ✅ Enter: Jump to matching block
- ✅ Home/End: First/last block
- ✅ Works with screen readers
- ✅ Visual focus indicator clear
- ✅ Keyboard tests with jsdom

**Testing:** Keyboard event tests, accessibility tests **Documentation:**
Keyboard shortcuts reference

______________________________________________________________________

#### Issue 5.1: Create Block ID Mapping Utility

- **Type:** Frontend Utility
- **Depends On:** Backend 1.4 (for block IDs)
- **Blocks:** Hover/click synchronization
- **Time:** 25 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/utils/block-mapping.ts`

**Acceptance Criteria:**

- ✅ Maps source block ID → translation block ID
- ✅ Reverse mapping available
- ✅ Fast lookup (O(1))
- ✅ Handles unmapped blocks gracefully
- ✅ Handles deleted blocks
- ✅ Unit tests with large content

**Testing:** Mapping logic tests, performance tests **Documentation:** Utility
API documentation

______________________________________________________________________

### Batch 2.4: Frontend Error Handling (Week 7)

**Issues:** 4.4, 4.5, 4.6 **Estimated Time:** 1.5 hours **Rationale:** Error
handling improves user experience significantly

#### Issue 4.4: Create Error Toast Notification Component

- **Type:** Frontend Component
- **Depends On:** Backend 4.1 (error format)
- **Blocks:** Error display workflow
- **Time:** 30 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/ErrorToast.svelte`

**Acceptance Criteria:**

- ✅ Shows error message
- ✅ Auto-dismiss after 5 seconds
- ✅ Manual dismiss button
- ✅ Severity indicator
- ✅ Optional retry button
- ✅ Multiple toasts stack
- ✅ ARIA announcements
- ✅ Component tests

**Testing:** Component tests, accessibility tests **Documentation:** Component
usage guide

______________________________________________________________________

#### Issue 4.5: Create Critical Error Modal Component

- **Type:** Frontend Component
- **Depends On:** Backend 4.1
- **Blocks:** Error workflow
- **Time:** 25 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/ErrorModal.svelte`

**Acceptance Criteria:**

- ✅ Shows error title and message
- ✅ Displays error code
- ✅ Suggests fixes/actions
- ✅ Copy button for bug report
- ✅ Cannot be dismissed accidentally
- ✅ Accessible keyboard navigation
- ✅ Component tests

**Testing:** Component tests, interaction tests **Documentation:** Component
usage guide

______________________________________________________________________

#### Issue 4.6: Implement Retry Logic with Countdown

- **Type:** Frontend Utility
- **Depends On:** Backend 4.1, 4.3 (rate limiting)
- **Blocks:** Rate limit handling
- **Time:** 30 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/utils/retry.ts`

**Acceptance Criteria:**

- ✅ Exponential backoff strategy
- ✅ Max retry limit enforced
- ✅ Countdown timer display
- ✅ Button disabled until ready
- ✅ Clear wait time messages
- ✅ Automatic retry option
- ✅ Unit tests for retry logic

**Testing:** Retry logic tests, timer tests **Documentation:** Retry strategy
documentation

______________________________________________________________________

### Batch 2.5: Frontend Advanced Sync (Week 8)

**Issues:** 5.2, 5.3 **Estimated Time:** 1 hour **Rationale:** Complete
synchronization features, add mobile support

#### Issue 5.2: Implement Scroll Synchronization Mode

- **Type:** Frontend Feature (Optional)
- **Depends On:** Issues 1.5, 5.1
- **Blocks:** Advanced sync modes
- **Time:** 30 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/DualPaneLayout.svelte`

**Acceptance Criteria:**

- ✅ Keep blocks aligned mode (sync scroll both panes)
- ✅ Independent scroll mode
- ✅ Toggle button to switch
- ✅ Mode persists to localStorage
- ✅ Smooth scroll (no jank)
- ✅ Touch device support
- ✅ Component tests

**Testing:** Scroll behavior tests, mode persistence tests **Documentation:**
Sync mode behavior documentation

______________________________________________________________________

#### Issue 5.3: Add Touch Support for Mobile

- **Type:** Frontend Feature
- **Depends On:** Issues 1.12, 1.13
- **Blocks:** Mobile experience
- **Time:** 30 min
- **Layer:** Frontend + Testing
- **Files:** `frontend/src/lib/components/DualPaneLayout.svelte`

**Acceptance Criteria:**

- ✅ Tap block to highlight (no hover needed)
- ✅ Swipe to navigate blocks
- ✅ Touch-friendly tap targets (48px minimum)
- ✅ No hover requirement
- ✅ Works on real devices
- ✅ Touch event tests

**Testing:** Touch event tests, device tests **Documentation:** Mobile
interaction guide

______________________________________________________________________

## Implementation Timeline

```
Week 1: Phase 0 - Infrastructure Setup
├─ Backend project initialization
├─ Frontend project initialization
├─ Development environment setup
├─ Testing frameworks configured
└─ CI/CD pipeline basic setup
  Status: BLOCKING all Phase 1 work

Week 2-3: Batch 1.1 - Backend Core Foundation
├─ 1.1: Translation API Endpoint
├─ 1.2: Translation Service
├─ 1.3: Content Extraction Service
└─ 1.4: Content Extraction Endpoint
  Cumulative Time: 2.5 hours
  Status: FOUNDATION for all other work

Week 3: Batch 1.2 - Backend Configuration
├─ 3.1: Configuration Validation Endpoint
└─ 4.1: Error Response Standardization
  Cumulative Time: 3.75 hours
  Status: Enables config UI and error handling

Week 4: Batch 1.3 - Backend Error Handling & Content Types
├─ 4.2: Handle URL Fetch Errors
├─ 4.3: Handle API Key Errors
├─ 2.2: News Article Support
├─ 2.3: Blog Post Support
└─ 2.5: Content Caching
  Cumulative Time: 6.25 hours

Week 4: Batch 1.4 - Streaming Translation Backend
└─ 1.10: Streaming Translation Endpoint
  Cumulative Time: 6.65 hours
  Status: BLOCKS frontend progressive rendering

Week 5: Batch 2.1 - Frontend Foundation
├─ 1.5: Dual-Pane Layout Component
├─ 1.6: Draggable Divider
├─ 1.7: Skeleton Loading
├─ 3.2: Configuration Store
└─ 3.3: Configuration Panel
  Cumulative Time: 9.15 hours
  Status: FOUNDATION for frontend features

Week 5-6: Batch 2.2 - Frontend Pane Display
├─ 1.8: Source Pane Display
├─ 1.9: Translation Pane Display
└─ 3.4: Settings Page
  Cumulative Time: 10.65 hours
  Status: Ready for content integration

Week 6-7: Batch 2.3 - Frontend Integration
├─ 1.11: Progressive Block Rendering
├─ 1.12: Block Hover Highlighting
├─ 1.13: Block Click Navigation
├─ 1.14: Keyboard Navigation
└─ 5.1: Block ID Mapping Utility
  Cumulative Time: 12.65 hours
  Status: Core interaction features complete

Week 7: Batch 2.4 - Frontend Error Handling
├─ 4.4: Error Toast Notifications
├─ 4.5: Critical Error Modal
└─ 4.6: Retry Logic with Countdown
  Cumulative Time: 14.15 hours
  Status: User-facing error handling

Week 8: Batch 2.5 - Frontend Advanced Sync
├─ 5.2: Scroll Synchronization Mode
└─ 5.3: Touch Support
  Cumulative Time: 15.15 hours
  Status: PHASE 1 COMPLETE

Testing & Documentation: Throughout all weeks
├─ Unit tests (included in each feature)
├─ Integration tests (included in batches)
├─ API documentation (updated during backend)
└─ User documentation (Phase 1 docs)
```

______________________________________________________________________

## GitHub Milestones

### Milestone: Phase 0 - Infrastructure Setup

- Status: Not Started
- Target: Week 1
- Issues: 7 infrastructure issues from
  [infrastructure-requirements.md](infrastructure-requirements.md)

### Milestone: Phase 1 - Core Translation Workbench

- Status: Ready to Start
- Target: Week 2-8
- Issues: 32 atomic features from [atomic-features.md](atomic-features.md)
- Sub-batches:
  - [x] Batch 1.1: Backend Foundation (4 issues)
  - [x] Batch 1.2: Configuration (2 issues)
  - [x] Batch 1.3: Error & Content (5 issues)
  - [x] Batch 1.4: Streaming (1 issue)
  - [x] Batch 2.1: Frontend Foundation (5 issues)
  - [x] Batch 2.2: Frontend Display (3 issues)
  - [x] Batch 2.3: Frontend Integration (5 issues)
  - [x] Batch 2.4: Error UI (3 issues)
  - [x] Batch 2.5: Advanced Sync (2 issues)

______________________________________________________________________

## Issue Numbering Convention

Issues will be numbered:

- **Infrastructure (Phase 0):** #1-#10 (Phase 0)
- **Phase 1 Backend:** #11-#25 (Batches 1.1-1.4)
- **Phase 1 Frontend:** #26-#42 (Batches 2.1-2.5)
- **Phase 1 Testing:** Included in each issue
- **Phase 1 Documentation:** #43-#50

**Total Phase 1 Issues:** 40+ issues

______________________________________________________________________

## Success Criteria by Batch

### Batch 1.1: Backend Core Foundation ✓

- All three translation/extraction endpoints working
- Services properly abstracted
- All tests passing
- Error handling in place

### Batch 1.2: Backend Configuration ✓

- Configuration validation endpoint working
- Error response format standardized
- All error codes documented
- Configuration guide available

### Batch 1.3: Backend Error & Content ✓

- Content type detection working
- Caching reducing redundant requests
- All error cases handled
- Content type documentation complete

### Batch 1.4: Streaming ✓

- SSE endpoint returning proper events
- Frontend can parse streaming responses
- Connection interruption handled gracefully

### Batch 2.1: Frontend Foundation ✓

- Layout component responsive
- Configuration store working
- Configuration UI complete
- Settings page accessible

### Batch 2.2: Frontend Display ✓

- Both panes displaying content correctly
- Block hierarchy respected
- Typography optimized
- Settings saved and applied

### Batch 2.3: Frontend Integration ✓

- Progressive rendering working
- Hover and click interactions working
- Keyboard navigation complete
- Block synchronization accurate

### Batch 2.4: Error UI ✓

- Error messages clear and actionable
- Retry logic working
- User can recover from errors
- Error logging functional

### Batch 2.5: Advanced Features ✓

- Scroll sync mode optional
- Touch interactions working
- Mobile experience polished

______________________________________________________________________

## Dependency Resolution Strategy

**Critical Path:** Backend 1.1 → 1.2 → 1.10 → Frontend 1.11

**Parallel Opportunities:**

- Batch 1.2 (Config) can start during 1.1 (requires only Phase 0)
- Batch 2.1 (Frontend) can start during 1.3 (independent of 1.10)
- Frontend 1.5-1.9 can be completed before 1.11

**Recommended Sequencing:** Exactly as defined above to maximize parallelization
while respecting critical dependencies.

______________________________________________________________________

## References

- [atomic-features.md](atomic-features.md) - Detailed atomic feature specs
- [layer-mapping.md](layer-mapping.md) - Feature to layer mapping
- [feature-dependency-analysis.md](feature-dependency-analysis.md) - High-level
  dependencies
- [adr/](adr/) - Architecture Decision Records
- [infrastructure-requirements.md](infrastructure-requirements.md) - Phase 0
  setup
