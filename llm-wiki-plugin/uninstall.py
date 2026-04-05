#!/usr/bin/env python3
"""
LLM Wiki — Uninstaller (Cross-platform)

Removes the wiki-tools plugin and marketplace registration.
Does NOT delete the wiki data unless --all is used.

Usage:
    python uninstall.py                        # removes plugin + marketplace only
    python uninstall.py --all /path/to/wiki    # removes everything
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def main():
    claude_cmd = shutil.which("claude")

    # ── Remove plugin via CLI ─────────────────────────────────
    print("Removing wiki-tools plugin...")
    if claude_cmd:
        rc, _ = run([claude_cmd, "plugin", "uninstall", "wiki-tools"])
        if rc == 0:
            print("  -> Uninstalled via Claude CLI")
        else:
            print("  -> Not installed via CLI (or already removed)")

        # Remove marketplace registration
        rc, out = run([claude_cmd, "plugin", "marketplace", "list"])
        if "llm-wiki" in out:
            run([claude_cmd, "plugin", "marketplace", "remove", "llm-wiki"])
            print("  -> Marketplace 'llm-wiki' removed")

    # ── Remove fallback local-plugins copy ────────────────────
    fallback_dir = Path.home() / ".claude" / "local-plugins" / "wiki-tools"
    if fallback_dir.exists():
        shutil.rmtree(fallback_dir)
        print(f"  -> Removed: {fallback_dir}")

    # ── Remove config file ────────────────────────────────────
    config_path = Path.home() / ".claude" / "wiki-tools.json"
    if config_path.exists():
        config_path.unlink()
        print(f"  -> Removed: {config_path}")

    # ── Optionally remove wiki data ───────────────────────────
    if len(sys.argv) >= 3 and sys.argv[1] == "--all":
        wiki_path = Path(sys.argv[2]).expanduser().resolve()
        confirm = input(
            f"\nThis will permanently delete: {wiki_path}\nAre you sure? (y/N): "
        ).strip()
        if confirm.lower() == "y":
            shutil.rmtree(wiki_path)
            print(f"  -> Removed: {wiki_path}")
        else:
            print("  -> Skipped")

    print("\nDone. Run /reload-plugins in Claude Code.")


if __name__ == "__main__":
    main()
