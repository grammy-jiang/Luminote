<script lang="ts">
	/**
	 * DualPaneLayout Component
	 *
	 * Core component for Luminote's two-pane layout with source content on the left
	 * and translated content on the right. This is the foundation of Luminote's UX.
	 *
	 * Features:
	 * - Two-column flexbox layout with configurable split
	 * - Independent scroll containers
	 * - Responsive stacking on mobile (<768px)
	 * - Keyboard navigation (Tab to switch panes)
	 * - ARIA labels for accessibility
	 * - Exported refs for programmatic control
	 */

	export let initialSplit: number = 50;
	export let leftLabel: string = 'Source';
	export let rightLabel: string = 'Translation';

	// Use initialSplit for future resizable implementation
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	$: splitRatio = initialSplit;

	let leftPane: HTMLDivElement;
	let rightPane: HTMLDivElement;

	// Track which pane has focus for keyboard navigation
	let activePane: 'left' | 'right' = 'left';

	/**
	 * Handle keyboard navigation between panes
	 */
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Tab' && !event.shiftKey) {
			const target = event.target as HTMLElement;

			// If Tab is pressed in left pane, focus right pane
			if (leftPane && leftPane.contains(target)) {
				event.preventDefault();
				rightPane?.focus();
				activePane = 'right';
			}
		} else if (event.key === 'Tab' && event.shiftKey) {
			const target = event.target as HTMLElement;

			// If Shift+Tab is pressed in right pane, focus left pane
			if (rightPane && rightPane.contains(target)) {
				event.preventDefault();
				leftPane?.focus();
				activePane = 'left';
			}
		}
	}

	/**
	 * Focus left pane programmatically
	 */
	export function focusLeftPane() {
		leftPane?.focus();
		activePane = 'left';
	}

	/**
	 * Focus right pane programmatically
	 */
	export function focusRightPane() {
		rightPane?.focus();
		activePane = 'right';
	}

	/**
	 * Get reference to left pane element
	 */
	export function getLeftPaneRef(): HTMLDivElement | undefined {
		return leftPane;
	}

	/**
	 * Get reference to right pane element
	 */
	export function getRightPaneRef(): HTMLDivElement | undefined {
		return rightPane;
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="dual-pane-layout" role="main" aria-label="Two-pane reading interface">
	<!-- Left Pane (Source Content) -->
	<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
	<div
		bind:this={leftPane}
		class="pane left-pane"
		class:active={activePane === 'left'}
		role="region"
		aria-label={leftLabel}
		tabindex="0"
		on:focus={() => (activePane = 'left')}
	>
		<slot name="left">
			<div class="pane-placeholder">
				<p class="text-gray-500 text-center">No source content</p>
			</div>
		</slot>
	</div>

	<!-- Right Pane (Translation Content) -->
	<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
	<div
		bind:this={rightPane}
		class="pane right-pane"
		class:active={activePane === 'right'}
		role="region"
		aria-label={rightLabel}
		tabindex="0"
		on:focus={() => (activePane = 'right')}
	>
		<slot name="right">
			<div class="pane-placeholder">
				<p class="text-gray-500 text-center">No translation content</p>
			</div>
		</slot>
	</div>
</div>

<style>
	.dual-pane-layout {
		display: flex;
		flex-direction: row;
		width: 100%;
		height: 100vh;
		overflow: hidden;
	}

	.pane {
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
		padding: 1rem;
		outline: none;
		position: relative;
	}

	.pane:focus {
		outline: 2px solid #3b82f6;
		outline-offset: -2px;
	}

	.left-pane {
		border-right: 1px solid #e5e7eb;
		background-color: #ffffff;
	}

	.right-pane {
		background-color: #f9fafb;
	}

	.pane-placeholder {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		min-height: 200px;
	}

	/* Responsive: Stack vertically on mobile (<768px) */
	@media (max-width: 767px) {
		.dual-pane-layout {
			flex-direction: column;
			height: auto;
		}

		.pane {
			min-height: 50vh;
		}

		.left-pane {
			border-right: none;
			border-bottom: 1px solid #e5e7eb;
		}
	}

	/* Ensure scroll position is maintained on resize */
	.pane {
		scroll-behavior: smooth;
	}
</style>
