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

- Node.js 20+
- npm 10+

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
# Run tests once
npm test

# Watch mode
npm run test:watch

# With coverage report
npm run test:coverage
```

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

- Run quality checks before committing: `npm run lint && npm run format && npm run type-check`
- Ensure dev server starts: `npm run dev`
- Write clear commit messages using conventional commits format

## Integration with Backend

The backend API runs on `http://localhost:8000`. Configure API endpoints in environment variables or a config file (to be added in Phase 1).

## Troubleshooting

### Port 5000 Already in Use

If port 5000 is already in use, you can:

1. Stop the process using port 5000
2. Or temporarily change the port in `vite.config.ts` (not recommended for this project)

### Type Errors

If you see TypeScript errors after installing dependencies:

```bash
npm run type-check
```

This will show all type errors. Fix them before proceeding.

### Build Errors

Clear the build cache and rebuild:

```bash
rm -rf .svelte-kit
npm run build
```

## Next Steps

This is the Phase 0 infrastructure setup. Phase 1 development will add:

- Dual-pane layout component
- URL input and content extraction
- Translation service integration
- Error handling UI
- Loading states and progressive rendering

## Resources

- [SvelteKit Documentation](https://kit.svelte.dev/docs)
- [Svelte Documentation](https://svelte.dev/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Vitest Documentation](https://vitest.dev)

## License

GPL-3.0 - See LICENSE file in repository root
