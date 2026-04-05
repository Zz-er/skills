# llm-wiki-plugin

A personal knowledge base maintained by an LLM. Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Provides three global skills: `/wiki-query`, `/wiki-update`, `/wiki-ingest` — accessible from any project.

## Skills Included

| Skill | Trigger | What it does |
|-------|---------|-------------|
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

# 3. Configure your wiki location
echo '{ "wiki_dir": "/path/to/your/wiki" }' > ~/.claude/wiki-tools.json
```

To update later:

```bash
claude plugin update wiki-tools
```

### First-time Wiki Setup

If you don't have a wiki directory yet, use the bundled installer to scaffold one:

```bash
# Clone the repo
git clone https://github.com/Zz-er/skills.git /tmp/skills

# Run the installer — creates directory structure, CLAUDE.md schema, seed files
cd /tmp/skills/llm-wiki-plugin
python install.py ~/my-wiki
```

The installer will:
- Create the wiki directory with `raw/`, `wiki/`, templates, and `CLAUDE.md`
- Write `~/.claude/wiki-tools.json` pointing to your wiki path
- Install the plugin via marketplace

## How Paths Work

All skills read the wiki location from `~/.claude/wiki-tools.json`:

```json
{ "wiki_dir": "/home/alice/my-wiki" }
```

To change the wiki path, just edit this file — no reinstall needed.

## Core Workflows

### Ingest
Drop a document into `raw/`, tell Claude "ingest this". It reads, summarizes, creates wiki pages, updates cross-references.

### Query
Ask Claude any question. It searches the wiki, synthesizes an answer with citations.

### Lint
Ask Claude for a health check. It finds orphan pages, broken links, contradictions, and gaps.

## Integration with reimpl-tutorial

If you also use the `reimpl-tutorial` plugin, run the patch script to add Wiki integration:

```bash
python patch_reimpl_tutorial.py                          # auto-detect skill location
python patch_reimpl_tutorial.py /path/to/.claude/skills  # explicit path
```

This adds:
- **Phase 1 Step 0** — automatically queries the wiki for existing knowledge before analysis
- **Phase 6** — syncs tutorial knowledge back into the wiki after completion
- **Quality checklist** — wiki sync verification item

The patch is idempotent — safe to run multiple times.

## Plugin Structure

```
llm-wiki-plugin/
├── .claude-plugin/marketplace.json
├── README.md
├── install.py                         # First-time wiki scaffolding
├── uninstall.py                       # Clean removal
├── patch_reimpl_tutorial.py           # Optional reimpl-tutorial integration
├── plugins/wiki-tools/
│   ├── .claude-plugin/plugin.json
│   └── skills/
│       ├── wiki-query/SKILL.md
│       ├── wiki-update/SKILL.md
│       └── wiki-ingest/SKILL.md
└── templates/                         # Wiki directory templates
    ├── CLAUDE.md.tmpl
    ├── gitignore.tmpl
    └── wiki/*.md.tmpl
```

## Uninstall

```bash
python uninstall.py                        # remove plugin + config (keeps wiki data)
python uninstall.py --all ~/my-wiki        # remove everything
```

## Requirements

- Python 3.6+
- [Claude Code](https://claude.ai/claude-code) CLI
- `git` (for version history)

## License

MIT
