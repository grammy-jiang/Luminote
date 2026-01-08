<!-- mdformat-toc start --slug=github --maxlevel=3 --minlevel=1 -->

- [Luminote](#luminote)
  - [Why Luminote?](#why-luminote)
  - [Product Roadmap & Features](#product-roadmap--features)
  - [Quick Start](#quick-start)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
  - [Documentation](#documentation)
    - [Planning & Architecture](#planning--architecture)
    - [Feature Documentation](#feature-documentation)
    - [Development](#development)
  - [Support & Community](#support--community)
  - [Contributing](#contributing)
  - [License](#license)

<!-- mdformat-toc end -->

![Luminote](docs/assets/logo.webp)

# Luminote<a name="luminote"></a>

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 22+](https://img.shields.io/badge/node.js-22+-green.svg)](https://nodejs.org/)
[![Status: Planning](https://img.shields.io/badge/status-planning-yellow.svg)](docs/PROJECT-STATUS.md)

> AI-powered two-pane translation workbench for fast, accurate understanding and
> verification of web content.

**🔨 Project Status:** Currently in planning phase. See
[PROJECT-STATUS.md](docs/PROJECT-STATUS.md) for detailed progress.

**✅ Planning Completed:**

- Feature dependency analysis
  ([feature-dependency-analysis.md](docs/feature-dependency-analysis.md))
- Infrastructure requirements
  ([infrastructure-requirements.md](docs/infrastructure-requirements.md))
- Architecture decision records ([adr/](docs/adr/))
- Atomic features breakdown ([atomic-features.md](docs/atomic-features.md))
- Tech stack layer mapping ([layer-mapping.md](docs/layer-mapping.md))
- Implementation sequence
  ([implementation-sequence.md](docs/implementation-sequence.md))

**What makes Luminote different**

- **Two-pane reading**: source on the left (reader-mode), **translation is the
  primary, persistent view** on the right
- **Selection commands**: select text on either pane → explain / define terms /
  summarize / (later) verify
- **Versioned artifacts**: notes/highlights/history + prompt-driven regeneration
  (keep recent versions)

Luminote is a local-first, AI-driven reading workbench that transforms web
materials into **understandable, verifiable, and reviewable** knowledge assets.
The original content appears on the left in reader-mode, and the AI translation
is your primary, persistent view on the right. AI insights and verification
capabilities are on-demand and user-controlled.

## Why Luminote?<a name="why-luminote"></a>

Most translation tools stop at converting words. Luminote targets the real
problem: **fast, accurate understanding and verification** of high-density
materials—news articles, research papers, technical documentation, financial
reports. Translation is the core function, but it serves a bigger goal:
**understand + verify + retain**.

## Product Roadmap & Features<a name="product-roadmap--features"></a>

**Phase 1**

- [ ] Dual-pane translation with progressive, block-level rendering
- [ ] Reader-mode extraction from **most public URLs** (titles, paragraphs,
  lists, quotes, code, images)
- [ ] BYOK configuration for target language, provider/model, and API key
- [ ] Clear error handling for fetch failures, invalid keys, and rate limits
- [ ] Block-level synchronization with hover/click linkage between panes

**Phase 2**

- [ ] Re-translate per-block or full document with custom prompts
- [ ] Local visit history and quick paste-text translation (fallback when
  extraction fails)
- [ ] Selection-based commands: Explain, Define terms, Summarize (and save as
  notes)
- [ ] Prompt templates and termbase setup; translation versioning (keep last
  versions)

**Phase 3**

- [ ] On-demand AI insights and verification packs (claims checklist, internal
  consistency)
- [ ] Highlights, notes, and saved AI explanations
- [ ] Link cards with bilingual summaries; optional web-browsing/RAG with
  citations
- [ ] Multi-model cross-check and refinement (enhanced mode)

For detailed specifications, see
[docs/feature-specifications.md](docs/feature-specifications.md).

## Quick Start<a name="quick-start"></a>

### Prerequisites<a name="prerequisites"></a>

- Backend: Python 3.12+, FastAPI
- Frontend: Node.js 22+, SvelteKit
- Access: A valid API key from OpenAI, Anthropic, or other supported providers

### Installation<a name="installation"></a>

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

### Usage<a name="usage"></a>

1. Enter a URL in the input field
1. Click "Translate" to fetch and translate the content
1. View original content (left) and translation (right) side-by-side
1. Hover over blocks to see synchronized highlighting
1. Configure settings in the top-right menu (language, provider, model)

## Documentation<a name="documentation"></a>

### Planning & Architecture<a name="planning--architecture"></a>

- **[Project Status](docs/PROJECT-STATUS.md)** ⭐ - Current progress, next steps,
  and achievements
- **[GitHub Issue Methodology](docs/github-issue-creation-methodology.md)** -
  Systematic issue creation process
- **[Feature Dependencies](docs/feature-dependency-analysis.md)** - Dependency
  graphs and implementation batches
- **[Infrastructure Requirements](docs/infrastructure-requirements.md)** -
  Complete setup and tooling guide
- **[Architecture Decision Records](docs/adr/)** - Key architectural choices and
  rationale

### Feature Documentation<a name="feature-documentation"></a>

- **[Feature Specifications](docs/feature-specifications.md)** - Comprehensive
  specifications for all phases
- **[API Reference](docs/API.md)** - Backend API endpoints and usage (coming
  soon)
- **[Architecture Overview](ARCHITECTURE.md)** - System architecture and design
  patterns

### Development<a name="development"></a>

- **[Contributing Guide](CONTRIBUTING.md)** - Setup, coding standards, and
  workflow
- **[Development Environment](docs/infrastructure-requirements.md#phase-0-infrastructure-setup-week-1)**
  \- Local setup instructions

## Support & Community<a name="support--community"></a>

- Bug reports & feature requests:
  [GitHub Issues](https://github.com/grammy-jiang/Luminote/issues)
- Questions & discussions:
  [GitHub Discussions](https://github.com/grammy-jiang/Luminote/discussions)
- Security vulnerabilities: Contact the maintainer directly rather than filing
  public issues
- Status: This project is actively maintained; see
  [CONTRIBUTING.md](CONTRIBUTING.md) for development info

## Contributing<a name="contributing"></a>

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Coding style and conventions
- Branching model and pull request workflow
- How to report bugs and propose features

## License<a name="license"></a>

This project is licensed under the **GNU General Public License v3.0
(GPL-3.0)**. See [LICENSE](LICENSE) for details. By contributing, you agree your
contributions will be licensed under GPL-3.0.
