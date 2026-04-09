# CLAUDE.md

## Project Overview

A Claude Code plugin marketplace containing two plugins:
- **reimpl-tutorial** (`reimpl-tutorial-plugin/`) — Tutorial generation via project reimplementation
- **wiki-tools** (`llm-wiki-plugin/`) — Personal LLM Wiki knowledge base

## Version Management

**Every code change that modifies plugin behavior must bump the version number before committing.**

Version files:
- `reimpl-tutorial-plugin/.claude-plugin/plugin.json` → `"version": "x.y.z"`
- `llm-wiki-plugin/plugins/wiki-tools/.claude-plugin/plugin.json` → `"version": "x.y.z"`

Versioning rules (semver):
- **Patch** (x.y.Z): bug fixes, typo corrections, minor wording changes
- **Minor** (x.Y.0): new features, new prompt files, new template sections, structural changes
- **Major** (X.0.0): breaking changes to skill behavior or output format

## Repository Structure

```
skills/
├── .claude-plugin/marketplace.json    # Plugin discovery for marketplace
├── README.md                          # Installation guide
├── reimpl-tutorial-plugin/
│   ├── .claude-plugin/plugin.json     # Plugin metadata + version
│   └── skills/
│       ├── reimpl-tutorial/           # Main tutorial generation skill
│       │   ├── SKILL.md               # Authoritative spec (~700 lines)
│       │   ├── prompts/               # Writing guidance
│       │   │   ├── analysis-deep.md
│       │   │   ├── derivation-prompt.md
│       │   │   ├── feature-extraction.md
│       │   │   ├── style-guide.md
│       │   │   └── walkthrough-prompt.md
│       │   ├── templates/             # Notebook structure templates
│       │   │   ├── cognitive-order.yaml
│       │   │   └── feature-template.md
│       │   └── scripts/               # Helper utilities
│       └── excalidraw-diagram/        # Bundled diagram skill
└── llm-wiki-plugin/
    └── plugins/wiki-tools/
        ├── .claude-plugin/plugin.json
        └── skills/                    # wiki-query, wiki-update, wiki-ingest, etc.
```

## Commit Conventions

- Prefix: `add`, `fix`, `update`, `bump`, `refactor`
- Include `Co-Authored-By` trailer
- If plugin files changed, include version bump in the same commit or a separate `bump` commit
