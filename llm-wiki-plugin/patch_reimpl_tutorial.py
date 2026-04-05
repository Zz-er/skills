#!/usr/bin/env python3
"""
LLM Wiki — reimpl-tutorial Integration Patch (Cross-platform)

Adds Wiki integration to an existing reimpl-tutorial skill:
  - Phase 1 Step 0: query wiki for existing knowledge before analysis
  - Phase 6: sync tutorial knowledge back to wiki after completion
  - Quality checklist: wiki sync check item

Usage:
    python patch_reimpl_tutorial.py                            # auto-detect
    python patch_reimpl_tutorial.py /path/to/.claude/skills    # explicit

Safe to run multiple times — skips if already patched.
"""

import re
import sys
from pathlib import Path

PHASE1_PATCH = '''0. **Query the Wiki** — Use `/wiki-query` to check what the Wiki already knows
   about this project's domain. Look for existing concept pages (algorithms,
   patterns), entity pages (tools, frameworks, authors), and related analyses.
   This avoids re-deriving knowledge that's already been synthesized from
   previous tutorials or sources. Note which wiki pages are relevant — you'll
   link back to them later.
'''

PHASE6_PATCH = '''### Phase 6 — Wiki Knowledge Sync

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

---

'''

CHECKLIST_PATCH = (
    "- [ ] Tutorial knowledge has been synced to the LLM Wiki (Phase 6)"
    " — or user declined"
)


def find_skill_file(explicit_path=None):
    """Locate reimpl-tutorial/SKILL.md."""
    if explicit_path:
        p = Path(explicit_path) / "reimpl-tutorial" / "SKILL.md"
        if p.exists():
            return p
        # Maybe they passed the skills dir directly
        p2 = Path(explicit_path) / "SKILL.md"
        if p2.exists():
            return p2

    home = Path.home()
    candidates = [
        Path.cwd() / ".claude" / "skills" / "reimpl-tutorial" / "SKILL.md",
        Path.cwd().parent / ".claude" / "skills" / "reimpl-tutorial" / "SKILL.md",
        home / ".claude" / "skills" / "reimpl-tutorial" / "SKILL.md",
        home / ".claude" / "local-plugins" / "reimpl-tutorial" / "skills" / "reimpl-tutorial" / "SKILL.md",
    ]
    for c in candidates:
        if c.exists():
            return c

    # Walk upward
    d = Path.cwd()
    while d != d.parent:
        c = d / ".claude" / "skills" / "reimpl-tutorial" / "SKILL.md"
        if c.exists():
            return c
        d = d.parent

    return None


def main():
    explicit = sys.argv[1] if len(sys.argv) > 1 else None
    skill_file = find_skill_file(explicit)

    if not skill_file:
        print("ERROR: Could not find reimpl-tutorial/SKILL.md")
        print()
        print("Usage: python patch_reimpl_tutorial.py /path/to/.claude/skills")
        print()
        print("Searched:")
        print("  - .claude/skills/reimpl-tutorial/SKILL.md (relative)")
        print("  - ~/.claude/skills/reimpl-tutorial/SKILL.md")
        print("  - parent directories upward")
        sys.exit(1)

    print(f"Found: {skill_file}")
    print()

    content = skill_file.read_text(encoding="utf-8")

    # Check if already patched
    if "wiki-query" in content:
        print("Already patched (found /wiki-query reference). Nothing to do.")
        return

    modified = False

    # ── Patch 1: Phase 1 Step 0 ──────────────────────────────
    print("[1/3] Adding Phase 1 Step 0 (wiki query before analysis)...")
    marker = "1. **Read every source file."
    if marker in content:
        content = content.replace(marker, PHASE1_PATCH + marker)
        print("  -> Inserted Step 0 in Phase 1")
        modified = True
    else:
        print("  -> WARNING: Could not find Phase 1 insertion point. Add manually.")

    # ── Patch 2: Phase 6 ─────────────────────────────────────
    print("[2/3] Adding Phase 6 (wiki knowledge sync)...")
    marker2 = "## Output Directory Structure"
    if marker2 in content:
        content = content.replace(marker2, PHASE6_PATCH + marker2)
        print("  -> Inserted Phase 6 before Output Directory Structure")
        modified = True
    else:
        print("  -> WARNING: Could not find insertion point. Add Phase 6 manually.")

    # ── Patch 3: Quality checklist ────────────────────────────
    print("[3/3] Adding wiki sync to quality checklist...")
    checklist_marker = "have been applied back to the skill files"
    if checklist_marker in content:
        # Find the full line and append after it
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if checklist_marker in line:
                new_lines.append(CHECKLIST_PATCH)
        content = "\n".join(new_lines)
        print("  -> Added checklist item")
        modified = True
    else:
        print("  -> WARNING: Could not find checklist insertion point. Add manually.")

    if modified:
        skill_file.write_text(content, encoding="utf-8")

    print(f"""
{'=' * 50}
  reimpl-tutorial patched for Wiki integration!

  Modified: {skill_file}

  Changes:
    Phase 1 Step 0 - /wiki-query before analysis
    Phase 6        - /wiki-ingest after completion
    Checklist      - wiki sync verification
{'=' * 50}""")


if __name__ == "__main__":
    main()
