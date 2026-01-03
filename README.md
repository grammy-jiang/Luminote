![Luminote](docs/assets/logo.webp)

# Luminote

> AI two‑pane translation reader for fast, accurate comprehension of web content.

Luminote is a dual‑pane (original/translation) AI translation reader that emphasizes translation quality and uninterrupted reading flow. The original content appears on the left (reader‑mode), and the translation is the primary, persistent view on the right. Insights and verification stay off by default and are triggered when needed.

## Installing / Getting Started

Clone the repo, run the FastAPI backend, and start the Svelte frontend.

```bash
# Clone and open
git clone https://github.com/grammy-jiang/Luminote.git
cd Luminote

# Explore product docs
# - docs/purpose_and_functionality.md
# - docs/pov_features.md

# Run backend (FastAPI)
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # or manually create .env
uvicorn app.main:app --reload --port 8000
```

```powershell
# Frontend (Svelte + Rollup, TypeScript)
cd frontend
npm install
npm run dev          # builds and serves with live reload
# in another terminal, run the backend: uvicorn app.main:app --reload --port 8000
```

Notes:
- The UI expects the API at http://127.0.0.1:8000 by default. You can change it in the top‑right input (persisted in localStorage).
- Minimal styling on purpose; focus is on the two‑pane interactions and API flow.
- Main functions live on the primary view, with tabs for settings and history>.

### Initial Configuration (BYOK)

Planned environment variables (final names may change):

- `LUMINOTE_TARGET_LANG`: Target language (e.g., `zh`, `en`, `ja`).
- `LUMINOTE_PROVIDER`: Provider id (e.g., `openai`, `azure_openai`, `anthropic`, `groq`).
- `LUMINOTE_MODEL`: Model name (e.g., `gpt-4.1-mini`, `claude-3.5-sonnet`).
- `LUMINOTE_API_KEY`: API key for the chosen provider>.

Notes:
- Keys are stored locally for POV. Provide Test/Clear actions; hardening later.
- Translation is single‑model initially; multi‑model features are out of scope for the POV.

## Features

Core POV (Phase 0):
- Stable two‑pane translation with progressive, block‑level rendering
- Single‑user local settings: target language, provider/model, BYOK key
- Reader‑mode extraction (titles, paragraphs, lists, quotes, code, images)
- Clear error handling (fetch failures, invalid keys, rate limits) and fallbacks

Planned next steps:
- Re‑translate per‑block/full document with a light prompt
- Local history of visits
- Paste‑text quick translate when fetch/extraction fails
- Highlights/notes; save AI explanations (later phase)
- On‑demand insights and verification that do not disrupt reading (later phase)

See detailed product scope in docs.

## Configuration

User‑tunable settings (POV scope):
- Target language
- Provider and model (single model)
- API key (BYOK)

Optional behaviors:
- Manual source‑language override
- Lightweight re‑translate for style/terminology tweaks

## Minimal API (POV‑ready)

Internal API surface planned for the app backend:

- `GET /health`: Connectivity and configuration checks (e.g., provider reachability)
- `POST /fetch`: Retrieve raw content from URL via backend proxy
- `POST /extract`: Parse into reading‑mode blocks (title, paragraphs, lists, quotes, code, images)
- `POST /translate`: Translate blocks progressively using configured provider/model

These endpoints are designed for reliability, cost control, and consistent UX.

## Roadmap (Phasing Summary)

- Phase 0 (POV v0.0)
  - URL input; backend fetch + reader‑mode extraction
  - Left original rendering; right translation (progressive)
  - Local settings for target language/provider/model/API key
  - Basic error handling; optional block hover/click linkage
- Phase 0.5 (POV v0.1)
  - Local history (recent visits)
  - Re‑translate current block/full doc (light prompt)
  - Paste‑text quick translate on failure
- Phase 1 (POV v0.3)
  - Highlights/notes; save AI explanations
  - Dual context (Translation/Reading) and link cards
  - On‑demand insights and verification (offline)
  - Translation versioning (keep last 2)
- Phase 2 (V1)
  - Interactive login/Cloudflare (remote session) pre‑extraction
  - Insights/verification with external retrieval + citations
  - Finance: structured metric extraction; document comparisons
  - History retrieval (keyword/vector)
- Phase 3 (V2)
  - PDF/EPUB support
  - Multi‑model arbitration/debate (ROI‑gated)
  - Optional multi‑user/team sharing/cloud sync

## Developing

Current layout:
- `backend/`: FastAPI app, env-driven config (SQLite by default, Postgres-ready).
- `frontend/`: Svelte + Rollup + TypeScript single-page UI with tabs (main/settings/history).
- `docs/`: Product and POV documents (see docs/purpose_and_functionality.md).

Standards (to be formalized in CONTRIBUTING):
- TypeScript for frontend; Python with FastAPI for backend.
- Lint/format to be added; keep PRs small and focused.

## Building

Backend: run via uvicorn (no separate build step yet).

Frontend:

```bash
npm run build
```

## Deploying / Publishing

Not productionized yet. Target options:
- Self-hosted FastAPI + static frontend on a small VM/container.
- Later: CDN for frontend, API behind a gateway/load balancer.

## Links

- Product purpose & functionality: docs/purpose_and_functionality.md
- POV features: docs/pov_features.md
- Repository: https://github.com/grammy-jiang/Luminote
- Issue tracker: https://github.com/grammy-jiang/Luminote/issues

For sensitive security issues, please contact the maintainer directly rather than filing a public issue.

## Contributing

Contributions are welcome! If you’d like to help:
- Fork the repo and create a feature branch
- Keep changes focused and add tests when reasonable
- Open a pull request with a clear description and rationale

A full guide (coding style, commit conventions, branching model) will live in `CONTRIBUTING.md` when available.

## Licensing

The code in this project is licensed under the GNU General Public License v3.0 (GPL-3.0). See [LICENSE](LICENSE) for the full text. By contributing, you agree that your contributions will be licensed under GPL-3.0.

