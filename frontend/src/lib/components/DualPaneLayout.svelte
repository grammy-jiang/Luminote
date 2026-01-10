<script lang="ts">
	import { createEventDispatcher, setContext, onDestroy } from 'svelte';
	import { writable } from 'svelte/store';

	/**
	 * DualPaneLayout Component
	 *
	 * Core component for Luminote's two-pane layout with source content on the left
	 * and translated content on the right. This is the foundation of Luminote's UX.
	 *
	 * Features:
	 * - Two-column flexbox layout with configurable split
	 * - Draggable divider for resizing panes
	 * - Independent scroll containers
	 * - Responsive stacking on mobile (<768px)
	 * - Keyboard navigation (Tab to switch panes, Ctrl+Arrow to resize)
	 * - ARIA labels for accessibility
	 * - Exported refs for programmatic control
	 * - localStorage persistence for split ratio
	 * - Block hover highlighting coordination via context
	 */

	export let leftLabel: string = 'Source';
	export let rightLabel: string = 'Translation';
	export let minPaneWidth: number = 20; // Minimum pane width percentage
	export let persistKey: string = 'luminote-split'; // localStorage key

	const dispatch = createEventDispatcher<{
		splitChange: { leftWidth: number; rightWidth: number };
	}>();

	let leftPane: HTMLDivElement;
	let rightPane: HTMLDivElement;
	let divider: HTMLDivElement;
	let containerRef: HTMLDivElement;

	// Track which pane has focus for keyboard navigation
	let activePane: 'left' | 'right' = 'left';

	// Hover state for block highlighting - shared via context
	const hoveredBlockId = writable<string | null>(null);
	setContext('highlightedBlockId', hoveredBlockId);

	// Split ratio state (percentage for left pane)
	let leftWidth = 50;
	let isDragging = false;
	let isHovering = false;
	let initialized = false;

	// Load split ratio from localStorage on mount or when persistKey changes
	$: if (!initialized && persistKey && typeof window !== 'undefined') {
		const saved = localStorage.getItem(persistKey);
		if (saved) {
			const parsed = parseFloat(saved);
			if (!isNaN(parsed) && parsed >= minPaneWidth && parsed <= 100 - minPaneWidth) {
				leftWidth = parsed;
			}
		}
		initialized = true;
	}

	// Save split ratio to localStorage
	function saveSplitRatio() {
		if (typeof window !== 'undefined') {
			localStorage.setItem(persistKey, leftWidth.toString());
		}
		dispatch('splitChange', {
			leftWidth: leftWidth,
			rightWidth: 100 - leftWidth
		});
	}

	// Handle mouse down on divider
	function handleDividerMouseDown(event: MouseEvent) {
		event.preventDefault();
		isDragging = true;
		document.body.style.cursor = 'col-resize';
		document.body.style.userSelect = 'none';
	}

	// Handle touch start on divider
	function handleDividerTouchStart(event: TouchEvent) {
		event.preventDefault();
		isDragging = true;
	}

	// Handle mouse move during drag
	function handleMouseMove(event: MouseEvent) {
		if (!isDragging || !containerRef) return;

		const containerRect = containerRef.getBoundingClientRect();
		const mouseX = event.clientX - containerRect.left;
		const percentage = (mouseX / containerRect.width) * 100;

		// Enforce min/max constraints
		leftWidth = Math.max(minPaneWidth, Math.min(100 - minPaneWidth, percentage));
	}

	// Handle touch move during drag
	function handleTouchMove(event: TouchEvent) {
		if (!isDragging || !containerRef) return;

		const touch = event.touches[0];
		const containerRect = containerRef.getBoundingClientRect();
		const touchX = touch.clientX - containerRect.left;
		const percentage = (touchX / containerRect.width) * 100;

		// Enforce min/max constraints
		leftWidth = Math.max(minPaneWidth, Math.min(100 - minPaneWidth, percentage));
	}

	// Handle mouse up (end drag)
	function handleMouseUp() {
		if (isDragging) {
			isDragging = false;
			document.body.style.cursor = '';
			document.body.style.userSelect = '';
			saveSplitRatio();
		}
	}

	// Handle touch end (end drag)
	function handleTouchEnd() {
		if (isDragging) {
			isDragging = false;
			saveSplitRatio();
		}
	}

	/**
	 * Handle keyboard navigation between panes
	 * Only intercepts Tab when the pane container itself has focus, not child elements
	 * Also handles Ctrl+Arrow keys for resizing
	 */
	function handleKeydown(event: KeyboardEvent) {
		// Handle resize shortcuts (Ctrl + Arrow keys)
		if (event.ctrlKey && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) {
			event.preventDefault();
			const step = 5;

			if (event.key === 'ArrowLeft') {
				// Decrease left pane width
				leftWidth = Math.max(minPaneWidth, leftWidth - step);
			} else {
				// Increase left pane width
				leftWidth = Math.min(100 - minPaneWidth, leftWidth + step);
			}

			saveSplitRatio();
			return;
		}

		// Handle Tab navigation
		if (event.key === 'Tab' && !event.shiftKey) {
			const target = event.target as HTMLElement;

			// Only intercept if the pane container itself has focus
			if (target === leftPane) {
				event.preventDefault();
				rightPane?.focus();
				activePane = 'right';
			}
		} else if (event.key === 'Tab' && event.shiftKey) {
			const target = event.target as HTMLElement;

			// Only intercept if the pane container itself has focus
			if (target === rightPane) {
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
	 *
	 * Note: This should only be called after the component has mounted.
	 * @throws {Error} If called before the component has mounted
	 */
	export function getLeftPaneRef(): HTMLDivElement {
		if (!leftPane) {
			throw new Error(
				'Left pane ref is not available yet. Call this after the component has mounted.'
			);
		}
		return leftPane;
	}

	/**
	 * Get reference to right pane element
	 *
	 * Note: This should only be called after the component has mounted.
	 * @throws {Error} If called before the component has mounted
	 */
	export function getRightPaneRef(): HTMLDivElement {
		if (!rightPane) {
			throw new Error(
				'Right pane ref is not available yet. Call this after the component has mounted.'
			);
		}
		return rightPane;
	}

	/**
	 * Get current split ratio
	 */
	export function getSplitRatio(): number {
		return leftWidth;
	}

	/**
	 * Set split ratio programmatically
	 */
	export function setSplitRatio(percentage: number) {
		leftWidth = Math.max(minPaneWidth, Math.min(100 - minPaneWidth, percentage));
		saveSplitRatio();
	}

	/**
	 * Handle block hover from either pane.
	 */
	function handleBlockHover(event: CustomEvent<{ blockId: string }>) {
		hoveredBlockId.set(event.detail.blockId);
	}

	/**
	 * Handle block leave from either pane.
	 */
	function handleBlockLeave(event: CustomEvent<{ blockId: string }>) {
		hoveredBlockId.update((current) => {
			// Only clear if it's the same block that's leaving
			return current === event.detail.blockId ? null : current;
		});
	}

	// Track scroll animation state
	let isScrolling = false;
	let scrollAnimationController: AbortController | null = null;
	let navigationAnnouncementElement: HTMLDivElement;
	
	// Track timeout IDs for cleanup
	let announcementTimeout: ReturnType<typeof setTimeout> | null = null;
	let pulseAnimationTimeout: ReturnType<typeof setTimeout> | null = null;
	let scrollCompleteTimeout: ReturnType<typeof setTimeout> | null = null;

	// Clean up timeouts on component destroy to prevent memory leaks
	onDestroy(() => {
		if (announcementTimeout) {
			clearTimeout(announcementTimeout);
			announcementTimeout = null;
		}
		if (pulseAnimationTimeout) {
			clearTimeout(pulseAnimationTimeout);
			pulseAnimationTimeout = null;
		}
		if (scrollCompleteTimeout) {
			clearTimeout(scrollCompleteTimeout);
			scrollCompleteTimeout = null;
		}
		if (scrollAnimationController) {
			scrollAnimationController.abort();
			scrollAnimationController = null;
		}
	});

	/**
	 * Announce navigation to screen readers.
	 */
	function announceNavigation(source: 'source' | 'translation') {
		if (navigationAnnouncementElement) {
			const message =
				source === 'source' ? 'Navigated to translation block' : 'Navigated to source block';
			navigationAnnouncementElement.textContent = message;
			// Clear after announcement
			if (announcementTimeout) {
				clearTimeout(announcementTimeout);
			}
			announcementTimeout = setTimeout(() => {
				if (navigationAnnouncementElement) {
					navigationAnnouncementElement.textContent = '';
				}
				announcementTimeout = null;
			}, 1000);
		}
	}

	/**
	 * Add pulse animation to a block element.
	 */
	function addPulseAnimation(element: HTMLElement) {
		element.classList.add('block-pulse');
		if (pulseAnimationTimeout) {
			clearTimeout(pulseAnimationTimeout);
		}
		pulseAnimationTimeout = setTimeout(() => {
			element.classList.remove('block-pulse');
			pulseAnimationTimeout = null;
		}, 600);
	}

	/**
	 * Scroll to a block with smooth animation centered in viewport.
	 */
	function scrollToBlock(blockId: string, paneElement: HTMLDivElement) {
		const targetBlock = paneElement.querySelector(`[data-block-id="${blockId}"]`);
		if (!targetBlock) {
			return;
		}

		// Cancel any ongoing scroll animation
		if (scrollAnimationController) {
			scrollAnimationController.abort();
		}

		// Create new abort controller for this animation
		scrollAnimationController = new AbortController();
		isScrolling = true;

		// Add pulse animation to target block
		addPulseAnimation(targetBlock as HTMLElement);

		// Scroll with smooth animation, centering the block
		targetBlock.scrollIntoView({
			behavior: 'smooth',
			block: 'center',
			inline: 'nearest'
		});

		// Mark scrolling as complete after animation duration (300ms)
		if (scrollCompleteTimeout) {
			clearTimeout(scrollCompleteTimeout);
		}
		scrollCompleteTimeout = setTimeout(() => {
			if (!scrollAnimationController?.signal.aborted) {
				isScrolling = false;
				scrollAnimationController = null;
			}
			scrollCompleteTimeout = null;
		}, 300);
	}

	/**
	 * Handle block click from left pane - scroll right pane to matching block.
	 */
	function handleLeftPaneBlockClick(event: CustomEvent<{ blockId: string }>) {
		const blockId = event.detail.blockId;
		scrollToBlock(blockId, rightPane);
		announceNavigation('source');
	}

	/**
	 * Handle block click from right pane - scroll left pane to matching block.
	 */
	function handleRightPaneBlockClick(event: CustomEvent<{ blockId: string }>) {
		const blockId = event.detail.blockId;
		scrollToBlock(blockId, leftPane);
		announceNavigation('translation');
	}

	/**
	 * Cancel scroll animation on user interaction.
	 */
	function handleUserScroll() {
		if (isScrolling && scrollAnimationController) {
			scrollAnimationController.abort();
			isScrolling = false;
			scrollAnimationController = null;
		}
	}
</script>

<svelte:window
	on:keydown={handleKeydown}
	on:mousemove={handleMouseMove}
	on:mouseup={handleMouseUp}
	on:touchmove={handleTouchMove}
	on:touchend={handleTouchEnd}
/>

<div
	bind:this={containerRef}
	class="dual-pane-layout"
	role="main"
	aria-label="Two-pane reading interface"
>
	<!-- ARIA live region for navigation announcements -->
	<div
		bind:this={navigationAnnouncementElement}
		class="sr-only"
		role="status"
		aria-live="polite"
		aria-atomic="true"
	></div>

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
		on:blockHover={handleBlockHover}
		on:blockLeave={handleBlockLeave}
		on:blockClick={handleLeftPaneBlockClick}
		on:scroll={handleUserScroll}
		style="width: {leftWidth}%;"
	>
		<slot name="left">
			<div class="pane-placeholder">
				<p class="text-gray-500 text-center">No source content</p>
			</div>
		</slot>
	</div>

	<!-- Draggable Divider -->
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<div
		bind:this={divider}
		class="divider"
		class:dragging={isDragging}
		class:hovering={isHovering}
		role="separator"
		aria-label="Resize panes"
		aria-orientation="vertical"
		aria-valuenow={leftWidth}
		aria-valuemin={minPaneWidth}
		aria-valuemax={100 - minPaneWidth}
		on:mousedown={handleDividerMouseDown}
		on:touchstart={handleDividerTouchStart}
		on:mouseenter={() => (isHovering = true)}
		on:mouseleave={() => (isHovering = false)}
	></div>

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
		on:blockHover={handleBlockHover}
		on:blockLeave={handleBlockLeave}
		on:blockClick={handleRightPaneBlockClick}
		on:scroll={handleUserScroll}
		style="width: {100 - leftWidth}%;"
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
		position: relative;
	}

	.pane {
		overflow-y: auto;
		overflow-x: hidden;
		padding: 1rem;
		outline: none;
		position: relative;
		flex-shrink: 0;
	}

	.pane:focus {
		outline: 2px solid #3b82f6;
		outline-offset: -2px;
	}

	.left-pane {
		border-right: none;
		background-color: #ffffff;
	}

	.right-pane {
		background-color: #f9fafb;
	}

	.divider {
		width: 8px;
		background-color: #e5e7eb;
		cursor: col-resize;
		flex-shrink: 0;
		position: relative;
		transition: background-color 0.2s ease;
		user-select: none;
		touch-action: none;
	}

	.divider:hover,
	.divider.hovering {
		background-color: #d1d5db;
	}

	.divider.dragging {
		background-color: #3b82f6;
	}

	/* Visual indicator on divider */
	.divider::before {
		content: '';
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 3px;
		height: 40px;
		background-color: #9ca3af;
		border-radius: 2px;
		transition: background-color 0.2s ease;
	}

	.divider:hover::before,
	.divider.hovering::before {
		background-color: #6b7280;
	}

	.divider.dragging::before {
		background-color: #ffffff;
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
			width: 100% !important; /* Override inline styles on mobile */
		}

		.left-pane {
			border-right: none;
			border-bottom: 1px solid #e5e7eb;
		}

		.divider {
			display: none; /* Hide divider on mobile */
		}
	}

	/* Ensure scroll position is maintained on resize */
	.pane {
		scroll-behavior: smooth;
	}

	/* Screen reader only content */
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

	/* Pulse animation for block navigation feedback */
	:global(.block-pulse) {
		animation: pulse-highlight 0.6s ease-in-out;
	}

	@keyframes pulse-highlight {
		0% {
			background-color: transparent;
			transform: scale(1);
		}
		50% {
			background-color: #dbeafe;
			transform: scale(1.02);
		}
		100% {
			background-color: transparent;
			transform: scale(1);
		}
	}
</style>
