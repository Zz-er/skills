#!/usr/bin/env python3
"""
extract-tests.py — Copy original project tests into the tutorial's
original-tests/ directory and fix import paths.

Usage:
    python scripts/extract-tests.py <source-project-dir> <tutorial-output-dir>

Example:
    python scripts/extract-tests.py /path/to/openevolve ./openevolve-from-scratch
"""

import sys
import shutil
import re
from pathlib import Path


def extract_tests(source_dir: Path, output_dir: Path) -> None:
    source_dir = source_dir.resolve()
    tests_source = source_dir / "tests"

    if not tests_source.exists():
        # Try common alternative locations
        for alt in ["test", "spec", "testing"]:
            candidate = source_dir / alt
            if candidate.exists():
                tests_source = candidate
                break
        else:
            print(f"No tests directory found in {source_dir}")
            print("Searched: tests/, test/, spec/, testing/")
            sys.exit(1)

    dest_dir = output_dir / "original-tests"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy all test files
    copied = []
    for test_file in tests_source.rglob("test_*.py"):
        dest_file = dest_dir / test_file.name
        shutil.copy2(test_file, dest_file)
        copied.append(dest_file)
        print(f"  Copied: {test_file.name}")

    if not copied:
        print("WARNING: No test files (test_*.py) found.")
        return

    # Create a conftest.py that adds our-implementation to sys.path
    impl_dir = output_dir / "our-implementation"
    impl_dir.mkdir(parents=True, exist_ok=True)

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

    # Create empty __init__.py for our-implementation
    init = impl_dir / "__init__.py"
    if not init.exists():
        init.write_text("# Our reimplementation — built incrementally in the notebooks\n")
        print(f"  Created: our-implementation/__init__.py")

    print(f"\nExtracted {len(copied)} test file(s) to {dest_dir}")
    print("\nNext steps:")
    print("  1. Run: pytest original-tests/ -v  (most will fail initially)")
    print("  2. Work through notebooks to implement features")
    print("  3. Tests will turn green as features are implemented")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    extract_tests(Path(sys.argv[1]), Path(sys.argv[2]))
