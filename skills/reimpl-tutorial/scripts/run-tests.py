#!/usr/bin/env python3
"""
run-tests.py — Run the original test suite against our-implementation/
and report which features are passing.

Usage:
    python scripts/run-tests.py [tutorial-output-dir]
    python scripts/run-tests.py [tutorial-output-dir] --feature <feature-name>

Example:
    python scripts/run-tests.py ./openevolve-from-scratch
    python scripts/run-tests.py ./openevolve-from-scratch --feature database
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(tutorial_dir: Path, feature_filter: str = None) -> int:
    tests_dir = tutorial_dir / "original-tests"

    if not tests_dir.exists():
        print(f"ERROR: original-tests/ not found in {tutorial_dir}")
        print("Run scripts/extract-tests.py first.")
        return 1

    # Find test files
    if feature_filter:
        pattern = f"test_{feature_filter}*.py"
        test_files = list(tests_dir.glob(pattern))
        if not test_files:
            print(f"No test files matching: {pattern}")
            print(f"Available: {[f.name for f in tests_dir.glob('test_*.py')]}")
            return 1
    else:
        test_files = list(tests_dir.glob("test_*.py"))

    if not test_files:
        print("No test files found.")
        return 1

    print(f"Running {len(test_files)} test file(s)...\n")

    # Run pytest
    cmd = [
        sys.executable, "-m", "pytest",
        str(tests_dir),
        "-v",
        "--tb=short",
        "--no-header",
        "-q",
    ]

    if feature_filter:
        cmd.append(f"-k={feature_filter}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=tutorial_dir,
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[-1000:])

    # Parse results
    lines = result.stdout.splitlines()
    summary = [l for l in lines if "passed" in l or "failed" in l or "error" in l]
    if summary:
        print("\n" + "="*60)
        print("SUMMARY:", summary[-1])
        print("="*60)

    return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tutorial_dir",
        nargs="?",
        default=".",
        help="Tutorial output directory (default: current directory)",
    )
    parser.add_argument(
        "--feature",
        help="Only run tests matching this feature name",
    )
    args = parser.parse_args()

    sys.exit(run_tests(Path(args.tutorial_dir), args.feature))
