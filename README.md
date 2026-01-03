![Luminote](docs/assets/logo.webp)

# Luminote

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 22+](https://img.shields.io/badge/node.js-22+-green.svg)](https://nodejs.org/)

> AI-powered two-pane translation workbench for fast, accurate understanding and verification of web content.

Luminote is a local-first, AI-driven reading workbench that transforms web materials into **understandable, verifiable, and reviewable** knowledge assets. The original content appears on the left in reader-mode, and the AI translation is your primary, persistent view on the right. AI insights and verification capabilities are on-demand and user-controlled.

## Why Luminote?

Most translation tools stop at converting words. Luminote targets the real problem: **fast, accurate understanding and verification** of high-density materials—news articles, research papers, technical documentation, financial reports. Translation is the core function, but it serves a bigger goal: **understand + verify + retain**.

## Product Roadmap & Features

**Phase 0**
- [ ] Dual-pane translation with progressive, block-level rendering
- [ ] Reader-mode extraction from any URL (titles, paragraphs, lists, quotes, code, images)
- [ ] BYOK configuration for target language, provider/model, and API key
- [ ] Clear error handling for fetch failures, invalid keys, and rate limits
- [ ] Block-level synchronization with hover/click linkage between panes

**Phase 1**
- [ ] Re-translate per-block or full document with custom prompts
- [ ] Local visit history and quick paste-text translation
- [ ] Selection-based commands: Explain, Define terms, Summarize (and save as notes)
- [ ] Prompt templates and termbase setup; translation versioning (keep last versions)

**Phase 2**
- [ ] On-demand AI insights and verification packs (claims checklist, internal consistency)
- [ ] Highlights, notes, and saved AI explanations
- [ ] Link cards with bilingual summaries; optional web-browsing/RAG with citations
- [ ] Multi-model cross-check and refinement (enhanced mode)

See [docs/pov_features.md](docs/pov_features.md) for the detailed phase breakdown.

## Quick Start

### Prerequisites

- Backend: Python 3.12+, FastAPI
- Frontend: Node.js 22+, SvelteKit
- Access: A valid API key from OpenAI, Anthropic, or other supported providers

### Installation

```bash
# Clone and open
git clone https://github.com/grammy-jiang/Luminote.git
cd Luminote

# Run backend (FastAPI)
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Linux/Mac: cp; Windows: copy
# Edit .env and set:
#   LUMINOTE_TARGET_LANG (e.g., zh, en, ja)
#   LUMINOTE_PROVIDER (e.g., openai, anthropic)
#   LUMINOTE_MODEL (e.g., gpt-4o-mini, claude-3-5-sonnet)
#   LUMINOTE_API_KEY (your API key)

uvicorn app.main:app --reload --port 8000
```

```bash
# Frontend (Svelte + Rollup, TypeScript) - in a new terminal
cd frontend
npm install
npm run dev  # serves at http://localhost:5000
```

### Usage

1. Enter a URL in the input field
2. Click "Translate" to fetch and translate the content
3. View original content (left) and translation (right) side-by-side
4. Hover over blocks to see synchronized highlighting
5. Configure settings in the top-right menu (language, provider, model)

## Documentation

- **Product Purpose & Functionality:** [docs/purpose_and_functionality.md](docs/purpose_and_functionality.md)
- **POV Features & Roadmap:** [docs/pov_features.md](docs/pov_features.md)
- **API Reference:** [docs/API.md](docs/API.md)
- **Development & Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Architecture:** Coming soon in `ARCHITECTURE.md`

## Support & Community

- **Issues:** [GitHub Issues](https://github.com/grammy-jiang/Luminote/issues)
- **Questions:** Use [GitHub Discussions](https://github.com/grammy-jiang/Luminote/discussions) (when available)
- **Security Issues:** Contact the maintainer directly rather than filing public issues

## Contributing

Contributions are welcome! To help:
1. Fork the repo and create a feature branch
2. Keep changes focused and add tests when reasonable
3. Open a pull request with a clear description and rationale

A full contribution guide (coding style, commit conventions, branching model) will be available in `CONTRIBUTING.md`.

## License

The code in this project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See [LICENSE](LICENSE) for the full text. By contributing, you agree that your contributions will be licensed under GPL-3.0.

