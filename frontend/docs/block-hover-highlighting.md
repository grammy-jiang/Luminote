# Block-Level Hover Highlighting Feature

## Overview

This document describes the implementation of the block-level hover highlighting feature for Luminote's two-pane reading interface.

## Feature Description

When users hover over content blocks in either the source or translation pane, the corresponding block in the other pane is automatically highlighted. This provides visual feedback to help users understand the block-to-block mapping between source and translated content.

## Implementation Details

### Components Modified

#### 1. SourcePane.svelte
- **Added Props:**
  - `highlightedBlockId: string | null` - ID of the block to highlight
  
- **Added Events:**
  - `blockHover` - Emitted when mouse enters a block or block receives focus
  - `blockLeave` - Emitted when mouse leaves a block or block loses focus

- **Event Handlers:**
  - `handleBlockMouseEnter(blockId)` - Debounced by 50ms to prevent flicker
  - `handleBlockMouseLeave(blockId)` - Clears pending hover timeout
  - `handleBlockFocus(blockId)` - Immediate, not debounced
  - `handleBlockBlur(blockId)` - Immediate

- **DOM Changes:**
  - All block elements now have `tabindex="0"` for keyboard navigation
  - All block elements have `block-hoverable` class for cursor styling
  - Highlighted blocks receive `block-highlighted` class

#### 2. TranslationPane.svelte
- Same changes as SourcePane, with identical API and behavior

#### 3. DualPaneLayout.svelte
- **Added State:**
  - `hoveredBlockId: string | null` - Tracks currently hovered block

- **Event Coordination:**
  - Listens to `blockHover` and `blockLeave` events from both panes
  - Updates `hoveredBlockId` when blocks are hovered
  - Passes `hoveredBlockId` to both panes via slot props
  - Provides bidirectional highlighting (source ↔ translation)

### Styling

#### Highlight Styles
```css
.block-highlighted {
    background-color: #fef3c7;      /* Light amber/yellow */
    border-left: 3px solid #f59e0b; /* Amber border */
    padding-left: 0.5rem;
    transition: background-color 0.2s ease, border-left 0.2s ease;
    outline: 2px solid #f59e0b;
    outline-offset: 2px;
}
```

#### Focus Styles
```css
[tabindex='0']:focus {
    outline: 2px solid #3b82f6; /* Blue for focus */
    outline-offset: 2px;
}

.block-highlighted:focus {
    outline: 2px solid #f59e0b; /* Amber when both highlighted and focused */
}
```

#### Cursor
```css
.block-hoverable {
    cursor: pointer;
}
```

### Accessibility Features

1. **Keyboard Navigation:**
   - All blocks are focusable with `tabindex="0"`
   - Tab key moves focus between blocks
   - Focus triggers highlighting immediately (no debounce)

2. **Visual Indicators:**
   - Uses both background color AND border (not color alone)
   - Distinct focus outline (blue) vs hover highlight (amber)
   - Smooth transitions for visual comfort

3. **ARIA Attributes:**
   - Code blocks have `aria-label` describing language
   - All blocks maintain semantic HTML structure

4. **Svelte Accessibility Warnings:**
   - Added `<!-- svelte-ignore a11y-no-noninteractive-tabindex -->` where intentionally making non-interactive elements focusable for this feature

### Performance Optimizations

1. **Debouncing:**
   - Mouse hover events debounced by 50ms to prevent flicker
   - Keyboard focus events NOT debounced for immediate feedback

2. **Minimal DOM Operations:**
   - Only CSS classes toggle, no DOM manipulation
   - Transitions handled by CSS, not JavaScript

3. **Tested with Large Documents:**
   - Validated with 150+ blocks
   - Renders in <500ms
   - No performance degradation observed

### Debounce Logic

```typescript
let hoverTimeout: ReturnType<typeof setTimeout> | null = null;

function handleBlockMouseEnter(blockId: string) {
    if (hoverTimeout) {
        clearTimeout(hoverTimeout);
    }
    hoverTimeout = setTimeout(() => {
        dispatch('blockHover', { blockId });
    }, 50);
}

function handleBlockMouseLeave(blockId: string) {
    if (hoverTimeout) {
        clearTimeout(hoverTimeout);
        hoverTimeout = null;
    }
    dispatch('blockLeave', { blockId });
}
```

**Rationale:**
- Prevents rapid-fire events when moving mouse quickly
- Clears pending timeout if mouse leaves before debounce completes
- Keyboard focus bypasses debounce for immediate response

### Event Flow

```
User hovers over block in SourcePane
    ↓
mouseenter event (debounced 50ms)
    ↓
SourcePane emits 'blockHover' with blockId
    ↓
DualPaneLayout receives event
    ↓
DualPaneLayout updates hoveredBlockId state
    ↓
DualPaneLayout passes hoveredBlockId to both panes
    ↓
TranslationPane receives highlightedBlockId prop
    ↓
Block with matching ID gets 'block-highlighted' class
    ↓
CSS transitions apply visual highlight
```

## Usage Example

```svelte
<script>
    import DualPaneLayout from './DualPaneLayout.svelte';
    import SourcePane from './SourcePane.svelte';
    import TranslationPane from './TranslationPane.svelte';
    
    let sourceBlocks = [...];
    let translationBlocks = [...];
</script>

<DualPaneLayout>
    <div slot="left">
        <SourcePane blocks={sourceBlocks} />
    </div>
    
    <div slot="right">
        <TranslationPane blocks={translationBlocks} />
    </div>
</DualPaneLayout>
```

**Note:** The hover coordination happens automatically within DualPaneLayout. No additional configuration needed.

## Testing

### Test Coverage

- **17 new tests** in `BlockHoverHighlight.test.ts`
- **All 265 tests passing** (including existing tests)
- **Test categories:**
  - Hover event emission and debouncing
  - Keyboard focus event handling
  - Highlight class application
  - Accessibility verification
  - Performance validation

### Key Test Cases

1. **Hover Events:**
   - Emits `blockHover` after 50ms debounce
   - Emits `blockLeave` immediately
   - Cancels pending hover if mouse leaves quickly

2. **Keyboard Events:**
   - Focus emits `blockHover` immediately
   - Blur emits `blockLeave` immediately
   - No debounce for keyboard events

3. **Styling:**
   - Applies `.block-highlighted` when `highlightedBlockId` matches
   - Works for all block types (paragraph, heading, code, list, quote, image)
   - Removes highlight when `highlightedBlockId` changes to null

4. **Accessibility:**
   - All blocks have `tabindex="0"`
   - All blocks have `.block-hoverable` class
   - Keyboard focus works identically to mouse hover

5. **Performance:**
   - Renders 150 blocks in <500ms
   - Debouncing prevents multiple events from rapid mouse movement

### Running Tests

```bash
cd frontend

# Run hover highlight tests
npm test -- src/lib/components/BlockHoverHighlight.test.ts

# Run all tests
npm test

# Run with coverage
npm run test:coverage
```

## Browser Compatibility

- **Chrome/Edge:** Fully supported
- **Firefox:** Fully supported  
- **Safari:** Fully supported
- **Mobile:** Touch events not implemented (hover-only feature)

## Future Enhancements

Potential improvements for future iterations:

1. **Touch Support:**
   - Add tap-and-hold for mobile highlighting
   - Consider alternative interaction for touch devices

2. **Scroll Synchronization:**
   - Option to auto-scroll opposite pane to highlighted block
   - "Sticky highlight" that persists on click

3. **Customization:**
   - User-selectable highlight colors
   - Configurable debounce delay
   - Toggle hover feature on/off

4. **Analytics:**
   - Track which blocks users hover over most
   - Use data to improve translation quality

## References

- **Issue:** #1.12 - Add Block-Level Hover Highlighting
- **ADR:** None (UX enhancement, no architectural decisions)
- **Dependencies:** Issues #1.8 and #1.9 (block rendering)
- **Blocks:** Issue #1.13 (block click navigation)
