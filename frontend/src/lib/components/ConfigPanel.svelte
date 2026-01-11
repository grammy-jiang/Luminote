<script lang="ts">
	/**
	 * Configuration Panel Component
	 *
	 * UI component for users to configure provider, model, target language, and API key.
	 * Features:
	 * - Provider dropdown (OpenAI, Anthropic)
	 * - Model selector (dynamic based on provider)
	 * - API key input (password field)
	 * - Target language selector (ISO 639-1 codes)
	 * - Test connection button
	 * - Save and reset buttons
	 * - Visual feedback (loading, success, error)
	 * - Form validation
	 * - Accessible labels
	 */

	import { configStore } from '$lib/stores/config';
	import type { ConfigState } from '$lib/stores/config';
	import Button from './Button.svelte';

	// Props
	export let onSave: (() => void) | undefined = undefined;
	export let onReset: (() => void) | undefined = undefined;
	export let onTestConnection:
		| ((config: ConfigState) => Promise<{ valid: boolean; message: string }>)
		| undefined = undefined;

	// Model options per provider
	const MODELS_BY_PROVIDER: Record<string, string[]> = {
		openai: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
		anthropic: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
	};

	// Common language codes (ISO 639-1)
	const LANGUAGES = [
		{ code: 'en', name: 'English' },
		{ code: 'es', name: 'Spanish' },
		{ code: 'fr', name: 'French' },
		{ code: 'de', name: 'German' },
		{ code: 'it', name: 'Italian' },
		{ code: 'pt', name: 'Portuguese' },
		{ code: 'ru', name: 'Russian' },
		{ code: 'ja', name: 'Japanese' },
		{ code: 'ko', name: 'Korean' },
		{ code: 'zh', name: 'Chinese' },
		{ code: 'ar', name: 'Arabic' },
		{ code: 'hi', name: 'Hindi' }
	];

	// Local state for form
	let provider = $configStore.provider;
	let model = $configStore.model;
	let targetLanguage = $configStore.target_language;
	let apiKey = $configStore.api_key;

	// UI state
	let isTestingConnection = false;
	let isSaving = false;
	let testResult: { type: 'success' | 'error'; message: string } | null = null;
	let saveResult: { type: 'success' | 'error'; message: string } | null = null;

	// Form validation
	let errors: {
		provider?: string;
		model?: string;
		targetLanguage?: string;
		apiKey?: string;
	} = {};

	// Update model list when provider changes
	$: availableModels = MODELS_BY_PROVIDER[provider] || [];

	// Validate and update model when provider changes
	$: {
		if (provider && availableModels.length > 0 && !availableModels.includes(model)) {
			model = availableModels[0];
		}
	}

	/**
	 * Validate form fields
	 */
	function validateForm(): boolean {
		errors = {};
		let isValid = true;

		if (!provider) {
			errors.provider = 'Provider is required';
			isValid = false;
		}

		if (!model || model.trim().length === 0) {
			errors.model = 'Model is required';
			isValid = false;
		}

		if (!targetLanguage || !/^[a-z]{2}$/.test(targetLanguage)) {
			errors.targetLanguage = 'Valid language code is required (e.g., en, es, fr)';
			isValid = false;
		}

		if (!apiKey || apiKey.trim().length === 0) {
			errors.apiKey = 'API key is required';
			isValid = false;
		}

		return isValid;
	}

	/**
	 * Handle provider change
	 */
	function handleProviderChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		provider = target.value as 'openai' | 'anthropic';
		// Clear test/save results when config changes
		testResult = null;
		saveResult = null;
	}

	/**
	 * Handle model change
	 */
	function handleModelChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		model = target.value;
		testResult = null;
		saveResult = null;
	}

	/**
	 * Handle language change
	 */
	function handleLanguageChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		targetLanguage = target.value;
		testResult = null;
		saveResult = null;
	}

	/**
	 * Handle API key change
	 */
	function handleApiKeyChange(event: Event) {
		const target = event.target as HTMLInputElement;
		apiKey = target.value;
		testResult = null;
		saveResult = null;
	}

	/**
	 * Test connection to provider
	 */
	async function handleTestConnection() {
		// Clear previous results
		testResult = null;
		saveResult = null;

		// Validate form
		if (!validateForm()) {
			testResult = {
				type: 'error',
				message: 'Please fix validation errors before testing connection'
			};
			return;
		}

		if (!onTestConnection) {
			testResult = {
				type: 'error',
				message: 'Test connection handler not configured'
			};
			return;
		}

		isTestingConnection = true;

		try {
			const config: ConfigState = {
				provider,
				model,
				target_language: targetLanguage,
				api_key: apiKey
			};

			const result = await onTestConnection(config);

			if (result.valid) {
				testResult = {
					type: 'success',
					message: result.message || 'Connection successful'
				};
			} else {
				testResult = {
					type: 'error',
					message: result.message || 'Connection failed'
				};
			}
		} catch (error) {
			testResult = {
				type: 'error',
				message: error instanceof Error ? error.message : 'Connection test failed'
			};
		} finally {
			isTestingConnection = false;
		}
	}

	/**
	 * Save configuration
	 */
	function handleSave() {
		// Clear previous results
		testResult = null;
		saveResult = null;

		// Validate form
		if (!validateForm()) {
			saveResult = {
				type: 'error',
				message: 'Please fix validation errors before saving'
			};
			return;
		}

		isSaving = true;

		try {
			// Update store
			configStore.set({
				provider,
				model,
				target_language: targetLanguage,
				api_key: apiKey
			});

			saveResult = {
				type: 'success',
				message: 'Configuration saved successfully'
			};

			// Call optional callback
			if (onSave) {
				onSave();
			}
		} catch (error) {
			saveResult = {
				type: 'error',
				message: error instanceof Error ? error.message : 'Failed to save configuration'
			};
		} finally {
			isSaving = false;
		}
	}

	/**
	 * Reset configuration to defaults
	 */
	function handleReset() {
		// Clear results
		testResult = null;
		saveResult = null;
		errors = {};

		// Reset store to defaults
		configStore.reset();

		// Reset local form state
		provider = $configStore.provider;
		model = $configStore.model;
		targetLanguage = $configStore.target_language;
		apiKey = $configStore.api_key;

		// Call optional callback
		if (onReset) {
			onReset();
		}
	}
</script>

<div class="config-panel" role="form" aria-label="Configuration panel">
	<h2 class="panel-title">Configuration</h2>

	<!-- Provider Selection -->
	<div class="form-group">
		<label for="provider-select" class="form-label">
			Provider
			<span class="required" aria-label="required">*</span>
		</label>
		<select
			id="provider-select"
			class="form-select"
			class:error={errors.provider}
			value={provider}
			on:change={handleProviderChange}
			aria-required="true"
			aria-invalid={!!errors.provider}
			aria-describedby={errors.provider ? 'provider-error' : undefined}
		>
			<option value="openai">OpenAI</option>
			<option value="anthropic">Anthropic</option>
		</select>
		{#if errors.provider}
			<div id="provider-error" class="error-message" role="alert">
				{errors.provider}
			</div>
		{/if}
	</div>

	<!-- Model Selection -->
	<div class="form-group">
		<label for="model-select" class="form-label">
			Model
			<span class="required" aria-label="required">*</span>
		</label>
		<select
			id="model-select"
			class="form-select"
			class:error={errors.model}
			value={model}
			on:change={handleModelChange}
			aria-required="true"
			aria-invalid={!!errors.model}
			aria-describedby={errors.model ? 'model-error' : undefined}
		>
			{#each availableModels as modelOption}
				<option value={modelOption}>{modelOption}</option>
			{/each}
		</select>
		{#if errors.model}
			<div id="model-error" class="error-message" role="alert">
				{errors.model}
			</div>
		{/if}
	</div>

	<!-- Target Language Selection -->
	<div class="form-group">
		<label for="language-select" class="form-label">
			Target Language
			<span class="required" aria-label="required">*</span>
		</label>
		<select
			id="language-select"
			class="form-select"
			class:error={errors.targetLanguage}
			value={targetLanguage}
			on:change={handleLanguageChange}
			aria-required="true"
			aria-invalid={!!errors.targetLanguage}
			aria-describedby={errors.targetLanguage ? 'language-error' : undefined}
		>
			{#each LANGUAGES as language}
				<option value={language.code}>{language.name} ({language.code})</option>
			{/each}
		</select>
		{#if errors.targetLanguage}
			<div id="language-error" class="error-message" role="alert">
				{errors.targetLanguage}
			</div>
		{/if}
	</div>

	<!-- API Key Input -->
	<div class="form-group">
		<label for="api-key-input" class="form-label">
			API Key
			<span class="required" aria-label="required">*</span>
		</label>
		<input
			id="api-key-input"
			type="password"
			class="form-input"
			class:error={errors.apiKey}
			value={apiKey}
			on:input={handleApiKeyChange}
			placeholder="Enter your API key"
			aria-required="true"
			aria-invalid={!!errors.apiKey}
			aria-describedby={errors.apiKey ? 'api-key-error' : undefined}
		/>
		{#if errors.apiKey}
			<div id="api-key-error" class="error-message" role="alert">
				{errors.apiKey}
			</div>
		{/if}
		<div class="form-help">Your API key is stored only in memory and never persisted.</div>
	</div>

	<!-- Test Connection Button -->
	<div class="form-group">
		<Button
			label={isTestingConnection ? 'Testing...' : 'Test Connection'}
			variant="secondary"
			disabled={isTestingConnection}
			onclick={handleTestConnection}
		/>
	</div>

	<!-- Test Result Display -->
	{#if testResult}
		<div
			class="result-message"
			class:success={testResult.type === 'success'}
			class:error={testResult.type === 'error'}
			role="status"
			aria-live="polite"
		>
			{testResult.message}
		</div>
	{/if}

	<!-- Action Buttons -->
	<div class="action-buttons">
		<Button label={isSaving ? 'Saving...' : 'Save'} variant="primary" disabled={isSaving} onclick={handleSave} />
		<Button label="Reset" variant="danger" onclick={handleReset} />
	</div>

	<!-- Save Result Display -->
	{#if saveResult}
		<div
			class="result-message"
			class:success={saveResult.type === 'success'}
			class:error={saveResult.type === 'error'}
			role="status"
			aria-live="polite"
		>
			{saveResult.message}
		</div>
	{/if}
</div>

<style>
	.config-panel {
		max-width: 500px;
		padding: 1.5rem;
		border: 1px solid #e0e0e0;
		border-radius: 0.5rem;
		background-color: #ffffff;
	}

	.panel-title {
		font-size: 1.5rem;
		font-weight: bold;
		margin-bottom: 1.5rem;
		color: #333;
	}

	.form-group {
		margin-bottom: 1.25rem;
	}

	.form-label {
		display: block;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: #555;
	}

	.required {
		color: #dc3545;
		margin-left: 0.25rem;
	}

	.form-select,
	.form-input {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 0.25rem;
		font-size: 1rem;
		transition: border-color 0.2s;
	}

	.form-select:focus,
	.form-input:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
	}

	.form-select.error,
	.form-input.error {
		border-color: #dc3545;
	}

	.form-select.error:focus,
	.form-input.error:focus {
		box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
	}

	.form-help {
		margin-top: 0.375rem;
		font-size: 0.875rem;
		color: #6c757d;
	}

	.error-message {
		margin-top: 0.375rem;
		font-size: 0.875rem;
		color: #dc3545;
	}

	.action-buttons {
		display: flex;
		gap: 0.75rem;
		margin-top: 1.5rem;
	}

	.result-message {
		margin-top: 1rem;
		padding: 0.75rem;
		border-radius: 0.25rem;
		font-size: 0.9375rem;
	}

	.result-message.success {
		background-color: #d4edda;
		color: #155724;
		border: 1px solid #c3e6cb;
	}

	.result-message.error {
		background-color: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}
</style>
