<script lang="ts">
	/**
	 * Manual test page for ErrorToast component
	 * Run with: npm run dev
	 * Navigate to: http://localhost:5000/test-toast
	 */

	import ErrorToast from '$lib/components/ErrorToast.svelte';
	import { onMount } from 'svelte';

	let toasts: Array<{
		id: number;
		message: string;
		severity: 'error' | 'warning' | 'info';
		showRetry: boolean;
	}> = [];

	let nextId = 1;

	function addToast(
		message: string,
		severity: 'error' | 'warning' | 'info' = 'error',
		showRetry = false
	) {
		const id = nextId++;
		toasts = [...toasts, { id, message, severity, showRetry }];
	}

	function removeToast(id: number) {
		toasts = toasts.filter((t) => t.id !== id);
	}

	function handleRetry() {
		console.log('Retry clicked!');
	}

	onMount(() => {
		// Auto-add some sample toasts
		addToast('This is an error message', 'error', true);
		setTimeout(() => addToast('This is a warning message', 'warning'), 500);
		setTimeout(() => addToast('This is an info message', 'info'), 1000);
	});
</script>

<svelte:head>
	<title>ErrorToast Manual Test</title>
</svelte:head>

<div class="test-page">
	<h1>ErrorToast Component Manual Test</h1>

	<div class="controls">
		<button on:click={() => addToast('New error message', 'error', true)}>
			Add Error Toast (with Retry)
		</button>
		<button on:click={() => addToast('New warning message', 'warning')}> Add Warning Toast </button>
		<button on:click={() => addToast('New info message', 'info')}> Add Info Toast </button>
		<button
			on:click={() =>
				addToast(
					'This is a very long error message that should wrap properly within the toast container without breaking the layout or causing overflow issues. It should remain readable and well-formatted.',
					'error'
				)}
		>
			Add Long Message Toast
		</button>
	</div>

	<div class="toast-container">
		{#each toasts as toast (toast.id)}
			<ErrorToast
				message={toast.message}
				severity={toast.severity}
				showRetry={toast.showRetry}
				onRetry={handleRetry}
				onDismiss={() => removeToast(toast.id)}
			/>
		{/each}
	</div>
</div>

<style>
	.test-page {
		padding: 2rem;
		max-width: 1200px;
		margin: 0 auto;
	}

	h1 {
		margin-bottom: 2rem;
		color: #333;
	}

	.controls {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.controls button {
		padding: 0.75rem 1.5rem;
		background-color: #007bff;
		color: white;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		font-size: 1rem;
		transition: background-color 0.2s;
	}

	.controls button:hover {
		background-color: #0056b3;
	}

	.toast-container {
		position: fixed;
		top: 1rem;
		right: 1rem;
		z-index: 9999;
		display: flex;
		flex-direction: column;
		align-items: flex-end;
	}

	@media (max-width: 640px) {
		.toast-container {
			left: 1rem;
			right: 1rem;
			align-items: stretch;
		}
	}
</style>
