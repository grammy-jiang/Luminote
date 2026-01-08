<script lang="ts">
	/**
	 * Simple Button component for testing purposes.
	 */
	export let label = 'Click me';
	export let variant: 'primary' | 'secondary' | 'danger' = 'primary';
	export let disabled = false;
	export let onclick: (() => void) | undefined = undefined;

	function handleClick() {
		if (onclick && !disabled) {
			onclick();
		}
	}
</script>

<button
	class="btn btn-{variant}"
	class:disabled
	{disabled}
	on:click={handleClick}
	aria-label={label}
>
	{label}
</button>

<style>
	.btn {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 0.25rem;
		cursor: pointer;
		font-size: 1rem;
		transition: background-color 0.2s;
	}

	.btn-primary {
		background-color: #007bff;
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background-color: #0056b3;
	}

	.btn-secondary {
		background-color: #6c757d;
		color: white;
	}

	.btn-secondary:hover:not(:disabled) {
		background-color: #545b62;
	}

	.btn-danger {
		background-color: #dc3545;
		color: white;
	}

	.btn-danger:hover:not(:disabled) {
		background-color: #c82333;
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
