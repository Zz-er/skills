---
name: wiki-update
description: >
  Write to the LLM Wiki knowledge base from any project. Use this skill when
  you need to add new knowledge, update existing pages, or create new concept/
  entity/analysis pages in the wiki. Trigger on phrases like "add to wiki",
  "update the wiki", "记到知识库", "写入wiki", "wiki-update", or when a task
  produces reusable knowledge that should be preserved. Also triggered
  automatically after learning activities when the user confirms wiki sync.
---

# Wiki Update — Global Knowledge Write

You are writing to the LLM Wiki knowledge base to add or update knowledge.
This ensures that knowledge produced during any task — not just within the
wiki project itself — gets properly filed, cross-referenced, and preserved.

## Wiki Location

Read `~/.claude/wiki-tools.json` to get the wiki directory path:

```json
{ "wiki_dir": "/path/to/your/wiki" }
```

Schema is defined in: `<wiki_dir>/CLAUDE.md`

## What Can Be Written

| Type | Directory | When to Use |
|------|-----------|-------------|
| Source summary | `wiki/sources/` | Ingested a new document, article, tutorial |
| Concept | `wiki/concepts/` | Learned about an algorithm, pattern, theory |
| Entity | `wiki/entities/` | Encountered a notable person, project, tool |
| Analysis | `wiki/analyses/` | Produced a comparison, deep-dive, or insight |

## Process

### Step 1 — Determine What to Write

Classify the knowledge:
- Is it a **new concept** the wiki doesn't cover yet?
- Is it an **update** to an existing page (new evidence, corrections)?
- Is it a **new entity** (project, person, tool)?
- Is it an **analysis** (comparison, insight, design decision)?

### Step 2 — Check for Existing Pages

Read `<wiki_dir>/wiki/index.md` to check if relevant
pages already exist. **Always prefer updating over creating duplicates.**

### Step 3 — Write the Page(s)

Follow the templates defined in the Wiki's CLAUDE.md:

#### Frontmatter (Required on Every Page)

```yaml
---
title: "Page Title"
type: source | entity | concept | analysis
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
sources: [source-filename-1]
---
```

#### Rules

- **Filenames**: kebab-case (e.g., `transformer-architecture.md`)
- **Language**: Chinese (简体中文) by default
- **Cross-references**: use `[[wikilinks]]` format (e.g., `[[attention-mechanism]]`)
- **Citations**: `[Source: filename]` for tracing provenance
- **Contradictions**: mark with `> ⚠️ Contradiction:` callout on both pages

### Step 4 — Update Existing Pages

When adding new knowledge, check if it connects to existing pages:

1. Search for related terms across all wiki pages
2. Add `[[wikilinks]]` on existing pages pointing to the new content
3. Add new evidence to existing concept/entity pages if relevant
4. Flag contradictions if the new knowledge conflicts with existing content

### Step 5 — Update Index and Log

1. **Update `wiki/index.md`** — add new pages with one-line summaries
2. **Append to `wiki/log.md`**:

```markdown
## [YYYY-MM-DD] update | <Brief description>
- Context: <which project/skill triggered this update>
- Pages created: [list]
- Pages updated: [list]
- Key knowledge added: [1-2 sentences]
```

3. **Update `wiki/overview.md`** if the new knowledge significantly changes
   the big picture

## Bulk Operations

When syncing a large amount of knowledge (e.g., from a completed tutorial):

1. Plan all pages to create/update before starting
2. Create pages in dependency order (concepts before analyses that reference them)
3. Do a single cross-reference pass at the end
4. Write one comprehensive log entry (not one per page)

## Quality Checks

Before finishing:
- [ ] All new pages have proper frontmatter
- [ ] All `[[wikilinks]]` point to existing pages
- [ ] `wiki/index.md` includes all new pages
- [ ] `wiki/log.md` has been updated
- [ ] No duplicate pages created (checked index first)
- [ ] Contradictions flagged on both sides if any

## Skill Self-Improvement

After completing this update, briefly self-check:

- Was the page template adequate, or did you need to invent structure?
- Was the cross-referencing pass clear, or did you miss connections?
- Did you discover a better categorization or tagging pattern?

If any issue was encountered, append an entry to
`<wiki_dir>/WIKI-SKILL-IMPROVEMENTS.md` (create the file if it doesn't exist):

```markdown
### [Short title]
- **Skill:** wiki-update
- **Date:** YYYY-MM-DD
- **Current behavior:** [What the skill says or doesn't say]
- **Problem:** [What went wrong or was suboptimal]
- **Suggested fix:** [Concrete change to the skill's SKILL.md]
```

When the user runs `/wiki-improve` or asks to "update wiki skills", review
this file and apply generalizable improvements back to the skill files.
