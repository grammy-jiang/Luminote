---
applyTo: frontend/src/components/**/*.svelte
excludeAgent: []
---

# Frontend Components Instructions

This instruction file applies to all Svelte component files in
`frontend/src/components/` - the reusable UI components layer.

## Component Architecture

### Single-File Components

Use Svelte's single-file component structure:

```svelte
<script lang="ts">
  // Component logic, imports, props
  import { onMount } from 'svelte';
  import type { TranslationResult } from '$lib/types';

  // Props
  export let content: string;
  export let language: string;

  // State
  let isLoading = false;

  // Lifecycle
  onMount(() => {
    console.log('Component mounted');
  });
</script>

<!-- Markup -->
<div class="component-wrapper">
  <h2>{language}</h2>
  <p>{content}</p>
</div>

<!-- Scoped styles -->
<style>
  .component-wrapper {
    padding: 1rem;
  }
</style>
```

### Component Naming

- Use PascalCase for component files: `TranslationPane.svelte`,
  `ContentBlock.svelte`
- Component names should be descriptive and specific
- Avoid generic names like `Container.svelte`, `Item.svelte`

## Core UX Principles

### Two-Pane Reading (CRITICAL)

**Never replace the translation pane with alternative content.**

This is Luminote's fundamental UX principle:

```svelte
<!-- ✅ Good - translation always visible on right -->
<div class="dual-pane-layout">
  <div class="source-pane">
    <slot name="source" />
  </div>
  <div class="translation-pane">
    <slot name="translation" />
  </div>
</div>

<!-- ❌ Bad - translation can be hidden/replaced -->
<div class="pane">
  {#if showTranslation}
    <TranslationPane />
  {:else}
    <SettingsPanel />
  {/if}
</div>
```

### No Automatic AI Calls

All AI operations must be **explicitly triggered by the user**:

```svelte
<script lang="ts">
  import { translateContent } from '$lib/api';

  // ✅ Good - user clicks button
  async function handleTranslate() {
    const result = await translateContent(content, targetLanguage, apiKey);
  }

  // ❌ Bad - automatic on mount
  onMount(async () => {
    await translateContent(...); // Never auto-trigger AI!
  });
</script>

<button on:click={handleTranslate}>
  Translate
</button>
```

## State Management

Use Svelte stores for shared state (defined in `frontend/src/stores/`):

```svelte
<script lang="ts">
  import { translationStore } from '$lib/stores/translation';

  // Subscribe to store
  $: currentTranslation = $translationStore.current;

  // Update store
  function updateTranslation(newText: string) {
    translationStore.update(state => ({
      ...state,
      current: newText,
    }));
  }
</script>
```

See
[ADR-005: Frontend State Management](../../docs/adr/005-frontend-state-management.md)
for patterns.

## Props and TypeScript

### Type-Safe Props

Always use TypeScript for prop definitions:

```svelte
<script lang="ts">
  import type { ContentBlock, TranslationStatus } from '$lib/types';

  // ✅ Good - typed props
  export let blocks: ContentBlock[];
  export let status: TranslationStatus = 'idle';
  export let onTranslate: (blockId: string) => Promise<void>;

  // ❌ Bad - no types
  export let blocks;
  export let status;
  export let onTranslate;
</script>
```

### Optional Props

```svelte
<script lang="ts">
  // Optional with default
  export let maxHeight: number = 500;

  // Optional without default (undefined if not provided)
  export let customClass: string | undefined = undefined;
</script>
```

## Event Handling

Use Svelte's event forwarding and custom events:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{
    translate: { blockId: string; language: string };
    error: { message: string };
  }>();

  function handleClick() {
    dispatch('translate', {
      blockId: '123',
      language: 'es',
    });
  }
</script>

<button on:click={handleClick}>
  Translate
</button>
```

**Parent component:**

```svelte
<TranslationButton
  on:translate={handleTranslateEvent}
  on:error={handleErrorEvent}
/>
```

## Styling

### Tailwind CSS

Use Tailwind utility classes:

```svelte
<div class="flex flex-col gap-4 p-4 bg-white rounded-lg shadow-md">
  <h2 class="text-xl font-bold text-gray-800">
    Title
  </h2>
  <p class="text-gray-600">
    Content
  </p>
</div>
```

### Scoped Styles

For component-specific styles, use the `<style>` block:

```svelte
<style>
  /* Scoped to this component only */
  .custom-component {
    /* Custom styles that Tailwind doesn't cover */
    writing-mode: vertical-rl;
  }
</style>
```

### Responsive Design

Use Tailwind's responsive prefixes:

```svelte
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
  <!-- Single column on mobile, two columns on tablet+ -->
</div>
```

## API Integration

### Never Expose API Keys

API keys must **never** reach the frontend:

```svelte
<script lang="ts">
  // ❌ Bad - API key in frontend
  const apiKey = 'sk-1234567890';
  const result = await fetch('https://api.openai.com/...', {
    headers: { 'Authorization': `Bearer ${apiKey}` }
  });

  // ✅ Good - backend handles API keys
  const result = await fetch('/api/v1/translations', {
    method: 'POST',
    body: JSON.stringify({
      content: text,
      targetLanguage: 'es',
      apiKey: userProvidedKey,  // User's key, sent to backend, not stored
    }),
  });
</script>
```

### Error Handling

Display user-friendly error messages:

```svelte
<script lang="ts">
  let error: string | null = null;

  async function handleTranslate() {
    try {
      error = null;
      const response = await fetch('/api/v1/translations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        error = errorData.message || 'Translation failed';
        return;
      }

      const result = await response.json();
      // Handle success
    } catch (err) {
      error = 'Network error. Please check your connection.';
    }
  }
</script>

{#if error}
  <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
    {error}
  </div>
{/if}
```

## Testing Components

Use Vitest + @testing-library/svelte:

```typescript
import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import TranslationButton from './TranslationButton.svelte';

describe('TranslationButton', () => {
  it('renders with correct text', () => {
    const { getByText } = render(TranslationButton, {
      props: { label: 'Translate' },
    });

    expect(getByText('Translate')).toBeInTheDocument();
  });

  it('emits translate event on click', async () => {
    const { component, getByRole } = render(TranslationButton);

    let eventFired = false;
    component.$on('translate', () => {
      eventFired = true;
    });

    const button = getByRole('button');
    await fireEvent.click(button);

    expect(eventFired).toBe(true);
  });

  it('shows loading state', () => {
    const { getByRole } = render(TranslationButton, {
      props: { isLoading: true },
    });

    const button = getByRole('button');
    expect(button).toBeDisabled();
  });
});
```

### Test Coverage

Components should have **≥85% test coverage**:

```bash
cd frontend
npm run test:coverage
```

## Accessibility

### Semantic HTML

Use semantic elements:

```svelte
<!-- ✅ Good - semantic -->
<nav>
  <ul>
    <li><a href="/">Home</a></li>
  </ul>
</nav>

<!-- ❌ Bad - divs everywhere -->
<div class="nav">
  <div class="list">
    <div class="item">
      <div class="link">Home</div>
    </div>
  </div>
</div>
```

### ARIA Labels

Add ARIA labels for screen readers:

```svelte
<button
  aria-label="Translate to Spanish"
  on:click={handleTranslate}
>
  <TranslateIcon />
</button>

<div role="status" aria-live="polite">
  {#if isLoading}
    Translating...
  {/if}
</div>
```

### Keyboard Navigation

Ensure keyboard accessibility:

```svelte
<div
  role="button"
  tabindex="0"
  on:click={handleClick}
  on:keydown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Click me
</div>
```

## Performance

### Lazy Loading

Use dynamic imports for large components:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';

  let HeavyComponent;

  onMount(async () => {
    const module = await import('./HeavyComponent.svelte');
    HeavyComponent = module.default;
  });
</script>

{#if HeavyComponent}
  <svelte:component this={HeavyComponent} />
{/if}
```

### Virtual Scrolling

For long lists, use virtual scrolling:

```svelte
<script lang="ts">
  import { VirtualList } from 'svelte-virtual-scroll-list';

  export let items: Array<any>;
</script>

<VirtualList {items} let:item>
  <div class="item">
    {item.text}
  </div>
</VirtualList>
```

## Code Quality

### Formatting

Use ESLint and Prettier:

```bash
cd frontend

# Run linting
npm run lint

# Run formatting
npm run format

# Type checking
npm run type-check
```

### Before Committing

```bash
cd frontend

# Format
npm run format

# Lint
npm run lint

# Type check
npm run type-check

# Test
npm test

# Build check
npm run build
```

## What NOT to Do

❌ **Never:**

- Replace the translation pane with alternative content
- Trigger AI calls automatically (always require user action)
- Store or log API keys in frontend code
- Use `any` type in TypeScript
- Skip accessibility attributes
- Create deeply nested component hierarchies (keep it flat)
- Mutate props directly
- Use global CSS that could leak to other components

## Common Patterns

### Loading States

```svelte
<script lang="ts">
  let isLoading = false;
  let data = null;
  let error = null;

  async function loadData() {
    isLoading = true;
    error = null;

    try {
      const response = await fetch('/api/data');
      data = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      isLoading = false;
    }
  }
</script>

{#if isLoading}
  <div class="spinner">Loading...</div>
{:else if error}
  <div class="error">{error}</div>
{:else if data}
  <div class="content">{data.text}</div>
{:else}
  <button on:click={loadData}>Load Data</button>
{/if}
```

## References

- [ADR-005: Frontend State Management](../../docs/adr/005-frontend-state-management.md)
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Two-pane principle
- [AGENTS.md](../../AGENTS.md) - Frontend code standards
