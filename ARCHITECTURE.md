<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
# Architecture

- [Luminote Architecture (Overview)](#luminote-architecture-overview)
  - [Goals](#goals)
  - [High-Level Diagram (conceptual)](#high-level-diagram-conceptual)
  - [Components](#components)
    - [Frontend (SvelteKit + TypeScript)](#frontend-sveltekit--typescript)
    - [Backend (FastAPI)](#backend-fastapi)
    - [Data Model](#data-model)
  - [Design Principles](#design-principles)
  - [Flows](#flows)
    - [Fetch & Extract](#fetch--extract)
    - [Translate (progressive)](#translate-progressive)
    - [Settings (BYOK)](#settings-byok)
  - [Non-Goals (early phases)](#non-goals-early-phases)
  - [Future Considerations](#future-considerations)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# Luminote Architecture (Overview)

## Goals

- Keep translation as the primary pane; support on-demand AI for insights/verification.
- Remain local-first with BYOK (bring your own key); avoid leaking keys to the frontend.
- Enable progressive rendering for readable, fast translations.
- Ensure all AI operations are user-triggered (no automatic background calls).
- Support multi-provider AI backends with configurable governance.

## High-Level Diagram (conceptual)

- Frontend (SvelteKit) → Backend API (FastAPI) → AI Provider(s)
- Backend also handles fetch/extract to normalize content into reader-mode blocks.

## Components

### Frontend (SvelteKit + TypeScript)

- **Requirements:** Node.js 22+
- **UI:** Dual-pane layout with left reader-mode source, right translation.
- **State:** Blocks, translations, settings (lang/provider/model/key stored locally).
- **Interactions:** Block sync, selection commands (future), re-translate actions.
- **Networking:** Calls backend for fetch/extract/translate; no direct calls to AI providers.
- **Code quality:** ESLint (linting), Prettier (formatting, 72 char line length).

### Backend (FastAPI)

- **Requirements:** Python 3.12+ with `uv` for dependency management
- **Entry point:** `luminote serve` command (defined in pyproject.toml)
- **Endpoints:** health, fetch, extract, translate (see docs/API.md).
- **Services:** Provider clients (OpenAI, Anthropic, etc.), extraction pipeline, translation orchestration.
- **Config:** env-driven (see .env.example); BYOK stored server-side for calls.
- **Code quality:** isort (imports), black (formatting, 72 char), ruff (linting), mypy (type checking, strict mode).
- **Testing:** pytest (unit/smoke/e2e tests), tox (multi-version testing).
- **Coverage requirements:** Core modules (app/core/) ≥95%, other modules ≥85%.
- **Packaging:** PyPI-publishable Python package with wheel and source distributions.

### Data Model

- **Document:** Extracted and cleaned content from a URL.
- **Block:** Normalized content unit (paragraph, heading, list, quote, code, image).
- **Translation:** Block-mapped translation with version tracking.
- **AI Job:** Any model request with prompt version and metadata.
- **Artifact:** Saved output from an AI Job (note, link card, verification, etc.).

## Design Principles

These principles guide all architecture and feature decisions:

1. **Two-pane reading is primary** — Translation always visible on the right pane. Never replace this with alternative content.

2. **On-demand AI, user-controlled cost** — All AI operations must be explicitly triggered by users. No automatic background AI calls.

3. **BYOK multi-provider** — Users bring their own API keys. Support multiple providers (OpenAI, Anthropic, etc.).

4. **Configurable governance** — Make prompts and terminology configurable per task type for consistency.

5. **All AI outputs are versioned assets** — Save every AI output with full provenance (model, prompt version, referenced blocks) for replay and regeneration.

6. **Compliance-first** — Never bypass authentication, anti-bot mechanisms, or paywalls automatically. All sessions are user-driven.

## Flows

### Fetch & Extract

1) Frontend sends URL → backend `/fetch` (proxy) → raw HTML.
2) Backend `/extract` → normalized blocks (titles, headings, paragraphs, lists, quotes, code, images).
3) Frontend renders blocks in reader-mode (left pane).

### Translate (progressive)

1) Frontend requests `/translate` with blocks + target_lang.
2) Backend streams translations block-by-block.
3) Frontend renders progressively in the right pane.

### Settings (BYOK)

- API keys and configuration stored client-side for UX; sent to backend for calls.
- Backend uses provided key per request; does not expose keys onward.
- Configuration includes: target language, provider (OpenAI, Anthropic, etc.), model, and API key.

## Non-Goals (early phases)

- Multi-user/team sync
- Bypassing login/Cloudflare/anti-bot
- Heavy server-side persistence (local-first focus initially)

## Future Considerations

- Add persistence for history, notes, artifacts (SQLite/Postgres)
- Add auth for hosted deployments
- Add RAG/browsing and multi-model arbitration (Phase 3)
- Deployment architectures:
  - **Self-hosted:** FastAPI backend on VM/container, static frontend, reverse proxy (nginx/caddy)
  - **Cloud:** Frontend on CDN (Cloudflare, Vercel), backend via API gateway + load balancer, managed PostgreSQL
