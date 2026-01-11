# ConfigPanel Component Usage Guide

## Overview

The `ConfigPanel` component provides a complete UI for configuring Luminote's AI
translation settings. It includes provider selection, model configuration, API
key management, and connection testing.

## Features

- **Provider Selection**: Choose between OpenAI and Anthropic
- **Dynamic Model Selection**: Model options update based on selected provider
- **Secure API Key Input**: Password-protected field, stored only in memory
- **Language Selection**: Support for 12 common languages with ISO 639-1 codes
- **Connection Testing**: Validate configuration before saving
- **Form Validation**: Real-time validation with accessible error messages
- **Visual Feedback**: Loading, success, and error states
- **Full Accessibility**: ARIA labels, roles, and keyboard navigation

## Basic Usage

```svelte
<script lang="ts">
	import ConfigPanel from '$lib/components/ConfigPanel.svelte';
	import { validateConfig } from '$lib/api/config';
	import type { ConfigState } from '$lib/stores/config';

	async function handleTestConnection(config: ConfigState) {
		try {
			// Call backend validation endpoint using the API wrapper
			const result = await validateConfig({
				provider: config.provider,
				model: config.model,
				api_key: config.api_key
			});

			return {
				valid: result.data.valid,
				message: result.data.valid
					? `Connected successfully to ${config.provider}`
					: 'Connection failed'
			};
		} catch (error) {
			return {
				valid: false,
				message: error instanceof Error ? error.message : 'Connection failed'
			};
		}
	}

	function handleSave() {
		console.log('Configuration saved');
		// Optionally navigate away or show additional feedback
	}

	function handleReset() {
		console.log('Configuration reset to defaults');
	}
</script>

<ConfigPanel onTestConnection={handleTestConnection} onSave={handleSave} onReset={handleReset} />
```

## Props

| Prop               | Type                                                                    | Required | Description                              |
| ------------------ | ----------------------------------------------------------------------- | -------- | ---------------------------------------- |
| `onTestConnection` | `(config: ConfigState) => Promise<{ valid: boolean; message: string }>` | No       | Async handler for testing API connection |
| `onSave`           | `() => void`                                                            | No       | Callback invoked after successful save   |
| `onReset`          | `() => void`                                                            | No       | Callback invoked after reset             |

## Integration with Config Store

The component automatically reads from and writes to the `configStore`:

```svelte
<script lang="ts">
	import { configStore } from '$lib/stores/config';
	import ConfigPanel from '$lib/components/ConfigPanel.svelte';

	// Access current config
	$: currentProvider = $configStore.provider;
	$: currentModel = $configStore.model;

	// The ConfigPanel will automatically update the store on save
</script>

<div>
	<p>Current Provider: {currentProvider}</p>
	<p>Current Model: {currentModel}</p>

	<ConfigPanel />
</div>
```

## Accessibility

The component follows WCAG 2.1 AA guidelines:

- All form fields have proper labels and ARIA attributes
- Required fields are marked visually and with `aria-required`
- Validation errors are announced with `role="alert"`
- Status messages use `aria-live="polite"`
- Full keyboard navigation support
- Error messages are linked to inputs via `aria-describedby`

## Styling

The component uses scoped CSS with a clean, modern design:

- Responsive layout (max-width: 500px)
- Clear visual hierarchy
- Accessible color contrast
- Focus indicators for keyboard navigation
- Consistent spacing and typography

To customize styling, wrap in a container with your own classes or use CSS
custom properties.

## Provider-Specific Models

The component automatically updates available models when the provider changes:

**OpenAI Models:**

- gpt-4
- gpt-4-turbo
- gpt-3.5-turbo

**Anthropic Models:**

- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307

## Supported Languages

The component includes 12 common languages with ISO 639-1 codes:

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Arabic (ar)
- Hindi (hi)

## Form Validation

The component validates:

1. **Provider**: Must be selected (always valid due to dropdown)
1. **Model**: Must be a non-empty string
1. **Target Language**: Must be a valid 2-letter ISO 639-1 code
1. **API Key**: Must be non-empty

Validation errors are displayed below each field and announced to screen
readers.

## Testing

The component includes comprehensive unit tests (42 tests, 100% statement
coverage):

```bash
npm run test -- ConfigPanel.test.ts
```

Tests cover:

- All form interactions
- Provider/model switching
- Validation logic
- Connection testing
- Save/reset functionality
- Accessibility features
- Error handling

## Security

- API keys are **never persisted** to localStorage
- API keys are stored only in memory during the session
- Password-type input prevents shoulder surfing
- Clear notice that keys are not stored

## Example: Full Integration

```svelte
<script lang="ts">
	import ConfigPanel from '$lib/components/ConfigPanel.svelte';
	import { validateConfig } from '$lib/api/config';
	import { goto } from '$app/navigation';
	import type { ConfigState } from '$lib/stores/config';

	let showPanel = true;

	async function testConnection(config: ConfigState) {
		try {
			const result = await validateConfig({
				provider: config.provider,
				model: config.model,
				api_key: config.api_key
			});

			return {
				valid: result.data.valid,
				message: result.data.valid
					? `Successfully connected to ${config.provider}`
					: 'Invalid API key or configuration'
			};
		} catch (error) {
			return {
				valid: false,
				message: error instanceof Error ? error.message : 'Network error'
			};
		}
	}

	function handleSave() {
		// Optionally navigate to main app
		showPanel = false;
		goto('/translate');
	}

	function handleReset() {
		// Show confirmation
		if (confirm('Are you sure you want to reset all settings?')) {
			console.log('Configuration reset');
		}
	}
</script>

{#if showPanel}
	<div class="config-container">
		<h1>Settings</h1>
		<ConfigPanel onTestConnection={testConnection} onSave={handleSave} onReset={handleReset} />
	</div>
{/if}

<style>
	.config-container {
		max-width: 600px;
		margin: 2rem auto;
		padding: 1rem;
	}
</style>
```
