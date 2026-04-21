# bug-analyze-plugin

A Claude Code plugin that provides a methodology-first approach to analyzing bug reports in multi-layer codebases (front-end + IPC + back-end).

## Skills included

| Skill | Description |
|-------|-------------|
| **bug-analyze** | Take a UI-level phenomenon bug report and produce a 4-part analysis: symptom, code-cited reasoning across all relevant layers, discriminating follow-up questions, and 2–3 solution candidates with tradeoffs. |

## The problem it solves

Testers report bugs as UI-level symptoms ("button doesn't respond", "model in wrong place", "save doesn't stick"). The defect itself lives one or more layers deeper — in a FE slot, an IPC payload, a backend persistence attribute, or the interaction between them.

Naive analysis that only looks at one layer routinely misses the bug. This skill encodes a **multi-layer tracing discipline** plus a **structured output format** that makes each analysis reviewable and actionable.

## Output structure (for every bug)

1. **现象** — one-sentence restatement of the tester's UI-level description
2. **代码侧分析** — depth is the value:
   - Which layer(s) likely own the bug (trace the user action through the system)
   - Specific `file:line` + function names
   - At least 2 cross-reference pieces of evidence
   - Contradictions with nearby conventions (past fixes, sibling code that does it right) — these are evidence
3. **缺的信息** — discriminating questions where each possible answer maps to a specific hypothesis / code path. Not "please give me repro steps".
4. **解决方案** — 2–3 candidates with tradeoffs:
   - Minimal patch (low intrusion, often symptomatic)
   - Root fix (bigger change, systemic)
   - Workaround (UI message / flag, zero code risk but limited)

## Installation

### Via Claude Code plugin marketplace

```bash
claude plugin marketplace add https://github.com/Zz-er/skills
claude plugin install bug-analyze
```

### Manual installation

```bash
git clone https://github.com/Zz-er/skills.git ~/.claude/local-plugins/_skills_repo
ln -s ~/.claude/local-plugins/_skills_repo/bug-analyze-plugin \
      ~/.claude/local-plugins/bug-analyze
```

## Pairing with a tracker skill

`bug-analyze` itself does not talk to any bug tracker. To fetch bug data and post analyses back, pair it with a tracker-specific skill. Current examples:

- **`zentao-plugin`** (same repo) — fetches bug details via legacy session-cookie `.json` API; posts analyses via `comment-bug <id> --file <draft> --yes`

The `bug-analyze` skill's workflow delegates all tracker I/O to the tracker skill; this keeps the methodology generic so the same skill can drive Jira / Linear / GitHub Issues once the tracker side has a skill.

## Usage

The skill triggers on phrases like:

- "分析这个 bug"
- "定位 bug #35924"
- "深入分析"
- "这个 bug 怎么回事"
- "帮我看看这个禅道 bug"

Or invoke directly: `/bug-analyze`

When invoked, the skill:

1. If a bug id is given, uses the tracker skill (e.g., `zentao:zentao`) to fetch title / reporter / steps / existing comments.
2. Maps the phenomenon to likely project layers based on the current project's `CLAUDE.md` architecture notes.
3. Runs targeted greps or subagents (one per code region) to gather evidence.
4. Drafts the 4-part analysis (≤ 1500 chars so it fits in a single ZenTao comment).
5. **Presents the draft for human approval** (never auto-posts — team visibility is high-stakes).
6. If approved, posts via the tracker skill.

## Anti-patterns this skill refuses

- Analyzing only one layer when the bug is a UI phenomenon
- Generic "please give me repro steps" asks
- Single-solution presentation
- Assuming architecture without reading the project's CLAUDE.md
- Posting without human review

See `skills/bug-analyze/SKILL.md` for full details.

## Plugin structure

```
bug-analyze-plugin/
├── .claude-plugin/plugin.json
├── README.md
└── skills/
    └── bug-analyze/
        └── SKILL.md
```

## License

MIT
