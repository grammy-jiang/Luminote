<script lang="ts">
	import { createEventDispatcher, onDestroy, getContext } from 'svelte';
	import type { ContentBlock } from '$lib/types/api';
	import type { Writable } from 'svelte/store';

	/**
	 * TranslationPane Component
	 *
	 * Displays translated content blocks in the right pane of the DualPaneLayout.
	 * Optimized for reading translated text with enhanced typography and RTL support.
	 *
	 * Features:
	 * - Renders ContentBlock array with proper formatting
	 * - Heading hierarchy (H1-H6) based on metadata.level
	 * - Code blocks with syntax highlighting support
	 * - Images with lazy loading and alt text
	 * - Lists (ordered and unordered) based on metadata.ordered
	 * - Blockquotes with visual styling
	 * - Loading state indicators for in-progress blocks
	 * - RTL text support for Arabic, Hebrew, etc.
	 * - Optimized line height (1.7) for reading comfort
	 * - Maintains block IDs for synchronization with source pane
	 * - Responsive typography
	 * - Accessible markup (semantic HTML, ARIA labels)
	 * - Block hover highlighting for cross-pane synchronization
	 *
	 * Note: Text content is escaped for security. HTML links in block.text will
	 * be rendered as plain text, not as clickable anchors.
	 */

	export let blocks: ContentBlock[] = [];
	export let loading: boolean = false;
	export let highlightedBlockId: string | null = null;

	// Try to get highlightedBlockId from context if not provided as prop
	const highlightedBlockIdContext = getContext<Writable<string | null>>('highlightedBlockId');

	// Use context if available, otherwise use prop
	$: effectiveHighlightedBlockId = highlightedBlockIdContext
		? $highlightedBlockIdContext
		: highlightedBlockId;

	const dispatch = createEventDispatcher<{
		blockHover: { blockId: string };
		blockLeave: { blockId: string };
		blockClick: { blockId: string };
	}>();

	let hoverTimeout: ReturnType<typeof setTimeout> | null = null;

	// Clean up timeout on component destroy to prevent memory leaks
	onDestroy(() => {
		if (hoverTimeout) {
			clearTimeout(hoverTimeout);
			hoverTimeout = null;
		}
	});

	/**
	 * Handle mouse enter on a block with debouncing.
	 */
	function handleBlockMouseEnter(blockId: string) {
		if (hoverTimeout) {
			clearTimeout(hoverTimeout);
		}
		hoverTimeout = setTimeout(() => {
			dispatch('blockHover', { blockId });
		}, 50);
	}

	/**
	 * Handle mouse leave on a block.
	 */
	function handleBlockMouseLeave(blockId: string) {
		if (hoverTimeout) {
			clearTimeout(hoverTimeout);
			hoverTimeout = null;
		}
		dispatch('blockLeave', { blockId });
	}

	/**
	 * Handle keyboard focus on a block.
	 */
	function handleBlockFocus(blockId: string) {
		dispatch('blockHover', { blockId });
	}

	/**
	 * Handle keyboard blur on a block.
	 */
	function handleBlockBlur(blockId: string) {
		dispatch('blockLeave', { blockId });
	}

	/**
	 * Handle block click to navigate to matching source block.
	 */
	function handleBlockClick(blockId: string) {
		dispatch('blockClick', { blockId });
	}

	/**
	 * Handle keyboard Enter/Space key to trigger navigation.
	 */
	function handleBlockKeydown(event: KeyboardEvent, blockId: string) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			dispatch('blockClick', { blockId });
		} else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
			event.preventDefault();
			navigateToAdjacentBlock(blockId, event.key === 'ArrowDown' ? 'next' : 'previous');
		} else if (event.key === 'Home') {
			event.preventDefault();
			navigateToFirstBlock();
		} else if (event.key === 'End') {
			event.preventDefault();
			navigateToLastBlock();
		}
	}

	/**
	 * Navigate to the adjacent block (next or previous).
	 */
	function navigateToAdjacentBlock(currentBlockId: string, direction: 'next' | 'previous') {
		const currentIndex = blocks.findIndex((block) => block.id === currentBlockId);
		if (currentIndex === -1) return;

		const targetIndex = direction === 'next' ? currentIndex + 1 : currentIndex - 1;
		if (targetIndex >= 0 && targetIndex < blocks.length) {
			const targetBlock = blocks[targetIndex];
			focusBlock(targetBlock.id);
		}
	}

	/**
	 * Navigate to the first block.
	 */
	function navigateToFirstBlock() {
		if (blocks.length > 0) {
			focusBlock(blocks[0].id);
		}
	}

	/**
	 * Navigate to the last block.
	 */
	function navigateToLastBlock() {
		if (blocks.length > 0) {
			focusBlock(blocks[blocks.length - 1].id);
		}
	}

	/**
	 * Focus a specific block by its ID.
	 */
	function focusBlock(blockId: string) {
		// Use setTimeout to ensure DOM is updated
		setTimeout(() => {
			const blockElement = document.querySelector(`[data-block-id="${blockId}"]`) as HTMLElement;
			if (blockElement) {
				blockElement.focus();
				// Scroll into view if needed (check if function exists for test compatibility)
				if (typeof blockElement.scrollIntoView === 'function') {
					blockElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
				}
			}
		}, 0);
	}

	/**
	 * RTL language codes (ISO 639-1).
	 * These languages are written right-to-left.
	 */
	const RTL_LANGUAGES = new Set([
		'ar', // Arabic
		'he', // Hebrew
		'fa', // Persian
		'ur', // Urdu
		'yi' // Yiddish
	]);

	/**
	 * Detect if text direction should be RTL based on language metadata.
	 * Falls back to auto detection if language not specified.
	 */
	function getTextDirection(metadata: Record<string, unknown>): 'ltr' | 'rtl' | 'auto' {
		const lang = metadata.language;
		if (typeof lang === 'string' && lang.length === 2) {
			return RTL_LANGUAGES.has(lang.toLowerCase()) ? 'rtl' : 'ltr';
		}
		// Use 'auto' to let browser detect based on content
		return 'auto';
	}

	/**
	 * Parse list items from text content.
	 * Handles both "- Item" and "1. Item" formats.
	 */
	function parseListItems(text: string): string[] {
		return text
			.split('\n')
			.map((line) => line.trim())
			.filter((line) => line.length > 0)
			.map((line) => {
				// Remove leading markers (-, *, 1., 2., etc.)
				return line.replace(/^[-*]\s+/, '').replace(/^\d+\.\s+/, '');
			});
	}

	/**
	 * Get heading level from metadata, defaulting to h2.
	 */
	function getHeadingLevel(metadata: Record<string, unknown>): number {
		const level = metadata.level;
		if (typeof level === 'number' && level >= 1 && level <= 6) {
			return level;
		}
		return 2; // Default to h2
	}

	/**
	 * Get language from code block metadata for syntax highlighting.
	 * Validates that language contains only safe characters.
	 */
	function getCodeLanguage(metadata: Record<string, unknown>): string {
		const lang = metadata.language;
		if (typeof lang === 'string') {
			// Validate language contains only alphanumeric, hyphens, and underscores
			if (/^[a-zA-Z0-9_-]+$/.test(lang)) {
				return lang;
			}
		}
		return 'plaintext';
	}

	/**
	 * Check if list is ordered from metadata.
	 */
	function isOrderedList(metadata: Record<string, unknown>): boolean {
		return metadata.ordered === true;
	}

	/**
	 * Validate image src URL to prevent XSS attacks.
	 * Only allows http:// and https:// protocols.
	 */
	function validateImageSrc(src: string): string {
		if (!src) return '';
		try {
			const url = new URL(src);
			// Only allow http and https protocols
			if (url.protocol === 'http:' || url.protocol === 'https:') {
				return src;
			}
		} catch {
			// Invalid URL, return empty string
		}
		return '';
	}

	/**
	 * Check if a block is loading based on metadata.
	 */
	function isBlockLoading(metadata: Record<string, unknown>): boolean {
		return metadata.loading === true;
	}
</script>

<div class="translation-pane-content" role="article" aria-label="Translation content">
	{#if blocks.length === 0}
		<div class="empty-state">
			{#if loading}
				<div class="loading-indicator" role="status" aria-live="polite">
					<div class="spinner"></div>
					<p class="loading-text">Translating content...</p>
				</div>
			{:else}
				<p class="empty-state-text">No translated content to display</p>
			{/if}
		</div>
	{:else}
		{#each blocks as block (block.id)}
			{@const direction = getTextDirection(block.metadata)}
			{@const blockLoading = isBlockLoading(block.metadata)}

			{#if block.type === 'paragraph'}
				<div class="block-wrapper" class:block-loading={blockLoading}>
					<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
					<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
					<p
						id={block.id}
						data-block-id={block.id}
						data-block-type="paragraph"
						class="block-paragraph block-hoverable"
						class:block-highlighted={effectiveHighlightedBlockId === block.id}
						dir={direction}
						tabindex="0"
						on:mouseenter={() => handleBlockMouseEnter(block.id)}
						on:mouseleave={() => handleBlockMouseLeave(block.id)}
						on:focus={() => handleBlockFocus(block.id)}
						on:blur={() => handleBlockBlur(block.id)}
						on:click={() => handleBlockClick(block.id)}
						on:keydown={(e) => handleBlockKeydown(e, block.id)}
					>
						{block.text}
					</p>
					{#if blockLoading}
						<div class="block-loading-overlay">
							<div class="spinner-small"></div>
						</div>
					{/if}
				</div>
			{:else if block.type === 'heading'}
				{@const level = getHeadingLevel(block.metadata)}
				{@const tag = `h${level}`}
				<div class="block-wrapper" class:block-loading={blockLoading}>
					<!-- svelte-ignore a11y-no-static-element-interactions -->
					<svelte:element
						this={tag}
						id={block.id}
						data-block-id={block.id}
						data-block-type="heading"
						class="block-heading block-heading-{level} block-hoverable"
						class:block-highlighted={effectiveHighlightedBlockId === block.id}
						dir={direction}
						tabindex="0"
						on:mouseenter={() => handleBlockMouseEnter(block.id)}
						on:mouseleave={() => handleBlockMouseLeave(block.id)}
						on:focus={() => handleBlockFocus(block.id)}
						on:blur={() => handleBlockBlur(block.id)}
						on:click={() => handleBlockClick(block.id)}
						on:keydown={(e) => handleBlockKeydown(e, block.id)}
					>
						{block.text}
					</svelte:element>
					{#if blockLoading}
						<div class="block-loading-overlay">
							<div class="spinner-small"></div>
						</div>
					{/if}
				</div>
			{:else if block.type === 'code'}
				{@const language = getCodeLanguage(block.metadata)}
				<div class="block-wrapper" class:block-loading={blockLoading}>
					<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
					<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
					<pre
						id={block.id}
						data-block-id={block.id}
						data-block-type="code"
						class="block-code block-hoverable"
						class:block-highlighted={effectiveHighlightedBlockId === block.id}
						dir={direction}
						tabindex="0"
						aria-label="Code block{language !== 'plaintext' ? ` in ${language}` : ''}"
						on:mouseenter={() => handleBlockMouseEnter(block.id)}
						on:mouseleave={() => handleBlockMouseLeave(block.id)}
						on:focus={() => handleBlockFocus(block.id)}
						on:blur={() => handleBlockBlur(block.id)}
						on:click={() => handleBlockClick(block.id)}
						on:keydown={(e) => handleBlockKeydown(e, block.id)}><code class="language-{language}"
							>{block.text}</code
						></pre>
					{#if blockLoading}
						<div class="block-loading-overlay">
							<div class="spinner-small"></div>
						</div>
					{/if}
				</div>
			{:else if block.type === 'list'}
				{@const items = parseListItems(block.text)}
				{@const ordered = isOrderedList(block.metadata)}
				<div class="block-wrapper" class:block-loading={blockLoading}>
					{#if ordered}
						<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
						<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
						<ol
							id={block.id}
							data-block-id={block.id}
							data-block-type="list"
							class="block-list block-list-ordered block-hoverable"
							class:block-highlighted={effectiveHighlightedBlockId === block.id}
							dir={direction}
							tabindex="0"
							on:mouseenter={() => handleBlockMouseEnter(block.id)}
							on:mouseleave={() => handleBlockMouseLeave(block.id)}
							on:focus={() => handleBlockFocus(block.id)}
							on:blur={() => handleBlockBlur(block.id)}
							on:click={() => handleBlockClick(block.id)}
							on:keydown={(e) => handleBlockKeydown(e, block.id)}
						>
							{#each items as item}
								<li>{item}</li>
							{/each}
						</ol>
					{:else}
						<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
						<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
						<ul
							id={block.id}
							data-block-id={block.id}
							data-block-type="list"
							class="block-list block-list-unordered block-hoverable"
							class:block-highlighted={effectiveHighlightedBlockId === block.id}
							dir={direction}
							tabindex="0"
							on:mouseenter={() => handleBlockMouseEnter(block.id)}
							on:mouseleave={() => handleBlockMouseLeave(block.id)}
							on:focus={() => handleBlockFocus(block.id)}
							on:blur={() => handleBlockBlur(block.id)}
							on:click={() => handleBlockClick(block.id)}
							on:keydown={(e) => handleBlockKeydown(e, block.id)}
						>
							{#each items as item}
								<li>{item}</li>
							{/each}
						</ul>
					{/if}
					{#if blockLoading}
						<div class="block-loading-overlay">
							<div class="spinner-small"></div>
						</div>
					{/if}
				</div>
			{:else if block.type === 'quote'}
				<div class="block-wrapper" class:block-loading={blockLoading}>
					<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
					<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
					<blockquote
						id={block.id}
						data-block-id={block.id}
						data-block-type="quote"
						class="block-quote block-hoverable"
						class:block-highlighted={effectiveHighlightedBlockId === block.id}
						dir={direction}
						tabindex="0"
						on:mouseenter={() => handleBlockMouseEnter(block.id)}
						on:mouseleave={() => handleBlockMouseLeave(block.id)}
						on:focus={() => handleBlockFocus(block.id)}
						on:blur={() => handleBlockBlur(block.id)}
						on:click={() => handleBlockClick(block.id)}
						on:keydown={(e) => handleBlockKeydown(e, block.id)}
					>
						{block.text}
					</blockquote>
					{#if blockLoading}
						<div class="block-loading-overlay">
							<div class="spinner-small"></div>
						</div>
					{/if}
				</div>
			{:else if block.type === 'image'}
				{@const alt = String(block.metadata.alt || 'Translated image')}
				{@const rawSrc = String(block.metadata.src || block.text)}
				{@const src = validateImageSrc(rawSrc)}
				{@const width = block.metadata.width ? Number(block.metadata.width) : undefined}
				{@const height = block.metadata.height ? Number(block.metadata.height) : undefined}
				{#if src}
					<div class="block-wrapper" class:block-loading={blockLoading}>
						<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
						<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
						<figure
							id={block.id}
							data-block-id={block.id}
							data-block-type="image"
							class="block-image block-hoverable"
							class:block-highlighted={effectiveHighlightedBlockId === block.id}
							tabindex="0"
							on:mouseenter={() => handleBlockMouseEnter(block.id)}
							on:mouseleave={() => handleBlockMouseLeave(block.id)}
							on:focus={() => handleBlockFocus(block.id)}
							on:blur={() => handleBlockBlur(block.id)}
							on:click={() => handleBlockClick(block.id)}
							on:keydown={(e) => handleBlockKeydown(e, block.id)}
						>
							<img {src} {alt} loading="lazy" {width} {height} />
							{#if block.text && block.text !== rawSrc}
								<figcaption dir={direction}>{block.text}</figcaption>
							{/if}
						</figure>
						{#if blockLoading}
							<div class="block-loading-overlay">
								<div class="spinner-small"></div>
							</div>
						{/if}
					</div>
				{/if}
			{/if}
		{/each}
	{/if}
</div>

<style>
	.translation-pane-content {
		width: 100%;
		max-width: 100%;
		color: #1f2937;
		line-height: 1.7; /* Optimized for reading translated text */
	}

	.empty-state {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 200px;
		padding: 2rem;
	}

	.empty-state-text {
		color: #6b7280;
		text-align: center;
	}

	.loading-indicator {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
	}

	.loading-text {
		color: #6b7280;
		font-size: 0.875rem;
	}

	/* Spinner animation */
	.spinner {
		width: 40px;
		height: 40px;
		border: 3px solid #e5e7eb;
		border-top-color: #3b82f6;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	.spinner-small {
		width: 20px;
		height: 20px;
		border: 2px solid #e5e7eb;
		border-top-color: #3b82f6;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	/* Block wrapper for loading states */
	.block-wrapper {
		position: relative;
	}

	.block-wrapper.block-loading {
		opacity: 0.6;
	}

	.block-loading-overlay {
		position: absolute;
		top: 50%;
		right: 0.5rem;
		transform: translateY(-50%);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	/* Paragraph styling */
	.block-paragraph {
		margin-bottom: 1rem;
		font-size: 1rem;
		color: #374151;
	}

	/* Heading styles with hierarchy */
	.block-heading {
		font-weight: 700;
		line-height: 1.3;
		color: #111827;
		margin-top: 1.5rem;
		margin-bottom: 1rem;
	}

	.block-heading-1 {
		font-size: 2.25rem;
		margin-top: 0;
	}

	.block-heading-2 {
		font-size: 1.875rem;
	}

	.block-heading-3 {
		font-size: 1.5rem;
	}

	.block-heading-4 {
		font-size: 1.25rem;
	}

	.block-heading-5 {
		font-size: 1.125rem;
	}

	.block-heading-6 {
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	/* Code block styling */
	.block-code {
		background-color: #f3f4f6;
		border: 1px solid #e5e7eb;
		border-radius: 0.375rem;
		padding: 1rem;
		overflow-x: auto;
		margin-bottom: 1rem;
		font-family: 'Courier New', Courier, monospace;
		font-size: 0.875rem;
		line-height: 1.5;
	}

	.block-code code {
		background: none;
		padding: 0;
		font-size: inherit;
		color: #1f2937;
	}

	/* List styling */
	.block-list {
		margin-bottom: 1rem;
		padding-left: 1.5rem;
	}

	/* RTL list styling */
	.block-list[dir='rtl'] {
		padding-left: 0;
		padding-right: 1.5rem;
	}

	.block-list-unordered {
		list-style-type: disc;
	}

	.block-list-ordered {
		list-style-type: decimal;
	}

	.block-list li {
		margin-bottom: 0.5rem;
		color: #374151;
	}

	/* Blockquote styling */
	.block-quote {
		border-left: 4px solid #10b981;
		margin: 1rem 0;
		font-style: italic;
		color: #4b5563;
		background-color: #f0fdf4;
		padding: 1rem 1rem 1rem 1.5rem;
		border-radius: 0.25rem;
	}

	/* RTL blockquote styling */
	.block-quote[dir='rtl'] {
		border-left: none;
		border-right: 4px solid #10b981;
		padding: 1rem 1.5rem 1rem 1rem;
	}

	/* Image styling */
	.block-image {
		margin: 1.5rem 0;
		text-align: center;
	}

	.block-image img {
		max-width: 100%;
		height: auto;
		border-radius: 0.375rem;
		box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
	}

	.block-image figcaption {
		margin-top: 0.5rem;
		font-size: 0.875rem;
		color: #6b7280;
		font-style: italic;
	}

	/* Responsive typography */
	@media (max-width: 640px) {
		.translation-pane-content {
			font-size: 0.9375rem;
		}

		.block-heading-1 {
			font-size: 1.875rem;
		}

		.block-heading-2 {
			font-size: 1.5rem;
		}

		.block-heading-3 {
			font-size: 1.25rem;
		}

		.block-heading-4,
		.block-heading-5,
		.block-heading-6 {
			font-size: 1rem;
		}

		.block-code {
			font-size: 0.8125rem;
			padding: 0.75rem;
		}
	}

	/* Block highlighting styles */
	.block-highlighted {
		background-color: #fef3c7;
		border-left: 3px solid #f59e0b;
		padding-left: 0.5rem;
		margin-left: -0.5rem; /* Compensate for padding to prevent layout shift */
		transition:
			background-color 0.2s ease,
			border-left 0.2s ease;
		outline: 2px solid #f59e0b;
		outline-offset: 2px;
	}

	/* Ensure keyboard focus is visible */
	[tabindex='0']:focus {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	/* When both highlighted and focused */
	.block-highlighted:focus {
		outline: 2px solid #f59e0b;
	}

	/* Cursor indicates clickable block for navigation */
	.block-hoverable {
		cursor: pointer;
		transition: background-color 0.15s ease-in-out;
	}

	.block-hoverable:hover {
		background-color: rgba(15, 23, 42, 0.03);
	}
</style>
