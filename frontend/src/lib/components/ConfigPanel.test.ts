/**
 * Unit tests for ConfigPanel component.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render } from '../test-utils';
import { screen, fireEvent, waitFor } from '@testing-library/svelte';
import ConfigPanel from './ConfigPanel.svelte';
import { configStore } from '$lib/stores/config';
import type { ConfigState } from '$lib/stores/config';

describe('ConfigPanel Component', () => {
	// Reset config store before each test
	beforeEach(() => {
		configStore.reset();
		// Clear localStorage
		if (typeof window !== 'undefined') {
			localStorage.clear();
		}
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	describe('Rendering', () => {
		it('renders with default values', () => {
			render(ConfigPanel);

			expect(screen.getByRole('form', { name: 'Configuration panel' })).toBeInTheDocument();
			expect(screen.getByText('Configuration')).toBeInTheDocument();
			expect(screen.getByLabelText(/Provider/i)).toBeInTheDocument();
			expect(screen.getByLabelText(/Model/i)).toBeInTheDocument();
			expect(screen.getByLabelText(/Target Language/i)).toBeInTheDocument();
			expect(screen.getByLabelText(/API Key/i)).toBeInTheDocument();
		});

		it('has accessible form elements', () => {
			render(ConfigPanel);

			const providerSelect = screen.getByLabelText(/Provider/i);
			const modelSelect = screen.getByLabelText(/Model/i);
			const languageSelect = screen.getByLabelText(/Target Language/i);
			const apiKeyInput = screen.getByLabelText(/API Key/i);

			expect(providerSelect).toHaveAttribute('aria-required', 'true');
			expect(modelSelect).toHaveAttribute('aria-required', 'true');
			expect(languageSelect).toHaveAttribute('aria-required', 'true');
			expect(apiKeyInput).toHaveAttribute('aria-required', 'true');
		});

		it('shows required indicators', () => {
			render(ConfigPanel);

			const requiredMarks = screen.getAllByLabelText('required');
			expect(requiredMarks).toHaveLength(4); // Provider, Model, Language, API Key
		});
	});

	describe('Provider Dropdown', () => {
		it('displays provider options', () => {
			render(ConfigPanel);

			const providerSelect = screen.getByLabelText(/Provider/i);
			expect(providerSelect).toBeInTheDocument();

			const options = (providerSelect as HTMLSelectElement).options;
			expect(options).toHaveLength(2);
			expect(options[0].value).toBe('openai');
			expect(options[0].text).toBe('OpenAI');
			expect(options[1].value).toBe('anthropic');
			expect(options[1].text).toBe('Anthropic');
		});

		it('defaults to openai provider', () => {
			render(ConfigPanel);

			const providerSelect = screen.getByLabelText(/Provider/i) as HTMLSelectElement;
			expect(providerSelect.value).toBe('openai');
		});

		it('allows changing provider', async () => {
			render(ConfigPanel);

			const providerSelect = screen.getByLabelText(/Provider/i);
			await fireEvent.change(providerSelect, { target: { value: 'anthropic' } });

			expect((providerSelect as HTMLSelectElement).value).toBe('anthropic');
		});
	});

	describe('Model Selector', () => {
		it('displays OpenAI models by default', () => {
			render(ConfigPanel);

			const modelSelect = screen.getByLabelText(/Model/i) as HTMLSelectElement;
			const options = modelSelect.options;

			expect(options).toHaveLength(3);
			expect(options[0].value).toBe('gpt-4');
			expect(options[1].value).toBe('gpt-4-turbo');
			expect(options[2].value).toBe('gpt-3.5-turbo');
		});

		it('updates models when provider changes to Anthropic', async () => {
			render(ConfigPanel);

			const providerSelect = screen.getByLabelText(/Provider/i);
			await fireEvent.change(providerSelect, { target: { value: 'anthropic' } });

			await waitFor(() => {
				const modelSelect = screen.getByLabelText(/Model/i) as HTMLSelectElement;
				const options = modelSelect.options;

				expect(options).toHaveLength(3);
				expect(options[0].value).toContain('claude-3-opus');
				expect(options[1].value).toContain('claude-3-sonnet');
				expect(options[2].value).toContain('claude-3-haiku');
			});
		});

		it('resets model when provider changes', async () => {
			render(ConfigPanel);

			const providerSelect = screen.getByLabelText(/Provider/i);
			const modelSelect = screen.getByLabelText(/Model/i) as HTMLSelectElement;

			// Initially OpenAI with gpt-4
			expect(modelSelect.value).toBe('gpt-4');

			// Change to Anthropic
			await fireEvent.change(providerSelect, { target: { value: 'anthropic' } });

			await waitFor(() => {
				expect(modelSelect.value).toContain('claude-3-opus');
			});
		});

		it('allows selecting different models', async () => {
			render(ConfigPanel);

			const modelSelect = screen.getByLabelText(/Model/i);
			await fireEvent.change(modelSelect, { target: { value: 'gpt-4-turbo' } });

			expect((modelSelect as HTMLSelectElement).value).toBe('gpt-4-turbo');
		});
	});

	describe('API Key Input', () => {
		it('renders password type input', () => {
			render(ConfigPanel);

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			expect(apiKeyInput).toHaveAttribute('type', 'password');
		});

		it('has placeholder text', () => {
			render(ConfigPanel);

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			expect(apiKeyInput).toHaveAttribute('placeholder', 'Enter your API key');
		});

		it('shows security notice', () => {
			render(ConfigPanel);

			expect(
				screen.getByText(/Your API key is stored only in memory and never persisted/i)
			).toBeInTheDocument();
		});

		it('allows entering API key', async () => {
			render(ConfigPanel);

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key-123' } });

			expect((apiKeyInput as HTMLInputElement).value).toBe('sk-test-key-123');
		});
	});

	describe('Target Language Selector', () => {
		it('displays language options', () => {
			render(ConfigPanel);

			const languageSelect = screen.getByLabelText(/Target Language/i) as HTMLSelectElement;
			const options = languageSelect.options;

			expect(options.length).toBeGreaterThan(0);
			// Check for some common languages
			const values = Array.from(options).map((opt) => opt.value);
			expect(values).toContain('en');
			expect(values).toContain('es');
			expect(values).toContain('fr');
			expect(values).toContain('de');
		});

		it('defaults to English', () => {
			render(ConfigPanel);

			const languageSelect = screen.getByLabelText(/Target Language/i) as HTMLSelectElement;
			expect(languageSelect.value).toBe('en');
		});

		it('shows language names with codes', () => {
			render(ConfigPanel);

			const languageSelect = screen.getByLabelText(/Target Language/i) as HTMLSelectElement;
			const options = Array.from(languageSelect.options);

			// Check format: "Name (code)"
			const englishOption = options.find((opt) => opt.value === 'en');
			expect(englishOption?.text).toMatch(/English.*\(en\)/);

			const spanishOption = options.find((opt) => opt.value === 'es');
			expect(spanishOption?.text).toMatch(/Spanish.*\(es\)/);
		});

		it('allows changing target language', async () => {
			render(ConfigPanel);

			const languageSelect = screen.getByLabelText(/Target Language/i);
			await fireEvent.change(languageSelect, { target: { value: 'es' } });

			expect((languageSelect as HTMLSelectElement).value).toBe('es');
		});
	});

	describe('Test Connection Button', () => {
		it('renders test connection button', () => {
			render(ConfigPanel);

			const testButton = screen.getByRole('button', { name: /Test Connection/i });
			expect(testButton).toBeInTheDocument();
			expect(testButton).not.toBeDisabled();
		});

		it('shows loading state while testing', async () => {
			const onTestConnection = vi.fn().mockImplementation(
				() =>
					new Promise((resolve) => {
						setTimeout(() => resolve({ valid: true, message: 'Success' }), 100);
					})
			);

			render(ConfigPanel, { props: { onTestConnection } });

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test' } });

			const testButton = screen.getByRole('button', { name: /Test Connection/i });
			await fireEvent.click(testButton);

			expect(screen.getByRole('button', { name: /Testing.../i })).toBeInTheDocument();
			expect(screen.getByRole('button', { name: /Testing.../i })).toBeDisabled();
		});

		it('calls onTestConnection handler with config', async () => {
			const onTestConnection = vi.fn().mockResolvedValue({
				valid: true,
				message: 'Connection successful'
			});

			render(ConfigPanel, { props: { onTestConnection } });

			// Fill in API key
			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			// Click test button
			const testButton = screen.getByRole('button', { name: /Test Connection/i });
			await fireEvent.click(testButton);

			await waitFor(() => {
				expect(onTestConnection).toHaveBeenCalledWith({
					provider: 'openai',
					model: 'gpt-4',
					target_language: 'en',
					api_key: 'sk-test-key'
				});
			});
		});

		it('displays success message on successful connection', async () => {
			const onTestConnection = vi.fn().mockResolvedValue({
				valid: true,
				message: 'Connection successful'
			});

			render(ConfigPanel, { props: { onTestConnection } });

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			const testButton = screen.getByRole('button', { name: /Test Connection/i });
			await fireEvent.click(testButton);

			await waitFor(() => {
				expect(screen.getByText(/Connection successful/i)).toBeInTheDocument();
			});

			// Check styling - the result-message div itself has the success class
			const successMessage = screen.getByText(/Connection successful/i).closest('.result-message');
			expect(successMessage).toHaveClass('success');
		});

		it('displays error message on failed connection', async () => {
			const onTestConnection = vi.fn().mockResolvedValue({
				valid: false,
				message: 'Invalid API key'
			});

			render(ConfigPanel, { props: { onTestConnection } });

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'invalid-key' } });

			const testButton = screen.getByRole('button', { name: /Test Connection/i });
			await fireEvent.click(testButton);

			await waitFor(() => {
				expect(screen.getByText(/Invalid API key/i)).toBeInTheDocument();
			});

			const errorMessage = screen.getByText(/Invalid API key/i).closest('.result-message');
			expect(errorMessage).toHaveClass('error');
		});

		it('handles connection test exceptions', async () => {
			const onTestConnection = vi.fn().mockRejectedValue(new Error('Network error'));

			render(ConfigPanel, { props: { onTestConnection } });

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			const testButton = screen.getByRole('button', { name: /Test Connection/i });
			await fireEvent.click(testButton);

			await waitFor(() => {
				expect(screen.getByText(/Network error/i)).toBeInTheDocument();
			});
		});

		it('validates form before testing connection', async () => {
			const onTestConnection = vi.fn();

			render(ConfigPanel, { props: { onTestConnection } });

			// Don't fill in API key - should fail validation
			const testButton = screen.getByRole('button', { name: /Test Connection/i });
			await fireEvent.click(testButton);

			await waitFor(() => {
				expect(
					screen.getByText(/Please fix validation errors before testing connection/i)
				).toBeInTheDocument();
			});

			expect(onTestConnection).not.toHaveBeenCalled();
		});
	});

	describe('Save Button', () => {
		it('renders save button', () => {
			render(ConfigPanel);

			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			expect(saveButton).toBeInTheDocument();
		});

		it('saves configuration to store', async () => {
			render(ConfigPanel);

			// Fill in form
			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			const languageSelect = screen.getByLabelText(/Target Language/i);
			await fireEvent.change(languageSelect, { target: { value: 'es' } });

			// Click save
			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			// Check store was updated
			let storeValue: ConfigState | undefined;
			const unsubscribe = configStore.subscribe((value) => {
				storeValue = value;
			});
			unsubscribe();

			expect(storeValue?.target_language).toBe('es');
			expect(storeValue?.api_key).toBe('sk-test-key');
		});

		it('displays success message after saving', async () => {
			render(ConfigPanel);

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			await waitFor(() => {
				expect(screen.getByText(/Configuration saved successfully/i)).toBeInTheDocument();
			});
		});

		it('calls onSave callback', async () => {
			const onSave = vi.fn();

			render(ConfigPanel, { props: { onSave } });

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			await waitFor(() => {
				expect(onSave).toHaveBeenCalled();
			});
		});

		it('validates form before saving', async () => {
			render(ConfigPanel);

			// Clear API key to trigger validation error
			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: '' } });

			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			await waitFor(() => {
				expect(screen.getByText(/Please fix validation errors before saving/i)).toBeInTheDocument();
			});
		});
	});

	describe('Reset Button', () => {
		it('renders reset button', () => {
			render(ConfigPanel);

			const resetButton = screen.getByRole('button', { name: /Reset/i });
			expect(resetButton).toBeInTheDocument();
		});

		it('resets configuration to defaults', async () => {
			render(ConfigPanel);

			// Change some values
			const providerSelect = screen.getByLabelText(/Provider/i);
			await fireEvent.change(providerSelect, { target: { value: 'anthropic' } });

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			// Reset
			const resetButton = screen.getByRole('button', { name: /Reset/i });
			await fireEvent.click(resetButton);

			// Check values were reset
			await waitFor(() => {
				expect((providerSelect as HTMLSelectElement).value).toBe('openai');
				expect((apiKeyInput as HTMLInputElement).value).toBe('');
			});
		});

		it('clears validation errors', async () => {
			render(ConfigPanel);

			// Trigger validation error by saving without API key
			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			await waitFor(() => {
				expect(screen.getByText(/API key is required/i)).toBeInTheDocument();
			});

			// Reset
			const resetButton = screen.getByRole('button', { name: /Reset/i });
			await fireEvent.click(resetButton);

			// Error should be cleared
			await waitFor(() => {
				expect(screen.queryByText(/API key is required/i)).not.toBeInTheDocument();
			});
		});

		it('calls onReset callback', async () => {
			const onReset = vi.fn();

			render(ConfigPanel, { props: { onReset } });

			const resetButton = screen.getByRole('button', { name: /Reset/i });
			await fireEvent.click(resetButton);

			expect(onReset).toHaveBeenCalled();
		});
	});

	describe('Form Validation', () => {
		it('shows validation error for empty API key', async () => {
			render(ConfigPanel);

			// Try to save without API key
			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			await waitFor(() => {
				expect(screen.getByText(/API key is required/i)).toBeInTheDocument();
			});

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			expect(apiKeyInput).toHaveAttribute('aria-invalid', 'true');
		});

		it('clears validation errors when field is corrected', async () => {
			render(ConfigPanel);

			// Trigger validation error
			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			await waitFor(() => {
				expect(screen.getByText(/API key is required/i)).toBeInTheDocument();
			});

			// Fix the error
			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			// Try saving again - should succeed
			await fireEvent.click(saveButton);

			await waitFor(() => {
				expect(screen.queryByText(/API key is required/i)).not.toBeInTheDocument();
				expect(screen.getByText(/Configuration saved successfully/i)).toBeInTheDocument();
			});
		});
	});

	describe('Visual Feedback', () => {
		it('clears test result when form changes', async () => {
			const onTestConnection = vi.fn().mockResolvedValue({
				valid: true,
				message: 'Connection successful'
			});

			render(ConfigPanel, { props: { onTestConnection } });

			// Test connection
			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			const testButton = screen.getByRole('button', { name: /Test Connection/i });
			await fireEvent.click(testButton);

			await waitFor(() => {
				expect(screen.getByText(/Connection successful/i)).toBeInTheDocument();
			});

			// Change provider - should clear test result
			const providerSelect = screen.getByLabelText(/Provider/i);
			await fireEvent.change(providerSelect, { target: { value: 'anthropic' } });

			await waitFor(() => {
				expect(screen.queryByText(/Connection successful/i)).not.toBeInTheDocument();
			});
		});

		it('has accessible status regions for feedback', async () => {
			const onTestConnection = vi.fn().mockResolvedValue({
				valid: true,
				message: 'Success'
			});

			render(ConfigPanel, { props: { onTestConnection } });

			const apiKeyInput = screen.getByLabelText(/API Key/i);
			await fireEvent.input(apiKeyInput, { target: { value: 'sk-test-key' } });

			const testButton = screen.getByRole('button', { name: /Test Connection/i });
			await fireEvent.click(testButton);

			await waitFor(() => {
				const statusElement = screen.getByRole('status');
				expect(statusElement).toHaveAttribute('aria-live', 'polite');
			});
		});
	});

	describe('Accessibility', () => {
		it('has proper ARIA attributes for form', () => {
			render(ConfigPanel);

			const form = screen.getByRole('form');
			expect(form).toHaveAttribute('aria-label', 'Configuration panel');
		});

		it('links validation errors with inputs', async () => {
			render(ConfigPanel);

			// Trigger validation error
			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			await waitFor(() => {
				const apiKeyInput = screen.getByLabelText(/API Key/i);
				const errorId = apiKeyInput.getAttribute('aria-describedby');
				expect(errorId).toBe('api-key-error');

				const errorElement = document.getElementById(errorId!);
				expect(errorElement).toHaveTextContent(/API key is required/i);
			});
		});

		it('marks invalid fields with aria-invalid', async () => {
			render(ConfigPanel);

			// Trigger validation
			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			await waitFor(() => {
				const apiKeyInput = screen.getByLabelText(/API Key/i);
				expect(apiKeyInput).toHaveAttribute('aria-invalid', 'true');
			});
		});

		it('has error messages with role="alert"', async () => {
			render(ConfigPanel);

			const saveButton = screen.getByRole('button', { name: /^Save$/i });
			await fireEvent.click(saveButton);

			await waitFor(() => {
				const alerts = screen.getAllByRole('alert');
				expect(alerts.length).toBeGreaterThan(0);
			});
		});
	});
});
