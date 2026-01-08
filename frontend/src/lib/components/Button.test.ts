/**
 * Unit tests for Button component.
 */

import { describe, it, expect, vi } from 'vitest';
import { render } from '../test-utils';
import { screen, fireEvent } from '@testing-library/svelte';
import Button from './Button.svelte';

describe('Button Component', () => {
	it('renders button with default label', () => {
		render(Button);
		const button = screen.getByRole('button', { name: 'Click me' });
		expect(button).toBeInTheDocument();
	});

	it('renders button with custom label', () => {
		render(Button, { props: { label: 'Submit' } });
		const button = screen.getByRole('button', { name: 'Submit' });
		expect(button).toBeInTheDocument();
		expect(button).toHaveTextContent('Submit');
	});

	it('applies primary variant class by default', () => {
		render(Button);
		const button = screen.getByRole('button');
		expect(button).toHaveClass('btn', 'btn-primary');
	});

	it('applies secondary variant class when specified', () => {
		render(Button, { props: { variant: 'secondary' } });
		const button = screen.getByRole('button');
		expect(button).toHaveClass('btn', 'btn-secondary');
	});

	it('applies danger variant class when specified', () => {
		render(Button, { props: { variant: 'danger' } });
		const button = screen.getByRole('button');
		expect(button).toHaveClass('btn', 'btn-danger');
	});

	it('is enabled by default', () => {
		render(Button);
		const button = screen.getByRole('button');
		expect(button).not.toBeDisabled();
	});

	it('can be disabled', () => {
		render(Button, { props: { disabled: true } });
		const button = screen.getByRole('button');
		expect(button).toBeDisabled();
		expect(button).toHaveClass('disabled');
	});

	it('calls onclick handler when clicked', async () => {
		const handleClick = vi.fn();
		render(Button, { props: { onclick: handleClick } });

		const button = screen.getByRole('button');
		await fireEvent.click(button);

		expect(handleClick).toHaveBeenCalledTimes(1);
	});

	it('does not call onclick handler when disabled', async () => {
		const handleClick = vi.fn();
		render(Button, { props: { onclick: handleClick, disabled: true } });

		const button = screen.getByRole('button');
		await fireEvent.click(button);

		expect(handleClick).not.toHaveBeenCalled();
	});

	it('has correct aria-label', () => {
		render(Button, { props: { label: 'Test Button' } });
		const button = screen.getByRole('button');
		expect(button).toHaveAttribute('aria-label', 'Test Button');
	});
});
