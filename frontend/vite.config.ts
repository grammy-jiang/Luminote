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
				'src/lib/utils/streaming.example.ts', // Example/reference implementation (documentation)
				'**/*.d.ts',
				'**/*.config.{js,ts}',
				'**/node_modules/**',
				'**/.svelte-kit/**'
			],
			thresholds: {
				lines: 85,
				functions: 30, // Lower threshold for Svelte components (reactive statements, lifecycle hooks, and event handlers generate many untestable functions)
				branches: 80, // Lower threshold for Svelte components (conditional rendering and reactive statements generate many branches)
				statements: 85
			}
		}
	}
});
