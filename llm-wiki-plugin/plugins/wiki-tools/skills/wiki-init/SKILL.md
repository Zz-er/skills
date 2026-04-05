---
name: wiki-init
description: >
  Initialize a new LLM Wiki directory from scratch. Use this skill when the user
  has just installed the wiki-tools plugin and needs to create their wiki for the
  first time. Trigger on "/wiki-init", "create a wiki", "initialize wiki",
  "setup wiki", "新建知识库", "初始化wiki". This skill creates the full directory
  structure, writes the CLAUDE.md schema, seeds index/log/overview files,
  configures the wiki path, and initializes a git repo — all without requiring
  any external scripts or cloning.
---

# Wiki Init — Create a New LLM Wiki

Set up a complete LLM Wiki directory from scratch. This replaces the old
`install.py` workflow — everything happens inside Claude Code, no external
scripts or repo cloning needed.

## Process

### Step 1 — Determine Wiki Location

Ask the user where they want their wiki. Suggest `~/llm_wiki` as the default.
Accept a path argument if provided (e.g., `/wiki-init ~/my-wiki`).

### Step 2 — Create Directory Structure

```bash
mkdir -p <wiki_dir>/raw/assets
mkdir -p <wiki_dir>/wiki/sources
mkdir -p <wiki_dir>/wiki/entities
mkdir -p <wiki_dir>/wiki/concepts
mkdir -p <wiki_dir>/wiki/analyses
```

### Step 3 — Write CLAUDE.md

Read the template from this plugin's `templates/` directory and write it to
`<wiki_dir>/CLAUDE.md`:

```bash
# The template is at:
# <this-plugin-root>/templates/CLAUDE.md.tmpl
# Where <this-plugin-root> is 3 levels up from this SKILL.md:
#   wiki-init/SKILL.md -> skills/ -> wiki-tools/ -> plugins/ -> llm-wiki-plugin/
```

Find the plugin root by navigating upward from this skill's directory:
`<this-skill-dir>/../../..` → the `llm-wiki-plugin/` directory containing `templates/`.

Copy `templates/CLAUDE.md.tmpl` → `<wiki_dir>/CLAUDE.md` (no replacements needed).

### Step 4 — Write Seed Wiki Files

Read templates and replace `YYYY-MM-DD` with today's date:

| Template | Destination |
|----------|-------------|
| `templates/wiki/index.md.tmpl` | `<wiki_dir>/wiki/index.md` |
| `templates/wiki/log.md.tmpl` | `<wiki_dir>/wiki/log.md` |
| `templates/wiki/overview.md.tmpl` | `<wiki_dir>/wiki/overview.md` |
| `templates/gitignore.tmpl` | `<wiki_dir>/.gitignore` |

### Step 5 — Write Wiki Config

Write the wiki path to `~/.claude/wiki-tools.json` so all other wiki skills
can find it:

```json
{ "wiki_dir": "/absolute/path/to/wiki" }
```

### Step 6 — Initialize Git

```bash
cd <wiki_dir>
git init
git add -A
git commit -m "Initial LLM Wiki setup: directory structure, schema, and seed files"
```

### Step 7 — Confirm

Tell the user:

```
Wiki initialized at: <wiki_dir>

Next steps:
  1. Drop a document into <wiki_dir>/raw/
  2. Tell Claude: "ingest the new source"

Global skills now available:
  /wiki-query   — search the knowledge base
  /wiki-update  — add knowledge to the wiki
  /wiki-ingest  — import a tutorial project
```

## Notes

- If `<wiki_dir>` already exists and has content, warn the user and ask before
  overwriting. Never silently overwrite existing files.
- If `~/.claude/wiki-tools.json` already exists, show the current path and ask
  if the user wants to update it.
- Always use absolute paths in the config file.
