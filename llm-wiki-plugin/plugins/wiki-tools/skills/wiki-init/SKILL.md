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

Set up a complete LLM Wiki directory from scratch. Everything happens inside
Claude Code — no external scripts, no repo cloning.

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
`<wiki_dir>/CLAUDE.md`.

Find the plugin root by navigating upward from this skill's directory:
`<this-skill-dir>/../../..` → the `llm-wiki-plugin/` directory containing
`templates/`.

Copy `templates/CLAUDE.md.tmpl` → `<wiki_dir>/CLAUDE.md` (no replacements).

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

### Step 7 — Detect and Integrate with Knowledge Skills

After the wiki is created, scan for other installed skills that could benefit
from wiki integration. For each detected skill, check if integration is already
present — if so, skip silently. If not, ask the user whether to add it.

#### 7.1 — reimpl-tutorial Integration

Search for `reimpl-tutorial`'s `SKILL.md` in these locations (stop at first match):

- `~/.claude/local-plugins/*/skills/reimpl-tutorial/SKILL.md`
- `~/.claude/skills/reimpl-tutorial/SKILL.md`
- `.claude/skills/reimpl-tutorial/SKILL.md` (project-level, walking upward)

**If found**, read the file and check whether it already contains `wiki-query`.

- **Already integrated** → print "reimpl-tutorial: wiki integration already
  present, skipping" and move on.
- **Not integrated** → ask the user: "Found reimpl-tutorial. Add wiki
  integration? This adds Phase 1 wiki lookup and Phase 6 knowledge sync."

  If the user agrees, apply these three edits to the SKILL.md:

  **Edit A — Phase 1 Step 0** (insert before the first numbered step in
  Phase 1, i.e. before `1. **Read`):

  ```
  0. **Query the Wiki** — Use `/wiki-query` to check what the Wiki already knows
     about this project's domain. Look for existing concept pages (algorithms,
     patterns), entity pages (tools, frameworks, authors), and related analyses.
     This avoids re-deriving knowledge that's already been synthesized from
     previous tutorials or sources. Note which wiki pages are relevant — you'll
     link back to them later.
  ```

  **Edit B — Phase 6** (insert after Phase 5, before `## Output Directory
  Structure`):

  ```
  ### Phase 6 — Wiki Knowledge Sync

  Sync the tutorial's knowledge into the LLM Wiki **after Phase 4 is complete
  and all quality checks pass**. This step is part of the standard flow — ask
  the user for confirmation before proceeding.

  1. **Run `/wiki-ingest`** — invoke the global wiki-ingest skill, passing the
     path to this tutorial's output directory. The skill handles everything:
     - Copies SUMMARY.md to the Wiki's `raw/` directory
     - Creates source summary, concept, entity, and analysis pages
     - Updates index and log
     - Cross-references with existing wiki content
     - Flags contradictions
  2. **Review the output** — the wiki-ingest skill will report what pages were
     created/updated. Verify the results make sense.
  3. **Mention wiki connections in notebooks** — if the wiki already had relevant
     concept pages (found in Phase 1 Step 0), add a note in the relevant
     notebooks linking to those existing wiki entries for deeper context.

  **Why this matters:** Without this step, the deep knowledge generated during
  tutorial creation stays locked in notebooks. The Wiki makes it searchable,
  cross-referenced, and available for future tutorials on related topics.
  ```

  **Edit C — Quality Checklist** (append after the last checklist item):

  ```
  - [ ] Tutorial knowledge has been synced to the LLM Wiki (Phase 6) — or user declined
  ```

**If not found** → print "reimpl-tutorial not detected, skipping wiki
integration" and move on.

#### 7.2 — Future Skills (placeholder)

This section is for future knowledge-related skills that could benefit from
wiki integration. When new skills are added to this plugin or the ecosystem,
add detection logic here following the same pattern:

1. Search for the skill's SKILL.md
2. Check if wiki integration markers already exist
3. Ask the user before modifying
4. Apply targeted edits (never overwrite the whole file)

### Step 8 — Confirm

Tell the user:

```
Wiki initialized at: <wiki_dir>

Next steps:
  1. Drop a document into <wiki_dir>/raw/
  2. Tell Claude: "ingest the new source"

Global skills now available:
  /wiki-init    — (you just ran this)
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
- When editing other skills' SKILL.md files, use the Edit tool for targeted
  insertions — never rewrite the entire file.
