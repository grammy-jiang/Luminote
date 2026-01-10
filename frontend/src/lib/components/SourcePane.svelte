<script lang="ts">
	import type { ContentBlock } from '$lib/types/api';

	/**
	 * SourcePane Component
	 *
	 * Displays extracted content blocks in the left pane of the DualPaneLayout.
	 * Supports multiple block types with proper semantic HTML and accessibility.
	 *
	 * Features:
	 * - Renders ContentBlock array with proper formatting
	 * - Heading hierarchy (H1-H6) based on metadata.level
	 * - Code blocks with syntax highlighting support
	 * - Images with lazy loading and alt text
	 * - Lists (ordered and unordered) based on metadata.ordered
	 * - Blockquotes with visual styling
	 * - Maintains block IDs for synchronization
	 * - Responsive typography
	 * - Accessible markup (semantic HTML, ARIA labels)
	 *
	 * Note: Text content is escaped for security. HTML links in block.text will
	 * be rendered as plain text, not as clickable anchors.
	 */

	export let blocks: ContentBlock[] = [];

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
</script>

<div class="source-pane-content" role="article" aria-label="Source content">
	{#if blocks.length === 0}
		<div class="empty-state">
			<p class="empty-state-text">No content blocks to display</p>
		</div>
	{:else}
		{#each blocks as block (block.id)}
			{#if block.type === 'paragraph'}
				<p
					id={block.id}
					data-block-id={block.id}
					data-block-type="paragraph"
					class="block-paragraph"
				>
					{block.text}
				</p>
			{:else if block.type === 'heading'}
				{@const level = getHeadingLevel(block.metadata)}
				{@const tag = `h${level}`}
				<svelte:element
					this={tag}
					id={block.id}
					data-block-id={block.id}
					data-block-type="heading"
					class="block-heading block-heading-{level}"
				>
					{block.text}
				</svelte:element>
			{:else if block.type === 'code'}
				{@const language = getCodeLanguage(block.metadata)}
				<pre
					id={block.id}
					data-block-id={block.id}
					data-block-type="code"
					class="block-code"
					aria-label="Code block{language !== 'plaintext' ? ` in ${language}` : ''}"><code
						class="language-{language}">{block.text}</code
					></pre>
			{:else if block.type === 'list'}
				{@const items = parseListItems(block.text)}
				{@const ordered = isOrderedList(block.metadata)}
				{#if ordered}
					<ol
						id={block.id}
						data-block-id={block.id}
						data-block-type="list"
						class="block-list block-list-ordered"
					>
						{#each items as item}
							<li>{item}</li>
						{/each}
					</ol>
				{:else}
					<ul
						id={block.id}
						data-block-id={block.id}
						data-block-type="list"
						class="block-list block-list-unordered"
					>
						{#each items as item}
							<li>{item}</li>
						{/each}
					</ul>
				{/if}
			{:else if block.type === 'quote'}
				<blockquote
					id={block.id}
					data-block-id={block.id}
					data-block-type="quote"
					class="block-quote"
				>
					{block.text}
				</blockquote>
			{:else if block.type === 'image'}
				{@const alt = String(block.metadata.alt || 'Image')}
				{@const rawSrc = String(block.metadata.src || block.text)}
				{@const src = validateImageSrc(rawSrc)}
				{@const width = block.metadata.width ? Number(block.metadata.width) : undefined}
				{@const height = block.metadata.height ? Number(block.metadata.height) : undefined}
				{#if src}
					<figure
						id={block.id}
						data-block-id={block.id}
						data-block-type="image"
						class="block-image"
					>
						<img {src} {alt} loading="lazy" {width} {height} />
						{#if block.text && block.text !== rawSrc}
							<figcaption>{block.text}</figcaption>
						{/if}
					</figure>
				{/if}
			{/if}
		{/each}
	{/if}
</div>

<style>
	.source-pane-content {
		width: 100%;
		max-width: 100%;
		color: #1f2937;
		line-height: 1.7;
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
		border-left: 4px solid #3b82f6;
		margin: 1rem 0;
		font-style: italic;
		color: #4b5563;
		background-color: #f9fafb;
		padding: 1rem 1rem 1rem 1.5rem;
		border-radius: 0.25rem;
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
		.source-pane-content {
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
</style>
