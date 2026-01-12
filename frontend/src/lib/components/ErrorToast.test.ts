/**
 * Unit tests for ErrorToast component.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render } from '../test-utils';
import { screen, fireEvent } from '@testing-library/svelte';
import ErrorToast from './ErrorToast.svelte';

describe('ErrorToast Component', () => {
	beforeEach(() => {
		vi.useFakeTimers();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('Rendering', () => {
		it('renders toast with message', () => {
			render(ErrorToast, { props: { message: 'Test error message' } });

			expect(screen.getByText('Test error message')).toBeInTheDocument();
		});

		it('renders with default error severity', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Error message' }
			});

			const toast = container.querySelector('.toast');
			expect(toast).toHaveClass('toast-error');
		});

		it('renders with warning severity', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Warning message', severity: 'warning' }
			});

			const toast = container.querySelector('.toast');
			expect(toast).toHaveClass('toast-warning');
		});

		it('renders with info severity', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Info message', severity: 'info' }
			});

			const toast = container.querySelector('.toast');
			expect(toast).toHaveClass('toast-info');
		});

		it('displays severity icon for error', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Error', severity: 'error' }
			});

			const icon = container.querySelector('.toast-icon');
			expect(icon).toHaveTextContent('✕');
		});

		it('displays severity icon for warning', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Warning', severity: 'warning' }
			});

			const icon = container.querySelector('.toast-icon');
			expect(icon).toHaveTextContent('⚠');
		});

		it('displays severity icon for info', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Info', severity: 'info' }
			});

			const icon = container.querySelector('.toast-icon');
			expect(icon).toHaveTextContent('ℹ');
		});
	});

	describe('Auto-dismiss', () => {
		it('renders with autoDismiss enabled by default', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Auto dismiss test' }
			});

			// Toast should be visible
			const toast = container.querySelector('[data-testid="error-toast"]');
			expect(toast).toBeInTheDocument();
		});

		it('renders with custom dismissDelay prop', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Custom delay test', dismissDelay: 3000 }
			});

			// Toast should be visible
			const toast = container.querySelector('[data-testid="error-toast"]');
			expect(toast).toBeInTheDocument();
		});

		it('does not set up auto-dismiss timeout when autoDismiss is false', () => {
			const timerCountBefore = vi.getTimerCount();
			render(ErrorToast, {
				props: { message: 'No auto dismiss', autoDismiss: false }
			});

			// No new timers should be created
			expect(vi.getTimerCount()).toBe(timerCountBefore);
		});

		it('toast is visible when autoDismiss is false after time passes', async () => {
			const { container } = render(ErrorToast, {
				props: { message: 'No auto dismiss', autoDismiss: false }
			});

			// Toast should be visible initially
			let toast = container.querySelector('[data-testid="error-toast"]');
			expect(toast).toBeInTheDocument();

			// Fast-forward time by 10 seconds
			await vi.advanceTimersByTimeAsync(10000);

			// Toast should still be visible
			toast = container.querySelector('[data-testid="error-toast"]');
			expect(toast).toBeInTheDocument();
		});
	});

	describe('Manual Dismiss', () => {
		it('shows dismiss button', () => {
			render(ErrorToast, { props: { message: 'Test' } });

			const dismissButton = screen.getByLabelText('Dismiss notification');
			expect(dismissButton).toBeInTheDocument();
		});

		it('dismisses toast when dismiss button is clicked', async () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Manual dismiss test', autoDismiss: false }
			});

			const dismissButton = screen.getByLabelText('Dismiss notification');
			await fireEvent.click(dismissButton);

			const toast = container.querySelector('[data-testid="error-toast"]');
			expect(toast).not.toBeInTheDocument();
		});

		it('calls onDismiss callback when dismissed', async () => {
			const onDismiss = vi.fn();
			render(ErrorToast, {
				props: { message: 'Test', onDismiss, autoDismiss: false }
			});

			const dismissButton = screen.getByLabelText('Dismiss notification');
			await fireEvent.click(dismissButton);

			expect(onDismiss).toHaveBeenCalledTimes(1);
		});

		it('emits dismiss event when dismissed', async () => {
			const { component } = render(ErrorToast, {
				props: { message: 'Test', autoDismiss: false }
			});

			const dismissHandler = vi.fn();
			component.$on('dismiss', dismissHandler);

			const dismissButton = screen.getByLabelText('Dismiss notification');
			await fireEvent.click(dismissButton);

			expect(dismissHandler).toHaveBeenCalledTimes(1);
		});

		it('clears auto-dismiss timeout when manually dismissed', async () => {
			const onDismiss = vi.fn();
			const { container } = render(ErrorToast, {
				props: { message: 'Test', onDismiss, dismissDelay: 10000 }
			});

			// Manually dismiss before timeout
			const dismissButton = screen.getByLabelText('Dismiss notification');
			await fireEvent.click(dismissButton);

			// Verify toast is dismissed
			let toast = container.querySelector('[data-testid="error-toast"]');
			expect(toast).not.toBeInTheDocument();
			expect(onDismiss).toHaveBeenCalledTimes(1);

			// Fast-forward past the original timeout
			vi.advanceTimersByTime(10000);
			await vi.runAllTimersAsync();

			// onDismiss should not be called again
			expect(onDismiss).toHaveBeenCalledTimes(1);
		});
	});

	describe('Retry Button', () => {
		it('does not show retry button by default', () => {
			render(ErrorToast, { props: { message: 'Test' } });

			const retryButton = screen.queryByLabelText('Retry action');
			expect(retryButton).not.toBeInTheDocument();
		});

		it('shows retry button when showRetry is true and onRetry is provided', () => {
			const onRetry = vi.fn();
			render(ErrorToast, {
				props: { message: 'Test', showRetry: true, onRetry }
			});

			const retryButton = screen.getByLabelText('Retry action');
			expect(retryButton).toBeInTheDocument();
			expect(retryButton).toHaveTextContent('Retry');
		});

		it('does not show retry button when showRetry is true but onRetry is not provided', () => {
			render(ErrorToast, {
				props: { message: 'Test', showRetry: true }
			});

			const retryButton = screen.queryByLabelText('Retry action');
			expect(retryButton).not.toBeInTheDocument();
		});

		it('calls onRetry callback when retry button is clicked', async () => {
			const onRetry = vi.fn();
			render(ErrorToast, {
				props: { message: 'Test', showRetry: true, onRetry, autoDismiss: false }
			});

			const retryButton = screen.getByLabelText('Retry action');
			await fireEvent.click(retryButton);

			expect(onRetry).toHaveBeenCalledTimes(1);
		});

		it('emits retry event when retry button is clicked', async () => {
			const onRetry = vi.fn();
			const { component } = render(ErrorToast, {
				props: { message: 'Test', showRetry: true, onRetry, autoDismiss: false }
			});

			const retryHandler = vi.fn();
			component.$on('retry', retryHandler);

			const retryButton = screen.getByLabelText('Retry action');
			await fireEvent.click(retryButton);

			expect(retryHandler).toHaveBeenCalledTimes(1);
		});

		it('dismisses toast after retry', async () => {
			const onRetry = vi.fn();
			const { container } = render(ErrorToast, {
				props: { message: 'Test', showRetry: true, onRetry, autoDismiss: false }
			});

			const retryButton = screen.getByLabelText('Retry action');
			await fireEvent.click(retryButton);

			const toast = container.querySelector('[data-testid="error-toast"]');
			expect(toast).not.toBeInTheDocument();
		});
	});

	describe('Accessibility', () => {
		it('has alert role', () => {
			render(ErrorToast, { props: { message: 'Test' } });

			const toast = screen.getByRole('alert');
			expect(toast).toBeInTheDocument();
		});

		it('has aria-live="assertive" attribute', () => {
			render(ErrorToast, { props: { message: 'Test' } });

			const toast = screen.getByRole('alert');
			expect(toast).toHaveAttribute('aria-live', 'assertive');
		});

		it('has aria-atomic="true" attribute', () => {
			render(ErrorToast, { props: { message: 'Test' } });

			const toast = screen.getByRole('alert');
			expect(toast).toHaveAttribute('aria-atomic', 'true');
		});

		it('has aria-label on severity icon for error', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test', severity: 'error' }
			});

			const icon = container.querySelector('.toast-icon');
			expect(icon).toHaveAttribute('aria-label', 'Error');
		});

		it('has aria-label on severity icon for warning', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test', severity: 'warning' }
			});

			const icon = container.querySelector('.toast-icon');
			expect(icon).toHaveAttribute('aria-label', 'Warning');
		});

		it('has aria-label on severity icon for info', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test', severity: 'info' }
			});

			const icon = container.querySelector('.toast-icon');
			expect(icon).toHaveAttribute('aria-label', 'Information');
		});

		it('dismiss button has aria-label', () => {
			render(ErrorToast, { props: { message: 'Test' } });

			const dismissButton = screen.getByLabelText('Dismiss notification');
			expect(dismissButton).toBeInTheDocument();
		});

		it('retry button has aria-label when shown', () => {
			const onRetry = vi.fn();
			render(ErrorToast, {
				props: { message: 'Test', showRetry: true, onRetry }
			});

			const retryButton = screen.getByLabelText('Retry action');
			expect(retryButton).toBeInTheDocument();
		});

		it('buttons have type="button" attribute', () => {
			const onRetry = vi.fn();
			render(ErrorToast, {
				props: { message: 'Test', showRetry: true, onRetry }
			});

			const dismissButton = screen.getByLabelText('Dismiss notification');
			const retryButton = screen.getByLabelText('Retry action');

			expect(dismissButton).toHaveAttribute('type', 'button');
			expect(retryButton).toHaveAttribute('type', 'button');
		});
	});

	describe('Severity Colors', () => {
		it('applies error color class', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test', severity: 'error' }
			});

			const toast = container.querySelector('.toast');
			expect(toast).toHaveClass('toast-error');
		});

		it('applies warning color class', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test', severity: 'warning' }
			});

			const toast = container.querySelector('.toast');
			expect(toast).toHaveClass('toast-warning');
		});

		it('applies info color class', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test', severity: 'info' }
			});

			const toast = container.querySelector('.toast');
			expect(toast).toHaveClass('toast-info');
		});
	});

	describe('Message Display', () => {
		it('displays short message', () => {
			render(ErrorToast, { props: { message: 'Short message' } });

			expect(screen.getByText('Short message')).toBeInTheDocument();
		});

		it('displays long message', () => {
			const longMessage =
				'This is a very long error message that should wrap properly within the toast container without breaking the layout or causing overflow issues.';
			render(ErrorToast, { props: { message: longMessage } });

			expect(screen.getByText(longMessage)).toBeInTheDocument();
		});

		it('displays message with special characters', () => {
			const message = 'Error: "Invalid input" - check your <data>';
			render(ErrorToast, { props: { message } });

			expect(screen.getByText(message)).toBeInTheDocument();
		});
	});

	describe('Component Structure', () => {
		it('has toast class', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test' }
			});

			const toast = container.querySelector('.toast');
			expect(toast).toBeInTheDocument();
		});

		it('has toast-icon element', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test' }
			});

			const icon = container.querySelector('.toast-icon');
			expect(icon).toBeInTheDocument();
		});

		it('has toast-message element', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test' }
			});

			const message = container.querySelector('.toast-message');
			expect(message).toBeInTheDocument();
		});

		it('has toast-actions element', () => {
			const { container } = render(ErrorToast, {
				props: { message: 'Test' }
			});

			const actions = container.querySelector('.toast-actions');
			expect(actions).toBeInTheDocument();
		});
	});

	describe('Multiple Actions', () => {
		it('shows both retry and dismiss buttons', () => {
			const onRetry = vi.fn();
			render(ErrorToast, {
				props: { message: 'Test', showRetry: true, onRetry }
			});

			const retryButton = screen.getByLabelText('Retry action');
			const dismissButton = screen.getByLabelText('Dismiss notification');

			expect(retryButton).toBeInTheDocument();
			expect(dismissButton).toBeInTheDocument();
		});

		it('allows interaction with both buttons', async () => {
			const onRetry = vi.fn();
			const onDismiss = vi.fn();

			render(ErrorToast, {
				props: { message: 'Test', showRetry: true, onRetry, onDismiss, autoDismiss: false }
			});

			const retryButton = screen.getByLabelText('Retry action');
			await fireEvent.click(retryButton);

			expect(onRetry).toHaveBeenCalledTimes(1);
			expect(onDismiss).toHaveBeenCalledTimes(1); // Dismiss called after retry
		});
	});

	describe('Edge Cases', () => {
		it('handles empty message', () => {
			render(ErrorToast, { props: { message: '' } });

			const toast = screen.getByRole('alert');
			expect(toast).toBeInTheDocument();
		});

		it('accepts custom dismiss delay prop', () => {
			render(ErrorToast, {
				props: { message: 'Test', dismissDelay: 100 }
			});

			// Component renders successfully with custom delay
			const toast = screen.getByRole('alert');
			expect(toast).toBeInTheDocument();
		});

		it('accepts zero dismiss delay prop', () => {
			render(ErrorToast, {
				props: { message: 'Test', dismissDelay: 0 }
			});

			// Component renders successfully with zero delay
			const toast = screen.getByRole('alert');
			expect(toast).toBeInTheDocument();
		});
	});
});
