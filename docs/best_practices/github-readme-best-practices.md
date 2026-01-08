<!-- mdformat-toc start --slug=github --maxlevel=3 --minlevel=1 -->

- [GitHub README.md Best Practices (End‑User First)](#github-readmemd-best-practices-end%E2%80%91user-first)
  - [1) Project name + one‑liner](#1-project-name--one%E2%80%91liner)
  - [2) Key features up front](#2-key-features-up-front)
  - [3) Quick start for end‑users](#3-quick-start-for-end%E2%80%91users)
    - [Installation](#installation)
    - [Minimal usage example](#minimal-usage-example)
  - [4) Badges: high signal, low noise](#4-badges-high-signal-low-noise)
  - [5) Documentation funnel: README as the front door](#5-documentation-funnel-readme-as-the-front-door)
  - [6) Separate developer-facing content cleanly](#6-separate-developer-facing-content-cleanly)
  - [7) Help, support, and project status](#7-help-support-and-project-status)
  - [8) License and acknowledgments](#8-license-and-acknowledgments)
  - [9) Readability and structure standards](#9-readability-and-structure-standards)
  - [10) Language-specific conventions (Python / JS/TS / Rust)](#10-language-specific-conventions-python--jsts--rust)
    - [Python (libraries/tools)](#python-librariestools)
    - [JavaScript/TypeScript](#javascripttypescript)
    - [Rust](#rust)
  - [Practical README skeleton (copy/paste)](#practical-readme-skeleton-copypaste)
  - [Sources (high-level)](#sources-high-level)
- [中文版本（简要）](#%E4%B8%AD%E6%96%87%E7%89%88%E6%9C%AC%EF%BC%88%E7%AE%80%E8%A6%81%EF%BC%89)
  - [核心要点](#%E6%A0%B8%E5%BF%83%E8%A6%81%E7%82%B9)
  - [语言生态建议](#%E8%AF%AD%E8%A8%80%E7%94%9F%E6%80%81%E5%BB%BA%E8%AE%AE)

<!-- mdformat-toc end -->

# GitHub README.md Best Practices (End‑User First)<a name="github-readmemd-best-practices-end%E2%80%91user-first"></a>

> **Goal:** Help end-users understand your project’s purpose and key features
> quickly, while providing clear paths to deeper developer/design docs.

______________________________________________________________________

## 1) Project name + one‑liner<a name="1-project-name--one%E2%80%91liner"></a>

- Put the **project name** at the top.
- Follow with a **one‑sentence value proposition**: what it is, who it’s for,
  and why it matters.
- Keep it plain English; avoid internal jargon.

______________________________________________________________________

## 2) Key features up front<a name="2-key-features-up-front"></a>

- Add a short **Features / Highlights** section immediately after the intro.
- Use **3–7 bullet points**. Focus on outcomes and differentiators (not
  implementation).
- If relevant, note **supported platforms** and major constraints (OS, versions,
  runtime).

______________________________________________________________________

## 3) Quick start for end‑users<a name="3-quick-start-for-end%E2%80%91users"></a>

### Installation<a name="installation"></a>

Provide the most common install path first:

- **Python:** `pip install <package>`
- **JavaScript/TypeScript:** `npm i <package>` / `yarn add <package>`
- **Rust:** `cargo add <crate>` (library) / `cargo install <crate>` (CLI)

If prerequisites exist (Python/Node/Rust version, OS requirements), list them
**before** install steps.

### Minimal usage example<a name="minimal-usage-example"></a>

- Include a **copy‑pasteable** minimal example (CLI command or small code
  snippet).
- Show expected output or behavior when possible.
- Consider a screenshot/GIF for UI projects—visual proof reduces user friction.

______________________________________________________________________

## 4) Badges: high signal, low noise<a name="4-badges-high-signal-low-noise"></a>

Badges are useful to show project health at a glance. Keep them minimal and
meaningful:

Recommended:

- Build/CI status
- Release version (PyPI/npm/crates.io/GitHub Releases)
- License
- Coverage (if you genuinely maintain it)

Avoid:

- Vanity metrics or too many badges (visual noise)
- Badges that are frequently broken or outdated

______________________________________________________________________

## 5) Documentation funnel: README as the front door<a name="5-documentation-funnel-readme-as-the-front-door"></a>

Treat README as an **elevator pitch + onboarding**. Don’t overload it with deep
technical material.

Instead:

- Link to **Documentation** (docs site, `docs/`, wiki)
- Link to **Architecture / Design docs** (e.g., `ARCHITECTURE.md`,
  `docs/design/`)
- Link to **API reference** (Rustdoc, typedoc, sphinx, mkdocs, etc.)

A good pattern is:

- “Quick start” in README
- “Advanced usage + API” in docs
- “Contribution + development setup” in CONTRIBUTING.md

______________________________________________________________________

## 6) Separate developer-facing content cleanly<a name="6-separate-developer-facing-content-cleanly"></a>

Add (or link to) dedicated files:

- `CONTRIBUTING.md` — contribution workflow and dev setup
- `CODE_OF_CONDUCT.md` — community expectations
- `SECURITY.md` — vuln reporting policy (especially for widely used libs)
- `CHANGELOG.md` — release notes and breaking changes

In README, keep a short “Contributing” section with a pointer to these
documents.

______________________________________________________________________

## 7) Help, support, and project status<a name="7-help-support-and-project-status"></a>

Users want to know:

- **Where to ask questions / get support** (Issues, Discussions, Discord/Slack,
  email)
- **How to report bugs** (issue templates help)
- Whether the project is **actively maintained**

If the project is unmaintained, state it clearly near the top (saves everyone
time).

______________________________________________________________________

## 8) License and acknowledgments<a name="8-license-and-acknowledgments"></a>

- Include a short **License** section and link to `LICENSE`.
- Add **Acknowledgments/Credits** if your project builds on others.

______________________________________________________________________

## 9) Readability and structure standards<a name="9-readability-and-structure-standards"></a>

- Use clear headings (`##`) and consistent section order.
- Prefer short paragraphs + lists for scannability.
- Keep the tone direct and professional.
- Consider a Table of Contents if the README is long (GitHub also provides an
  auto TOC in the UI).

A useful heuristic:

> “As short as it can be without being any shorter.”

______________________________________________________________________

## 10) Language-specific conventions (Python / JS/TS / Rust)<a name="10-language-specific-conventions-python--jsts--rust"></a>

### Python (libraries/tools)<a name="python-librariestools"></a>

- Mention supported Python versions.
- Provide `pip install ...` and a minimal snippet.
- Link to docs (ReadTheDocs/MkDocs/Sphinx) for advanced API.
- Common badges: PyPI version, CI, license, coverage.

### JavaScript/TypeScript<a name="javascripttypescript"></a>

- Mention supported Node.js versions.
- Provide npm/yarn install and minimal example.
- If a web demo exists, link it.
- Common badges: npm version, CI, license.

### Rust<a name="rust"></a>

- Mention MSRV (minimum supported Rust version) if you enforce one.
- Provide cargo add/install and a minimal snippet.
- Link to docs.rs (or generated docs).
- Common badges: crates.io version, CI, license.

______________________________________________________________________

## Practical README skeleton (copy/paste)<a name="practical-readme-skeleton-copypaste"></a>

```markdown

# ProjectName

> One-line description: what it does, who it's for, why it matters.

[![CI](...)](...) [![License](...)](...) [![Version](...)](...)

## Features

- Feature 1 (end-user benefit)
- Feature 2
- Feature 3

## Quick Start

### Install

- (Prereqs)
- Command(s)

### Use

- Minimal example
- Expected output

## Documentation

- User guide: ...
- API reference: ...
- Design/architecture: ...

## Support

- Issues / Discussions / Contact

## Contributing

See CONTRIBUTING.md

## License

MIT (see LICENSE)

```

______________________________________________________________________

## Sources (high-level)<a name="sources-high-level"></a>

- GitHub docs: README purpose and typical content.
- Community guides and checklists on structuring READMEs, documentation funnels,
  and badge usage.
- Curated example lists (“awesome README”) and standardized README specs
  (“Standard Readme”).

______________________________________________________________________

# 中文版本（简要）<a name="%E4%B8%AD%E6%96%87%E7%89%88%E6%9C%AC%EF%BC%88%E7%AE%80%E8%A6%81%EF%BC%89"></a>

> **目标：** README 主要服务终端用户：让用户在 30–60 秒内理解“这是什么、能解决什么、怎么开始”。开发者信息用链接下沉到文档。

## 核心要点<a name="%E6%A0%B8%E5%BF%83%E8%A6%81%E7%82%B9"></a>

- **标题 + 一句话价值主张：** 直接说明用途、目标用户、收益。
- **功能亮点优先：** 3–7 条 bullet，讲结果/价值，不讲实现细节。
- **Quick Start：** 先给最常用的安装方式 + 最小可复制示例（CLI 或代码片段）。
- **Badges：** 少而精（CI、版本、License、覆盖率）；避免堆砌。
- **README 做入口：** 深度内容放 docs/、Wiki、ARCHITECTURE.md、CONTRIBUTING.md，并在 README 链接。
- **支持与状态：** 明确支持渠道（Issues/Discussions/群组）以及是否维护中。
- **License：** 明确协议并链接 LICENSE。

## 语言生态建议<a name="%E8%AF%AD%E8%A8%80%E7%94%9F%E6%80%81%E5%BB%BA%E8%AE%AE"></a>

- **Python：** 标注 Python 版本；`pip install`；示例；链接到文档站点。
- **JS/TS：** 标注 Node 版本；npm/yarn；示例；如有 demo，给链接。
- **Rust：** 标注 MSRV（如有）；cargo add/install；示例；链接 docs.rs。
