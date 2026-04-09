#!/usr/bin/env python3
"""
run-tests.py — Run the original test suite against our-implementation/
and report which features are passing.

Usage:
    python scripts/run-tests.py [tutorial-output-dir] [--language LANG] [--feature NAME]

Example:
    python scripts/run-tests.py ./openevolve-from-scratch
    python scripts/run-tests.py ./openevolve-from-scratch --feature database
    python scripts/run-tests.py ./myproject-from-scratch --language go --feature handler
"""

import sys
import subprocess
import argparse
from pathlib import Path


# Test file patterns by language
TEST_FILE_PATTERNS = {
    "python": "test_*.py",
    "go": "*_test.go",
    "rust": "*.rs",
    "javascript": "*.test.{js,ts}",
    "typescript": "*.test.{ts,js}",
    "java": "*Test.java",
}


def build_test_command(language: str, tests_dir: Path, tutorial_dir: Path,
                       feature_filter: str = None) -> list[str]:
    """Build the test command for the given language."""
    if language == "python":
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
        return cmd

    elif language == "go":
        cmd = ["go", "test", "./...", "-v"]
        if feature_filter:
            cmd.extend(["-run", feature_filter])
        return cmd

    elif language == "rust":
        cmd = ["cargo", "test"]
        if feature_filter:
            cmd.append(feature_filter)
        cmd.append("--")
        cmd.append("--nocapture")
        return cmd

    elif language in ("javascript", "typescript"):
        cmd = ["npx", "jest", str(tests_dir), "--verbose"]
        if feature_filter:
            cmd.extend(["-t", feature_filter])
        return cmd

    elif language == "java":
        cmd = ["mvn", "test"]
        if feature_filter:
            cmd.extend([f"-Dtest={feature_filter}"])
        return cmd

    else:
        # Fallback to pytest
        cmd = [sys.executable, "-m", "pytest", str(tests_dir), "-v"]
        if feature_filter:
            cmd.append(f"-k={feature_filter}")
        return cmd


def run_tests(tutorial_dir: Path, language: str = "python",
              feature_filter: str = None) -> int:
    tests_dir = tutorial_dir / "original-tests"

    if not tests_dir.exists():
        print(f"ERROR: original-tests/ not found in {tutorial_dir}")
        print("Run scripts/extract-tests.py first.")
        return 1

    # Find test files
    pattern = TEST_FILE_PATTERNS.get(language, "test_*.py")
    if feature_filter and language == "python":
        pattern = f"test_{feature_filter}*.py"
    elif feature_filter and language == "go":
        pattern = f"*{feature_filter}*_test.go"

    test_files = list(tests_dir.glob(pattern))

    if not test_files:
        print(f"No test files matching: {pattern}")
        available = list(tests_dir.iterdir())
        print(f"Available: {[f.name for f in available if f.is_file()]}")
        return 1

    print(f"Running {len(test_files)} test file(s) [{language}]...\n")

    cmd = build_test_command(language, tests_dir, tutorial_dir, feature_filter)

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
    summary = [l for l in lines if "passed" in l or "failed" in l
               or "error" in l or "PASS" in l or "FAIL" in l or "ok" in l]
    if summary:
        print("\n" + "="*60)
        print("SUMMARY:", summary[-1])
        print("="*60)

    return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "tutorial_dir",
        nargs="?",
        default=".",
        help="Tutorial output directory (default: current directory)",
    )
    parser.add_argument(
        "--language",
        default="python",
        choices=list(TEST_FILE_PATTERNS.keys()),
        help="Project language (default: python)",
    )
    parser.add_argument(
        "--feature",
        help="Only run tests matching this feature name",
    )
    args = parser.parse_args()

    sys.exit(run_tests(Path(args.tutorial_dir), args.language, args.feature))
