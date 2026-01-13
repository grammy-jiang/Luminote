<script lang="ts">
	/**
	 * BlockRetranslate Component
	 *
	 * Modal dialog for re-translating individual content blocks with custom prompts.
	 * Allows users to refine translations without re-fetching the entire document.
	 *
	 * Features:
	 * - Display original and current translation
	 * - Custom prompt input for translation refinement
	 * - Model selector (inherits from config)
	 * - Accept/Discard actions for version management
	 * - Keyboard shortcuts (Ctrl+Enter to accept)
	 * - Loading states during translation
	 * - Error handling with user feedback
	 */

	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { configStore } from '$lib/stores/config';
	import { apiClient } from '$lib/utils/api';
	import type { ContentBlock } from '$lib/types/api';

	// Props
	export let block: ContentBlock;
	export let originalText: string;
	export let onClose: (() => void) | undefined = undefined;

	// Local state
	let modalElement: HTMLDivElement | null = null;
	let customPrompt: string = '';
	let selectedModel: string = '';
	let isLoading: boolean = false;
	let error: string | null = null;
	let newTranslation: string = '';
	let translationComplete: boolean = false;

	// Config values
	let provider: string = '';
	let apiKey: string = '';
	let targetLanguage: string = '';

	const dispatch = createEventDispatcher<{
		close: void;
		accept: { blockId: string; newText: string };
		discard: { blockId: string };
	}>();

	// Subscribe to config store
	const unsubscribe = configStore.subscribe((config) => {
		provider = config.provider;
		apiKey = config.api_key;
		targetLanguage = config.target_language;
		selectedModel = config.model;
	});

	/**
	 * Handle modal close
	 */
	function handleClose() {
		dispatch('close');
		if (onClose) {
			onClose();
		}
	}

	/**
	 * Handle keyboard events (combines both Esc/Ctrl+Enter and focus trap)
	 */
	function handleKeydown(event: KeyboardEvent) {
		// Handle Esc and Ctrl+Enter
		if (event.key === 'Escape') {
			handleClose();
			return;
		} else if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
			if (translationComplete && newTranslation) {
				handleAccept();
			}
			return;
		}

		// Focus trap implementation
		if (event.key !== 'Tab' || !modalElement) {
			return;
		}

		const focusableElements = modalElement.querySelectorAll<HTMLElement>(
			'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
		);

		if (focusableElements.length === 0) {
			return;
		}

		const firstElement = focusableElements[0];
		const lastElement = focusableElements[focusableElements.length - 1];

		if (event.shiftKey) {
			if (document.activeElement === firstElement) {
				lastElement.focus();
				event.preventDefault();
			}
		} else {
			if (document.activeElement === lastElement) {
				firstElement.focus();
				event.preventDefault();
			}
		}
	}

	/**
	 * Perform re-translation with custom prompt
	 */
	async function handleRetranslate() {
		if (!apiKey) {
			error = 'API key is required. Please configure it first.';
			return;
		}

		isLoading = true;
		error = null;
		newTranslation = '';

		try {
			// Prepare the content block with custom prompt if provided
			const blockToTranslate: ContentBlock = {
				...block,
				text: originalText,
				metadata: {
					...block.metadata,
					...(customPrompt && { custom_prompt: customPrompt })
				}
			};

			// Call the translation API
			const response = await apiClient.post<{
				translated_blocks: Array<{
					id: string;
					type: string;
					text: string;
					metadata: Record<string, unknown>;
				}>;
			}>('/api/v1/translate', {
				content_blocks: [blockToTranslate],
				target_language: targetLanguage,
				provider: provider,
				model: selectedModel,
				api_key: apiKey
			});

			// Extract translated text
			if (response.data.translated_blocks && response.data.translated_blocks.length > 0) {
				newTranslation = response.data.translated_blocks[0].text;
				translationComplete = true;
			} else {
				throw new Error('No translation returned from server');
			}
		} catch (err) {
			console.error('Translation error:', err);
			error = err instanceof Error ? err.message : 'Translation failed. Please try again.';
			translationComplete = false;
		} finally {
			isLoading = false;
		}
	}

	/**
	 * Accept new translation
	 */
	function handleAccept() {
		if (!newTranslation) return;

		dispatch('accept', {
			blockId: block.id,
			newText: newTranslation
		});
		handleClose();
	}

	/**
	 * Discard and revert to current translation
	 */
	function handleDiscard() {
		dispatch('discard', {
			blockId: block.id
		});
		handleClose();
	}

	// Lifecycle
	onMount(() => {
		document.addEventListener('keydown', handleKeydown);
		document.body.style.overflow = 'hidden';
	});

	onDestroy(() => {
		document.removeEventListener('keydown', handleKeydown);
		document.body.style.overflow = '';
		unsubscribe();
	});
</script>

<!-- Backdrop -->
<div
	class="modal-backdrop"
	on:click={handleClose}
	on:keydown={handleKeydown}
	role="presentation"
	data-testid="modal-backdrop"
></div>

<!-- Modal Dialog -->
<div
	class="modal-container"
	role="dialog"
	aria-modal="true"
	aria-labelledby="modal-title"
	bind:this={modalElement}
	data-testid="retranslate-modal"
>
	<!-- Header -->
	<div class="modal-header">
		<h2 id="modal-title" class="modal-title">Re-translate Block</h2>
		<button
			class="close-button"
			on:click={handleClose}
			aria-label="Close re-translate dialog"
			type="button"
			data-testid="close-button"
		>
			×
		</button>
	</div>

	<!-- Body -->
	<div class="modal-body">
		<!-- Original Text -->
		<div class="text-section">
			<h3 class="section-title">Original Text</h3>
			<div class="text-display original" data-testid="original-text">
				{originalText}
			</div>
		</div>

		<!-- Current Translation -->
		<div class="text-section">
			<h3 class="section-title">Current Translation</h3>
			<div class="text-display current" data-testid="current-translation">
				{block.text}
			</div>
		</div>

		<!-- Model Selector -->
		<div class="form-group">
			<label for="model-select" class="form-label">
				Model
				<span class="required" aria-label="required">*</span>
			</label>
			<select
				id="model-select"
				bind:value={selectedModel}
				class="form-select"
				disabled={isLoading}
				data-testid="model-select"
			>
				{#if provider === 'openai'}
					<option value="gpt-4">GPT-4</option>
					<option value="gpt-4-turbo">GPT-4 Turbo</option>
					<option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
				{:else if provider === 'anthropic'}
					<option value="claude-3-opus-20240229">Claude 3 Opus</option>
					<option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
					<option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
				{:else}
					<option value={selectedModel}>{selectedModel}</option>
				{/if}
			</select>
		</div>

		<!-- Custom Prompt -->
		<div class="form-group">
			<label for="custom-prompt" class="form-label">
				Custom Prompt (optional)
				<span class="help-text">Refine the translation with specific instructions</span>
			</label>
			<textarea
				id="custom-prompt"
				bind:value={customPrompt}
				class="form-textarea"
				placeholder="e.g., Make it more formal, use technical terminology, etc."
				rows="3"
				disabled={isLoading}
				data-testid="custom-prompt"
			></textarea>
		</div>

		<!-- Re-translate Button -->
		<div class="action-row">
			<button
				class="btn btn-primary"
				on:click={handleRetranslate}
				disabled={isLoading || !apiKey}
				data-testid="retranslate-button"
			>
				{isLoading ? 'Translating...' : 'Re-translate'}
			</button>
			{#if !apiKey}
				<p class="warning-text">Please configure your API key in the settings</p>
			{/if}
		</div>

		<!-- Error Display -->
		{#if error}
			<div class="error-message" role="alert" data-testid="error-message">
				{error}
			</div>
		{/if}

		<!-- New Translation Display -->
		{#if translationComplete && newTranslation}
			<div class="text-section new-translation">
				<h3 class="section-title">New Translation</h3>
				<div class="text-display new" data-testid="new-translation">
					{newTranslation}
				</div>
			</div>
		{/if}
	</div>

	<!-- Footer -->
	<div class="modal-footer">
		<button
			class="btn btn-secondary"
			on:click={handleDiscard}
			type="button"
			data-testid="discard-button"
		>
			Discard
		</button>

		<button
			class="btn btn-success"
			on:click={handleAccept}
			disabled={!translationComplete || !newTranslation}
			type="button"
			data-testid="accept-button"
			aria-label="Accept new translation (Ctrl+Enter)"
		>
			Accept
			<span class="keyboard-hint">Ctrl+Enter</span>
		</button>
	</div>
</div>

<style>
	/* Backdrop */
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		z-index: 9998;
		animation: fadeIn 0.2s ease-out;
	}

	/* Modal Container */
	.modal-container {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 90%;
		max-width: 800px;
		max-height: 90vh;
		background-color: white;
		border-radius: 0.5rem;
		box-shadow:
			0 20px 25px -5px rgba(0, 0, 0, 0.1),
			0 10px 10px -5px rgba(0, 0, 0, 0.04);
		z-index: 9999;
		display: flex;
		flex-direction: column;
		animation: slideIn 0.3s ease-out;
		overflow: hidden;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@keyframes slideIn {
		from {
			transform: translate(-50%, -45%);
			opacity: 0;
		}
		to {
			transform: translate(-50%, -50%);
			opacity: 1;
		}
	}

	/* Header */
	.modal-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.5rem;
		border-bottom: 1px solid #e5e7eb;
		flex-shrink: 0;
	}

	.modal-title {
		font-size: 1.5rem;
		font-weight: 700;
		color: #1f2937;
		margin: 0;
	}

	.close-button {
		background: transparent;
		border: none;
		font-size: 2rem;
		line-height: 1;
		color: #6b7280;
		cursor: pointer;
		padding: 0;
		width: 2rem;
		height: 2rem;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 0.25rem;
		transition: all 0.2s;
	}

	.close-button:hover {
		background-color: #f3f4f6;
		color: #1f2937;
	}

	.close-button:focus {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	/* Body */
	.modal-body {
		padding: 1.5rem;
		flex: 1;
		overflow-y: auto;
		color: #1f2937;
	}

	/* Text Sections */
	.text-section {
		margin-bottom: 1.5rem;
	}

	.text-section.new-translation {
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: 2px solid #10b981;
	}

	.section-title {
		font-size: 0.875rem;
		font-weight: 600;
		color: #374151;
		margin: 0 0 0.5rem 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.text-display {
		padding: 1rem;
		border-radius: 0.375rem;
		border: 1px solid #e5e7eb;
		background-color: #f9fafb;
		font-size: 0.9375rem;
		line-height: 1.6;
		color: #1f2937;
		white-space: pre-wrap;
		word-wrap: break-word;
	}

	.text-display.original {
		background-color: #fef3c7;
		border-color: #fbbf24;
	}

	.text-display.current {
		background-color: #dbeafe;
		border-color: #60a5fa;
	}

	.text-display.new {
		background-color: #d1fae5;
		border-color: #10b981;
		font-weight: 500;
	}

	/* Form Elements */
	.form-group {
		margin-bottom: 1.25rem;
	}

	.form-label {
		display: block;
		font-size: 0.875rem;
		font-weight: 600;
		color: #374151;
		margin-bottom: 0.5rem;
	}

	.required {
		color: #dc2626;
		margin-left: 0.25rem;
	}

	.help-text {
		display: block;
		font-size: 0.75rem;
		font-weight: 400;
		color: #6b7280;
		margin-top: 0.25rem;
	}

	.form-select,
	.form-textarea {
		width: 100%;
		padding: 0.625rem 0.75rem;
		font-size: 0.9375rem;
		border: 1px solid #d1d5db;
		border-radius: 0.375rem;
		background-color: white;
		color: #1f2937;
		transition: all 0.2s;
	}

	.form-select:focus,
	.form-textarea:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.form-select:disabled,
	.form-textarea:disabled {
		background-color: #f3f4f6;
		cursor: not-allowed;
		opacity: 0.6;
	}

	.form-textarea {
		resize: vertical;
		min-height: 4rem;
		font-family: inherit;
	}

	/* Action Row */
	.action-row {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.warning-text {
		font-size: 0.875rem;
		color: #dc2626;
		margin: 0;
	}

	/* Error Message */
	.error-message {
		padding: 1rem;
		background-color: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: 0.375rem;
		color: #991b1b;
		font-size: 0.875rem;
		margin-bottom: 1rem;
	}

	/* Buttons */
	.btn {
		padding: 0.625rem 1.25rem;
		font-size: 0.9375rem;
		font-weight: 500;
		border-radius: 0.375rem;
		cursor: pointer;
		transition: all 0.2s;
		border: 1px solid transparent;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-primary {
		background-color: #3b82f6;
		color: white;
		border-color: #3b82f6;
	}

	.btn-primary:hover:not(:disabled) {
		background-color: #2563eb;
		border-color: #2563eb;
	}

	.btn-primary:focus {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	.btn-secondary {
		background-color: #f3f4f6;
		color: #374151;
		border-color: #d1d5db;
	}

	.btn-secondary:hover:not(:disabled) {
		background-color: #e5e7eb;
		border-color: #9ca3af;
	}

	.btn-secondary:focus {
		outline: 2px solid #6b7280;
		outline-offset: 2px;
	}

	.btn-success {
		background-color: #10b981;
		color: white;
		border-color: #10b981;
	}

	.btn-success:hover:not(:disabled) {
		background-color: #059669;
		border-color: #059669;
	}

	.btn-success:focus {
		outline: 2px solid #10b981;
		outline-offset: 2px;
	}

	.keyboard-hint {
		font-size: 0.75rem;
		opacity: 0.8;
		font-weight: 400;
	}

	/* Footer */
	.modal-footer {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1.5rem;
		border-top: 1px solid #e5e7eb;
		flex-shrink: 0;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.modal-container {
			width: 95%;
			max-height: 95vh;
		}

		.modal-header,
		.modal-body,
		.modal-footer {
			padding: 1rem;
		}

		.modal-title {
			font-size: 1.25rem;
		}

		.keyboard-hint {
			display: none;
		}
	}

	/* Reduced motion */
	@media (prefers-reduced-motion: reduce) {
		.modal-backdrop,
		.modal-container {
			animation: none;
		}
	}
</style>
