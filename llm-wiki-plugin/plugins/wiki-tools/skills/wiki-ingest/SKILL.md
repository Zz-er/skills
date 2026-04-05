---
name: wiki-ingest
description: >
  Ingest a completed reimpl-tutorial project into the LLM Wiki knowledge base.
  Use this skill when the user wants to sync tutorial knowledge into the wiki,
  or after a reimpl-tutorial project is complete. Trigger on phrases like
  "sync to wiki", "ingest tutorial", "把教程同步到wiki", "导入知识库",
  "wiki-ingest", "reimpl-ingest", or any request to import a completed
  tutorial project into the LLM Wiki system.
---

# Reimpl-Tutorial → Wiki Ingest

You are importing a completed reimpl-tutorial project into the LLM Wiki
knowledge base. This converts transient tutorial knowledge into permanent,
cross-referenced, searchable wiki entries.

## Wiki Location

Read `~/.claude/wiki-tools.json` to get the wiki directory path:

```json
{ "wiki_dir": "/path/to/your/wiki" }
```

All paths below are relative to this `wiki_dir`.

## Input

The user provides a path to a completed `<project>-from-scratch/` directory.
If no path is given, search for recent tutorial output directories under the
current workspace.

## Prerequisites

- `~/.claude/wiki-tools.json` must exist (created by install.py)
- The tutorial project must have completed at least through Phase 4
  (SUMMARY.md and notebooks/ must exist)

## Process

### Step 1 — Gather Tutorial Content

Read the following files from the tutorial project:

1. `SUMMARY.md` — full notebook listing
2. `README.md` — project overview and setup
3. `references/papers.md` — cited papers (if exists)
4. `SKILL-IMPROVEMENTS.md` — lessons learned (if exists)
5. Scan all `notebooks/*.ipynb` — extract markdown cells to identify:
   - Core concepts taught (algorithms, patterns, data structures)
   - Entities mentioned (people, projects, tools, frameworks)
   - Design decisions and their rationale
   - Mathematical derivations and formulas
   - Key diagrams and architecture descriptions

### Step 2 — Copy Source to Wiki Raw

Copy `SUMMARY.md` into the Wiki's raw directory:

```bash
cp <project>-from-scratch/SUMMARY.md <wiki_dir>/raw/reimpl-<project-name>-summary.md
```

### Step 3 — Create Source Summary Page

Create `wiki/sources/reimpl-<project-name>.md` following the source template:

```yaml
---
title: "手撕 <Project Name>"
type: source
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [reimpl-tutorial, <domain-tags>]
sources: [reimpl-<project-name>-summary]
---
```

Include:
- Project overview and motivation
- List of all notebooks with one-line descriptions
- Running example description
- Key takeaways (3-5 bullet points)
- Link to the tutorial directory

### Step 4 — Create/Update Concept Pages

For each core concept identified in Step 1:

1. Check `wiki/index.md` — does a page already exist for this concept?
2. If **yes**: update the existing page
   - Add a new entry under "Evidence & Sources" citing this tutorial
   - Update the description if the tutorial provides deeper insight
   - Add new `[[wikilinks]]` to related concepts from the same tutorial
3. If **no**: create a new page in `wiki/concepts/`
   - Use the Wiki's concept template
   - Include: explanation from the tutorial, formula (if any), source mapping
   - Tag with `reimpl-tutorial` and domain-specific tags

**Typical concepts to extract:**
- Algorithms (e.g., MAP-Elites, beam search, gradient descent)
- Design patterns (e.g., observer, strategy, event loop)
- Mathematical foundations (e.g., KL divergence, softmax, backpropagation)
- Architectural patterns (e.g., controller-evaluator, pipeline, DAG scheduler)

### Step 5 — Create/Update Entity Pages

For each entity identified in Step 1:

1. **The project itself** — create an entity page for the original project
   (not the tutorial), describing what it does, who built it, its significance
2. **Key people** — authors, contributors mentioned in papers or README
3. **Tools/frameworks** — important dependencies that others might also study
4. **Papers** — each cited paper gets an entity page (or update if exists)

### Step 6 — Create Analysis Page

Create `wiki/analyses/reimpl-<project-name>-insights.md`:

```yaml
---
title: "手撕 <Project Name> — 设计洞察"
type: analysis
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [reimpl-tutorial, design-analysis, <domain-tags>]
sources: [reimpl-<project-name>]
---
```

Include:
- **Architecture decisions** — why the project is designed the way it is
- **Interesting trade-offs** — what was sacrificed for what
- **Patterns worth reusing** — transferable ideas for other projects
- **Lessons learned** — from SKILL-IMPROVEMENTS.md if available
- **Comparison** — how does this project compare to similar ones in the wiki?

### Step 7 — Update Index and Log

1. **Update `wiki/index.md`** — add all new pages under appropriate categories
2. **Append to `wiki/log.md`**:

```markdown
## [YYYY-MM-DD] reimpl-ingest | <Project Name>
- Tutorial: `<path>/<project>-from-scratch/`
- Notebooks: [count]
- Pages created: [list with links]
- Pages updated: [list with links]
- Key concepts: [list]
- Key entities: [list]
```

3. **Update `wiki/overview.md`** — refresh the high-level synthesis if this
   tutorial adds a significant new domain or changes the knowledge landscape

### Step 8 — Cross-Reference Pass

Do a final pass across all wiki pages:

1. Search for mentions of concepts/entities from this tutorial in existing pages
2. Add `[[wikilinks]]` wherever relevant connections are missing
3. Flag any contradictions between this tutorial's findings and existing content
4. Check if any existing orphan pages are now connected through the new content

## Output

After completion, report to the user:
- Number of pages created and updated
- List of new concepts added to the knowledge graph
- Any contradictions found
- Suggestions for further exploration (e.g., "the wiki now has 3 sources about
  attention mechanisms — consider creating a comparison analysis")

## Quality Checks

- [ ] Source summary page accurately reflects the tutorial
- [ ] Every core concept has a dedicated wiki page
- [ ] All new pages have proper frontmatter and `[[wikilinks]]`
- [ ] `wiki/index.md` is complete and accurate
- [ ] `wiki/log.md` has been updated
- [ ] No broken `[[wikilinks]]` introduced
- [ ] Contradictions (if any) are flagged on both sides
