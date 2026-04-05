---
name: wiki-improve
description: >
  Review and apply accumulated skill improvement suggestions. Use this skill
  when the user says "update wiki skills", "improve wiki skills", "优化wiki技能",
  "/wiki-improve", or periodically after several wiki operations have been
  performed. This skill reads WIKI-SKILL-IMPROVEMENTS.md from the wiki
  directory, filters out project-specific issues, and applies generalizable
  improvements back to the wiki skill files (SKILL.md).
---

# Wiki Improve — Skill Self-Iteration

Review accumulated improvement suggestions from `WIKI-SKILL-IMPROVEMENTS.md`
and apply them back to the wiki skill files, making the skills better with
every use.

## Wiki Location

Read `~/.claude/wiki-tools.json` to get the wiki directory path.

## Process

### Step 1 — Read Improvement Suggestions

Read `<wiki_dir>/WIKI-SKILL-IMPROVEMENTS.md`. If the file doesn't exist or is
empty, tell the user "No improvement suggestions accumulated yet" and stop.

### Step 2 — Classify Each Suggestion

For each entry, determine:

1. **Generalizable** — would this improvement help future wiki operations
   across any project? (e.g., "the query skill should search by tags, not
   just filenames")
2. **Project-specific** — only relevant to this particular wiki's content or
   structure? (e.g., "my wiki has too many concept pages about sorting")
3. **Already addressed** — the skill file has already been updated to handle
   this case?

### Step 3 — Present to the User

Show the user a summary:

```
Found N improvement suggestions:
  - N generalizable (will apply to skill files)
  - N project-specific (will skip)
  - N already addressed (will skip)

Generalizable improvements to apply:
  1. [wiki-query] <title> — <one-line summary>
  2. [wiki-update] <title> — <one-line summary>
  ...
```

Ask the user to confirm before applying.

### Step 4 — Apply Improvements

For each accepted generalizable suggestion:

1. **Locate the target skill file** — find the SKILL.md for the skill named
   in the suggestion. The skill files are siblings of this skill:
   `<this-skill-dir>/../<skill-name>/SKILL.md`
2. **Apply the change** — use the Edit tool for targeted modifications. Never
   rewrite entire files. Common change types:
   - Add a step to the process
   - Clarify an ambiguous instruction
   - Add a new tip or quality check item
   - Fix an incorrect or outdated instruction
   - Add a new pattern or template
3. **Verify** — read back the modified section to confirm the edit is correct

### Step 5 — Update the Improvements File

After applying, update `<wiki_dir>/WIKI-SKILL-IMPROVEMENTS.md`:

1. Add a `## Changelog` section at the bottom (or append to existing one)
2. For each suggestion, record whether it was accepted or rejected with reason:

```markdown
## Changelog

### YYYY-MM-DD — Batch review
- **[wiki-query] <title>**: ✅ Applied — added tag-based search step
- **[wiki-update] <title>**: ✅ Applied — clarified frontmatter rules
- **[wiki-ingest] <title>**: ❌ Rejected — project-specific, doesn't generalize
- **[wiki-query] <title>**: ⏭️ Already addressed in previous iteration
```

3. Move processed suggestions from the main body to an `## Archive` section
   so they don't get re-processed.

### Step 6 — Log

Append to `<wiki_dir>/wiki/log.md`:

```markdown
## [YYYY-MM-DD] skill-improve | Wiki skill self-iteration
- Suggestions reviewed: [count]
- Applied: [count] — [list of changes]
- Rejected: [count]
- Skills modified: [list of skill names]
```

### Step 7 — Sync to Remote *(optional)*

If the wiki skill files live in a git repo (check if the plugin directory has
a `.git` directory or is a symlink to a git-tracked directory), ask the user
whether to commit and push the changes.

## When to Trigger

This skill should be suggested (not forced) when:

- `WIKI-SKILL-IMPROVEMENTS.md` has 5+ unprocessed entries
- The user explicitly asks to improve or update the wiki skills
- A significant wiki milestone is reached (e.g., 10th ingest, 50th query)

The other wiki skills (query, update, ingest) each write to
`WIKI-SKILL-IMPROVEMENTS.md` when they encounter issues. This skill
is the counterpart that processes those suggestions.

## Quality Checks

- [ ] Only generalizable improvements were applied to skill files
- [ ] Each applied change is a targeted edit, not a full rewrite
- [ ] The improvements file has a changelog recording what was done
- [ ] Modified skill files still have valid YAML frontmatter
- [ ] `wiki/log.md` records this iteration
