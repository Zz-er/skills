# Feature Notebook Template
#
# Use this as a checklist when writing each feature notebook.
# Copy the structure below into your notebook, filling in each section.
# Delete sections that don't apply (e.g., no math → skip Theory section).

---

## Notebook: [Feature Name]

**File:** `notebooks/NN-feature-name.ipynb`
**Builds on:** Notebooks 00 through NN-1
**Tests unlocked:** `original-tests/test_feature_name.py`

---

### Cell 1 — Imports & Setup (Code)

```python
import sys
sys.path.insert(0, "..")   # so we can import our-implementation

# Standard imports
import numpy as np
# ... project-specific imports

# Our implementation so far
from our_implementation import ...
```

---

### Cell 2 — What This Notebook Covers (Markdown)

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

Show concretely what breaks *without* this feature. A short failing example
is worth a thousand words of explanation.

```python
# Without this feature, here's what goes wrong:
# [demo of the failure]
```

---

### Cell 4 — Theory / Derivation (Markdown) [OPTIONAL]

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

```python
# Write the implementation to the module file so future notebooks can import it.
# Use %%writefile or manually write the function to the appropriate module.
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

### Cell 10 — Verification (Code)

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

---

### Cell 11 — What We Built (Markdown)

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
