#!/usr/bin/env python3
"""
LLM Wiki — Portable Installer (Cross-platform)

Usage:
    python install.py                     # interactive — asks for wiki location
    python install.py /path/to/my/wiki    # non-interactive
    WIKI_DIR=/path python install.py      # via environment variable

What it does:
    1. Creates the wiki directory structure (raw/, wiki/, etc.)
    2. Writes CLAUDE.md schema and seed files (index, log, overview)
    3. Writes wiki path config to ~/.claude/wiki-tools.json
    4. Registers portable/ as a local marketplace and installs wiki-tools plugin
    5. Initializes a git repo in the wiki directory
    6. Installs recommended Claude Code plugins
    7. Optionally patches reimpl-tutorial for Wiki integration
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


def run(cmd, **kwargs):
    """Run a command and return (returncode, stdout)."""
    r = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return r.returncode, r.stdout.strip()


def replace_in_file(src: Path, dst: Path, replacements: dict):
    """Read a template, apply replacements, write to destination."""
    text = src.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def main():
    script_dir = Path(__file__).resolve().parent
    today = date.today().isoformat()

    # ── Determine wiki location ──────────────────────────────
    if len(sys.argv) > 1:
        wiki_dir = sys.argv[1]
    elif os.environ.get("WIKI_DIR"):
        wiki_dir = os.environ["WIKI_DIR"]
    else:
        default = str(Path.home() / "llm_wiki")
        wiki_dir = input(f"Where should the wiki live? (default: {default}): ").strip()
        if not wiki_dir:
            wiki_dir = default

    wiki_path = Path(wiki_dir).expanduser().resolve()
    wiki_dir_str = str(wiki_path)

    print(f"\nInstalling LLM Wiki to: {wiki_dir_str}\n")

    # ── 1. Create directory structure ────────────────────────
    print("[1/6] Creating directory structure...")
    for d in [
        "raw/assets",
        "wiki/sources",
        "wiki/entities",
        "wiki/concepts",
        "wiki/analyses",
    ]:
        (wiki_path / d).mkdir(parents=True, exist_ok=True)

    # ── 2. Write schema and seed files ───────────────────────
    print("[2/6] Writing CLAUDE.md and seed files...")

    tmpl_dir = script_dir / "templates"

    # CLAUDE.md — no date replacement (YYYY-MM-DD are template examples)
    shutil.copy2(tmpl_dir / "CLAUDE.md.tmpl", wiki_path / "CLAUDE.md")

    # Seed wiki files — replace dates with today
    for f in ["index.md", "log.md", "overview.md"]:
        replace_in_file(
            tmpl_dir / "wiki" / f"{f}.tmpl",
            wiki_path / "wiki" / f,
            {"YYYY-MM-DD": today},
        )

    # .gitignore
    shutil.copy2(tmpl_dir / "gitignore.tmpl", wiki_path / ".gitignore")

    # ── 3. Write wiki path config ────────────────────────────
    print("[3/6] Writing wiki path config...")

    claude_dir = Path.home() / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    config_path = claude_dir / "wiki-tools.json"
    config_path.write_text(
        json.dumps({"wiki_dir": wiki_dir_str}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  -> {config_path}")

    # ── 4. Install wiki-tools plugin via marketplace ─────────
    print("[4/6] Installing wiki-tools plugin...")

    claude_cmd = shutil.which("claude")
    marketplace_path = str(script_dir)

    if claude_cmd:
        # Check if marketplace already registered
        rc, out = run([claude_cmd, "plugin", "marketplace", "list"])
        if "llm-wiki" in out:
            # Update existing marketplace
            run([claude_cmd, "plugin", "marketplace", "update", "llm-wiki"])
            print("  -> Marketplace 'llm-wiki' updated")
        else:
            # Register new marketplace from local path
            rc, out = run([
                claude_cmd, "plugin", "marketplace", "add", marketplace_path,
            ])
            if rc == 0:
                print(f"  -> Marketplace 'llm-wiki' registered from: {marketplace_path}")
            else:
                print(f"  -> WARNING: Failed to register marketplace: {out}")
                print(f"    Try manually: claude plugin marketplace add {marketplace_path}")

        # Install the wiki-tools plugin
        rc, out = run([claude_cmd, "plugin", "list"])
        if "wiki-tools" in out:
            # Update existing installation
            rc2, out2 = run([claude_cmd, "plugin", "update", "wiki-tools"])
            if rc2 == 0:
                print("  -> wiki-tools: updated")
            else:
                print("  -> wiki-tools: already installed")
        else:
            rc2, out2 = run([claude_cmd, "plugin", "install", "wiki-tools"])
            if rc2 == 0:
                print("  -> wiki-tools: installed")
            else:
                print(f"  -> WARNING: Failed to install wiki-tools: {out2}")
                _fallback_install(script_dir, wiki_dir_str)
    else:
        print("  -> Claude Code CLI not found, using fallback installation...")
        _fallback_install(script_dir, wiki_dir_str)

    # ── 5. Initialize git repo ───────────────────────────────
    print("[5/6] Initializing git repo...")

    if not (wiki_path / ".git").exists():
        subprocess.run(["git", "init"], cwd=wiki_path, check=True)
        subprocess.run(["git", "add", "-A"], cwd=wiki_path, check=True)
        subprocess.run(
            [
                "git", "commit", "-m",
                "Initial LLM Wiki setup: directory structure, schema, and seed files",
            ],
            cwd=wiki_path,
            check=True,
        )
    else:
        print("  -> Git repo already exists, skipping init")

    # ── 6. Install recommended plugins ───────────────────────
    print("[6/6] Installing recommended Claude Code plugins...")

    plugins = [
        "commit-commands", "context7", "hookify",
        "explanatory-output-style", "playground",
    ]

    if claude_cmd:
        rc, installed = run([claude_cmd, "plugin", "list"])
        for p in plugins:
            if p in installed:
                print(f"  -> {p}: already installed")
            else:
                rc, _ = run([claude_cmd, "plugin", "install", p])
                print(f"  -> {p}: {'installed' if rc == 0 else 'failed (install manually)'}")
    else:
        print("  -> Claude Code CLI not found. Install plugins manually:")
        print(f"    claude plugin install {' '.join(plugins)}")

    # ── Optional: patch reimpl-tutorial ───────────────────────
    reimpl_found = _find_reimpl_tutorial(wiki_path)

    if reimpl_found and "wiki-query" not in reimpl_found.read_text(encoding="utf-8"):
        print(f"\n[Optional] Found reimpl-tutorial skill at: {reimpl_found}")
        confirm = input("Patch it for Wiki integration? (Y/n): ").strip()
        if confirm.lower() != "n":
            patch_script = script_dir / "patch_reimpl_tutorial.py"
            subprocess.run(
                [sys.executable, str(patch_script), str(reimpl_found.parent.parent)],
                check=False,
            )

    # ── Done ──────────────────────────────────────────────────
    print(f"""
{'=' * 50}
  LLM Wiki installed successfully!

  Wiki location:  {wiki_dir_str}
  Wiki config:    {config_path}

  Next steps:
    1. Run: claude -p {wiki_dir_str}
    2. Drop a document into {wiki_dir_str}{os.sep}raw{os.sep}
    3. Tell Claude: "ingest the new source"

  Global skills (available in any project):
    /wiki-query   - search the knowledge base
    /wiki-update  - add knowledge to the wiki
    /wiki-ingest  - import a tutorial project

  Run /reload-plugins in Claude Code to activate.
{'=' * 50}""")


def _fallback_install(script_dir: Path, wiki_dir_str: str):
    """Fallback: copy plugin directly to local-plugins/ if CLI is unavailable."""
    plugin_dir = Path.home() / ".claude" / "local-plugins" / "wiki-tools"
    src_plugin = script_dir / "plugins" / "wiki-tools"

    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
    shutil.copytree(src_plugin, plugin_dir)

    print(f"  -> Fallback: copied to {plugin_dir}")


def _find_reimpl_tutorial(wiki_path: Path):
    """Search common locations for reimpl-tutorial SKILL.md."""
    home = Path.home()
    candidates = [
        wiki_path.parent / ".claude" / "skills" / "reimpl-tutorial" / "SKILL.md",
        home / ".claude" / "skills" / "reimpl-tutorial" / "SKILL.md",
        home / ".claude" / "local-plugins" / "reimpl-tutorial" / "skills" / "reimpl-tutorial" / "SKILL.md",
    ]
    for c in candidates:
        if c.exists():
            return c

    # Search upward from cwd
    d = Path.cwd()
    while d != d.parent:
        candidate = d / ".claude" / "skills" / "reimpl-tutorial" / "SKILL.md"
        if candidate.exists():
            return candidate
        d = d.parent

    return None


if __name__ == "__main__":
    main()
