# Feature Extraction Prompt
#
# Use this after completing Phase 1 analysis, before writing any notebooks.
# The goal is to produce a final ordered feature list that becomes your
# notebook outline.

## Input

You have completed the deep analysis and have:
- A list of all features with dependencies
- A test inventory mapping features to tests
- Notes on algorithms, design decisions, and data structures

## Task: Order Features by Cognitive Complexity

### Rule 1: Dependency First

Feature B cannot appear before Feature A if B depends on A. This is a hard
constraint. Build a topological sort of features.

### Rule 2: Pain Before Solution

A feature should be introduced *after* the reader has experienced the problem
it solves. Example: Don't introduce retry logic before showing what happens
when a call fails.

Pattern for each feature notebook:
1. Show the system working without this feature
2. Demonstrate the failure / limitation
3. Implement the feature
4. Show the improvement

### Rule 3: Complexity Escalation

Within a dependency level, order features from simpler to more complex:
- Fewer parameters → more parameters
- Synchronous → asynchronous
- Single-threaded → parallel
- Happy path → error cases

### Rule 4: Early Wins

Put a "minimal viable" notebook early (notebook 01 or 02) that gives the reader
a complete, running (if limited) system as quickly as possible. This prevents
reader fatigue before they reach the interesting parts.

## Output Format

For each notebook in order, produce:

```
Notebook NN: [Title]
Feature(s): [feature names from analysis]
Prerequisite notebooks: [NN-1, ...]
Tests unlocked: [test_file.py::test_name, ...]
Has theory section: [yes/no — if yes, what math?]
Running example stage: [describe what the running example can do after this notebook]
Estimated difficulty: [beginner/intermediate/advanced]
```

## Common Ordering Mistakes to Avoid

- Introducing configuration before there's anything to configure
- Teaching parallelism before the serial version is understood
- Jumping to optimization before correctness is established
- Splitting tightly-coupled features into separate notebooks
  (better to cover them together)

## Validation

Before finalizing the order, check:
- [ ] Every feature is assigned to at least one notebook
- [ ] No notebook requires knowledge from a later notebook
- [ ] The running example can be demonstrated by notebook 02
- [ ] The full test suite passes by the final notebook
- [ ] A newcomer reading notebooks in order will never encounter unexplained jargon
