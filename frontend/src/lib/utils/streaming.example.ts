/**
 * Example usage of the streaming translation utility.
 *
 * This file demonstrates how to integrate the SSE streaming utility
 * with the TranslationPane component for progressive block rendering.
 *
 * @see src/lib/utils/streaming.ts
 * @see src/lib/components/TranslationPane.svelte
 */

import { streamTranslation, type StreamTranslationRequest } from '$lib/utils/streaming';
import type { ContentBlock } from '$lib/types/api';

/**
 * Example: Stream translation with progressive rendering.
 *
 * This function demonstrates the complete workflow:
 * 1. Initialize content blocks with loading state
 * 2. Start SSE stream to backend
 * 3. Update blocks progressively as translations arrive
 * 4. Handle errors gracefully
 * 5. Show completion state
 */
export async function exampleStreamTranslation(
	sourceBlocks: ContentBlock[],
	targetLanguage: string,
	provider: string,
	apiKey: string,
	onUpdate: (blocks: ContentBlock[]) => void,
	onError: (message: string) => void,
	onComplete: () => void,
	signal?: AbortSignal
): Promise<void> {
	// Step 1: Initialize blocks with loading state
	const translationBlocks: ContentBlock[] = sourceBlocks.map((block) => ({
		...block,
		text: '', // Start with empty translation
		metadata: {
			...block.metadata,
			loading: true // Show skeleton loader
		}
	}));

	// Update UI immediately with loading state
	onUpdate([...translationBlocks]);

	// Step 2: Prepare streaming request
	const request: StreamTranslationRequest = {
		content_blocks: sourceBlocks.map((block) => ({
			id: block.id,
			type: block.type,
			text: block.text,
			metadata: block.metadata
		})),
		target_language: targetLanguage,
		provider,
		api_key: apiKey
	};

	// Step 3: Start streaming
	try {
		await streamTranslation(
			request,
			{
				// Handle each translated block
				onBlock: (event) => {
					// Find the block and update it
					const blockIndex = translationBlocks.findIndex((b) => b.id === event.block_id);
					if (blockIndex !== -1) {
						translationBlocks[blockIndex] = {
							...translationBlocks[blockIndex],
							text: event.translation,
							metadata: {
								...translationBlocks[blockIndex].metadata,
								loading: false, // Remove loading state
								tokens_used: event.tokens_used
							}
						};

						// Update UI with new translation
						onUpdate([...translationBlocks]);
					}
				},

				// Handle errors (per-block or stream-level)
				onError: (error) => {
					if (error.block_id) {
						// Per-block error - mark this block as failed
						const blockIndex = translationBlocks.findIndex((b) => b.id === error.block_id);
						if (blockIndex !== -1) {
							translationBlocks[blockIndex] = {
								...translationBlocks[blockIndex],
								text: `Error: ${error.message}`,
								metadata: {
									...translationBlocks[blockIndex].metadata,
									loading: false,
									error: true,
									error_code: error.code
								}
							};
							onUpdate([...translationBlocks]);
						}
					} else {
						// Stream-level error - notify user
						onError(`Translation error: ${error.message}`);
					}
				},

				// Handle completion
				onComplete: (done) => {
					// All blocks processed (some may have failed)
					console.log(
						`Translation complete: ${done.blocks_translated} succeeded, ${done.blocks_failed} failed`
					);
					console.log(`Total tokens used: ${done.total_tokens}`);
					console.log(`Processing time: ${done.processing_time}s`);

					onComplete();
				}
			},
			{
				signal, // For cancellation
				maxRetries: 3,
				retryDelay: 1000
			}
		);
	} catch (error) {
		// Connection failed after retries - fallback to non-streaming
		console.error('Streaming failed, consider fallback to regular API', error);
		onError('Failed to connect to translation service. Please try again.');
	}
}

/**
 * Example: Cancel ongoing translation stream.
 *
 * Use AbortController to cancel a stream mid-way.
 */
export function exampleCancelStream() {
	const abortController = new AbortController();

	// Start streaming with abort signal
	exampleStreamTranslation(
		[], // blocks
		'es',
		'openai',
		'key',
		() => {},
		() => {},
		() => {},
		abortController.signal // Pass signal
	).catch((error) => {
		console.log('Stream cancelled:', error);
	});

	// Later: Cancel the stream
	setTimeout(() => {
		abortController.abort();
		console.log('User cancelled translation');
	}, 5000);
}

/**
 * Example: Integrate with Svelte component.
 *
 * This shows how to use the streaming utility in a Svelte component
 * with TranslationPane for progressive rendering.
 */
export const svelteIntegrationExample = `
<script lang="ts">
  import { streamTranslation } from '$lib/utils/streaming';
  import TranslationPane from '$lib/components/TranslationPane.svelte';
  import type { ContentBlock } from '$lib/types/api';

  let sourceBlocks: ContentBlock[] = [
    { id: '1', type: 'paragraph', text: 'Hello world', metadata: {} },
    { id: '2', type: 'heading', text: 'Welcome', metadata: { level: 1 } },
  ];

  let translatedBlocks: ContentBlock[] = [];
  let isTranslating = false;
  let error: string | null = null;
  let abortController: AbortController | null = null;

  async function startTranslation() {
    isTranslating = true;
    error = null;
    abortController = new AbortController();

    // Initialize with loading state
    translatedBlocks = sourceBlocks.map(block => ({
      ...block,
      text: '',
      metadata: { ...block.metadata, loading: true }
    }));

    try {
      await streamTranslation(
        {
          content_blocks: sourceBlocks,
          target_language: 'es',
          provider: 'openai',
          api_key: 'your-api-key'
        },
        {
          onBlock: (event) => {
            const index = translatedBlocks.findIndex(b => b.id === event.block_id);
            if (index !== -1) {
              translatedBlocks[index] = {
                ...translatedBlocks[index],
                text: event.translation,
                metadata: { ...translatedBlocks[index].metadata, loading: false }
              };
              translatedBlocks = [...translatedBlocks]; // Trigger reactivity
            }
          },
          onError: (err) => {
            error = err.message;
          },
          onComplete: (done) => {
            isTranslating = false;
            console.log(\`Translated \${done.blocks_translated} blocks\`);
          }
        },
        { signal: abortController.signal }
      );
    } catch (err) {
      error = 'Translation failed';
      isTranslating = false;
    }
  }

  function cancelTranslation() {
    if (abortController) {
      abortController.abort();
      isTranslating = false;
    }
  }
</script>

<div>
  <button on:click={startTranslation} disabled={isTranslating}>
    Translate
  </button>
  
  {#if isTranslating}
    <button on:click={cancelTranslation}>
      Cancel
    </button>
  {/if}

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <TranslationPane blocks={translatedBlocks} loading={isTranslating} />
</div>
`;
