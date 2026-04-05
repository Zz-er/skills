---
name: wiki-query
description: >
  Query the LLM Wiki knowledge base from any project. Use this skill when the
  user or another skill needs to look up existing knowledge — concepts, entities,
  analyses, or sources — from the personal wiki. Trigger on phrases like
  "check the wiki", "wiki里有什么", "查查知识库", "what does the wiki say about",
  "wiki-query", or when you need background knowledge before starting a task.
  Also use proactively during reimpl-tutorial Phase 1 to check for existing
  concept pages that could inform the analysis.
---

# Wiki Query — Global Knowledge Lookup

You are querying the LLM Wiki knowledge base to retrieve existing knowledge.
The Wiki is a persistent, cross-referenced collection of markdown pages built
up over time from ingested sources, tutorials, and analyses.

## Wiki Location

Read `~/.claude/wiki-tools.json` to get the wiki directory path:

```json
{ "wiki_dir": "/path/to/your/wiki" }
```

All paths below are relative to this `wiki_dir`.

## Process

### Step 1 — Understand the Query

Determine what the user (or calling skill) is looking for:
- A specific concept (algorithm, pattern, theory)?
- An entity (person, project, tool, paper)?
- A source summary?
- A broad topic scan (what do we know about X)?

### Step 2 — Read the Index

Read `<wiki_dir>/wiki/index.md` to find relevant pages.
This is the master catalog — every wiki page is listed here with a one-line
summary.

### Step 3 — Read Relevant Pages

Based on the index, read the most relevant wiki pages. Typical lookup paths:

- **Concept lookup**: `wiki/concepts/<concept-name>.md`
- **Entity lookup**: `wiki/entities/<entity-name>.md`
- **Source lookup**: `wiki/sources/<source-name>.md`
- **Analysis lookup**: `wiki/analyses/<analysis-name>.md`
- **Broad scan**: read `wiki/overview.md` for the big picture

If the exact page isn't obvious from the index, use Grep to search across
all wiki pages:

```bash
grep -rl "<search-term>" <wiki_dir>/wiki/
```

### Step 4 — Synthesize and Return

Return the findings to the user or calling context:

1. **Direct answer** — synthesize what the wiki knows, with citations to
   specific wiki pages using `[[wikilinks]]`
2. **Gap identification** — if the wiki doesn't have what's needed, say so
   explicitly. Suggest whether a new source should be ingested or a new
   analysis page created.
3. **Cross-references** — mention related pages that might be useful even
   if not directly asked about.

### Step 5 — Log the Query

Append to `<wiki_dir>/wiki/log.md`:

```markdown
## [YYYY-MM-DD] query | <Brief question summary>
- Pages consulted: [list]
- Context: <which project/skill triggered this query>
- Result: <found/partial/not-found>
```

## Usage from Other Skills

When called from within another skill (e.g., reimpl-tutorial Phase 1):

1. Accept a query string or list of topics to look up
2. Return structured results:
   - `found_concepts`: list of relevant concept pages with key points
   - `found_entities`: list of relevant entity pages
   - `gaps`: topics not covered in the wiki
   - `contradictions`: any conflicting information found
3. The calling skill decides how to use the results

## Tips

- The wiki uses `[[wikilinks]]` for cross-references — follow them to find
  connected knowledge
- Check `wiki/log.md` to see recent activity if context helps
- If a query returns nothing useful, that's valuable information too — it
  identifies a knowledge gap
- Prefer reading wiki pages over raw sources. The wiki should already have
  the synthesized knowledge you need.

## Skill Self-Improvement

After completing this query, briefly self-check:

- Did the index lead you to the right pages efficiently, or did you need extra
  grep/search steps? If the index was missing useful entries, note it.
- Was the query workflow smooth, or did you hit an ambiguous/missing instruction?
- Did you discover a better search pattern worth standardizing?

If any issue was encountered, append an entry to
`<wiki_dir>/WIKI-SKILL-IMPROVEMENTS.md` (create the file if it doesn't exist):

```markdown
### [Short title]
- **Skill:** wiki-query
- **Date:** YYYY-MM-DD
- **Current behavior:** [What the skill says or doesn't say]
- **Problem:** [What went wrong or was suboptimal]
- **Suggested fix:** [Concrete change to the skill's SKILL.md]
```

When the user runs `/wiki-improve` or asks to "update wiki skills", review
this file and apply generalizable improvements back to the skill files. See
the `wiki-improve` section in the plugin documentation for details.
