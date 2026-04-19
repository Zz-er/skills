# Theory Derivation Prompt
#
# Use this when writing the theory section of a feature notebook.
# Good theory sections are what separate a great tutorial from documentation.

## When to Include a Theory Section

Include a theory/derivation section when:
- The feature implements a named algorithm (MAP-Elites, UCB, softmax, etc.)
- The feature uses non-obvious math (probability, information theory, optimization)
- A reader would naturally ask "but why does this work?"
- There's a paper or textbook that the implementation is based on

Skip theory when:
- The feature is straightforward engineering (config loading, file I/O, retries)
- The "theory" is just explaining what the code does (that goes in comments)

## Structure of a Good Theory Section

### 1. Intuition First (Always)

Before any math, give a one-paragraph plain-English explanation. Use an
analogy if possible. The reader should be able to follow the math better
because they already know where it's going.

Example: "MAP-Elites is like keeping a cabinet of drawers, where each drawer
holds the best solution found so far with a particular combination of properties.
Instead of tracking just the single best solution, we track the best solution
for each 'niche'."

**Tone note:** The intuition paragraph is Register 3 — warm but precise. Use
"说白了" / "In plain terms" to bridge from formal to casual. One humorous
aside is welcome here (e.g., "这个名字听着很唬人，但其实..."). The formal
derivation that follows is Register 4 — no jokes in the math, but brief
encouraging asides between steps are fine ("快到了，再坚持一步" / "Almost
there, one more step"). See `prompts/style-guide.md` §2.

### 2. Formal Setup

Define all symbols before using them. State what you're trying to compute or
optimize. Introduce constraints if any.

```markdown
Let $\mathcal{X}$ be the space of all programs, $f: \mathcal{X} \to \mathbb{R}$
be the evaluation function, and $\phi: \mathcal{X} \to \mathcal{B}$ be the
feature descriptor mapping programs to a discrete grid $\mathcal{B}$.
```

### 3. Step-by-Step Derivation

Show each step explicitly. Do not skip steps that might seem obvious — a
reader who is stuck will not think they're obvious.

Use numbered steps:

**Step 1:** [What you're doing and why]
$$\text{equation}$$

**Step 2:** [Substituting / expanding / simplifying]
$$\text{equation}$$

**Result:**
$$\boxed{\text{final formula}}$$

### 4. Concrete Numerical Example — MANDATORY

Immediately after the derivation, substitute **real numbers** from the tutorial's
running example into the formula. Show every arithmetic step.

```markdown
**Concrete Example:**
> Suppose our sorting algorithm scores: correctness = 0.9, speed = 0.7, memory = 0.8.
> Substituting into the formula:
> $f = \frac{1}{3}(0.9 + 0.7 + 0.8) = \frac{2.4}{3} = 0.8$
>
> So this algorithm gets a fitness of 0.8 out of 1.0.
```

Rules for numerical examples:
- Use values from the tutorial's running example for consistency
- Show the full calculation, not just the result
- Use realistic (not contrived) numbers
- If the formula has multiple cases, show an example for each case

### 5. Life Analogy — MANDATORY

After the numerical example, add a one-sentence real-world analogy:

```markdown
**Life Analogy:**
> Computing fitness is like calculating your semester GPA — average all course
> grades to get one number that summarizes your overall performance.
```

Good analogies:
- "期末考试算平均分" (semester GPA) for averaging formulas
- "抽奖轮盘" (lottery wheel) for probability-weighted selection
- "邮局分拣信件" (post office sorting mail) for grid/map operations
- "渔场管理" (fishery management) for population-based optimization
- "恒温器" (thermostat) for threshold/convergence checks

### 6. Implementation Mapping

After the math, explicitly map each symbol or step to code:

```markdown
| Math | Code | Meaning |
|------|------|---------|
| $\mathcal{B}$ | `self.grid` | The feature grid (dict) |
| $\phi(x)$ | `feature_descriptor(program)` | Maps program to grid cell |
| $f(x)$ | `evaluate(program)` | Evaluation score |
```

### 7. Source Citation

Always cite the original source. Prefer papers over blog posts over code
comments. Include the exact section or equation number.

```markdown
> **Source:** Mouret & Clune (2015), "Illuminating search spaces by mapping
> elites", [arXiv:1504.04909](https://arxiv.org/abs/1504.04909), Algorithm 1
>
> **Original code:** `openevolve/database.py:L234-L289`
```

## Code Verification of Theory

After the derivation, implement the formula directly from the math (not from
reading the original code) and verify it gives the same results:

```python
# Verify our derivation against the original implementation
from original_code import original_function
from our_implementation import our_function

import numpy as np

test_inputs = [...]
for x in test_inputs:
    expected = original_function(x)
    actual = our_function(x)
    assert np.isclose(expected, actual), f"Mismatch at {x}: {expected} vs {actual}"

print("✓ Our derivation matches the original implementation")
```

## Common Theory Mistakes

- **Symbols appear without definition** — Always define before first use
- **Steps skipped because "obvious"** — They're not obvious to the reader
- **Math without intuition** — Always give the plain-English version first
- **No connection to code** — Always show the math→code mapping table
- **Missing citation** — Every formula should trace back to a source
- **Formula without concrete example** — ALWAYS follow with a numerical example
  using real values from the running example
- **Formula without life analogy** — ALWAYS add a one-sentence real-world analogy
- **Abstract examples** — Use specific numbers (0.9, 0.7, 0.8), not variables (a, b, c)
- **Dry delivery throughout** — The theory section is precise, but it should
  not read like a textbook. Add brief human touches between derivation steps:
  "这一步有点绕，但核心就是把X换成Y" / "This step is a bit involved, but
  the core move is substituting X for Y." See `prompts/style-guide.md` §3.

## LaTeX in Jupyter Notebooks

When writing LaTeX for `.ipynb` files built with the Node.js builder pattern:

- Inside JavaScript template literals, use single backslash: `\\frac{1}{2}`
- `JSON.stringify()` handles double-escaping automatically
- Use `$...$` for inline math, `$$...$$` for display math
- Common formulas and their JS template literal forms:
  - Fraction: `\\frac{a}{b}`
  - Summation: `\\sum_{i=1}^{N} x_i`
  - Greek letters: `\\alpha`, `\\beta`, `\\epsilon`
  - Subscript/superscript: `x_{i}`, `x^{2}`
  - Boxed result: `\\boxed{f(x) = ...}`
- **Never** manually write JSON with LaTeX — always use the builder script
