# Feature Notebook Template
#
# Use this as a checklist when writing each feature notebook.
# Copy the structure below into your notebook, filling in each section.
# Delete sections that don't apply (e.g., no math → skip Theory section).

---

## Notebook: [Feature Name]

**File:** `notebooks/NN-feature-name.ipynb`
**Builds on:** Notebooks 00 through NN-1
**Tests unlocked:** `original-tests/test_feature_name.<ext>` (adapt extension to tutorial language)

---

### Cell 1 — Imports & Setup (Code)

Adapt to the tutorial language and runnability mode (Phase 1.6):

**Python (runnable):**
```python
import sys
sys.path.insert(0, "..")   # so we can import our-implementation

# Standard imports
import numpy as np
# ... project-specific imports

# Our implementation so far
from our_implementation import ...
```

**Other languages (runnable)** — use idiomatic imports:
```go
// Go example
import (
    "our-implementation/module"
    "testing"
)
```

**Explanatory mode** — minimal or no setup; mark code as non-executable:
```python
# NOTE: This code is for illustration. See README.md for setup instructions.
# [imports as needed for readability]
```

---

### Cell 2 — What This Notebook Covers (Markdown)

> **Tone:** Register 2 (casual). Hook the reader. Acknowledge the pain from
> the previous chapter. Build anticipation for what's coming. See
> `prompts/style-guide.md` §2.

```markdown
## [Feature Name]

In the previous notebook we built [X]. That gave us [capability], but we
immediately ran into a problem: [describe the pain point this feature solves].

In this notebook we'll implement [feature], which solves this by [brief summary].

By the end, you'll be able to [concrete capability], and these tests will pass:
- `test_feature_name.py::test_basic_case`
- `test_feature_name.py::test_edge_case`
```

---

### Cell 3 — The Problem (Markdown + Code)

> **Tone:** Register 1-2 (most casual). Be dramatic about the failure.
> Empathize with the reader. "看到没？崩了吧。" is the right energy. See
> `prompts/style-guide.md` §2.

Show concretely what breaks *without* this feature. A short failing example
is worth a thousand words of explanation.

```python
# Without this feature, here's what goes wrong:
# [demo of the failure]
```

---

### Cell 4 — Theory / Derivation (Markdown) [OPTIONAL]

> **Tone:** Register 3-4 (precise but warm). Technical terms must be exact.
> Humor via simplifying asides ("说白了就是..."), not in the math itself.
> See `prompts/style-guide.md` §2 and §7.

Only include this if the feature has non-obvious math or algorithm theory.

```markdown
## Theory: [Algorithm/Formula Name]

> Source: [Paper Title](URL), Section X.Y
> Original implementation: `path/to/original.py:L45-L89`

### Intuition

[One-paragraph plain-English explanation before any math]

### Formal Derivation

We want to compute $f(x)$ such that...

**Step 1:** Starting from [premise]...

$$
\text{[equation]}
$$

**Step 2:** Substituting...

$$
\text{[equation]}
$$

**Result:** This gives us the formula we'll implement:

$$
\boxed{f(x) = \text{[final formula]}}
$$

**Concrete Example:**
> [Substitute real numbers from the running example into the formula.
> Show every arithmetic step so the reader can follow along.]
> e.g.: "If correctness = 0.9, speed = 0.7, memory = 0.8, then:
> $f = \frac{1}{3}(0.9 + 0.7 + 0.8) = 0.8$"

**Life Analogy:**
> [One sentence comparing this formula to an everyday experience.]
> e.g.: "This is like computing your semester GPA — average all course grades."
```

**IMPORTANT:** Every formula in the notebook MUST include both a concrete
numerical example and a life analogy. Do not skip this — zero-background
readers rely on these to build intuition.

---

### Cell 5 — Code Walkthrough (Markdown) [QUASI-MANDATORY]

> **Tone:** Register 2-3 (conversational, encouraging). "别急，我们一步步来."
> This is where the "knowledgeable friend" voice shines most. Use rhetorical
> questions and colloquial transitions freely. See `prompts/style-guide.md` §2.

Walk through the implementation logic in plain language **before** showing
real code. This cell bridges problem/theory → implementation, helping the
reader build a mental model before encountering syntax. Skip ONLY for
trivially simple features (1-2 line implementations like a constant
definition or simple re-export).

See `prompts/walkthrough-prompt.md` for full guidance.

```markdown
## 代码思路拆解 / Code Walkthrough

> 在看具体代码之前，我们先用大白话把思路理清楚。
> Before diving into code, let's walk through the logic in plain language.

### 我们要做什么？ / What Are We Building?

[One sentence: what this code accomplishes in everyday terms.]

> **类比 / Analogy:** [A familiar real-world process that mirrors the code's
> workflow. e.g., "This is like a post office sorting room — letters arrive,
> get categorized by zip code, and placed into the right delivery bag."]

### 分步拆解 / Step-by-Step Breakdown

**Step 1: [Action in plain language]**
[1-3 sentences explaining what happens and why. Use "我们" / "we" voice.]

**Step 2: [Action in plain language]**
[Continue the logical flow. Each step is a natural consequence of the last.]

**Step 3: ...**

> **伪代码 / Pseudocode** (optional, for intricate logic):
> ```
> function do_the_thing(input):
>     for each item in input:
>         if item matches criteria:
>             transform it
>             add to results
>     return results
> ```

### 需要注意的地方 / Things to Watch For

- **[Edge case or subtlety]**: [Why it matters and how we handle it]
- **[Design choice]**: We use X instead of Y because [reason]

### 数据怎么流动？ / How Does Data Flow? (optional)

> Input (dict) → validate → merge defaults → frozen Config object

### 和理论的对应 / Mapping to Theory (only when Cell 4 exists)

> - 推导中的 $\phi(x)$ → Step 2 里的 `feature_descriptor()` 函数
> - 网格 $\mathcal{B}$ → Step 1 里的 Python dict
```

**GUIDELINES for writing good walkthroughs:**

1. **大白话优先 / Plain language first** — If a 15-year-old couldn't follow
   the explanation, simplify it. Avoid jargon; define technical terms inline.
2. **Process, not structure** — Describe what *happens* (verbs, data movement),
   not what *exists* (class hierarchies, type signatures).
3. **深入浅出 / Simple surface, deep core** — Start with one-sentence summary,
   then analogy, then detailed steps. Three layers of increasing depth.
4. **Foreshadow design decisions** — Preview non-obvious choices: "We'll use
   a dictionary because we need O(1) lookup by feature descriptor."
5. **Use the running example** — Ground steps in the tutorial's running example.
6. **Keep it concise** — Simple features: ~150 words. Complex: ~300-400 words.
   Never exceed the implementation code's length.

---

### Cell 6 — Implementation (Code)

> **Tone:** Register 3-4 (professional with personality in comments). Code
> itself is clean and standard. Comments can have personality: "# 这里有个坑"
> is fine; jokes in variable names are not. See `prompts/style-guide.md` §2.

```python
# FEATURE: [Feature Name]
# DECISION: [Why this approach over alternatives]
# REFERENCE: original-code/path/to/file.py:L45-L89

def feature_function(arg: type) -> return_type:
    """
    [One-line summary].

    [Explain what this does and why, in 2-4 sentences.]
    """
    # Step 1: [what and why]
    ...

    # Step 2: [what and why]
    # NOTE: we chose X over Y here because [reason]
    ...

    return result
```

---

### Cell 7 — Demo / Visualization (Code)

```python
# Make the feature's behavior visible and concrete.
# A plot, a printed trace, or a before/after comparison.

result = feature_function(example_input)
print(f"Input:  {example_input}")
print(f"Output: {result}")

# Optional: matplotlib visualization
import matplotlib.pyplot as plt
# ...
plt.title("[What this shows]")
plt.show()
```

---

### Cell 8 — Update our-implementation/ (Code)

**Runnable mode (incremental):**
```python
# Write the implementation to the module file so future notebooks can import it.
# Use the tutorial language's file extension (.py, .go, .rs, .ts, etc.)
# Preferred: use the builder script's fs.writeFileSync() instead of in-notebook writes.
```

**Explanatory mode:** Skip this cell, or include a markdown note:
```markdown
> The complete implementation for this feature can be found in
> `our-implementation/module.<ext>`.
```

---

### Cell 9 — Source Mapping Table (Markdown) — MANDATORY

```markdown
## Our Implementation vs. Original Source

| Our Implementation | Original Source | Notes |
|---|---|---|
| `FeatureClass` | `original/module.py` → `OriginalClass` | Simplified version |
| `our_function()` | `original/utils.py:L45-L89` → `original_function()` | Same algorithm |
| ... | ... | ... |
```

This table is **required** for every feature notebook. It helps readers
cross-reference with the original codebase.

---

### Cell 10 — Verification (Code or Markdown)

Choose the verification mode based on Phase 1.6 settings. See SKILL.md
"Verification Pattern" for all four modes (A/B/C/D).

**Mode A — Python + runnable (pytest):**
```python
import subprocess, sys

result = subprocess.run(
    [sys.executable, "-m", "pytest",
     "original-tests/test_feature_name.py",
     "-v", "--tb=short"],
    capture_output=True, text=True, cwd=".."
)
print(result.stdout[-3000:])
assert result.returncode == 0, "Tests failed — check implementation above"
print("\n✓ All tests for this feature pass!")
```

**Mode C — Non-Python + runnable (native test runner):**
```python
import subprocess

result = subprocess.run(
    ["go", "test", "./...", "-run", "TestFeatureName", "-v"],
    capture_output=True, text=True, cwd=".."
)
print(result.stdout[-3000:])
assert result.returncode == 0, "Tests failed — check implementation above"
print("\n✓ All tests for this feature pass!")
```

**Mode D — Explanatory-only (markdown cell):**
```markdown
## Verification

Run in your terminal from the project root:
\```bash
[language-specific test command]
\```
Expected: all tests for [feature name] pass.
```

---

### Cell 11 — What We Built (Markdown)

> **Tone:** Register 2-3 (celebratory, forward-looking). Acknowledge the
> accomplishment. "搞定！" / "Done!" energy. Tease the next chapter's
> challenge. See `prompts/style-guide.md` §2.

```markdown
## Summary

In this notebook we implemented [feature name]. Key points:

- **[Decision 1]**: We chose X because Y
- **[Decision 2]**: We handle edge case Z by...
- **[Insight]**: Notice that this design means...

The tests in `original-tests/test_feature_name.py` now pass.

**Next:** In [Notebook NN+1 — Next Feature](./NN+1-next-feature.ipynb),
we'll tackle [next problem], which becomes necessary once we have [this feature].
```

---

# Checklist before marking notebook done:
# [ ] All code cells run top-to-bottom without error
# [ ] Verification cell shows tests passing
# [ ] our-implementation/ updated with new code
# [ ] Code walkthrough present for non-trivial features (plain language, analogies, steps)
# [ ] Theory section cites original source (paper or file:line)
# [ ] Every formula has a concrete numerical example AND a life analogy
# [ ] Source mapping table present (Our Implementation vs. Original)
# [ ] "The Problem" cell shows a concrete failure before the fix
# [ ] Summary cell links to the next notebook
# [ ] Mermaid diagrams are in markdown cells (never code cells)
# [ ] .ipynb passes JSON validation (node -e "JSON.parse(...)")
# [ ] Tone varies appropriately between cells (see prompts/style-guide.md §2)
# [ ] Code language matches tutorial configuration (Phase 1.6)
# [ ] Verification mode matches runnability setting (runnable → code cell, explanatory → markdown)
