/**
 * Unit tests for BlockRetranslate component.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render } from '../test-utils';
import { screen, fireEvent, waitFor } from '@testing-library/svelte';
import BlockRetranslate from './BlockRetranslate.svelte';
import { configStore } from '$lib/stores/config';
import type { ContentBlock } from '$lib/types/api';
import * as apiUtils from '$lib/utils/api';

// Mock the API client
vi.mock('$lib/utils/api', () => ({
	apiClient: {
		post: vi.fn()
	}
}));

describe('BlockRetranslate Component', () => {
	const mockBlock: ContentBlock = {
		id: 'block-1',
		type: 'paragraph',
		text: 'Hola mundo',
		metadata: {}
	};

	const mockOriginalText = 'Hello world';

	beforeEach(() => {
		// Reset config store with API key
		configStore.update((state) => ({
			...state,
			provider: 'openai',
			model: 'gpt-4',
			target_language: 'es',
			api_key: 'sk-test-key'
		}));

		// Clear all mocks
		vi.clearAllMocks();
	});

	afterEach(() => {
		// Restore body overflow
		document.body.style.overflow = '';
	});

	describe('Rendering', () => {
		it('renders modal with correct title', () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			expect(screen.getByRole('dialog')).toBeInTheDocument();
			expect(screen.getByText('Re-translate Block')).toBeInTheDocument();
		});

		it('displays original text', () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			expect(screen.getByTestId('original-text')).toHaveTextContent(mockOriginalText);
		});

		it('displays current translation', () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			expect(screen.getByTestId('current-translation')).toHaveTextContent(mockBlock.text);
		});

		it('shows model selector with OpenAI models by default', () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const modelSelect = screen.getByTestId('model-select') as HTMLSelectElement;
			expect(modelSelect).toBeInTheDocument();

			const options = Array.from(modelSelect.options).map((opt) => opt.value);
			expect(options).toContain('gpt-4');
			expect(options).toContain('gpt-4-turbo');
			expect(options).toContain('gpt-3.5-turbo');
		});

		it('shows custom prompt textarea', () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const promptTextarea = screen.getByTestId('custom-prompt');
			expect(promptTextarea).toBeInTheDocument();
			expect(promptTextarea).toHaveAttribute('placeholder');
		});

		it('shows re-translate button', () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			expect(screen.getByTestId('retranslate-button')).toBeInTheDocument();
		});

		it('shows accept and discard buttons', () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			expect(screen.getByTestId('accept-button')).toBeInTheDocument();
			expect(screen.getByTestId('discard-button')).toBeInTheDocument();
		});
	});

	describe('Model Selection', () => {
		it('shows Anthropic models when provider is anthropic', () => {
			configStore.update((state) => ({
				...state,
				provider: 'anthropic',
				model: 'claude-3-opus-20240229'
			}));

			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const modelSelect = screen.getByTestId('model-select') as HTMLSelectElement;
			const options = Array.from(modelSelect.options).map((opt) => opt.value);

			expect(options).toContain('claude-3-opus-20240229');
			expect(options).toContain('claude-3-sonnet-20240229');
			expect(options).toContain('claude-3-haiku-20240307');
		});

		it('allows changing model', async () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const modelSelect = screen.getByTestId('model-select');
			await fireEvent.change(modelSelect, { target: { value: 'gpt-4-turbo' } });

			expect((modelSelect as HTMLSelectElement).value).toBe('gpt-4-turbo');
		});
	});

	describe('Custom Prompt', () => {
		it('allows entering custom prompt', async () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const promptTextarea = screen.getByTestId('custom-prompt');
			await fireEvent.input(promptTextarea, {
				target: { value: 'Make it more formal' }
			});

			expect((promptTextarea as HTMLTextAreaElement).value).toBe('Make it more formal');
		});
	});

	describe('Re-translation', () => {
		it('calls API with correct parameters when re-translate is clicked', async () => {
			const mockApiResponse = {
				data: {
					translated_blocks: [
						{
							id: 'block-1',
							type: 'paragraph',
							text: '¡Hola, mundo!',
							metadata: {}
						}
					]
				},
				request_id: 'test-request-id'
			};

			vi.mocked(apiUtils.apiClient.post).mockResolvedValue(mockApiResponse);

			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			// Enter custom prompt
			const promptTextarea = screen.getByTestId('custom-prompt');
			await fireEvent.input(promptTextarea, {
				target: { value: 'Use exclamation marks' }
			});

			// Click re-translate
			const retranslateButton = screen.getByTestId('retranslate-button');
			await fireEvent.click(retranslateButton);

			await waitFor(() => {
				expect(apiUtils.apiClient.post).toHaveBeenCalledWith('/api/v1/translate', {
					content_blocks: [
						{
							id: 'block-1',
							type: 'paragraph',
							text: mockOriginalText,
							metadata: {
								custom_prompt: 'Use exclamation marks'
							}
						}
					],
					target_language: 'es',
					provider: 'openai',
					model: 'gpt-4',
					api_key: 'sk-test-key'
				});
			});
		});

		it('displays new translation after successful re-translation', async () => {
			const newTranslationText = '¡Hola, mundo!';
			const mockApiResponse = {
				data: {
					translated_blocks: [
						{
							id: 'block-1',
							type: 'paragraph',
							text: newTranslationText,
							metadata: {}
						}
					]
				},
				request_id: 'test-request-id'
			};

			vi.mocked(apiUtils.apiClient.post).mockResolvedValue(mockApiResponse);

			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const retranslateButton = screen.getByTestId('retranslate-button');
			await fireEvent.click(retranslateButton);

			await waitFor(() => {
				expect(screen.getByTestId('new-translation')).toHaveTextContent(newTranslationText);
			});
		});

		it('shows loading state during translation', async () => {
			vi.mocked(apiUtils.apiClient.post).mockImplementation(
				() =>
					new Promise((resolve) => {
						setTimeout(
							() =>
								resolve({
									data: {
										translated_blocks: [{ id: 'block-1', type: 'paragraph', text: 'Test', metadata: {} }]
									},
									request_id: 'test'
								}),
							100
						);
					})
			);

			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const retranslateButton = screen.getByTestId('retranslate-button');
			await fireEvent.click(retranslateButton);

			expect(screen.getByText('Translating...')).toBeInTheDocument();
			expect(retranslateButton).toBeDisabled();
		});

		it('displays error message on translation failure', async () => {
			vi.mocked(apiUtils.apiClient.post).mockRejectedValue(new Error('API error occurred'));

			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const retranslateButton = screen.getByTestId('retranslate-button');
			await fireEvent.click(retranslateButton);

			await waitFor(() => {
				expect(screen.getByTestId('error-message')).toHaveTextContent('API error occurred');
			});
		});

		it('shows warning when API key is missing', () => {
			configStore.update((state) => ({
				...state,
				api_key: ''
			}));

			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			expect(
				screen.getByText('Please configure your API key in the settings')
			).toBeInTheDocument();
			expect(screen.getByTestId('retranslate-button')).toBeDisabled();
		});
	});

	describe('Accept Action', () => {
		it('dispatches accept event with new translation', async () => {
			const newTranslationText = '¡Hola, mundo!';
			const mockApiResponse = {
				data: {
					translated_blocks: [
						{
							id: 'block-1',
							type: 'paragraph',
							text: newTranslationText,
							metadata: {}
						}
					]
				},
				request_id: 'test-request-id'
			};

			vi.mocked(apiUtils.apiClient.post).mockResolvedValue(mockApiResponse);

			const { component } = render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			let acceptEventData: { blockId: string; newText: string } | null = null;
			component.$on('accept', (event) => {
				acceptEventData = event.detail;
			});

			// Re-translate first
			const retranslateButton = screen.getByTestId('retranslate-button');
			await fireEvent.click(retranslateButton);

			await waitFor(() => {
				expect(screen.getByTestId('new-translation')).toBeInTheDocument();
			});

			// Accept the new translation
			const acceptButton = screen.getByTestId('accept-button');
			await fireEvent.click(acceptButton);

			expect(acceptEventData).toEqual({
				blockId: 'block-1',
				newText: newTranslationText
			});
		});

		it('accept button is disabled before translation completes', () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const acceptButton = screen.getByTestId('accept-button');
			expect(acceptButton).toBeDisabled();
		});

		it('accept button is enabled after successful translation', async () => {
			const mockApiResponse = {
				data: {
					translated_blocks: [
						{
							id: 'block-1',
							type: 'paragraph',
							text: '¡Hola, mundo!',
							metadata: {}
						}
					]
				},
				request_id: 'test-request-id'
			};

			vi.mocked(apiUtils.apiClient.post).mockResolvedValue(mockApiResponse);

			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const retranslateButton = screen.getByTestId('retranslate-button');
			await fireEvent.click(retranslateButton);

			await waitFor(() => {
				const acceptButton = screen.getByTestId('accept-button');
				expect(acceptButton).not.toBeDisabled();
			});
		});
	});

	describe('Discard Action', () => {
		it('dispatches discard event when discard is clicked', async () => {
			const { component } = render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			let discardEventData: { blockId: string } | null = null;
			component.$on('discard', (event) => {
				discardEventData = event.detail;
			});

			const discardButton = screen.getByTestId('discard-button');
			await fireEvent.click(discardButton);

			expect(discardEventData).toEqual({
				blockId: 'block-1'
			});
		});
	});

	describe('Close Action', () => {
		it('dispatches close event when close button is clicked', async () => {
			const { component } = render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			let closeEventFired = false;
			component.$on('close', () => {
				closeEventFired = true;
			});

			const closeButton = screen.getByTestId('close-button');
			await fireEvent.click(closeButton);

			expect(closeEventFired).toBe(true);
		});

		it('calls onClose callback when provided', async () => {
			const onClose = vi.fn();

			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText,
					onClose
				}
			});

			const closeButton = screen.getByTestId('close-button');
			await fireEvent.click(closeButton);

			expect(onClose).toHaveBeenCalled();
		});

		it('closes when backdrop is clicked', async () => {
			const { component } = render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			let closeEventFired = false;
			component.$on('close', () => {
				closeEventFired = true;
			});

			const backdrop = screen.getByTestId('modal-backdrop');
			await fireEvent.click(backdrop);

			expect(closeEventFired).toBe(true);
		});
	});

	describe('Keyboard Shortcuts', () => {
		it('does not accept with Ctrl+Enter before translation completes', async () => {
			const { component } = render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			let acceptEventFired = false;
			component.$on('accept', () => {
				acceptEventFired = true;
			});

			// Press Ctrl+Enter before translation - nothing should happen
			const event = new KeyboardEvent('keydown', { 
				key: 'Enter', 
				ctrlKey: true, 
				bubbles: true 
			});
			document.dispatchEvent(event);

			// Wait a bit to ensure no event was fired
			await new Promise(resolve => setTimeout(resolve, 100));
			expect(acceptEventFired).toBe(false);
		});
	});

	describe('Accessibility', () => {
		it('has proper ARIA attributes', () => {
			render(BlockRetranslate, {
				props: {
					block: mockBlock,
					originalText: mockOriginalText
				}
			});

			const dialog = screen.getByRole('dialog');
			expect(dialog).toHaveAttribute('aria-modal', 'true');
			expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title');
		});
	});
});
