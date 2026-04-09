#!/usr/bin/env python3
"""
extract-tests.py — Copy original project tests into the tutorial's
original-tests/ directory and fix import paths.

Usage:
    python scripts/extract-tests.py <source-project-dir> <tutorial-output-dir> [--language LANG]

Example:
    python scripts/extract-tests.py /path/to/openevolve ./openevolve-from-scratch
    python scripts/extract-tests.py /path/to/myproject ./myproject-from-scratch --language go
"""

import sys
import shutil
import re
from pathlib import Path
import argparse


# Test file patterns by language
TEST_PATTERNS = {
    "python": {
        "dirs": ["tests", "test", "spec", "testing"],
        "globs": ["test_*.py", "*_test.py"],
    },
    "go": {
        "dirs": ["."],  # Go tests live alongside source
        "globs": ["*_test.go"],
    },
    "rust": {
        "dirs": ["tests"],
        "globs": ["*.rs"],
    },
    "javascript": {
        "dirs": ["tests", "test", "__tests__", "spec"],
        "globs": ["*.test.js", "*.spec.js", "*.test.ts", "*.spec.ts"],
    },
    "typescript": {
        "dirs": ["tests", "test", "__tests__", "spec"],
        "globs": ["*.test.ts", "*.spec.ts", "*.test.js", "*.spec.js"],
    },
    "java": {
        "dirs": ["src/test", "test"],
        "globs": ["*Test.java", "*Tests.java"],
    },
}


def find_test_dir(source_dir: Path, language: str) -> Path | None:
    """Find the test directory for the given language."""
    patterns = TEST_PATTERNS.get(language, TEST_PATTERNS["python"])
    for dirname in patterns["dirs"]:
        candidate = source_dir / dirname
        if candidate.exists():
            return candidate
    return None


def extract_tests(source_dir: Path, output_dir: Path, language: str = "python") -> None:
    source_dir = source_dir.resolve()
    patterns = TEST_PATTERNS.get(language, TEST_PATTERNS["python"])

    tests_source = find_test_dir(source_dir, language)
    if tests_source is None:
        print(f"No tests directory found in {source_dir}")
        print(f"Searched: {', '.join(d + '/' for d in patterns['dirs'])}")
        sys.exit(1)

    dest_dir = output_dir / "original-tests"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy all test files matching language patterns
    copied = []
    for glob_pattern in patterns["globs"]:
        for test_file in tests_source.rglob(glob_pattern):
            dest_file = dest_dir / test_file.name
            shutil.copy2(test_file, dest_file)
            copied.append(dest_file)
            print(f"  Copied: {test_file.name}")

    if not copied:
        print(f"WARNING: No test files found matching {patterns['globs']}.")
        return

    # Language-specific setup
    impl_dir = output_dir / "our-implementation"
    impl_dir.mkdir(parents=True, exist_ok=True)

    if language == "python":
        # Create conftest.py for pytest
        conftest = dest_dir / "conftest.py"
        conftest.write_text(f"""\
import sys
from pathlib import Path

# Add our reimplementation to sys.path so tests can import it
sys.path.insert(0, str(Path(__file__).parent.parent / "our-implementation"))

# Also add the original source in case tests import from it directly
# (tests will gradually switch to importing from our-implementation)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
""")
        print(f"  Created: conftest.py")

        # Create empty __init__.py
        init = impl_dir / "__init__.py"
        if not init.exists():
            init.write_text("# Our reimplementation — built incrementally in the notebooks\n")
            print(f"  Created: our-implementation/__init__.py")

    elif language == "go":
        # Create go.mod if needed
        go_mod = impl_dir / "go.mod"
        if not go_mod.exists():
            go_mod.write_text("module our-implementation\n\ngo 1.21\n")
            print(f"  Created: our-implementation/go.mod")

    elif language in ("javascript", "typescript"):
        # Create package.json if needed
        pkg = impl_dir / "package.json"
        if not pkg.exists():
            pkg.write_text('{\n  "name": "our-implementation",\n  "version": "0.0.1",\n  "private": true\n}\n')
            print(f"  Created: our-implementation/package.json")

    print(f"\nExtracted {len(copied)} test file(s) to {dest_dir}")
    print(f"Language: {language}")
    print(f"\nNext steps:")

    run_cmds = {
        "python": "pytest original-tests/ -v",
        "go": "go test ./original-tests/... -v",
        "rust": "cargo test",
        "javascript": "npx jest original-tests/",
        "typescript": "npx jest original-tests/",
        "java": "mvn test",
    }
    cmd = run_cmds.get(language, "pytest original-tests/ -v")
    print(f"  1. Run: {cmd}  (most will fail initially)")
    print("  2. Work through notebooks to implement features")
    print("  3. Tests will turn green as features are implemented")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source_dir", help="Path to the original project")
    parser.add_argument("output_dir", help="Path to the tutorial output directory")
    parser.add_argument("--language", default="python",
                        choices=list(TEST_PATTERNS.keys()),
                        help="Project language (default: python)")
    args = parser.parse_args()

    extract_tests(Path(args.source_dir), Path(args.output_dir), args.language)
