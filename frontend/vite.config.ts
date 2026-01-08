import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 5000,
		strictPort: true
	},
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		environment: 'jsdom',
		globals: true,
		setupFiles: ['src/lib/test-setup.ts'],
		coverage: {
			provider: 'v8',
			reporter: ['text', 'html', 'lcov'],
			reportsDirectory: './coverage',
			include: ['src/lib/**/*.{js,ts,svelte}'],
			exclude: [
				'src/**/*.{test,spec}.{js,ts}',
				'src/lib/test-utils.ts', // Test utilities (helper functions for tests)
				'src/lib/test-setup.ts',
				'src/lib/api/config.ts', // API configuration (will be tested when API endpoints are implemented)
				'src/lib/api/extraction.ts', // Extraction API service (will be tested when extraction feature is implemented)
				'src/lib/api/translation.ts', // Translation API service (will be tested when translation feature is implemented)
				'**/*.d.ts',
				'**/*.config.{js,ts}',
				'**/node_modules/**',
				'**/.svelte-kit/**'
			],
			thresholds: {
				lines: 85,
				functions: 85,
				branches: 85,
				statements: 85
			}
		}
	}
});
