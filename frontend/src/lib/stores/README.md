# Configuration Store

The configuration store manages user settings with localStorage persistence,
following ADR-003 (Client-Side Storage Strategy) and ADR-005 (Frontend State
Management).

## Features

- ✅ Type-safe configuration interface
- ✅ localStorage persistence (excluding API key)
- ✅ API key stored in memory only (security)
- ✅ Validation on all set operations
- ✅ SSR-compatible
- ✅ Change notifications via Svelte reactivity

## Configuration Schema

```typescript
interface ConfigState {
	provider: 'openai' | 'anthropic';
	model: string;
	target_language: string; // ISO 639-1 format (e.g., 'en', 'es')
	api_key: string; // Memory-only, never persisted
}
```

## Usage

### Basic Usage

```svelte
<script lang="ts">
	import { configStore } from '$lib/stores';

	// Auto-subscribe with $ prefix
	$: provider = $configStore.provider;
	$: model = $configStore.model;
	$: targetLanguage = $configStore.target_language;
	$: apiKey = $configStore.api_key;
</script>

<div>
	<p>Provider: {provider}</p>
	<p>Model: {model}</p>
	<p>Target Language: {targetLanguage}</p>
</div>
```

### Setting Configuration Values

```typescript
import { configStore } from '$lib/stores';

// Set provider (validated: must be 'openai' or 'anthropic')
configStore.setProvider('anthropic');

// Set model (validated: must be non-empty string)
configStore.setModel('claude-3-opus');

// Set target language (validated: must be ISO 639-1 format - 2 lowercase letters)
configStore.setTargetLanguage('es');

// Set API key (not validated, never persisted)
configStore.setAPIKey('sk-your-api-key-here');
```

### Reset to Defaults

```typescript
import { configStore } from '$lib/stores';

// Reset all configuration to default values
configStore.reset();

// Default values:
// - provider: 'openai'
// - model: 'gpt-4'
// - target_language: 'en'
// - api_key: ''
```

### Subscribe to Changes

```typescript
import { configStore } from '$lib/stores';

const unsubscribe = configStore.subscribe((config) => {
	console.log('Config changed:', config);
});

// Remember to unsubscribe when done
unsubscribe();
```

### Using set() or update()

```typescript
import { configStore } from '$lib/stores';

// Set entire config at once (all fields validated)
configStore.set({
	provider: 'anthropic',
	model: 'claude-3-opus',
	target_language: 'fr',
	api_key: 'sk-test'
});

// Update specific fields
configStore.update((config) => ({
	...config,
	model: 'gpt-4-turbo'
}));
```

## Validation Rules

### Provider

- Must be `'openai'` or `'anthropic'`
- Throws error if invalid

### Model

- Must be non-empty string
- Throws error if empty or whitespace-only

### Target Language

- Must be ISO 639-1 format: 2 lowercase letters (e.g., `'en'`, `'es'`, `'fr'`)
- Throws error if invalid format

### API Key

- No validation (user-provided)
- Never persisted to localStorage (security requirement)

## Examples

### Configuration Panel Component

```svelte
<script lang="ts">
	import { configStore } from '$lib/stores';

	function handleProviderChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		configStore.setProvider(target.value as 'openai' | 'anthropic');
	}

	function handleModelChange(event: Event) {
		const target = event.target as HTMLInputElement;
		configStore.setModel(target.value);
	}

	function handleLanguageChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		configStore.setTargetLanguage(target.value);
	}

	function handleApiKeyChange(event: Event) {
		const target = event.target as HTMLInputElement;
		configStore.setAPIKey(target.value);
	}
</script>

<div class="config-panel">
	<label>
		Provider:
		<select value={$configStore.provider} on:change={handleProviderChange}>
			<option value="openai">OpenAI</option>
			<option value="anthropic">Anthropic</option>
		</select>
	</label>

	<label>
		Model:
		<input type="text" value={$configStore.model} on:input={handleModelChange} />
	</label>

	<label>
		Target Language:
		<select value={$configStore.target_language} on:change={handleLanguageChange}>
			<option value="en">English</option>
			<option value="es">Spanish</option>
			<option value="fr">French</option>
			<option value="de">German</option>
			<option value="ja">Japanese</option>
			<option value="zh">Chinese</option>
		</select>
	</label>

	<label>
		API Key:
		<input
			type="password"
			value={$configStore.api_key}
			on:input={handleApiKeyChange}
			placeholder="sk-..."
		/>
		<small>API key is stored in memory only and never saved to disk.</small>
	</label>

	<button on:click={() => configStore.reset()}> Reset to Defaults </button>
</div>
```

### Error Handling

```typescript
import { configStore } from '$lib/stores';

try {
	configStore.setProvider('invalid' as any);
} catch (error) {
	console.error('Invalid provider:', error.message);
	// Output: "Invalid provider: invalid. Must be 'openai' or 'anthropic'."
}

try {
	configStore.setTargetLanguage('eng'); // Invalid: 3 letters
} catch (error) {
	console.error('Invalid language code:', error.message);
	// Output: "Invalid target_language: eng. Must be ISO 639-1 format (e.g., 'en', 'es')."
}
```

## Security

**CRITICAL:** The API key is **NEVER** persisted to localStorage. It exists only
in memory.

```typescript
// ✅ Safe: API key is only in memory
configStore.setAPIKey('sk-secret-key');

// ✅ Safe: API key is NOT in localStorage
const stored = localStorage.getItem('luminote_config');
console.log(JSON.parse(stored));
// Output: { provider: 'openai', model: 'gpt-4', target_language: 'en' }
// Note: No api_key field

// ✅ Safe: API key is cleared on page reload
// User must re-enter API key each session
```

## Storage

Configuration is automatically persisted to localStorage under the key
`luminote_config`.

**Persisted fields:**

- `provider`
- `model`
- `target_language`

**NOT persisted:**

- `api_key` (security requirement)

## Testing

See `config.test.ts` for comprehensive test examples.

```bash
# Run config store tests
npm test -- config.test.ts

# Run with coverage
npm run test:coverage -- config.test.ts
```

## References

- [ADR-003: Client-Side Storage Strategy](../../../docs/adr/003-client-side-storage-strategy.md)
- [ADR-005: Frontend State Management](../../../docs/adr/005-frontend-state-management.md)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
