# Deep Analysis Prompt
#
# Follow this prompt during Phase 1 of the tutorial generation process.
# Work through each section methodically. Take notes in a scratch document
# before writing any notebooks.

## Your Goal

Understand the target project well enough that you could reimplement it from
scratch without referring to the original code — and verify that reimplementation
by passing the original tests.

## Step 1: Entry Points

Find and read every entry point. Common patterns by language:

| Language | Entry points |
|----------|-------------|
| Python | `main.py`, `run.py`, `__main__.py`, `setup.cfg` / `pyproject.toml` entry_points, `api.py`, `__init__.py` exports |
| Go | `main.go`, `cmd/*/main.go` |
| Rust | `main.rs`, `lib.rs`, `bin/*.rs` |
| JavaScript / TypeScript | `index.js/ts`, `src/index.*`, `package.json` main/bin fields |
| Java / Kotlin | `*Application.java`, `public static void main`, `pom.xml` / `build.gradle` |

For each entry point, trace what happens when it's called:
- What arguments does it accept?
- What does it set up?
- What is the main loop / primary call chain?

## Step 1b: Language & Toolchain Detection

Identify and record:
- **Primary language** (by file count and lines of code)
- **Package manager / build system** (pip/poetry, cargo, go mod, npm/yarn, maven/gradle, etc.)
- **Test framework** and test file naming convention (pytest `test_*.py`, Go `*_test.go`, Rust `#[test]`, Jest `*.test.js`, JUnit `*Test.java`, etc.)
- **Whether a Jupyter kernel exists** for this language (Python: always; R: IRkernel; Julia: IJulia; Go/Rust/JS: community kernels exist but may not be installed)

Store this information — it feeds into Phase 1.6 Tutorial Configuration.

## Step 2: Core Data Structures

Identify the project's primary data structures:
- What are the main classes/dataclasses/TypedDicts?
- What data do they hold?
- What is their lifecycle (created where, mutated where, destroyed where)?
- Which data structures are passed between components?

## Step 3: Component Mapping

For each major module/class, document:
- **Purpose**: One sentence describing what it does
- **Inputs**: What data it receives
- **Outputs**: What data it produces or mutates
- **Dependencies**: What other components it calls
- **Key methods**: The 3-5 methods that matter most

Build a mental dependency graph: A → B means "A calls B or depends on B".

## Step 4: Algorithm Deep-Dives

For each non-trivial algorithm:
- What problem does it solve?
- What is the time/space complexity?
- Is there a paper or reference for this algorithm? Search for comments,
  docstrings, or README mentions of papers.
- What are the key parameters and what do they control?
- What are the edge cases and how are they handled?

## Step 5: Decision Archaeology

For each significant design decision you observe, ask:
- Why was this approach chosen? (Look for TODO/FIXME/NOTE comments,
  commit messages, issue references)
- What are the tradeoffs? (Speed vs. memory? Simplicity vs. flexibility?)
- What would break if this design were different?

Common decisions to look for:
- Parallelism approach (threads vs. processes vs. async)
- Caching strategy
- Error handling policy (raise vs. return None vs. retry)
- Configuration format (YAML vs. env vars vs. code)
- Storage format (DB vs. files vs. in-memory)

## Step 6: Test Inventory

Examine every test file:
- What does each test file cover? (group by feature)
- Which tests are unit tests vs. integration tests?
- What fixtures and mocks exist? What do they tell you about the real dependencies?
- Which tests are most valuable as a correctness oracle for our reimplementation?

Create a mapping: feature → test file(s) → specific test functions.

## Step 7: Feature List

Produce a complete feature list. For each feature:
```
Feature: [name]
Purpose: [one sentence]
Depends on: [other features]
Required by: [features that need this one]
Tests: [test file::test_function]
Complexity: [low/medium/high]
Has math/theory: [yes/no]
```

## Step 8: Running Example Selection

From the feature list, identify the best "running example" — a concrete use
case that:
- Exercises the core algorithm (not just peripheral features)
- Can be demonstrated in a few lines of code
- Has output that's easy to visualize
- Will grow naturally as more features are added
- **Can naturally extend at every cognitive level** — the example must work at
  Level 0 (basic), Level 1 (core), Level 2 (enhanced), and Level 3 (advanced)
  without feeling forced

This example should appear in **almost every notebook**, growing in
sophistication. A good test: for each planned notebook, write one sentence
describing how the running example appears in that notebook. If any notebook
feels awkward with the example, consider a different one.

**Example of a great running example:**
Sorting algorithms for an evolutionary coding system:
- Chapter 01: Bubble sort (simplest, easy to understand)
- Chapter 02: Multiple sorting strategies coexist (demonstrates diversity)
- Chapter 03: Different islands evolve different sorting methods independently
- Chapter 04: LLM suggests algorithmic improvements to sorting code
- Chapter 05: Quick validation catches broken sorts before full testing
- Chapter 06: Targeted diffs modify specific sort logic, not the whole program
- Chapter 07: Multiple sorting programs evaluated in parallel
- Chapter 08: Save/resume the sorting evolution state
- Chapter 09: Full pipeline evolves the best possible sorting algorithm

**Selection criteria (all must be satisfied):**
1. Simple enough to explain in 5 minutes to a beginner
2. Complex enough to benefit from every feature in the system
3. Has measurable output (scores, timings, correctness checks)
4. Fits the project's domain naturally (not contrived)

## Output

Produce a structured analysis document containing:
1. Dependency graph (text or mermaid)
2. Component map (component → purpose, inputs, outputs, key methods)
3. Algorithm summaries (name, paper, key params)
4. Design decisions (decision, rationale, tradeoff)
5. Feature list with dependencies and tests
6. Chosen running example with justification
7. Proposed cognitive ordering of notebooks
