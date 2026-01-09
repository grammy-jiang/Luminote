# Luminote Frontend

SvelteKit-based frontend for the Luminote translation workbench.

## Tech Stack

- **Framework:** SvelteKit 2.0
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS 3.4
- **Build Tool:** Vite 5
- **Testing:** Vitest
- **Linting:** ESLint + Prettier

## Prerequisites

- **Node.js 22+** (LTS version recommended)
  - **Note:** Node.js 22 is the project standard as specified in ARCHITECTURE.md
    and CONTRIBUTING.md. While Node.js 20 may work, 22+ is required for
    consistency and to ensure access to the latest features.
- **npm 10+** (comes with Node.js)

**Check your versions:**

```bash
node --version  # Should be 22 or higher
npm --version   # Should be 10 or higher
```

**Install Node.js 22:**

If you don't have Node.js 22, install it from:

- [Official Node.js website](https://nodejs.org/)

- Or use a version manager like [nvm](https://github.com/nvm-sh/nvm):

  ```bash
  # Install nvm (macOS/Linux)
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

  # Install and use Node.js 22
  nvm install 22
  nvm use 22
  ```

## Quick Start

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
# Start development server (http://localhost:5000)
npm run dev

# Run in different modes
npm run dev -- --host  # Expose to network
npm run dev -- --open  # Auto-open browser
```

### Building

```bash
# Production build
npm run build

# Preview production build
npm run preview
```

### Testing

```bash
# Run tests once (CI mode)
npm test

# Watch mode (re-runs on file changes)
npm run test:watch

# With coverage report (≥85% required)
npm run test:coverage
# Open coverage/index.html to view detailed coverage

# Run specific test file
npm test -- YourComponent.test.ts

# Run tests matching pattern
npm test -- --grep "Button component"
```

**Test structure:**

Tests are co-located with the code they test:

```
src/lib/
├── components/
│   ├── Button.svelte
│   └── Button.test.ts        # Tests for Button component
├── stores/
│   ├── settings.ts
│   └── settings.test.ts      # Tests for settings store
└── utils/
    ├── formatDate.ts
    └── formatDate.test.ts    # Tests for formatDate utility
```

**Writing tests:**

```typescript
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import Button from './Button.svelte';

describe('Button component', () => {
	it('renders with correct text', () => {
		render(Button, { props: { text: 'Click me' } });
		expect(screen.getByText('Click me')).toBeInTheDocument();
	});

	it('calls onClick when clicked', async () => {
		const onClick = vi.fn();
		render(Button, { props: { text: 'Click', onClick } });

		await fireEvent.click(screen.getByText('Click'));
		expect(onClick).toHaveBeenCalledOnce();
	});
});
```

**Coverage requirements:**

- All code must have **≥85%** coverage
- Tests must be meaningful, not just for coverage numbers
- Focus on behavior, not implementation details

### Code Quality

```bash
# Run all quality checks (before committing)
npm run lint && npm run format && npm run type-check

# Individual checks
npm run lint        # ESLint
npm run format      # Prettier
npm run type-check  # TypeScript
```

## Project Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/     # Reusable Svelte components
│   │   ├── stores/         # Svelte stores for state management
│   │   ├── utils/          # Utility functions and helpers
│   │   └── *.test.ts       # Test files co-located with the code they test
│   ├── routes/             # SvelteKit pages and layouts
│   │   ├── +layout.svelte  # Root layout
│   │   └── +page.svelte    # Home page
│   ├── app.html            # HTML template
│   └── app.css             # Global styles (Tailwind)
├── static/                 # Static assets
└── [config files]          # Various configuration files
```

## Path Aliases

The following path aliases are configured:

- `$lib` → `src/lib`
- `$components` → `src/lib/components`
- `$stores` → `src/lib/stores`
- `$utils` → `src/lib/utils`

Usage example:

```typescript
import { myStore } from '$stores/myStore';
import Button from '$components/Button.svelte';
import { formatDate } from '$utils/date';
```

## Configuration Files

- `svelte.config.js` - SvelteKit configuration
- `vite.config.ts` - Vite and Vitest configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `tsconfig.json` - TypeScript configuration (strict mode enabled)
- `.eslintrc.cjs` - ESLint configuration
- `.prettierrc` - Prettier configuration

## Development Guidelines

### Code Style

- Use TypeScript for all new files
- Follow the Prettier configuration (enforced on save)
- Fix all ESLint warnings before committing
- Use functional Svelte components (avoid class components)

### State Management

- Use Svelte stores for global state
- Keep component-local state in the component
- Create stores in `src/lib/stores/`

### Testing

- Write tests for all components and utilities
- Place tests next to the code: `MyComponent.test.ts`
- Aim for ≥85% code coverage
- Use Vitest for unit tests

### Commits

- Run quality checks before committing:
  `npm run lint && npm run format && npm run type-check`
- Ensure dev server starts: `npm run dev`
- Write clear commit messages using conventional commits format

## Integration with Backend

The frontend communicates with the backend via HTTP REST API:

- **Backend API:** http://localhost:8000
- **API base path:** `/api/v1/`
- **Health check:** http://localhost:8000/health

**API endpoints will be configured in Phase 1.** For now, ensure both servers
run simultaneously:

```bash
# Terminal 1: Backend
cd backend && source .venv/bin/activate && luminote serve

# Terminal 2: Frontend
cd frontend && npm run dev
```

**CORS configuration:**

The backend allows requests from the frontend origins. Default CORS origins:

- `http://localhost:5000`
- `http://127.0.0.1:5000`

If you change the frontend port, update `backend/.env`:

```bash
CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000,http://localhost:5001
```

## Architecture

The frontend follows a component-based architecture with clear separation of
concerns:

```
┌─────────────────────────────────────┐
│     Routes (src/routes/)            │  Page-level components
│     - SvelteKit pages               │  (file-based routing)
│     - Layouts                        │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   Components (src/lib/components/)  │  Reusable UI components
│     - DualPane layout (Phase 1)     │
│     - Input fields                  │
│     - Buttons, cards, etc.          │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   Stores (src/lib/stores/)          │  State management
│     - Settings (lang, provider)     │  (Svelte stores)
│     - Content blocks                │
│     - Translation state             │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   Utils (src/lib/utils/)            │  Helper functions
│     - API client                    │
│     - Formatters                    │
│     - Validators                    │
└─────────────────────────────────────┘
```

**Key principles:**

1. **Functional components** — Use Svelte's component syntax, avoid class
   components
1. **Svelte stores for state** — Global state managed via Svelte stores (see
   ADR-005)
1. **TypeScript strict mode** — All code must pass strict type checking
1. **Co-located tests** — Tests live next to the code they test
1. **Utility-first CSS** — Use Tailwind CSS classes, minimize custom CSS

For architecture decisions, see
[ADR-005: Frontend State Management](../docs/adr/005-frontend-state-management.md).

## Development Workflow

**Quick development cycle:**

1. Start dev server: `npm run dev`
1. Make changes to components/pages
1. Browser auto-refreshes (HMR)
1. Run tests: `npm test`
1. Check types: `npm run type-check`
1. Format code: `npm run format`
1. Lint code: `npm run lint`
1. Commit: `git commit -m "feat: your change"`

**Adding a new component:**

1. Create component: `src/lib/components/YourComponent.svelte`
1. Write the component with TypeScript: `<script lang="ts">`
1. Add tests: `src/lib/components/YourComponent.test.ts`
1. Ensure ≥85% coverage: `npm run test:coverage`
1. Use component in pages:
   `import YourComponent from '$components/YourComponent.svelte'`

**Adding a new store:**

1. Create store: `src/lib/stores/yourStore.ts`
1. Export store and methods
1. Add tests: `src/lib/stores/yourStore.test.ts`
1. Use in components: `import { yourStore } from '$stores/yourStore'`

For detailed workflow, see [docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md).

## Contributing

Contributions are welcome! Please see:

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — Setup, standards, and workflow
- **[docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md)** — Detailed development guide
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** — System architecture

**Before contributing:**

1. Read the contributing guidelines
1. Set up your development environment
1. Run all quality checks before submitting PR
1. Ensure tests pass and coverage ≥85%

## Documentation

- **[README.md](../README.md)** — Project overview
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — Contributing guidelines
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** — System architecture
- **[docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md)** — Development guide
- **[docs/adr/](../docs/adr/)** — Architecture Decision Records

## Troubleshooting

### Port 5000 Already in Use

**Symptom:** `Port 5000 is in use`

**Solution 1** — Kill the process using port 5000:

```bash
# macOS/Linux
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Solution 2** — Use a different port (not recommended for this project):

Edit `package.json`:

```json
"scripts": {
  "dev": "vite dev --port 5001"
}
```

### Node Modules Not Found

**Symptom:** `Cannot find module '@sveltejs/kit'`

**Solution:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Type Errors After Update

**Symptom:** `Type error: Property 'xyz' does not exist on type...`

**Solution:**

```bash
# Check all type errors
npm run type-check

# Clear cache and rebuild
rm -rf .svelte-kit node_modules
npm install
npm run build
```

### Vite Build Fails

**Symptom:** `✘ [ERROR] Build failed`

**Solution:**

```bash
# Clear Svelte cache
rm -rf .svelte-kit

# Check for syntax/type errors
npm run type-check
npm run lint

# Rebuild
npm run build
```

### Hot Module Replacement (HMR) Not Working

**Symptom:** Changes don't reflect in browser without manual refresh

**Solution:**

1. Check browser console for errors
1. Restart dev server: `npm run dev`
1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
1. Check file watcher limits (Linux):
   ```bash
   echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```

### Tests Failing

**Symptom:** Tests pass locally but fail in CI

**Solution:**

- Ensure Node.js version matches CI (22+)
- Check for timing issues (use `waitFor` for async operations)
- Avoid relying on specific DOM order
- Mock date/time if tests depend on it

For more troubleshooting tips, see
[docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md#troubleshooting).

## Next Steps

This is the Phase 0 infrastructure setup. Phase 1 development will add:

- Dual-pane layout component
- URL input and content extraction
- Translation service integration
- Error handling UI
- Loading states and progressive rendering

See [docs/feature-specifications.md](../docs/feature-specifications.md) for
detailed feature specs.

## Resources

- **[SvelteKit Documentation](https://kit.svelte.dev/docs)** — Frontend
  framework
- **[Svelte Documentation](https://svelte.dev/docs)** — Component framework
- **[Tailwind CSS Documentation](https://tailwindcss.com/docs)** — Styling
  framework
- **[TypeScript Documentation](https://www.typescriptlang.org/docs)** — Type
  system
- **[Vitest Documentation](https://vitest.dev)** — Testing framework

## License

This project is licensed under the **GNU General Public License v3.0
(GPL-3.0)**.

See [LICENSE](../LICENSE) for details.
