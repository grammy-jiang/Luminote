<script lang="ts">
	/**
	 * SkeletonLoader Component
	 *
	 * Displays animated skeleton placeholders during content loading (extraction/translation).
	 * Shows shimmer animation to indicate work in progress, improving perceived performance.
	 *
	 * Features:
	 * - Animated shimmer/pulse effect
	 * - Configurable number of skeleton blocks
	 * - Varying block heights for realistic appearance
	 * - Light and dark variants to match pane backgrounds
	 * - Accessible (ARIA labels, not focusable)
	 * - Responsive design (mobile friendly)
	 */

	export let blocks: number = 5;
	export let variant: 'light' | 'dark' = 'light';

	// Generate varying heights for realistic skeleton blocks
	// Heights cycle through: 80px, 120px, 100px, 140px, 90px
	const blockHeights = [80, 120, 100, 140, 90];

	function getBlockHeight(index: number): number {
		return blockHeights[index % blockHeights.length];
	}
</script>

<div
	class="skeleton-loader"
	class:light={variant === 'light'}
	class:dark={variant === 'dark'}
	role="status"
	aria-live="polite"
	aria-busy="true"
	aria-label="Loading content"
>
	<!-- eslint-disable-next-line @typescript-eslint/no-unused-vars -->
	{#each Array(blocks) as _item, index}
		<div class="skeleton-block" style="height: {getBlockHeight(index)}px;" aria-hidden="true"></div>
	{/each}
	<span class="sr-only">Loading content, please wait...</span>
</div>

<style>
	.skeleton-loader {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 1rem;
		width: 100%;
	}

	.skeleton-block {
		border-radius: 0.5rem;
		position: relative;
		overflow: hidden;
	}

	/* Light variant - matches left pane (#ffffff) */
	.light .skeleton-block {
		background-color: #e5e7eb;
	}

	/* Dark variant - matches right pane (#f9fafb) */
	.dark .skeleton-block {
		background-color: #d1d5db;
	}

	/* Shimmer animation effect */
	.skeleton-block::before {
		content: '';
		position: absolute;
		top: 0;
		left: -150%;
		width: 150%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
		animation: shimmer 2s infinite;
	}

	@keyframes shimmer {
		0% {
			left: -150%;
		}
		100% {
			left: 150%;
		}
	}

	/* Pulse animation as fallback */
	@media (prefers-reduced-motion: reduce) {
		.skeleton-block::before {
			animation: none;
		}
		.skeleton-block {
			animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
		}
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	/* Screen reader only text */
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border-width: 0;
	}

	/* Responsive: Adjust spacing on mobile */
	@media (max-width: 767px) {
		.skeleton-loader {
			gap: 0.75rem;
			padding: 0.75rem;
		}

		.skeleton-block {
			border-radius: 0.375rem;
		}
	}
</style>
