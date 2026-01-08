import { describe, it, expect } from 'vitest';

describe('Frontend setup', () => {
	it('should pass basic test', () => {
		expect(true).toBe(true);
	});

	it('should verify TypeScript is working', () => {
		const message: string = 'Hello, Luminote!';
		expect(message).toContain('Luminote');
	});
});
