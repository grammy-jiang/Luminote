<script lang="ts">
	/**
	 * Test page for ErrorModal component
	 * This page allows manual testing of the ErrorModal in the browser
	 */

	import ErrorModal from '$lib/components/ErrorModal.svelte';

	let showModal = false;
	let modalConfig = {
		title: 'Translation Service Error',
		message: 'Failed to translate content using OpenAI API. The service is currently unavailable or your API key may be invalid.',
		errorCode: 'TRANSLATION_ERROR_001',
		suggestedActions: [
			'Check your API key in the settings',
			'Verify your internet connection',
			'Try again in a few minutes',
			'Switch to a different translation provider'
		]
	};

	function openModal(type: 'simple' | 'with-actions' | 'long-message') {
		if (type === 'simple') {
			modalConfig = {
				title: 'Simple Error',
				message: 'Something went wrong.',
				errorCode: 'ERR_001',
				suggestedActions: []
			};
		} else if (type === 'with-actions') {
			modalConfig = {
				title: 'Translation Service Error',
				message: 'Failed to translate content using OpenAI API.',
				errorCode: 'TRANSLATION_ERROR',
				suggestedActions: [
					'Check your API key',
					'Verify network connection',
					'Try different provider'
				]
			};
		} else if (type === 'long-message') {
			modalConfig = {
				title: 'Content Extraction Failed',
				message: 'Unable to extract content from the provided URL. This could be due to several reasons: the website may be blocking automated access, the page structure might be incompatible with our extraction algorithm, or there could be network connectivity issues. Please verify the URL is correct and accessible, then try again. If the problem persists, consider reporting this issue with the URL and error code.',
				errorCode: 'EXTRACTION_ERROR_429',
				suggestedActions: [
					'Verify the URL is correct and publicly accessible',
					'Check if the website allows automated access',
					'Try accessing the URL in a private/incognito browser window',
					'Wait a few minutes and try again (may be rate limited)',
					'Report this issue with the error code and URL'
				]
			};
		}
		showModal = true;
	}

	function closeModal() {
		showModal = false;
	}
</script>

<svelte:head>
	<title>ErrorModal Test Page - Luminote</title>
</svelte:head>

<div class="container">
	<h1>ErrorModal Component Test</h1>

	<p class="description">
		Test the ErrorModal component with different configurations. Click the buttons below to open
		the modal with different error scenarios.
	</p>

	<div class="button-group">
		<button class="btn btn-primary" on:click={() => openModal('simple')}>
			Simple Error (No Actions)
		</button>

		<button class="btn btn-primary" on:click={() => openModal('with-actions')}>
			Error with Suggested Actions
		</button>

		<button class="btn btn-primary" on:click={() => openModal('long-message')}>
			Long Error Message
		</button>
	</div>

	<div class="info-box">
		<h2>Features to Test:</h2>
		<ul>
			<li>✓ Click backdrop to close</li>
			<li>✓ Press ESC key to close</li>
			<li>✓ Click close button (×) in header</li>
			<li>✓ Click "Dismiss" button in footer</li>
			<li>✓ Click "Copy Error Details" to copy to clipboard</li>
			<li>✓ Tab navigation (focus trap)</li>
			<li>✓ Responsive design (try resizing window)</li>
		</ul>
	</div>
</div>

{#if showModal}
	<ErrorModal
		title={modalConfig.title}
		message={modalConfig.message}
		errorCode={modalConfig.errorCode}
		suggestedActions={modalConfig.suggestedActions}
		onClose={closeModal}
	/>
{/if}

<style>
	.container {
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem;
	}

	h1 {
		font-size: 2rem;
		font-weight: 700;
		color: #1f2937;
		margin-bottom: 1rem;
	}

	.description {
		font-size: 1.125rem;
		color: #6b7280;
		margin-bottom: 2rem;
	}

	.button-group {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.btn {
		padding: 0.75rem 1.5rem;
		font-size: 1rem;
		font-weight: 500;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-primary {
		background-color: #3b82f6;
		color: white;
	}

	.btn-primary:hover {
		background-color: #2563eb;
	}

	.info-box {
		background-color: #f3f4f6;
		border: 1px solid #e5e7eb;
		border-radius: 0.5rem;
		padding: 1.5rem;
	}

	.info-box h2 {
		font-size: 1.25rem;
		font-weight: 600;
		color: #1f2937;
		margin-bottom: 1rem;
	}

	.info-box ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.info-box li {
		padding: 0.5rem 0;
		color: #4b5563;
		font-size: 0.875rem;
	}

	@media (min-width: 768px) {
		.button-group {
			flex-direction: row;
		}
	}
</style>
