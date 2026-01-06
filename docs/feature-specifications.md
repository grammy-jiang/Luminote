# Luminote: Comprehensive Design Document

This document provides the complete design specifications for Luminote, including purpose, roadmap, and detailed features for all development phases.

---

## Table of Contents

- [Purpose & Overview](#purpose--overview)
- [Product Roadmap](#product-roadmap)
- [Phase 1: Core Translation Workbench](#phase-1-core-translation-workbench-features)
- [Phase 2: Translation Refinement & User Knowledge Artifacts](#phase-2-translation-refinement--user-knowledge-artifacts)
- [Phase 3: AI Insights, Verification & Knowledge Integration](#phase-3-ai-insights-verification--knowledge-integration)
- [Architecture Overview](#architecture-overview)

---

## Purpose & Overview

### What is Luminote?

Luminote is a dual-pane translation workbench that makes dense web content understandable, verifiable, and reviewable. It keeps translation as the primary view while offering on-demand AI assistance for insights and verification.

### Who It Serves

- Readers of high-density materials (news, research papers, technical docs, financial reports)
- Bilingual/translation-heavy workflows needing accuracy and provenance
- Users who want local-first control with BYOK (Bring Your Own Key)

### Core Outcomes

- Faster comprehension of source content through progressive, block-level translation
- Greater confidence via optional verification and provenance of AI outputs
- Reduced friction with reader-mode extraction and synchronized dual-pane navigation

### Key Differentiators

- **Two-pane reading**: Source on the left (reader-mode), translation is the primary, persistent view on the right
- **Selection commands**: Select text on either pane → explain / define terms / summarize / verify
- **Versioned artifacts**: Notes/highlights/history + prompt-driven regeneration (keep recent versions)
- **On-demand AI**: User-controlled cost with explicit triggers for all AI operations
- **BYOK multi-provider**: Support OpenAI, Anthropic, and other providers with user's own API keys

---

## Product Roadmap

### Phase 1: Core Translation Workbench (Foundation)

Establish Luminote as a reliable, stable translation reader with essential features for daily use.

**Delivery Features:**
- Dual-pane translation with progressive, block-level rendering
- Reader-mode extraction from most public URLs (titles, paragraphs, lists, quotes, code, images)
- BYOK configuration for target language, provider/model, and API key
- Clear error handling for fetch failures, invalid keys, and rate limits
- Block-level synchronization with hover/click linkage between panes

### Phase 2: Enhanced Translation & Versioning

Extend with prompt control, local history, and selection-based insights.

**Delivery Features:**
- Re-translate per-block or full document with custom prompts
- Local visit history and quick paste-text translation (fallback when extraction fails)
- Selection-based commands: Explain, Define terms, Summarize (save as notes)
- Prompt templates, termbase setup, translation versioning (keep recent versions)

### Phase 3: Verification & Knowledge Integration

Add verification, highlights, multi-model checks, and optional web browsing.

**Delivery Features:**
- On-demand AI insights and verification packs (claims checklist, internal consistency)
- Highlights, notes, and saved AI explanations
- Link cards with bilingual summaries; optional web-browsing/RAG with citations
- Multi-model cross-check and refinement (enhanced mode)

---

# Phase 1: Core Translation Workbench Features

This phase establishes Luminote as a stable, reliable translation workbench.

---

## 1. Dual-Pane Translation with Progressive, Block-Level Rendering

### Overview
Display source and translated content side-by-side with intelligent block-level synchronization, enabling fast comprehension without losing context.

### Key Requirements

#### 1.1 Two-Pane Layout
- **Left Pane (Source)**: Reader-mode extraction of original content
  - Clean, distraction-free presentation
  - Proper typography and spacing preservation
  - Content hierarchy visualization (headings, subheadings, sections)

- **Right Pane (Translation)**: AI-translated content (primary view)
  - Full-width translation text
  - Maintains semantic structure parallel to source
  - Optimized for reading flow in target language

#### 1.2 Progressive Block-Level Rendering
- **Block Definition**: Content chunked at logical boundaries
  - Paragraphs
  - Lists (ordered/unordered)
  - Quotes/blockquotes
  - Code blocks
  - Images with captions
  - Tables
  - Headings + immediate subsections

- **Progressive Delivery**:
  - First visible block translates immediately (within 2-3 seconds of fetch)
  - Remaining blocks render sequentially as they complete translation
  - Each block shows completion state (skeleton/loading → rendered)
  - Users can read completed blocks while others load

- **UI Feedback**:
  - Loading skeleton for pending translations
  - Smooth fade-in transitions between states
  - Scroll anchor preservation (don't jump when blocks load above)

#### 1.3 Responsive Pane Sizing
- Adjustable pane width ratio (50/50 default, draggable divider)
- Mobile/tablet: stacked view with tab/toggle to switch panes
- Accessibility: keyboard shortcuts to navigate between panes

---

## 2. Reader-Mode Extraction from Most Public URLs

### Overview
Intelligently extract and clean main content from web pages, removing clutter while preserving structure, images, and semantic meaning.

### Key Requirements

#### 2.1 Content Extraction Coverage
Support extraction from:
- **News articles**: Headlines, bylines, dates, body paragraphs, pull quotes
- **Blog posts**: Title, metadata, body, comments section (optional)
- **Research papers/PDFs**: Title, abstract, sections, figures, tables, references
- **Technical documentation**: Headings, code blocks, examples, links
- **Financial reports**: Headers, data tables, charts, key metrics
- **Wikipedia/reference**: Article body, tables, infoboxes (cleaned)
- **Plain text/HTML**: Fallback graceful parsing

#### 2.2 Content Elements Preserved
- **Text**: Paragraphs, lists, inline formatting (emphasis, bold, code)
- **Structure**: Heading hierarchy (H1→H6), sections, subsections
- **Rich Content**:
  - Images (src, alt text, caption)
  - Code blocks (syntax-highlighted markers, language hints)
  - Tables (header/body rows, column alignment)
  - Blockquotes + citations
  - Embedded links (href preserved as footnotes or inline)
- **Metadata**: Article title, author, publication date, URL

#### 2.3 Content Filtering
- **Remove**: Navigation menus, footers, ads, tracking pixels, popups, "cookie consent" banners
- **Minimize**: Sidebar widgets, "related articles" suggestions
- **Flatten**: Complex CSS layouts to semantic HTML
- **Normalize**: Whitespace and line breaks for consistency

#### 2.4 Edge Cases & Fallbacks
- **JavaScript-heavy sites**: Use headless browser (Playwright/Selenium) if initial HTML extraction yields <30% content
- **Paywalled content**: Detect and skip; notify user with clear message
- **Non-HTML (images, videos)**: Graceful fallback—provide URL and request manual paste-text mode
- **Very long pages**: Chunk extraction into sections; auto-paginate or truncate with continuation pointer

#### 2.5 Performance
- Extraction completes within 5–10 seconds for typical articles
- Cache extracted content (browser storage) for revisits within 24 hours
- Lazy-load images (defer fetching until visible in viewport)

---

## 3. BYOK (Bring Your Own Key) Configuration

### Overview
Users provide their own API credentials, ensuring full privacy, cost control, and provider flexibility. No centralized credential storage.

### Key Requirements

#### 3.1 Configuration UI
- **Settings modal/panel** accessible from top-right menu
  - Provider selection dropdown:
    - OpenAI (GPT-4o, GPT-4o-mini)
    - Anthropic (Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku)
    - Other: extensible for future providers (Gemini, Llama Cloud, etc.)

  - Model selection (dynamic based on provider)
  - Target language dropdown (ISO 639-1 codes: zh, ja, ko, es, fr, de, etc.)
  - API Key input (masked, with "show/hide" toggle)
  - Test connection button (validates key before saving)

#### 3.2 Storage & Security
- **Browser-only storage**: default to session-only memory; allow opt-in persistence
  in localStorage or IndexedDB (client-side encryption optional)
- **No server-side storage** of API keys and never log keys
- **HTTPS only** in transit; keys are sent to the backend per request and
  forwarded to provider APIs without persistence
- **Clear warnings**: Users understand key handling and can choose persistence

#### 3.3 Validation & Error Messages
- **Pre-flight checks**:
  - API key format validation (non-empty, reasonable length)
  - Test API call to provider (quota check, not full rate limit)
- **Clear feedback**:
  - ✓ "Configuration saved. Ready to translate."
  - ✗ "Invalid API key. Check with provider."
  - ⚠ "Rate limit approaching. Reduce request size or wait."

#### 3.4 Fallback & Reset
- Allow partial config (e.g., remember provider+language, but re-enter key each session)
- One-click "Reset to defaults" button
- Download/export config (without key) for backup

---

## 4. Clear Error Handling for Fetch Failures, Invalid Keys, and Rate Limits

### Overview
Transparent, actionable error messages guide users to resolve issues without confusion or silent failures.

### Key Requirements

#### 4.1 Fetch/Network Errors
| Error | User Message | Action |
|-------|--------------|--------|
| Invalid URL | "URL not recognized. Check format and try again." | Enable user retry or paste URL |
| Host unreachable (DNS, timeout) | "Cannot reach the website. Check internet connection or URL." | Suggest retry, check firewall |
| 403/401 (blocked, unauthorized) | "Website blocked access. Try a different URL or check permissions." | Explain crawl limits (user-agent spoofing not advised) |
| 5xx (server error) | "Website returned an error. Try again in a few moments." | Retry button with exponential backoff |
| Extraction empty | "No readable content found on page." | Suggest manual paste fallback (Phase 2) or try a different URL |

#### 4.2 API Key & Provider Errors
| Error | User Message | Action |
|-------|--------------|--------|
| Invalid key format | "API key appears invalid. Check provider docs for correct format." | Link to provider setup guide |
| Key unauthorized | "API key rejected by provider. Verify key is active and not expired." | Suggest key regeneration |
| Model not available | "Selected model unavailable for your account. Choose different model." | Filter available models |
| Insufficient quota | "API quota exhausted. Upgrade account or wait for reset." | Link to provider account page |

#### 4.3 Rate Limiting
| Scenario | User Message | Action |
|----------|--------------|--------|
| Provider rate limit (429) | "Too many requests to provider. Wait 60s before next translation." | Countdown timer, disable button |
| Local rate limit (client-side) | "Translating too frequently. Please wait 10s." | Show cooldown timer |
| Batch size exceeded | "Content too long for single request. Breaking into chunks." | Auto-chunk with progress bar |

#### 4.4 UI Presentation
- **Toast notifications** (bottom-right): ephemeral feedback for minor issues
- **Error modal** (center screen): for critical blockers requiring action
- **Inline warnings** (in UI): for config issues (e.g., missing API key)
- **Expandable details**: "Show full error" for debugging/logs (console or user report)

#### 4.5 Logging & Debug Mode
- Client-side error logging (IndexedDB or local file)
- Optional "Debug Mode" toggle to show full stack traces and API responses
- User report generation: include sanitized logs (without API keys) for bug reports

---

## 5. Block-Level Synchronization with Hover/Click Linkage Between Panes

### Overview
Clicking or hovering over a block in one pane highlights the corresponding block in the other pane, maintaining mental mapping as users read across languages.

### Key Requirements

#### 5.1 Hover Linkage
- **Hover behavior**:
  - User hovers over any block in left (source) pane
  - Corresponding translation block in right pane highlights (e.g., light yellow background, 0.2s animation)
  - Block remains highlighted until hover leaves source pane
  - Reverse: hover right pane → highlight left source

- **Visual indicators**:
  - Subtle background color (light highlight, not distracting)
  - Optional left border highlight (colored accent)
  - Tooltip or label showing block type (e.g., "Paragraph 3 of 12")

#### 5.2 Click Linkage
- **Click behavior**:
  - User clicks on any block in left pane
  - Right pane auto-scrolls to corresponding translation block
  - Block remains "selected" (darker highlight) until click elsewhere
  - Keyboard: Tab key cycles through blocks; Enter to jump to corresponding block

- **Bi-directional**:
  - Click right → scroll left to source
  - Useful for verifying specific translations

#### 5.3 Block Mapping & Synchronization
- **Block ID system**:
  - Each extracted block assigned unique ID during extraction
  - Translation preserves block structure (same ID mapping)
  - Map stored with translation result for fast lookup

- **Scroll synchronization**:
  - When user scrolls one pane, optional side-scroll locking (disabled by default; toggle in settings)
  - "Keep blocks aligned" mode: scroll both panes to same block position

#### 5.4 Mobile & Accessibility
- **Touch devices**: Tap a block to highlight (no hover); swipe to navigate
- **Keyboard**:
  - Arrow Up/Down: navigate blocks in active pane
  - Alt+Tab: switch panes
  - Enter: jump to corresponding block in other pane
- **Screen readers**: Announce block position and linkage ("Paragraph 3: Click to see translation")

#### 5.5 Performance
- Lazy-load block mapping (only build when needed)
- Debounce hover events (50ms) to avoid excessive re-renders
- Virtual scrolling for pages with 1000+ blocks (render only visible blocks)

---

## Phase 1 Implementation Priority

1. **Must-Have (MVP)**:
   - Basic dual-pane layout
   - Reader-mode extraction (HTML parsing, images, basic structure)
   - BYOK config (OpenAI/Anthropic, simple localStorage)
   - Core error handling (network, invalid key, rate limit)
   - Block-level hover/click synchronization

2. **Should-Have** (polish):
   - Progressive rendering (skeleton loaders, smooth fade-in)
   - Advanced extraction (tables, code blocks, metadata)
   - Keyboard navigation
   - Mobile responsiveness

3. **Nice-to-Have** (future):
   - Cache & offline support
   - Headless browser extraction (JS-heavy sites)
   - Debug mode & logging
   - Multi-provider auto-fallback

## Phase 1 Success Metrics

- Extraction success rate: >85% for typical news/blog articles
- Time to first block render: <3 seconds on 1 Mbps connection
- Translation accuracy: subjective user feedback (target: >4/5 stars)
- Error recovery: users able to resolve >90% of issues with on-screen guidance
- Mobile usability: pane navigation <2 taps
- Block sync latency: <100ms from hover to highlight

---

# Phase 2: Translation Refinement & User Knowledge Artifacts

This phase extends Luminote with re-translation capabilities, fallback modes, content annotation, and versioning—enabling users to refine translations and build personal knowledge assets.

---

## 1. Re-Translate Per-Block or Full Document with Custom Prompts

### Overview
Allow users to regenerate translations at block or document level using custom prompts, system instructions, and alternative models. Maintain version history for comparison and rollback.

### Key Requirements

#### 1.1 Re-Translation Triggers
- **Block-level re-translation**:
  - Right-click menu on translated block: "Re-translate", "Re-translate with custom prompt"
  - Inline button (icon) on hover over translated block
  - Keyboard shortcut (e.g., Ctrl+Shift+T on selected block)

- **Full-document re-translation**:
  - Button in top toolbar: "Re-translate All"
  - Menu option with preview of changes
  - Batch mode (re-translate only modified blocks since last save)

#### 1.2 Custom Prompt Interface
- **Prompt template modal**:
  - Pre-filled template: `"Translate the following {source_lang} text to {target_lang}. Consider: [custom instructions]"`
  - Text area for user instructions (e.g., "Use formal tone, preserve technical terms")
  - Dropdown to select system role (e.g., "Professional translator", "Academic translator", "Casual translator")
  - Optional: insert variables like `{source_lang}`, `{target_lang}`, `{context}` (surrounding blocks)

- **Quick templates**:
  - Pre-built templates: "Formal", "Casual", "Technical", "Literal", "Interpretive"
  - Save custom templates for reuse (stored locally)
  - Share templates (export as JSON) for collaboration

#### 1.3 Model Selection for Re-Translation
- **Alternative model picker**:
  - Dropdown to select different model from configured provider
  - Cross-provider model picker (if multiple providers configured)
  - Model comparison mode: re-translate with Model A vs Model B, show side-by-side

- **Provider fallback**:
  - If primary provider fails, auto-retry with secondary provider (if configured)
  - Show which provider was used in result metadata

#### 1.4 Re-Translation Preview & Application
- **Preview before commit**:
  - Show old vs. new translation in split view
  - Highlight differences (insertions, deletions, modifications)
  - Word count and reading time comparison
  - Option to accept, reject, or edit manually

- **Batch apply**:
  - Select multiple blocks, re-translate all at once
  - Progress bar with estimated time
  - Cancel mid-process with option to keep partial results

#### 1.5 Contextual Re-Translation
- **Include context**:
  - Send surrounding blocks (previous + current + next) to model for better coherence
  - Toggle "context-aware" mode (default: on for paragraphs, off for individual sentences)
  - Context window size: configurable (1–5 blocks before/after)

- **Terminology consistency**:
  - Optional input of glossary terms (e.g., "API" stays as "API", not "应用程序接口")
  - Apply termbase to ensure consistent terminology across re-translations

#### 1.6 Re-Translation Performance
- **Streaming responses**:
  - For long blocks, stream translation token-by-token
  - Show partial translation as it arrives (avoid long wait)
  - Allow user to stop streaming and keep partial result

- **Batching**:
  - Combine small blocks into single API call if total < token limit
  - Auto-split large blocks to stay within token limits
  - Queue requests to respect rate limits

---

## 2. Local Visit History and Quick Paste-Text Translation

### Overview
Maintain a searchable browsing history of translated URLs, and provide fallback paste-text mode for content that cannot be extracted or fetched.

### Key Requirements

#### 2.1 Local Visit History
- **History storage**:
  - Store in IndexedDB (client-side, persisted across sessions)
  - Each entry: URL, title, extraction timestamp, source language, target language, provider/model used
  - Metadata: word count, extraction quality score (% of content successfully extracted)
  - Full extracted content cached for fast re-opening (optional compression)

- **History UI**:
  - Sidebar panel: "History" tab with searchable list
  - Sort by: recent, frequency, title, language pair
  - Filter by: provider, model, date range, quality score
  - Search: full-text search across titles and cached content
  - Quick preview: hover entry to show thumbnail/excerpt

- **Storage limits**:
  - Default: keep 100 most recent entries + 500 MB cache
  - Configurable in settings: adjust retention policy
  - Manual cleanup: delete individual entries or clear all
  - Export/backup: download history as JSON

#### 2.2 History Management
- **Revisit functionality**:
  - Click history entry to reload cached extraction + translation
  - Option to fetch fresh (re-extract if page changed)
  - Compare versions: side-by-side diff of old vs. new extraction

- **Trash/Archive**:
  - Move entries to trash (recoverable) before permanent deletion
  - Archive important entries (mark as "keep" for manual cleanup immunity)
  - Tag entries for personal organization (e.g., "research", "reading-list", "references")

#### 2.3 Paste-Text Translation (Fallback Mode)
- **When to use**:
  - User manually pastes text (fallback when URL extraction fails)
  - Direct text input for snippets, emails, or extracted content
  - Bypass extraction entirely when user has already cleaned content

- **Paste interface**:
  - Dedicated tab or mode: "Paste Text"
  - Large text area with placeholder: "Paste or type content here..."
  - Optional metadata input:
    - Document title
    - Source language (auto-detect or manual)
    - Content type (article, email, snippet, etc.)
  - Character counter: show current/max length (max configurable, e.g., 50k chars)

- **Paste handling**:
  - Auto-detect language (CLD3 or similar)
  - Preserve formatting: maintain line breaks, indentation, code blocks
  - Optional: parse basic Markdown or HTML in pasted content
  - Not stored in history by default (unless user clicks "Save to history")

#### 2.4 Quick Paste Workflow
- **One-click translate**:
  - Paste text → Click "Translate" → renders in dual-pane view
  - No extraction step, no URL parsing
  - Useful for quick translations without setup

- **Mobile-friendly**:
  - Simplified paste interface on mobile (full-screen text area)
  - One-button "Translate" prominently displayed
  - Result in full-screen reading mode

#### 2.5 History Performance & Privacy
- **Lazy loading**:
  - Load history list without full cached content initially
  - Fetch cached content on-demand when user clicks entry

- **Privacy controls**:
  - Option to exclude certain URLs from history (auto-exclude regex patterns)
  - Incognito mode: temporary translations not stored in history
  - Clear history on exit (browser session option)
  - Encryption of cached content (optional, with performance trade-off)

---

## 3. Selection-Based Commands: Explain, Define, Summarize (Save as Notes)

### Overview
Enable users to select text in either pane and trigger context-specific AI operations to build understanding and annotate content.

### Key Requirements

#### 3.1 Text Selection & Command Invocation
- **Selection mechanism**:
  - User selects text in source or translated pane
  - Floating context menu appears near selection (400ms delay to avoid flashing)
  - Menu includes: Explain, Define, Summarize, Add Note (+ extensibility for custom commands)
  - Keyboard shortcuts: Alt+E (Explain), Alt+D (Define), Alt+S (Summarize)

- **Command availability**:
  - All commands available in source pane (for reference understanding)
  - In translated pane, commands apply to target language context
  - Disable commands if selection <3 words or >2000 words (configurable)

#### 3.2 Explain Command
- **Behavior**:
  - User selects text (e.g., a technical term or concept)
  - Click "Explain" or press Alt+E
  - Modal opens with explanation in target language
  - Explanation includes: definition, usage examples, related concepts, context from document

- **Prompt template**:
  - "Explain the following term/concept in {target_lang}, providing: 1) Definition, 2) Two usage examples, 3) Related concepts. Context: [surrounding 1-2 sentences]"
  - Customizable system role: "English teacher", "Technical expert", "Domain specialist"

- **UI**:
  - Side panel or modal with explanation
  - Include source selection highlighted in left pane for reference
  - "Ask follow-up" input field for multi-turn conversation
  - Save to notes button

#### 3.3 Define Command
- **Behavior**:
  - Quick definition (sentence or two) for terms/phrases
  - Faster than Explain (use smaller/cheaper model if available)
  - Suitable for vocabulary building

- **Prompt template**:
  - "Define this term concisely (1-2 sentences) in {target_lang}: [selected text]"
  - Optional: include usage example

- **UI**:
  - Floating tooltip/popover (non-modal, dismissible by clicking elsewhere)
  - Show definition + part of speech if available
  - Optional dictionary link (if term has external reference)
  - Option to expand to full explanation or add to personal glossary

#### 3.4 Summarize Command
- **Behavior**:
  - Summarize selected text or entire block
  - Useful for reducing dense paragraphs or understanding key points
  - Output length: configurable (abstract: 1 sentence, brief: 3-5 sentences, standard: 1 paragraph)

- **Prompt template**:
  - "Summarize the following text in {target_lang} in {length} sentences, focusing on key ideas: [selected text]"

- **UI**:
  - Side panel with summary
  - Toggle between original and summary
  - Slider to adjust summary length
  - Save to notes

#### 3.5 Save as Notes
- **Note creation**:
  - Each Explain/Define/Summarize result includes "Add to Notes" button
  - Note metadata: timestamp, source URL/block, command type, user tags
  - Note content: original selection + AI result + user annotation

- **Note annotation**:
  - User can add personal comments to notes
  - Add tags/categories for organization
  - Rate note usefulness (1-5 stars)
  - Link related notes

#### 3.6 Notes Interface
- **Notes sidebar panel**:
  - List of notes, filterable by tag, date, rating
  - Search notes by content
  - Organize in folders or tag hierarchy
  - Export notes (Markdown, PDF, JSON)

- **Note viewing**:
  - Inline preview of note in sidebar
  - Click to expand full note in side panel
  - Jump to source document if still in history
  - Show highlighted original selection in left pane

#### 3.7 Command Extensibility
- **Custom commands**:
  - Plugin system for adding new selection-based commands
  - Config file to define command prompt templates
  - Hooks: `onSelection`, `onExecute`, `onSave`

- **Batch operations**:
  - Select multiple non-contiguous regions (hold Ctrl/Cmd)
  - Execute command on all selections together or individually
  - Aggregate results (e.g., "Define these 5 terms")

#### 3.8 Selection Command Performance
- **Request optimization**:
  - Debounce selection events (100ms) before showing context menu
  - Cache results for identical selections (within same session)
  - Use faster/cheaper models for Define (e.g., gpt-4o-mini) vs. Explain

- **Streaming responses**:
  - Stream explanations/summaries for better perceived performance
  - User can stop streaming and keep partial result

---

## 4. Prompt Templates and Termbase Setup; Translation Versioning

### Overview
Provide tools for managing reusable prompt templates, maintaining terminology consistency, and tracking translation history for comparison and refinement.

### Key Requirements

#### 4.1 Prompt Templates Management
- **Template structure**:
  - Name, description, category (e.g., "translation", "explanation", "summary")
  - Template body with variables: `{source_lang}`, `{target_lang}`, `{text}`, `{context}`, `{tone}`, `{custom_vars}`
  - System role (persona)
  - Model suggestion (model name or cost tier: fast, balanced, quality)
  - Input/output constraints (min/max tokens)
  - Tags for discovery

- **Built-in templates**:
  - "Standard Translation": default professional tone
  - "Casual Translation": conversational style
  - "Technical Translation": preserve technical terms
  - "Formal Translation": academic/business tone
  - "Creative Translation": interpretive, idiomatic
  - "Literal Translation": word-for-word fidelity

- **Template UI**:
  - Settings panel: "Translation Templates"
  - List of templates with quick preview
  - Create new: form to define template, test with sample text
  - Edit/delete existing templates
  - Duplicate for variation
  - Import/export templates (JSON)

- **Template library sharing**:
  - Export individual templates or collections
  - Import shared templates from community (future)
  - Version templates (track changes over time)

#### 4.2 Template Application
- **In-app usage**:
  - Re-translation modal shows available templates dropdown
  - Select template to auto-populate custom prompt
  - Variables populated contextually (language, tone, etc.)
  - Override any variable before executing

- **Template testing**:
  - Inline "Test" button in template editor
  - Test with sample text before saving
  - Show result with estimated token cost
  - Iterate on template without committing

#### 4.3 Termbase (Glossary) Setup
- **Termbase structure**:
  - Entries: source term → target term + metadata
  - Metadata: part of speech, context, approved/pending status, notes
  - Domain/category (e.g., "medical", "legal", "IT")
  - Multiple target translations (with preference ranking)
  - Examples of usage in context

- **Termbase UI**:
  - Settings panel: "Termbase" or "Glossary"
  - Import: upload CSV/JSON with term pairs
  - Create entry: input source term, target translation, metadata
  - Search: find term by source or target language
  - Edit/delete entries
  - Mark entries as approved/pending for collaborative setup

- **Termbase categories**:
  - Create multiple termbases for different domains
  - Apply specific termbase to specific documents
  - Combine termbases (use multiple at once)

#### 4.4 Termbase Application in Translations
- **Enforcement**:
  - When translating, check text against active termbase
  - Highlight terms from termbase in source (left pane) and translation (right pane)
  - If term appears in source but translation doesn't match termbase → show warning
  - Option to auto-correct or manually review

- **Termbase injection into prompts**:
  - Include glossary excerpt in translation prompt: "Use these terms: [relevant entries]"
  - Helps model maintain consistency across blocks
  - Works with custom prompts + templates

#### 4.5 Translation Versioning
- **Version storage**:
  - Each translation generates a version (immutable snapshot)
  - Version metadata: timestamp, model used, provider, template/prompt, language pair, user notes
  - Store translations in IndexedDB by default (local-first)
  - Optional backend sync only if explicitly enabled in a later phase with auth
  - Default retention: keep last 10 versions per document, or 30 days

- **Version comparison**:
  - View list of versions for a document (sidebar or modal)
  - Compare two versions side-by-side: highlight differences
  - Show change summary: blocks added/changed/deleted, word count delta
  - Rollback to previous version (mark as current)

- **Version UI**:
  - Version history panel: timeline of translations
  - Each entry shows: timestamp, model, changes count, user notes
  - Click to view version details
  - Diff view: old vs. new with color-coded changes
  - Restore button: make version current again

- **Version annotations**:
  - User can add notes to versions ("Better flow", "Fixed typo in para 3", etc.)
  - Tag versions ("approved", "draft", "final-submit")
  - Archive versions to exclude from auto-delete

#### 4.6 Per-Block Versioning
- **Block-level history**:
  - Each translated block has version history
  - Useful for comparing alternative translations of single paragraph
  - Show "translation alternatives" view for a block
  - Pin preferred version to use going forward

- **Block acceptance workflow**:
  - After re-translation, user accepts or rejects new version
  - Rejected versions still retained in history
  - Track which versions were actually used (auditing)

#### 4.7 Version Management Performance
- **Storage optimization**:
  - Store diffs instead of full copies (delta compression)
  - Compress older versions or archive to browser cache
  - Configurable retention limits in settings

- **Lazy loading**:
  - Load version list without full content initially
  - Fetch full version content on-demand

---

## Phase 2 Implementation Priority

1. **Must-Have (Phase 2 Core)**:
   - Re-translate per-block with custom prompt modal
   - Full-document re-translation
   - Local visit history (storage + UI)
   - Paste-text translation fallback mode
   - Explain & Define selection commands (basic)
   - Summarize command
   - Save notes from command results
   - Basic translation versioning (store + compare)

2. **Should-Have** (Polish & Completeness):
   - Template management (create, import, apply)
   - Termbase setup and enforcement
   - Per-block versioning
   - Advanced selection (multiple regions)
   - History search and filters
   - Version annotations and rollback

3. **Nice-to-Have** (Future Enhancement):
   - Cross-provider re-translation comparison
   - Collaborative glossary sharing
   - Template library (community templates)
   - Voice input for paste-text
   - OCR for image-to-text translation

## Phase 2 Success Metrics

- **Re-translation**:
  - User satisfaction with custom prompt feature: >4/5
  - Average time to re-translate block: <2 seconds
  - Template reuse rate: >60% of advanced users adopt templates

- **History**:
  - History search latency: <500ms for 100 entries
  - Storage efficiency: <100 MB for 100 translated documents
  - Revisit rate: >40% of documents accessed again within 1 month

- **Selection Commands**:
  - Explain/Define used in >30% of translation sessions
  - Notes saved per session: avg 1-3 notes
  - Note searchability satisfaction: >4/5

- **Versioning**:
  - Version comparison time: <1 second
  - User satisfaction with version rollback: >4/5
  - Storage overhead: <20% additional vs. single translation

- **Termbase**:
  - Termbase hit rate: >70% of terms found in glossary for matched entries
  - Time to set up termbase: <10 minutes for 100 terms
  - Terminology consistency improvement: measurable reduction in variant translations

---

# Phase 3: AI Insights, Verification & Knowledge Integration

This phase transforms Luminote into a comprehensive knowledge workbench with on-demand AI insights, multi-model verification, highlights/annotations, and web-browsing capabilities with citations.

---

## 1. On-Demand AI Insights and Verification Packs

### Overview
Provide users with advanced analysis capabilities: claims verification, internal consistency checking, argument extraction, and bias detection. Package these as reusable "packs" that apply multiple AI operations in sequence.

### Key Requirements

#### 1.1 Insight Types & Packs

##### Claims Verification Pack
- **Functionality**:
  - Extract factual claims from translated content
  - Evaluate claim credibility (checkable, verifiable, contested, etc.)
  - Flag uncertain claims for manual verification
  - Suggest verification sources (knowledge base, web search)

- **Prompt templates**:
  - "Extract all factual claims from this text: [content]. For each claim, assess: 1) Verifiability (high/medium/low), 2) Common knowledge (yes/no), 3) Contested status (consensus/disputed/novel)"
  - "Identify the source/authority cited for this claim: [claim]. Is the source reliable?"

- **Output**:
  - List of claims with metadata: text, type (quantitative, qualitative), verifiability, source
  - Color-coded annotations in translated pane (green: verifiable, yellow: uncertain, red: contested/false)
  - Each claim linked to source location in document
  - Suggestions for fact-checking resources (Snopes, PubMed, scholar.google.com, etc.)

- **UI**:
  - Side panel: "Claims Verification"
  - List of extracted claims with assessment
  - Click claim to highlight in document
  - "Verify" button to web-search or consult external sources (Phase 3+ feature)

##### Internal Consistency Pack
- **Functionality**:
  - Detect contradictions within document (claim X conflicts with claim Y)
  - Identify unresolved tensions or open questions
  - Flag assumptions that should be stated explicitly
  - Check definition consistency (term used differently across sections)

- **Prompt template**:
  - "Analyze this document for internal consistency. Report: 1) Contradictions between claims, 2) Unresolved tensions, 3) Implicit assumptions, 4) Terms used inconsistently"

- **Output**:
  - List of inconsistencies with severity (critical, warning, info)
  - Cross-references: which paragraphs/claims conflict
  - Suggestions for clarification
  - Confidence score per issue

- **UI**:
  - Side panel: "Consistency Check"
  - Expandable list of issues
  - Click issue to highlight conflicting sections (dual highlight in both panes)
  - "Review" button to add manual note (resolved/acknowledged/needs fix)

##### Argument Structure Pack
- **Functionality**:
  - Identify thesis/main argument
  - Extract supporting premises and evidence
  - Map argument chain (premise → conclusion → further implications)
  - Assess argument soundness (logical fallacies, weak assumptions)

- **Prompt template**:
  - "Analyze the argument structure of this text: 1) Main thesis, 2) Key premises, 3) Evidence provided, 4) Logical flow, 5) Potential fallacies or weak points"

- **Output**:
  - Argument tree/diagram (text representation or graphical)
  - Thesis statement highlighted
  - Premises color-coded (strong, weak, unsupported)
  - Identified logical fallacies (ad hominem, straw man, slippery slope, etc.)
  - Suggestions for strengthening argument

- **UI**:
  - Graphical argument map panel (nodes = premises/conclusion, edges = inference)
  - Alternative: text outline with hierarchical structure
  - Click node to highlight supporting text in document

##### Bias & Tone Detection Pack
- **Functionality**:
  - Detect language bias (political, cultural, gender bias)
  - Analyze tone (neutral, opinionated, inflammatory, etc.)
  - Identify loaded language and emotionality
  - Flag perspective/POV (author's position on topic)

- **Prompt template**:
  - "Analyze this text for: 1) Bias indicators (language, framing, implicit assumptions), 2) Tone (neutral/opinionated/emotional/inflammatory), 3) Author's apparent perspective, 4) Loaded or charged language"

- **Output**:
  - Bias score (scale: neutral → strong bias)
  - Type of bias identified (political, cultural, gender, religious, etc.)
  - Loaded language highlighted in document
  - Author perspective summary
  - Suggestions for neutral rephrasing

- **UI**:
  - Side panel: "Bias & Tone Analysis"
  - Overall bias/tone summary
  - List of identified bias instances with locations
  - Click to highlight biased language in document
  - "Neutral rewrite" button to generate alternative phrasing

##### Summarization & Key Takeaways Pack
- **Functionality**:
  - Multi-level summaries (executive summary, section summaries, key takeaways)
  - Extract questions the document answers
  - Identify knowledge gaps or unanswered questions
  - Generate discussion prompts

- **Prompt template**:
  - "Provide: 1) Executive summary (2-3 sentences), 2) Key takeaways (5 bullet points), 3) Questions answered by this document, 4) Gaps or unanswered questions"

- **Output**:
  - Multi-level summary (choose verbosity)
  - Question list with references to where answered
  - Identified knowledge gaps
  - Related topics for further exploration

- **UI**:
  - Collapsible summary panels
  - Executive summary always visible
  - Expandable sections for detailed summaries
  - Questions + answers linked to source locations

#### 1.2 Insight Pack Management
- **Pack selection UI**:
  - Button in toolbar or menu: "Insights"
  - Popup/modal listing available packs
  - Checkboxes to select multiple packs to run simultaneously
  - "Run" button triggers all selected analyses

- **Custom packs**:
  - Allow users to define custom insight packs (sequence of prompts)
  - Save as reusable templates
  - Share custom packs (export/import)
  - Example: "Academic paper review" = [Claims + Bias + Argument Structure]

- **Execution flow**:
  - Sequential execution of selected packs (avoid overwhelming API)
  - Progress indicator: show which pack is running
  - Results appear as tabs or sections in side panel as they complete
  - Allow early termination if user has enough insight

#### 1.3 Insight Performance & Cost
- **Optimization**:
  - Use cheaper/faster models for straightforward analysis (Define level)
  - Use advanced models for complex reasoning (Claims verification)
  - Batch requests when possible (send multiple paragraphs to single API call)
  - Cache results per document (same document, same insights apply)

- **Cost estimation**:
  - Show estimated tokens/cost before executing
  - Allow user to abort if cost too high
  - Auto-select tier (fast/balanced/quality) based on user preference in settings

- **Async execution**:
  - Run insights in background, user continues reading
  - Notify when insights complete
  - Partial results: show claims as they're extracted, rather than waiting for all

---

## 2. Highlights, Notes, and Saved AI Explanations

### Overview
Enable persistent annotation of documents: user-created highlights, notes, and AI-generated explanations grouped for easy review and export.

### Key Requirements

#### 2.1 Highlight System
- **Highlight creation**:
  - Select text in either pane (source or translation)
  - Click highlight button or press Ctrl+H
  - Choose color: yellow, green, blue, red, pink, purple (customizable)
  - Add optional label/tag (e.g., "important", "verify", "unclear")

- **Highlight types**:
  - Manual highlight: user-initiated
  - AI highlight: generated by insight packs (e.g., claims verification highlights biased language)
  - System highlight: auto-generated (e.g., flagged terms from termbase)

- **Highlight persistence**:
  - Store highlights in IndexedDB (linked to document URL)
  - Sync across sessions (same URL loads with previous highlights)
  - Export highlights (Markdown, HTML with color codes)

- **Highlight UI**:
  - Highlighted text has background color and optional border
  - Hover to show tooltip: color, label, timestamp, note (if attached)
  - Click highlight to expand to full note or details
  - Sidebar: "Highlights" panel listing all highlights with preview
  - Filter by color, label, or date range

#### 2.2 Note System
- **Note creation**:
  - From highlighted text: right-click → "Add note"
  - From anywhere: floating "Add note" button in side panel
  - Notes can be attached to highlights or standalone (linked to location)

- **Note content**:
  - Free-form text
  - Supports basic Markdown (bold, italic, links, code)
  - Tag system for categorization
  - Link to related notes
  - Timestamp and auto-save

- **Note types**:
  - Highlight note: attached to highlight
  - Marginal note: anchored to paragraph/block
  - Standalone note: general reflection on document
  - Citation note: quote + source location + interpretation

- **Note management**:
  - Edit notes inline or in expanded editor
  - Delete notes (soft delete, recoverable for 7 days)
  - Search notes by content
  - Filter by type, tag, date

#### 2.3 Saved AI Explanations
- **Auto-save explanations**:
  - When user runs Explain/Define on selection (Phase 2 feature), result is auto-saved
  - Grouped in "AI Explanations" panel
  - Can be edited, tagged, linked to highlights

- **Explanation linking**:
  - AI explanation linked to original text location
  - Click explanation to jump to source in document
  - Show source highlight when viewing explanation

- **Explanation review**:
  - Panel showing all explanations in document
  - Compare explanations across multiple runs (if re-translated)
  - Rate explanation quality (helpful/unhelpful)
  - Mark as "verified" or "questionable"

#### 2.4 Annotation Review Interface
- **Unified review panel**:
  - Tab-based view: Highlights | Notes | Explanations | All Annotations
  - Timeline view: chronological order of all annotations
  - Grouped view: by location, color, tag, etc.

- **Search and filter**:
  - Full-text search across notes + explanations
  - Filter by: type, tag, color, date range, importance rating
  - Saved filters (e.g., "important notes from this month")

- **Export annotations**:
  - Export as Markdown (with document context)
  - Export as PDF (annotations overlay on original)
  - Export as JSON (structured, for external tools)
  - Export format options: preserve colors, include timestamps, include ratings

#### 2.5 Annotation Sync (Multi-Device - Future)
- **Cloud sync** (Phase 3+):
  - Optional cloud backend to sync annotations across devices
  - E2E encryption for privacy
  - Conflict resolution for simultaneous edits
  - Offline-first: local edits sync when online

---

## 3. Link Cards with Bilingual Summaries

### Overview
For documents that contain links, generate bilingual summary cards that provide context and encourage exploration of related resources without leaving the workbench.

### Key Requirements

#### 3.1 Link Detection and Extraction
- **Link collection**:
  - Parse all hyperlinks from extracted content
  - Store link metadata: URL, anchor text, context (surrounding text)
  - Deduplicate links (same URL mentioned multiple times)
  - Detect link type: news article, research paper, product page, social media, etc.

- **Link metadata**:
  - Original anchor text (from source)
  - URL
  - Surrounding context (2-3 sentences before/after link)
  - Domain/source of link
  - Language of target page (if detectable)

#### 3.2 Link Card Generation
- **Link card content**:
  - Original link context (source language)
  - Bilingual title: auto-extract or AI-generate summary title
  - Bilingual description: 1-2 sentence summary in both source + target language
  - Link thumbnail/preview (if available from og:image)
  - Domain icon
  - "Preview" button (fetch and show linked content)

- **Card generation process**:
  - Fetch linked page (headless browser or API)
  - Extract title + first paragraph/summary
  - Translate title + summary to target language using configured model
  - Cache card (avoid re-fetching same link)
  - Graceful fallback if fetch fails (show URL only)

- **Prompt template for translation**:
  - "Translate this title and description to {target_lang} briefly: Title: [title], Description: [description]. Preserve meaning but adapt for fluent readability."

#### 3.3 Link Card UI
- **Link card panel**:
  - Sidebar or footer section: "Linked Resources" / "References"
  - Cards displayed in grid or list view
  - Each card shows: domain icon, bilingual summary, thumbnail
  - Sort/filter options: by domain, language, date added to document

- **Interactive features**:
  - Hover to see full context (surrounding paragraphs from source)
  - Click "Preview" to load linked page in main translation view
  - Click "Open" to open link in new browser tab
  - Right-click to copy URL or add to reading list
  - Rate card usefulness (for UX improvement)

- **Linked page translation**:
  - When previewing linked page, auto-translate using same settings
  - Maintain history of linked pages explored
  - Quick back button to return to original document

#### 3.4 Reading List Integration
- **Save to reading list**:
  - Each link card has "Save to reading list" button
  - Automatically linked to original document (for context)
  - Reading list stored in browser (or synced if backend available)

- **Reading list management**:
  - Dedicated UI for managing reading list
  - Organize by project/topic
  - Mark as read/unread
  - Archive completed reading
  - Export reading list (Markdown, JSON)

#### 3.5 Link Card Performance
- **Lazy fetching**:
  - Don't fetch all linked pages immediately
  - Fetch on-demand when user scrolls to card or clicks "Preview"
  - Show skeleton while fetching

- **Caching**:
  - Cache fetched link content (title, description, image)
  - Re-use cache for multiple occurrences of same link
  - Configurable cache TTL (default: 7 days)

- **Batch fetching**:
  - Queue link fetch requests to respect rate limits
  - Limit concurrent fetches (e.g., max 3 at a time)

---

## 4. Multi-Model Cross-Check and Refinement (Enhanced Mode)

### Overview
Enable power users to query multiple AI models in parallel, compare responses, and synthesize refined outputs—achieving higher confidence and accuracy through model diversity.

### Key Requirements

#### 4.1 Multi-Model Execution
- **Model selection**:
  - User selects 2–5 models from configured providers
  - Example: GPT-4o, Claude Sonnet, Gemini Pro (if configured)
  - Model compatibility check: filter models supporting target language

- **Parallel execution**:
  - Send same request to all selected models simultaneously
  - Track execution time per model
  - Show results as they arrive (streaming)
  - Timeout model if exceeds threshold (e.g., 30 seconds)

#### 4.2 Multi-Model Translation Comparison
- **Comparison UI**:
  - Side-by-side view of multiple translations (2–5 columns)
  - Color-code differences (red: significant deviation, yellow: minor variation)
  - Highlight consensus phrases (appear in all versions)
  - Show word count + reading time for each version

- **Consensus extraction**:
  - Identify sentences/phrases that appear consistently across models
  - Mark areas of disagreement
  - Suggest synthesized version (merge strong points from each model)

#### 4.3 Translation Refinement & Synthesis
- **Refinement workflow**:
  1. User reviews multi-model translations
  2. Selects best phrases from each version
  3. Or uses "Synthesize" button to auto-merge optimal passages
  4. Edit synthetic version manually
  5. Save as new version

- **Synthesis algorithm**:
  - BLEU/ROUGE scoring to assess translation quality
  - Merge highest-scoring phrases from each model
  - Preserve coherence and flow (post-processing to smooth transitions)
  - Optional: use primary model to refine synthetic version

- **Consensus confidence**:
  - Show confidence score per sentence (% models agreeing)
  - Green (>80% agreement), yellow (50–80%), red (<50%)

#### 4.4 Multi-Model Verification
- **Cross-model verification** for insights:
  - Run insight packs on multiple models (e.g., 2 models assess document bias)
  - Compare results (agreements, disagreements)
  - Highlight areas where models diverge (may indicate ambiguity)
  - Aggregate verdict (consensus across models)

- **Use case example**:
  - User runs "Claims Verification" on GPT and Claude
  - Both agree on claim X being disputed
  - They disagree on claim Y verifiability
  - UI highlights: consensus (X) vs. uncertain (Y)

#### 4.5 Enhanced Mode UI
- **Mode toggle**:
  - Settings: "Enhanced Mode" checkbox (disabled by default)
  - Enables multi-model options in relevant UI (translation, insights, etc.)
  - Warning: Enhanced Mode uses more API calls (higher cost)

- **Comparison panel**:
  - Collapsible section showing model results side-by-side
  - Tabs for Translation | Claims | Consistency | Bias (whatever insights were run)
  - Scoreboard: which model "won" on quality metrics

#### 4.6 Cost Management in Enhanced Mode
- **Cost estimation**:
  - Show total estimated cost before executing multi-model request
  - Break down by model (GPT-4o = $X, Claude = $Y, etc.)
  - Warning if cost exceeds user-set threshold

- **Throttling**:
  - Configurable: only use N models (select cheapest combination)
  - Time-based throttling: restrict enhanced mode to certain hours
  - Fallback to single-model if budget exhausted

---

## 5. Web-Browsing and RAG (Retrieval-Augmented Generation) with Citations

### Overview
For insight packs (especially claims verification), enable AI models to search the web and reference external sources, providing citations for verification results.

### Key Requirements

#### 5.1 Web-Search Integration
- **Search triggers**:
  - Claims verification pack: auto-search uncertain claims
  - User manually requests verification: "Verify this claim" button
  - Explain/Define command: optional web context for unknown terms

- **Search query generation**:
  - For claim: "Generate search query to verify: [claim]"
  - For term: "Search query for defining: [term]"
  - Model generates 1–3 search queries, execute all

- **Search providers**:
  - Primary: Google Custom Search API (requires API key)
  - Fallback: DuckDuckGo API (no key required, limited results)
  - Optional: scholarly search (scholar.google.com, Google Scholar API)
  - Keys are user-provided and stored locally; no server-side key storage

#### 5.2 Result Synthesis with Citations
- **RAG pipeline**:
  1. Generate search queries from claim/term
  2. Fetch top N results (5–10) from search provider
  3. Extract relevant snippets from results
  4. Prompt AI model to synthesize answer using search results
  5. Model provides answer with citations (e.g., "According to [Source 1], ...")

- **Citation format**:
  - In-text citations: [source #] or footnotes
  - Citation list: URL, title, domain, excerpt snippet
  - Link back to source (user can click to visit)

- **Fact-checking mode**:
  - For claims verification: present search results alongside claim
  - Highlight supporting or contradicting evidence
  - Show consensus across sources (if multiple sources verify)

#### 5.3 Search Result Caching
- **Cache search results**:
  - Cache for identical queries (avoid duplicate searches)
  - TTL: 7 days (information changes frequently)
  - Clear cache manually or auto-expire

- **Performance**:
  - Async execution: search happens in background
  - User continues reading while search completes
  - Results appear in panel when ready

#### 5.4 Verification UI
- **Verification panel**:
  - Claim statement with verification badge
  - Search results displayed as expandable list
  - Consensus indicator: "Generally verified", "Disputed", "No evidence found"
  - Color-coded results: green (supports), red (contradicts), gray (neutral)
  - Click result to read full excerpt

- **Citation management**:
  - One-click copy citation (APA, MLA, Chicago format)
  - Add searched sources to bibliography (for note-taking)
  - Export verification results with citations

#### 5.5 Privacy & Rate Limiting
- **Search API rate limits**:
  - Google CSE: 100 queries/day free tier
  - DuckDuckGo: no official limit, but throttle to 1/second
  - Queue searches and notify user if rate limited

- **Privacy**:
  - Searches are traceable to user (if logged into Google/DuckDuckGo)
  - Option to disable web search (use local knowledge only)
  - Clear search history option
  - Search requests go directly to providers; if a backend proxy is used for
    CORS, it must be stateless and avoid persisting queries or keys

#### 5.6 Offline Mode
- **Graceful degradation**:
  - If offline, skip web search
  - Use cached results if available (recent)
  - Show message: "Web search unavailable offline. Using cached data."

---

## 6. Integration of Phase 3 Features

### Overview
How Phase 3 features work together in common workflows.

#### 6.1 Comprehensive Document Review Workflow
1. User translates document (Phase 1)
2. Refines translation with custom prompts (Phase 2)
3. Saves annotations and notes (Phase 3)
4. Runs insight packs: claims verification + bias detection (Phase 3)
5. Web-search uncertain claims, add citations to notes (Phase 3)
6. Compare with alternative model translation (Enhanced Mode)
7. Export final document + annotations + bibliography (Phase 3)

#### 6.2 Research Paper Review Workflow
1. Extract and translate research paper
2. Highlight key claims and methodologies
3. Run insight pack: argument structure + claims verification
4. Web-search citations mentioned in paper
5. Generate reading list from linked references
6. Compare abstract translated by multiple models
7. Export annotated translation for future reference

#### 6.3 News Analysis Workflow
1. Translate news article
2. Run bias & tone detection
3. Extract claims and verify with web search
4. Identify key takeaways
5. Compare article with translations from other sources (link cards)
6. Highlight contradictions and consensus points
7. Save to reading list with personal annotations

---

## Phase 3 Implementation Priority

1. **Must-Have (Phase 3 Core)**:
   - Claims verification pack (extract claims, assess verifiability)
   - Internal consistency check pack (find contradictions)
   - Highlight system (create, color, persist)
   - Note system (create, attach to highlights, search)
   - Saved explanations (from Phase 2 Explain/Define)
   - Link card generation (fetch linked pages, translate summary)
   - Multi-model translation comparison (side-by-side view)

2. **Should-Have** (Polish & Depth):
   - Argument structure pack (map reasoning, identify fallacies)
   - Bias & tone detection pack
   - Summarization & takeaways pack
   - Annotation export (Markdown, PDF, JSON)
   - Web-search integration for claims verification
   - Citation generation (APA, MLA)
   - Enhanced Mode (multi-model verification)

3. **Nice-to-Have** (Future Enhancement):
   - Custom insight packs (user-defined sequences)
   - Reading list management
   - Annotation sync across devices
   - Scholarly search integration
   - Multi-language bias detection
   - Advanced RAG with document embedding

## Phase 3 Success Metrics

- **Insights**:
  - Claims extracted per document: average 5–10
  - User satisfaction with claims verification: >4/5
  - Internal consistency issues detected: average 2–3 per article
  - Adoption rate of insight packs: >40% of users

- **Annotations**:
  - Highlights created per document: avg 3–5
  - Notes saved per document: avg 1–3
  - Annotation export usage: >30% of users export
  - Search annotation latency: <200ms for 1000 annotations

- **Link Cards**:
  - Link cards generated: avg 5–8 per article
  - Link preview usage: >50% of cards clicked
  - Card fetch success rate: >80%
  - Reading list items per user: avg 10–20

- **Multi-Model**:
  - Consensus agreement across 2 models: avg 70–80%
  - User adoption of Enhanced Mode: >20% of users
  - Synthesis quality satisfaction: >4/5
  - Cost per multi-model request: 2–3x single model

- **Web Search**:
  - Verification success rate: >60% of claims searchable
  - Search result relevance: >4/5 user rating
  - Citation accuracy: >95%
  - Search latency: <10 seconds (including synthesis)

- **Overall Phase 3**:
  - Session time increase: +40–60% vs. Phase 1
  - Return user rate: >60%
  - Feature awareness: >50% of users know about Phase 3 capabilities
  - System satisfaction: >4.5/5 stars

---

## Architecture Overview

### Technology Stack

- **Backend:** Python 3.12+ with FastAPI (content fetch, extraction, translation orchestration)
- **Frontend:** Node.js 22+ with SvelteKit and TypeScript (dual-pane UI, block synchronization, settings management)
- **Storage:** Client-side (browser localStorage/IndexedDB) for config and local history
- **APIs:** OpenAI, Anthropic, and extensible for future providers
- **Package Management:** `uv` for Python, npm for frontend
- **Code Quality:**
  - Python: isort, black (72 char), ruff, mypy (strict mode)
  - TypeScript: ESLint, Prettier (72 char)
- **Testing:** pytest + tox (Python), npm test (TypeScript)

### Design Principles

1. **Two-pane reading is primary** — Translation always visible on the right pane. Never replace this with alternative content.

2. **On-demand AI, user-controlled cost** — All AI operations must be explicitly triggered by users. No automatic background AI calls.

3. **BYOK multi-provider** — Users bring their own API keys. Support multiple providers (OpenAI, Anthropic, etc.).

4. **Configurable governance** — Make prompts and terminology configurable per task type for consistency.

5. **All AI outputs are versioned assets** — Save every AI output with full provenance (model, prompt version, referenced blocks) for replay and regeneration.

6. **Compliance-first** — Never bypass authentication, anti-bot mechanisms, or paywalls automatically. All sessions are user-driven.

### Core Abstractions

- **Document:** Extracted and cleaned content from a URL
- **Block:** Normalized content unit (paragraph, heading, list, quote, code, image)
- **Translation:** Block-mapped translation with version tracking
- **AI Job:** Any model request with prompt version and metadata
- **Artifact:** Saved output from an AI Job (note, link card, verification, etc.)

### Reference Documentation

- **API Reference:** [API.md](API.md)
- **Architecture Details:** [../ARCHITECTURE.md](../ARCHITECTURE.md)
- **Contributing:** [../CONTRIBUTING.md](../CONTRIBUTING.md)

---

*This document was previously named `detailed-feature-specifications.md`.*
