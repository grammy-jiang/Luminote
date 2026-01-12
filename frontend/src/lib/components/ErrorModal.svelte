<script lang="ts">
	/**
	 * ErrorModal Component
	 *
	 * Displays critical errors as modal dialogs requiring user acknowledgment.
	 * Modal prevents interaction with the page until dismissed.
	 *
	 * Features:
	 * - Display error title and message
	 * - Show error code
	 * - Display suggested fixes/actions
	 * - Copy button for bug report
	 * - Cannot dismiss accidentally (requires explicit action)
	 * - Keyboard navigation (Esc to close)
	 * - Focus trap (keeps focus within modal)
	 * - Backdrop prevents interaction with page
	 * - ARIA attributes for screen readers
	 */

	import { createEventDispatcher, onMount, onDestroy } from 'svelte';

	// Props
	export let title: string;
	export let message: string;
	export let errorCode: string;
	export let suggestedActions: string[] = [];
	export let onClose: (() => void) | undefined = undefined;

	// Local state
	let modalElement: HTMLDivElement | null = null;
	let closeButtonElement: HTMLButtonElement | null = null;
	let copySuccess = false;

	const dispatch = createEventDispatcher<{
		close: void;
		copy: void;
	}>();

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
	 * Handle keyboard events
	 */
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			handleClose();
		}
	}

	/**
	 * Copy error details to clipboard for bug report
	 */
	async function handleCopy() {
		const suggestedActionsText =
			suggestedActions.length > 0
				? '\n\nSuggested Actions:\n' +
					suggestedActions.map((action, i) => `${i + 1}. ${action}`).join('\n')
				: '';

		const errorDetails = `Error Code: ${errorCode}\nTitle: ${title}\nMessage: ${message}${suggestedActionsText}`;

		try {
			await navigator.clipboard.writeText(errorDetails);
			copySuccess = true;
			dispatch('copy');

			// Reset success message after 2 seconds
			setTimeout(() => {
				copySuccess = false;
			}, 2000);
		} catch (err) {
			// Log error for debugging but don't break the UI
			console.error('Failed to copy to clipboard:', err);
		}
	}

	/**
	 * Focus trap implementation
	 * Keeps focus within the modal
	 */
	function trapFocus(event: KeyboardEvent) {
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
			// Shift + Tab: moving backwards
			if (document.activeElement === firstElement) {
				lastElement.focus();
				event.preventDefault();
			}
		} else {
			// Tab: moving forwards
			if (document.activeElement === lastElement) {
				firstElement.focus();
				event.preventDefault();
			}
		}
	}

	// Lifecycle: Setup focus trap and initial focus
	onMount(() => {
		// Focus the close button when modal opens (delay to ensure element is ready)
		setTimeout(() => {
			if (closeButtonElement) {
				closeButtonElement.focus();
			}
		}, 0);

		// Add event listeners
		document.addEventListener('keydown', handleKeydown);
		document.addEventListener('keydown', trapFocus);

		// Prevent body scroll when modal is open
		document.body.style.overflow = 'hidden';
	});

	// Cleanup on unmount
	onDestroy(() => {
		document.removeEventListener('keydown', handleKeydown);
		document.removeEventListener('keydown', trapFocus);
		document.body.style.overflow = '';
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
	aria-describedby="modal-description"
	bind:this={modalElement}
	data-testid="error-modal"
>
	<!-- Header -->
	<div class="modal-header">
		<h2 id="modal-title" class="modal-title">
			{title}
		</h2>
		<button
			class="close-button"
			on:click={handleClose}
			aria-label="Close error dialog"
			type="button"
			bind:this={closeButtonElement}
			data-testid="close-button"
		>
			×
		</button>
	</div>

	<!-- Body -->
	<div class="modal-body">
		<!-- Error Code -->
		<div class="error-code-container">
			<span class="error-code-label">Error Code:</span>
			<code class="error-code" data-testid="error-code">{errorCode}</code>
		</div>

		<!-- Message -->
		<p id="modal-description" class="error-message">
			{message}
		</p>

		<!-- Suggested Actions -->
		{#if suggestedActions.length > 0}
			<div class="suggested-actions">
				<h3 class="actions-title">Suggested Actions:</h3>
				<ul class="actions-list">
					{#each suggestedActions as action}
						<li class="action-item" data-testid="action-item">
							{action}
						</li>
					{/each}
				</ul>
			</div>
		{/if}
	</div>

	<!-- Footer -->
	<div class="modal-footer">
		<button
			class="copy-button"
			on:click={handleCopy}
			aria-label="Copy error details to clipboard"
			type="button"
			data-testid="copy-button"
		>
			{copySuccess ? '✓ Copied!' : 'Copy Error Details'}
		</button>

		<button
			class="dismiss-button"
			on:click={handleClose}
			aria-label="Dismiss error dialog"
			type="button"
			data-testid="dismiss-button"
		>
			Dismiss
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
		max-width: 600px;
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

	/* Animations */
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
		color: #dc2626;
		margin: 0;
		line-height: 1.4;
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
		flex-shrink: 0;
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

	/* Error Code */
	.error-code-container {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 1rem;
		padding: 0.75rem;
		background-color: #fef2f2;
		border-left: 4px solid #dc2626;
		border-radius: 0.25rem;
	}

	.error-code-label {
		font-weight: 600;
		color: #991b1b;
		font-size: 0.875rem;
	}

	.error-code {
		font-family: 'Courier New', Courier, monospace;
		font-size: 0.875rem;
		font-weight: 600;
		color: #991b1b;
		background-color: #fee2e2;
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
	}

	/* Message */
	.error-message {
		font-size: 1rem;
		line-height: 1.6;
		margin: 0 0 1.5rem 0;
		color: #374151;
		word-break: break-word;
	}

	/* Suggested Actions */
	.suggested-actions {
		margin-top: 1.5rem;
		padding: 1rem;
		background-color: #f9fafb;
		border-radius: 0.375rem;
		border: 1px solid #e5e7eb;
	}

	.actions-title {
		font-size: 1rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0 0 0.75rem 0;
	}

	.actions-list {
		margin: 0;
		padding-left: 1.5rem;
		list-style: decimal;
	}

	.action-item {
		font-size: 0.875rem;
		line-height: 1.6;
		color: #4b5563;
		margin-bottom: 0.5rem;
	}

	.action-item:last-child {
		margin-bottom: 0;
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

	.copy-button,
	.dismiss-button {
		padding: 0.625rem 1.25rem;
		font-size: 0.875rem;
		font-weight: 500;
		border-radius: 0.375rem;
		cursor: pointer;
		transition: all 0.2s;
		border: 1px solid transparent;
	}

	.copy-button {
		background-color: #f3f4f6;
		color: #374151;
		border-color: #d1d5db;
	}

	.copy-button:hover {
		background-color: #e5e7eb;
		border-color: #9ca3af;
	}

	.copy-button:focus {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	.dismiss-button {
		background-color: #dc2626;
		color: white;
		border-color: #dc2626;
	}

	.dismiss-button:hover {
		background-color: #b91c1c;
		border-color: #b91c1c;
	}

	.dismiss-button:focus {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	/* Responsive design */
	@media (max-width: 640px) {
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

		.modal-footer {
			flex-direction: column;
			gap: 0.5rem;
		}

		.copy-button,
		.dismiss-button {
			width: 100%;
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		.modal-backdrop,
		.modal-container {
			animation: none;
		}
	}
</style>
