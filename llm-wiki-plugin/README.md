# llm-wiki-plugin

A personal knowledge base maintained by an LLM. Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Provides four global skills — accessible from any project, no additional setup required.

## Skills Included

| Skill | Trigger | What it does |
|-------|---------|-------------|
| **wiki-init** | `/wiki-init ~/my-wiki` | Create a new wiki directory with full structure and schema |
| **wiki-query** | "check the wiki", "查查知识库" | Search and read from the wiki |
| **wiki-update** | "add to wiki", "写入wiki" | Create or update wiki pages |
| **wiki-ingest** | "sync to wiki", "导入知识库" | Import a completed tutorial or source document |

## Installation

### Via Claude Code Plugin Marketplace (recommended)

```bash
# 1. Add this repo as a marketplace source
claude plugin marketplace add https://github.com/Zz-er/skills

# 2. Install the plugin
claude plugin install wiki-tools
```

That's it. All four skills are now globally available.

### First-time Wiki Setup

After installing the plugin, initialize your wiki from within Claude Code:

```
/wiki-init ~/my-wiki
```

This creates the full directory structure, writes the CLAUDE.md schema, seeds
index/log/overview files, configures the wiki path, and initializes a git repo.
No cloning, no scripts — everything happens inside Claude Code.

### Updating

```bash
claude plugin update wiki-tools
```

## How Paths Work

All skills read the wiki location from `~/.claude/wiki-tools.json`:

```json
{ "wiki_dir": "/home/alice/my-wiki" }
```

This file is created automatically by `/wiki-init`. To change the wiki path,
edit it directly — no reinstall needed.

## Core Workflows

### Ingest
Drop a document into `raw/`, tell Claude "ingest this". It reads, summarizes,
creates wiki pages, updates cross-references.

### Query
Ask Claude any question. It searches the wiki, synthesizes an answer with citations.

### Lint
Ask Claude for a health check. It finds orphan pages, broken links,
contradictions, and gaps.

## Integration with reimpl-tutorial

During `/wiki-init`, if the `reimpl-tutorial` plugin is detected, you'll be
asked whether to add wiki integration. If you agree, it adds:

- **Phase 1 Step 0** — `wiki-query` checks for existing knowledge before analysis
- **Phase 6** — `wiki-ingest` syncs tutorial knowledge back into the wiki
- **Quality checklist** — wiki sync verification item

Already-integrated skills are detected and skipped automatically.

## Plugin Structure

```
llm-wiki-plugin/
├── .claude-plugin/marketplace.json
├── README.md
├── plugins/wiki-tools/
│   ├── .claude-plugin/plugin.json
│   └── skills/
│       ├── wiki-init/SKILL.md       # Create new wiki + detect integrations
│       ├── wiki-query/SKILL.md      # Search wiki
│       ├── wiki-update/SKILL.md     # Update wiki pages
│       └── wiki-ingest/SKILL.md     # Import sources
└── templates/                       # Wiki directory templates (used by wiki-init)
    ├── CLAUDE.md.tmpl
    ├── gitignore.tmpl
    └── wiki/*.md.tmpl
```

## Uninstall

```bash
claude plugin uninstall wiki-tools
```

This removes the plugin only. Your wiki data is untouched.

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI
- `git` (for version history)

## License

MIT
