<script lang="ts">
	/**
	 * ErrorToast Component
	 *
	 * Displays non-critical errors as toast notifications with auto-dismiss.
	 * Multiple toasts can be stacked vertically.
	 *
	 * Features:
	 * - Display error message with customizable severity (error/warning/info)
	 * - Auto-dismiss after 5 seconds
	 * - Manual dismiss button
	 * - Optional retry button
	 * - ARIA live region for screen readers
	 * - Severity color indicators
	 * - Smooth entrance and exit animations
	 */

	import { onMount, createEventDispatcher } from 'svelte';

	// Props
	export let message: string;
	export let severity: 'error' | 'warning' | 'info' = 'error';
	export let autoDismiss = true;
	export let dismissDelay = 5000; // 5 seconds
	export let showRetry = false;
	export let onRetry: (() => void) | undefined = undefined;
	export let onDismiss: (() => void) | undefined = undefined;

	// Local state
	let visible = true;
	let timeoutId: ReturnType<typeof setTimeout> | null = null;

	const dispatch = createEventDispatcher<{
		dismiss: void;
		retry: void;
	}>();

	// Auto-dismiss logic
	onMount(() => {
		if (autoDismiss) {
			timeoutId = setTimeout(() => {
				handleDismiss();
			}, dismissDelay);
		}

		// Cleanup timeout on unmount
		return () => {
			if (timeoutId !== null) {
				clearTimeout(timeoutId);
			}
		};
	});

	/**
	 * Handle manual dismiss
	 */
	function handleDismiss() {
		visible = false;

		// Clear timeout if exists
		if (timeoutId !== null) {
			clearTimeout(timeoutId);
			timeoutId = null;
		}

		// Dispatch event
		dispatch('dismiss');

		// Call optional callback
		if (onDismiss) {
			onDismiss();
		}
	}

	/**
	 * Handle retry action
	 */
	function handleRetry() {
		// Dispatch event
		dispatch('retry');

		// Call optional callback
		if (onRetry) {
			onRetry();
		}

		// Dismiss toast after retry
		handleDismiss();
	}

	/**
	 * Get severity icon and color classes
	 */
	function getSeverityInfo(sev: typeof severity): {
		icon: string;
		colorClass: string;
		ariaLabel: string;
	} {
		switch (sev) {
			case 'error':
				return {
					icon: '✕',
					colorClass: 'toast-error',
					ariaLabel: 'Error'
				};
			case 'warning':
				return {
					icon: '⚠',
					colorClass: 'toast-warning',
					ariaLabel: 'Warning'
				};
			case 'info':
				return {
					icon: 'ℹ',
					colorClass: 'toast-info',
					ariaLabel: 'Information'
				};
		}
	}

	$: severityInfo = getSeverityInfo(severity);
</script>

{#if visible}
	<div
		class="toast {severityInfo.colorClass}"
		role="alert"
		aria-live="assertive"
		aria-atomic="true"
		data-testid="error-toast"
	>
		<!-- Severity Icon -->
		<div class="toast-icon" aria-label={severityInfo.ariaLabel}>
			{severityInfo.icon}
		</div>

		<!-- Message -->
		<div class="toast-message">
			{message}
		</div>

		<!-- Actions -->
		<div class="toast-actions">
			{#if showRetry && onRetry}
				<button
					class="toast-button retry-button"
					on:click={handleRetry}
					aria-label="Retry action"
					type="button"
				>
					Retry
				</button>
			{/if}

			<button
				class="toast-button dismiss-button"
				on:click={handleDismiss}
				aria-label="Dismiss notification"
				type="button"
			>
				×
			</button>
		</div>
	</div>
{/if}

<style>
	.toast {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		min-width: 300px;
		max-width: 500px;
		padding: 1rem;
		border-radius: 0.5rem;
		box-shadow:
			0 4px 6px -1px rgba(0, 0, 0, 0.1),
			0 2px 4px -1px rgba(0, 0, 0, 0.06);
		animation: slideIn 0.3s ease-out;
		margin-bottom: 0.75rem;
	}

	/* Slide in animation */
	@keyframes slideIn {
		from {
			transform: translateX(100%);
			opacity: 0;
		}
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}

	/* Severity color variants */
	.toast-error {
		background-color: #fee2e2;
		border-left: 4px solid #dc2626;
		color: #7f1d1d;
	}

	.toast-warning {
		background-color: #fef3c7;
		border-left: 4px solid #f59e0b;
		color: #78350f;
	}

	.toast-info {
		background-color: #dbeafe;
		border-left: 4px solid #3b82f6;
		color: #1e3a8a;
	}

	/* Icon */
	.toast-icon {
		flex-shrink: 0;
		font-size: 1.25rem;
		font-weight: bold;
		line-height: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 1.5rem;
		height: 1.5rem;
	}

	/* Message */
	.toast-message {
		flex: 1;
		font-size: 0.875rem;
		line-height: 1.5;
		word-break: break-word;
	}

	/* Actions */
	.toast-actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-shrink: 0;
	}

	.toast-button {
		background: transparent;
		border: none;
		cursor: pointer;
		padding: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: opacity 0.2s;
		font-size: 0.875rem;
		font-weight: 500;
	}

	.toast-button:hover {
		opacity: 0.7;
	}

	.toast-button:focus {
		outline: 2px solid currentColor;
		outline-offset: 2px;
		border-radius: 0.25rem;
	}

	/* Retry button */
	.retry-button {
		padding: 0.375rem 0.75rem;
		border-radius: 0.25rem;
	}

	.toast-error .retry-button {
		background-color: #dc2626;
		color: white;
	}

	.toast-error .retry-button:hover {
		background-color: #b91c1c;
		opacity: 1;
	}

	.toast-warning .retry-button {
		background-color: #f59e0b;
		color: white;
	}

	.toast-warning .retry-button:hover {
		background-color: #d97706;
		opacity: 1;
	}

	.toast-info .retry-button {
		background-color: #3b82f6;
		color: white;
	}

	.toast-info .retry-button:hover {
		background-color: #2563eb;
		opacity: 1;
	}

	/* Dismiss button */
	.dismiss-button {
		font-size: 1.5rem;
		line-height: 1;
		width: 1.5rem;
		height: 1.5rem;
	}

	.toast-error .dismiss-button {
		color: #7f1d1d;
	}

	.toast-warning .dismiss-button {
		color: #78350f;
	}

	.toast-info .dismiss-button {
		color: #1e3a8a;
	}

	/* Responsive design */
	@media (max-width: 640px) {
		.toast {
			min-width: 280px;
			max-width: calc(100vw - 2rem);
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		.toast {
			animation: none;
		}
	}
</style>
