# Atomic Features Breakdown (Step 2.1)

This document breaks down high-level features from
[feature-specifications.md](feature-specifications.md) into atomic,
independently testable units following Step 2.1 of the
[github-issue-creation-methodology.md](github-issue-creation-methodology.md).

**Key Principle:** Each atomic feature should be:

- ✅ Independently valuable (can ship alone)
- ✅ Independently testable (has clear acceptance criteria)
- ✅ 15-30 minutes of review time
- ✅ Has clear dependencies documented
- ✅ Can be assigned to GitHub Copilot

## Phase 1: Core Translation Workbench

### Feature 1: Dual-Pane Translation with Progressive, Block-Level Rendering

**From Spec:** Display source and translated content side-by-side with
intelligent block-level synchronization.

#### Atomic Feature 1.1: Backend - Basic Translation API Endpoint

**Depends on:** Infrastructure setup (Phase 0) **Blocks:** Everything else in
Feature 1 **Implementation Time:** 30 minutes

```
POST /api/v1/translate
- Accepts: content blocks, target language, provider, model, API key
- Returns: translated blocks with metadata
- No streaming yet, simple request-response
```

**Acceptance Criteria:**

- Endpoint accepts JSON with content_blocks array
- Routes to translation service
- Returns translated blocks with same IDs
- Handles validation errors (400)
- Returns provider errors (4xx/5xx)

**Files:** `backend/app/api/v1/endpoints/translate.py`, tests

______________________________________________________________________

#### Atomic Feature 1.2: Backend - Translation Service with Provider Abstraction

**Depends on:** BYOK Configuration (Phase 1, Feature 3) **Blocks:** Translation
endpoints **Implementation Time:** 45 minutes

```python
TranslationService
- translate_block(block, target_language, provider, model, api_key)
- translate_blocks(blocks, ...)
- Abstracts provider differences (OpenAI, Anthropic, etc.)
```

**Acceptance Criteria:**

- Service can translate a single block
- Service can translate multiple blocks
- Provider-agnostic interface
- Token usage tracking
- Error handling for each provider type
- Unit tests for common cases
- Mock provider for testing

**Files:** `backend/app/services/translation_service.py`,
`backend/app/services/providers/`, tests

______________________________________________________________________

#### Atomic Feature 1.3: Backend - Content Extraction Service

**Depends on:** Infrastructure setup **Blocks:** Reader-mode extraction (1.2)
**Implementation Time:** 45 minutes

```python
ExtractionService
- extract(url: str) -> ExtractedContent
- Uses Mozilla Readability
- Returns structured blocks with types
```

**Acceptance Criteria:**

- Fetches URL and extracts content
- Returns title, author, date
- Returns content blocks with type (paragraph, heading, list, etc.)
- Handles network errors
- Handles non-HTML content
- Timeout after 30 seconds
- Unit tests with mock URLs
- Integration test with real URL

**Files:** `backend/app/services/extraction_service.py`, tests

______________________________________________________________________

#### Atomic Feature 1.4: Backend - Content Extraction Endpoint

**Depends on:** Content Extraction Service (1.3) **Blocks:** Frontend extraction
**Implementation Time:** 20 minutes

```
POST /api/v1/extract
- Accepts: {"url": "https://..."}
- Returns: ExtractedContent with blocks
```

**Acceptance Criteria:**

- Accepts URL in request body
- Validates URL format
- Returns 400 for invalid URL
- Returns 422 for extraction failure
- Returns 502 for unreachable host
- Returns structured content blocks
- Includes metadata (title, author, date)

**Files:** `backend/app/api/v1/endpoints/extract.py`, tests

______________________________________________________________________

#### Atomic Feature 1.5: Frontend - Basic Dual-Pane Layout Component

**Depends on:** Infrastructure setup **Blocks:** Source/translation display,
synchronization **Implementation Time:** 30 minutes

```svelte
DualPaneLayout
- Two-column layout (50/50 split by default)
- Left pane slot for source content
- Right pane slot for translated content
- Responsive (stacks on mobile)
```

**Acceptance Criteria:**

- Renders two columns side-by-side
- Accepts slots for left and right content
- Default 50/50 split
- Mobile: stacks vertically
- Maintains scroll position per pane
- TypeScript types defined
- Component tests with vitest

**Files:** `frontend/src/lib/components/DualPaneLayout.svelte`, tests

______________________________________________________________________

#### Atomic Feature 1.6: Frontend - Draggable Divider for Pane Resizing

**Depends on:** Dual-Pane Layout (1.5) **Blocks:** Responsive UI
**Implementation Time:** 30 minutes

```svelte
DualPaneLayout updates
- Draggable divider between panes
- Drag to adjust widths
- Minimum width enforcement (20%)
- Persist widths to localStorage
```

**Acceptance Criteria:**

- Divider is draggable horizontally
- Cursor changes to col-resize on hover
- Pane widths update during drag
- Minimum width enforced
- Widths saved to localStorage
- Works on touch devices
- Keyboard shortcuts (arrow keys) to adjust
- No visual jumping during drag

**Files:** `frontend/src/lib/components/DualPaneLayout.svelte`, tests

______________________________________________________________________

#### Atomic Feature 1.7: Frontend - Skeleton Loading States

**Depends on:** Dual-Pane Layout (1.5) **Blocks:** Progressive rendering (1.11)
**Implementation Time:** 25 minutes

```svelte
SkeletonLoader component
- Shows placeholder while content loads
- Animated shimmer effect
- Matches content block shapes
```

**Acceptance Criteria:**

- Loading skeleton animates
- Shows multiple block placeholders
- Different heights for variety
- Works in both panes
- Component tests
- Accessible (not marked as interactive)

**Files:** `frontend/src/lib/components/SkeletonLoader.svelte`, tests

______________________________________________________________________

#### Atomic Feature 1.8: Frontend - Source Content Display

**Depends on:** Dual-Pane Layout (1.5) **Blocks:** Block synchronization
**Implementation Time:** 30 minutes

```svelte
SourcePane component
- Renders extracted content blocks
- Heading hierarchy visualization
- Code block syntax highlighting
- Image display with alt text
- List and quote formatting
```

**Acceptance Criteria:**

- Renders paragraphs with proper spacing
- Headings (H1-H6) styled appropriately
- Lists (ul/ol) formatted correctly
- Blockquotes visually distinct
- Code blocks with syntax highlighting
- Images with lazy loading
- Links preserved (footnote style)
- Responsive typography
- Component tests for each block type

**Files:** `frontend/src/lib/components/SourcePane.svelte`, tests

______________________________________________________________________

#### Atomic Feature 1.9: Frontend - Translation Display Component

**Depends on:** Dual-Pane Layout (1.5) **Blocks:** Progressive rendering
**Implementation Time:** 20 minutes

```svelte
TranslationPane component
- Renders translated blocks
- Same structure as source
- Line height optimized for reading
```

**Acceptance Criteria:**

- Renders translated content with proper spacing
- Maintains block structure alignment
- Readable line height (1.6-1.8)
- Proper font sizing
- Supports RTL text (for future languages)
- Component tests

**Files:** `frontend/src/lib/components/TranslationPane.svelte`, tests

______________________________________________________________________

#### Atomic Feature 1.10: Backend - Streaming Translation Endpoint

**Depends on:** Translation Service (1.2) **Blocks:** Progressive rendering UI
**Implementation Time:** 40 minutes

Reference:
[ADR-002: Streaming Translation Architecture](adr/002-streaming-translation-architecture.md)

```
POST /api/v1/translate/stream
- Accepts: same as /api/v1/translate
- Returns: Server-Sent Events stream
- Each event: block translation result
- Final event: completion marker
```

**Acceptance Criteria:**

- Returns text/event-stream content type
- Sends block results as they complete
- Uses proper SSE format (data: {...})
- Error event on failure
- Done event on completion
- Can handle connection interruption
- Headers prevent proxy buffering
- Unit tests with mock provider
- Integration test with streaming

**Files:** `backend/app/api/v1/endpoints/translate.py`, tests

______________________________________________________________________

#### Atomic Feature 1.11: Frontend - Progressive Block Rendering

**Depends on:** Streaming Endpoint (1.10), Translation Display (1.9) **Blocks:**
Block synchronization **Implementation Time:** 35 minutes

```typescript
StreamingTranslation service
- Connect to /api/v1/translate/stream
- Handle SSE events
- Update UI for each block
- Handle errors gracefully
```

**Acceptance Criteria:**

- Connects to streaming endpoint
- Parses SSE events correctly
- Updates UI for each block in real-time
- Shows loading state for pending blocks
- Handles stream errors
- Disconnects cleanly
- Works with variable translation speed
- Unit tests for event parsing

**Files:** `frontend/src/lib/utils/streaming.ts`, tests

______________________________________________________________________

#### Atomic Feature 1.12: Frontend - Block-Level Hover Highlighting

**Depends on:** Source Pane (1.8), Translation Pane (1.9) **Blocks:** Complete
synchronization **Implementation Time:** 25 minutes

```
Hover interaction
- Hover source block → highlight in translation
- Hover translation block → highlight in source
- Show block position/count tooltip
```

**Acceptance Criteria:**

- Hover on source block highlights matching translation
- Hover on translation highlights matching source
- Highlight color is distinct but not harsh
- Debounced (50ms) to avoid flashing
- Works with keyboard focus
- Block ID mapping is accurate
- Component tests with hover simulation

**Files:** `frontend/src/lib/components/SourcePane.svelte`,
`TranslationPane.svelte`, tests

______________________________________________________________________

#### Atomic Feature 1.13: Frontend - Block-Level Click Navigation

**Depends on:** Block Hover (1.12) **Blocks:** Synchronization complete
**Implementation Time:** 20 minutes

```
Click interaction
- Click source block → scroll translation to matching block
- Click translation block → scroll source to matching block
- Smooth scroll animation
```

**Acceptance Criteria:**

- Click highlights block
- Scrolls other pane to matching block
- Smooth scroll animation (300ms)
- Handles blocks at edge of viewport
- Scroll anchor preserved (doesn't jump)
- Works on both panes
- Component tests

**Files:** `frontend/src/lib/components/DualPaneLayout.svelte`, tests

______________________________________________________________________

#### Atomic Feature 1.14: Frontend - Keyboard Navigation

**Depends on:** Block Navigation (1.13) **Blocks:** Accessibility features
**Implementation Time:** 25 minutes

```
Keyboard shortcuts
- Arrow Up/Down: Navigate blocks in current pane
- Tab: Switch between panes
- Enter: Jump to matching block in other pane
- Home/End: Jump to first/last block
```

**Acceptance Criteria:**

- Arrow keys move focus through blocks
- Tab moves to other pane
- Enter jumps to matching block
- Home/End work as expected
- Works with screen readers
- Visual focus indicator clear
- Keyboard tests with jsdom

**Files:** `frontend/src/lib/components/DualPaneLayout.svelte`, tests

______________________________________________________________________

### Feature 2: Reader-Mode Extraction from Most Public URLs

**From Spec:** Intelligently extract and clean main content from web pages.

#### Atomic Feature 2.1: Backend - Content Extraction Endpoint (Already 1.4)

**Depends on:** Extraction Service (1.3) **Status:** Already defined above

#### Atomic Feature 2.2: Backend - Support for News Articles

**Depends on:** Extraction Service (1.3) **Blocks:** Other content types
**Implementation Time:** 30 minutes

```
Readability improvements for news
- Detect and extract headlines
- Byline and date detection
- Pull quote extraction
- Image captions
```

**Acceptance Criteria:**

- Extracts headline as H1
- Detects byline and author
- Preserves publication date
- Extracts pull quotes
- Handles image captions
- Unit tests with 3 news articles
- Integration tests with real news sites

**Files:** `backend/app/services/extraction_service.py`, tests

______________________________________________________________________

#### Atomic Feature 2.3: Backend - Support for Blog Posts

**Depends on:** Extraction Service (1.3) **Blocks:** Other content types
**Implementation Time:** 25 minutes

```
Blog post extraction
- Title and metadata
- Author information
- Publication date
- Body paragraphs
- Comments section filtering
```

**Acceptance Criteria:**

- Extracts title and author
- Gets publication date
- Filters out comments section
- Handles sidebar content gracefully
- Unit tests with 3 blog posts
- Integration tests with popular blogs

**Files:** `backend/app/services/extraction_service.py`, tests

______________________________________________________________________

#### Atomic Feature 2.4: Backend - Support for Technical Documentation

**Depends on:** Extraction Service (1.3) **Blocks:** Other content types
**Implementation Time:** 30 minutes

```
Documentation extraction
- Heading hierarchy preservation
- Code block preservation
- Example extraction
- Links to reference docs
```

**Acceptance Criteria:**

- Code blocks preserved with formatting
- Heading structure maintained
- Examples clearly marked
- Links preserved
- Line numbers removed from code
- Unit tests with tech docs
- Integration tests with real docs sites

**Files:** `backend/app/services/extraction_service.py`, tests

______________________________________________________________________

#### Atomic Feature 2.5: Backend - Content Caching (24-hour TTL)

**Depends on:** Extraction Endpoint (1.4) **Blocks:** Performance optimization
**Implementation Time:** 30 minutes

```
Caching strategy
- Cache extracted content for 24 hours
- Use URL as cache key
- Compress cached content
- Cleanup expired cache
```

**Acceptance Criteria:**

- Same URL returns cached result if \< 24h old
- Returns fresh content after 24h
- Storage quota checked before caching
- Automatic cleanup of old entries
- Unit tests for cache logic
- Performance tests show improvement

**Files:** `backend/app/services/caching_service.py`, tests

______________________________________________________________________

### Feature 3: BYOK Configuration

**From Spec:** Users provide their own API credentials for full privacy and cost
control.

#### Atomic Feature 3.1: Backend - Configuration Validation Endpoint

**Depends on:** Infrastructure setup **Blocks:** Config UI, all translation
**Implementation Time:** 30 minutes

```
POST /api/v1/config/validate
- Accepts: provider, model, api_key
- Validates API key format
- Tests API key with provider
- Returns: success/error with details
```

**Acceptance Criteria:**

- Validates key format before API call
- Makes test API call to provider
- Returns clear error if key invalid
- Handles provider-specific errors
- Doesn't expose key in error messages
- Timeout protection (10 seconds)
- Unit tests with mocked providers
- Integration tests with real providers

**Files:** `backend/app/api/v1/endpoints/config.py`, tests

______________________________________________________________________

#### Atomic Feature 3.2: Frontend - Configuration Store with Persistence

**Depends on:** Infrastructure setup **Blocks:** Config UI **Implementation
Time:** 25 minutes

Reference:
[ADR-005: Frontend State Management](adr/005-frontend-state-management.md)

```typescript
ConfigStore (Svelte store)
- provider: string
- model: string
- target_language: string
- api_key: string (memory only)
- Persist config (except API key) to localStorage
```

**Acceptance Criteria:**

- Store persists configuration
- API key NOT persisted
- Can load from localStorage on startup
- Reset to defaults available
- Store methods typed with TypeScript
- Store tests with localStorage mock
- No API key in localStorage dumps

**Files:** `frontend/src/lib/stores/config.ts`, tests

______________________________________________________________________

#### Atomic Feature 3.3: Frontend - Configuration Modal/Panel

**Depends on:** Config Store (3.2) **Blocks:** Settings workflow
**Implementation Time:** 35 minutes

```svelte
ConfigPanel component
- Provider dropdown (OpenAI, Anthropic, etc.)
- Model selector (updates based on provider)
- API key input field
- Target language selector
- Test connection button
- Save and reset buttons
```

**Acceptance Criteria:**

- Provider dropdown shows all supported providers
- Model selector updates based on provider
- API key input is password field
- Language selector shows common languages
- Test button validates configuration
- Save button updates store
- Reset button clears and loads defaults
- Shows success/error messages
- Component tests with mock stores

**Files:** `frontend/src/lib/components/ConfigPanel.svelte`, tests

______________________________________________________________________

#### Atomic Feature 3.4: Frontend - Settings Page/Route

**Depends on:** Config Panel (3.3) **Blocks:** User workflow **Implementation
Time:** 25 minutes

```svelte
Settings page
- Config panel integrated
- Export configuration option
- Clear data option
- Version information
```

**Acceptance Criteria:**

- Route at `/settings`
- Config panel displayed
- Export button downloads JSON (no API key)
- Clear data button with confirmation
- Version info shown
- Page tests with mocked stores

**Files:** `frontend/src/routes/settings/+page.svelte`, tests

______________________________________________________________________

### Feature 4: Clear Error Handling

**From Spec:** Transparent, actionable error messages guide users to resolve
issues.

#### Atomic Feature 4.1: Backend - Error Response Standardization

**Depends on:** Infrastructure setup (Error Handling Framework) **Blocks:**
Error endpoints **Implementation Time:** 20 minutes

Reference:
[ADR-004: Error Handling Patterns](adr/004-error-handling-patterns.md)

```json
Standard format:
{
  "error": "Human readable message",
  "code": "ERROR_CODE",
  "details": { "field": "value" },
  "request_id": "uuid"
}
```

**Acceptance Criteria:**

- All error responses follow format
- HTTP status codes match error types
- Request IDs included
- No sensitive data in messages
- Unit tests for error formatting

**Files:** Already in infrastructure setup

______________________________________________________________________

#### Atomic Feature 4.2: Backend - URL Fetch Error Handling

**Depends on:** Extraction Service (1.3) **Blocks:** Error display
**Implementation Time:** 25 minutes

```
Error cases:
- Invalid URL format → 400
- Host unreachable → 502
- Timeout → 504
- Access denied → 403
- Server error → 500
```

**Acceptance Criteria:**

- Each error case handled
- Appropriate HTTP status codes
- User-friendly error messages
- Logged for debugging
- Unit tests for each case
- Integration tests with real URLs

**Files:** `backend/app/services/extraction_service.py`, tests

______________________________________________________________________

#### Atomic Feature 4.3: Backend - API Key Error Handling

**Depends on:** Translation Service (1.2) **Blocks:** Error display
**Implementation Time:** 20 minutes

```
Error cases:
- Invalid key format → 400
- Key unauthorized → 401
- Quota exceeded → 402 (or custom)
- Rate limited → 429
```

**Acceptance Criteria:**

- Each error case detected
- Appropriate HTTP status codes
- User can retry/recover
- Rate limit info included in response
- Unit tests with mocked providers
- Integration tests with real APIs

**Files:** `backend/app/services/providers/`, tests

______________________________________________________________________

#### Atomic Feature 4.4: Frontend - Error Toast Notifications

**Depends on:** Error Response Format (4.1) **Blocks:** Error display
**Implementation Time:** 30 minutes

```svelte
ErrorToast component
- Shows error message
- Auto-dismiss after 5 seconds
- Manual dismiss button
- Error severity indicator
- Optional retry button
```

**Acceptance Criteria:**

- Toast displays error message
- Dismisses automatically
- Can be dismissed manually
- Color indicates severity
- Retry button on transient errors
- Multiple toasts stack
- Accessible (ARIA announcements)
- Component tests

**Files:** `frontend/src/lib/components/ErrorToast.svelte`, tests

______________________________________________________________________

#### Atomic Feature 4.5: Frontend - Error Modal for Critical Errors

**Depends on:** Error handling foundation **Blocks:** Error workflow
**Implementation Time:** 25 minutes

```svelte
ErrorModal component
- Shows error title and detailed message
- Error code for debugging
- Suggested actions/links
- Copy error for bug report
```

**Acceptance Criteria:**

- Modal appears on critical errors
- Shows error code
- Suggests fixes/next steps
- Copy button for error details
- Modal cannot be dismissed accidentally
- Accessible keyboard navigation
- Component tests

**Files:** `frontend/src/lib/components/ErrorModal.svelte`, tests

______________________________________________________________________

#### Atomic Feature 4.6: Frontend - Retry Logic with Countdown

**Depends on:** Error handling **Blocks:** Rate limit handling **Implementation
Time:** 30 minutes

```typescript
RetryManager utility
- Exponential backoff
- Max retry limit
- Countdown timer display
- Automatic retry option
```

**Acceptance Criteria:**

- Shows countdown timer
- Disables button until ready
- Exponential backoff works
- Max retries respected
- Clear message about wait time
- Unit tests for retry logic

**Files:** `frontend/src/lib/utils/retry.ts`, tests

______________________________________________________________________

### Feature 5: Block-Level Synchronization

**From Spec:** Clicking or hovering highlights corresponding blocks between
panes.

**Status:** Already covered in Feature 1 (Items 1.12-1.14)

Additional synchronization features:

#### Atomic Feature 5.1: Frontend - Block ID Mapping and Lookup

**Depends on:** Translation Service (1.2) **Blocks:** Hover/click
synchronization **Implementation Time:** 25 minutes

```typescript
BlockMapper utility
- Maps source block ID → translation block ID
- Reverse mapping available
- Fast lookup (O(1))
- Handles unmapped blocks gracefully
```

**Acceptance Criteria:**

- Mapping created after extraction
- Lookup is fast
- Works with all block types
- Handles edge cases (deleted blocks)
- Unit tests with large content

**Files:** `frontend/src/lib/utils/block-mapping.ts`, tests

______________________________________________________________________

#### Atomic Feature 5.2: Frontend - Scroll Synchronization Mode (Optional)

**Depends on:** Block Synchronization (1.13) **Blocks:** Advanced features
**Implementation Time:** 30 minutes

```
Synchronization options
- Keep blocks aligned: scroll both panes
- Independent scroll: scroll one pane only
- Toggle button to switch modes
```

**Acceptance Criteria:**

- Both modes work
- Mode persists to localStorage
- Scroll sync feels natural (no jank)
- Works on touch devices
- Component tests

**Files:** `frontend/src/lib/components/DualPaneLayout.svelte`, tests

______________________________________________________________________

#### Atomic Feature 5.3: Frontend - Touch Support (Mobile)

**Depends on:** Hover/Click Sync (1.12-1.13) **Blocks:** Mobile experience
**Implementation Time:** 30 minutes

```
Touch interactions
- Tap block to highlight (no hover)
- Swipe to navigate blocks
- Touch-friendly tap targets (48px minimum)
```

**Acceptance Criteria:**

- Tap highlights block
- Swipe changes pane
- No hover required
- Touch targets ≥ 48px
- Works on real devices
- Touch tests in vitest

**Files:** `frontend/src/lib/components/DualPaneLayout.svelte`, tests

______________________________________________________________________

## Phase 2: Translation Refinement & User Knowledge Artifacts

### Feature 6: Re-Translation with Custom Prompts

#### Atomic Features 6.1-6.5: Re-translation workflow

**High-level breakdown:**

- 6.1: Backend - Re-translate endpoint (`POST /api/v1/translate/retry`)
- 6.2: Backend - Prompt template service
- 6.3: Frontend - Re-translate button on blocks
- 6.4: Frontend - Prompt input modal
- 6.5: Frontend - Translation preview and accept/reject UI

(Detailed breakdown can follow similar pattern to Feature 1)

______________________________________________________________________

### Feature 7: Local Visit History

#### Atomic Features 7.1-7.4: History management

- 7.1: Backend - History storage (IndexedDB schema)
- 7.2: Backend - History API endpoints (save, list, get, delete)
- 7.3: Frontend - History manager service
- 7.4: Frontend - History panel/sidebar with search

______________________________________________________________________

### Feature 8: Paste-Text Translation

#### Atomic Features 8.1-8.3: Paste mode

- 8.1: Frontend - Paste interface component
- 8.2: Backend - Handle plain text translation
- 8.3: Frontend - Treat pasted content as temporary session

______________________________________________________________________

### Feature 9: Selection Commands

#### Atomic Features 9.1-9.5: Explain, define, summarize

- 9.1: Frontend - Text selection handler
- 9.2: Frontend - Context menu on selection
- 9.3: Frontend - Selection command implementation (explain/define/summarize)
- 9.4: Backend - Command endpoints
- 9.5: Frontend - Save results as notes

______________________________________________________________________

## Phase 3: AI Insights & Verification

### Feature 10: On-Demand Verification

#### Atomic Features 10.1-10.4: Verification packs

- 10.1: Backend - Claims extraction
- 10.2: Backend - Internal consistency checking
- 10.3: Backend - Fact-check coordination
- 10.4: Frontend - Verification results display

______________________________________________________________________

(Similar pattern for remaining Phase 3 features)

______________________________________________________________________

## Atomic Features Statistics

### Phase 1 Breakdown

| Feature                    | Atomic Units | Total Time | Backend | Frontend | Testing |
| -------------------------- | ------------ | ---------- | ------- | -------- | ------- |
| 1: Dual-Pane & Progressive | 14           | 6.5h       | 5       | 7        | 2       |
| 2: Reader-Mode Extraction  | 5            | 2h         | 4       | 1        | -       |
| 3: BYOK Configuration      | 4            | 1.75h      | 1       | 2        | 1       |
| 4: Error Handling          | 6            | 2.25h      | 3       | 2        | 1       |
| 5: Block Synchronization   | 3            | 1.5h       | -       | 3        | -       |
| **Total Phase 1**          | **32**       | **14h**    | **13**  | **15**   | **4**   |

### Estimation Notes

- **Backend:** 30-45 min per API endpoint + service
- **Frontend:** 20-35 min per component
- **Testing:** Already included in items above
- **Review time:** 15-30 min per atomic feature

______________________________________________________________________

## Implementation Sequence (Recommended)

### Week 1 (Infrastructure - Phase 0)

Complete all infrastructure setup before starting Feature 1.

### Week 2 (Feature 1.1-1.4: Foundations)

- 1.1: Translation endpoint
- 1.2: Translation service
- 1.3: Extraction service
- 1.4: Extraction endpoint

### Week 3 (Feature 1.5-1.9: UI Components)

- 1.5: Dual-pane layout
- 1.6: Draggable divider
- 1.7: Skeleton loaders
- 1.8: Source pane
- 1.9: Translation pane

### Week 4 (Feature 1.10-1.14: Streaming & Sync)

- 1.10: Streaming endpoint
- 1.11: Progressive rendering
- 1.12: Hover highlighting
- 1.13: Click navigation
- 1.14: Keyboard navigation

### Week 5 (Feature 2: Extraction)

- 2.2-2.4: Content type support
- 2.5: Caching

### Week 6 (Feature 3: Configuration)

- 3.1: Validation
- 3.2: Store
- 3.3: Panel
- 3.4: Settings page

### Week 7 (Feature 4: Error Handling)

- 4.1-4.6: Error display and recovery

### Week 8 (Feature 5: Advanced Sync)

- 5.1-5.3: Mapping, sync modes, touch

______________________________________________________________________

## Next Steps

After this Step 2.1 completion:

1. **Step 2.2**: Map these atomic features to tech stack layers
1. **Step 2.3**: Finalize implementation sequence with dependencies
1. **Step 3**: Create GitHub issue templates
1. **Step 4**: Begin creating detailed GitHub issues for each atomic feature

______________________________________________________________________

## References

- [Feature Specifications](feature-specifications.md)
- [Feature Dependency Analysis](feature-dependency-analysis.md)
- [Infrastructure Requirements](infrastructure-requirements.md)
- [GitHub Issue Creation Methodology](github-issue-creation-methodology.md)
- [ADRs](adr/README.md)
