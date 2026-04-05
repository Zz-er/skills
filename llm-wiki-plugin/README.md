# LLM Wiki — Portable Installer

A personal knowledge base maintained by an LLM. Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Quick Start

```bash
# Clone or copy this directory to your new machine, then:
cd portable/
python install.py ~/my-wiki     # or any path you prefer

# In Claude Code:
/reload-plugins
```

Works on **Linux, macOS, and Windows**.

## What Gets Installed

| Component | Location | Purpose |
|-----------|----------|---------|
| Wiki repo | `<your-path>/` | Directory structure, CLAUDE.md schema, seed files |
| Wiki config | `~/.claude/wiki-tools.json` | Stores wiki path for all skills |
| wiki-tools plugin | Via `claude plugin install` | Global `/wiki-query`, `/wiki-update`, `/wiki-ingest` skills |
| Marketplace | `llm-wiki` local marketplace | Enables plugin updates via `claude plugin update wiki-tools` |
| Recommended plugins | Claude Code global | commit-commands, context7, hookify, etc. |

## How Paths Work

The installer writes the wiki location to `~/.claude/wiki-tools.json`:

```json
{ "wiki_dir": "/home/alice/my-wiki" }
```

All skills read this config at runtime. To change the wiki path, just edit this file — no reinstall needed.

## Global Skills

These work from **any project**, not just the wiki directory:

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `/wiki-query` | "check the wiki", "查查知识库" | Search and read from the wiki |
| `/wiki-update` | "add to wiki", "写入wiki" | Create or update wiki pages |
| `/wiki-ingest` | "sync to wiki", "导入知识库" | Import a completed tutorial project |

## Core Workflows

### Ingest
Drop a document into `raw/`, tell Claude "ingest this". It reads, summarizes, creates wiki pages, updates cross-references.

### Query
Ask Claude any question. It searches the wiki, synthesizes an answer with citations.

### Lint
Ask Claude for a health check. It finds orphan pages, broken links, contradictions, and gaps.

## Integration with reimpl-tutorial

If you use the `reimpl-tutorial` skill, run the patch script to add Wiki integration:

```bash
python patch_reimpl_tutorial.py                          # auto-detect skill location
python patch_reimpl_tutorial.py /path/to/.claude/skills  # explicit path
```

This adds:
- **Phase 1 Step 0** — automatically queries the wiki for existing knowledge before analysis
- **Phase 6** — syncs tutorial knowledge back into the wiki after completion
- **Quality checklist** — wiki sync verification item

The patch is idempotent — safe to run multiple times. The installer also auto-detects and offers to patch if reimpl-tutorial is found.

## Updating the Plugin

```bash
claude plugin update wiki-tools
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
