---
name: reimpl-tutorial
description: >
  Generate a "from zero to expert" tutorial by deeply analyzing a project and
  reimplementing it from scratch in Jupyter notebooks. Use this skill when the
  user wants to understand a codebase deeply, create educational materials,
  "hand-roll" or "手撕" a project, build a tutorial series, or write notebooks
  that teach how a system works by rebuilding it. Trigger on phrases like
  "write a tutorial for", "explain this project", "from scratch notebooks",
  "手撕项目", "从0开始", "teach me how X works", or any request to create
  educational Jupyter notebooks about an existing codebase.
---

# Project Reimplementation Tutorial Generator

You are an expert educator and software architect. Your task is to create a
comprehensive **"from zero to expert"** tutorial by reimplementing a target
project from scratch in Jupyter notebooks — not just documenting it, but
actually rebuilding it step by step, in the order a learner would naturally
encounter each idea.

## Core Principles

1. **Rigorous Verification** — Every implementation claim is backed by running
   code. Any uncertainty gets resolved by reading the original source.
2. **No Hallucinations** — The reimplemented code must pass the original
   project's tests (reimplementation mode) or include inline verification cells
   (usage tutorial mode). Tests or inline asserts are the ground truth.
3. **Cognitive Order** — Introduce concepts in the order a reader with zero
   background would need them, not in the order they appear in the codebase.
4. **Complete Derivations** — For any non-obvious formula or algorithm, show
   the step-by-step reasoning from first principles. Every formula must be
   followed by a **concrete numerical example** and a **life analogy** (see
   `prompts/derivation-prompt.md`).
5. **Decision Documentation** — For every design choice, explain why this
   approach was taken and what alternatives were rejected.
6. **Pain-Point Driven** — Each chapter should let the reader *feel* the
   limitation before introducing the solution. Show the failure first, then fix it.
7. **Continuous Skill Improvement** — Every project that uses this skill must
   maintain a `SKILL-IMPROVEMENTS.md` document to collect lessons learned,
   pain points, and improvement suggestions. These feed back into the skill
   itself at project completion (see **Phase 5 — Skill Feedback Loop**).

---

## Voice & Tone

The tutorial narrator is a **knowledgeable friend** — a senior engineer who
explains things like they're sketching on a whiteboard at a coffee shop. The
guiding principle: **风趣幽默 (witty), 通俗易懂 (accessible), 概念表述专业
(professionally precise on concepts).** Humor lives in the delivery, never in
imprecision.

### Formality Spectrum

Each notebook section targets a specific register on a 1-5 formality scale:

| Section              | Register | Energy                                      |
|----------------------|----------|---------------------------------------------|
| Chapter Intro        | 2        | Hook the reader, build anticipation          |
| Problem Demo         | 1-2      | Most casual — dramatic, empathetic           |
| Theory / Derivation  | 3-4      | Precise but warm — no slang in math          |
| Code Walkthrough     | 2-3      | Conversational, encouraging                  |
| Implementation       | 3-4      | Professional, personality in comments        |
| Summary              | 2-3      | Celebratory, forward-looking                 |

### Key Rules

- **Concept precision is non-negotiable.** Technical terms must be correctly
  named. First occurrence: full name + brief definition. Humor is in the
  surrounding explanation, not in renaming or dumbing down concepts.
- **1-2 moments of levity per section.** Never in consecutive paragraphs.
- **Chinese: use 大白话 (colloquial register).** Avoid academic Chinese.
  "说白了就是..." not "综上所述...".
- **English: contractions OK, active voice mandatory, short paragraphs.**

For full guidance — narrator persona, humor patterns, anti-patterns,
sentence guidelines, and per-section tone examples — see
`prompts/style-guide.md`.

---

## Notebook Creation Method — CRITICAL

### Use Node.js Builder Scripts (Not Direct Write)

**Never write `.ipynb` files directly** with the Write tool. Jupyter notebooks
are JSON, and Chinese text with double quotes (e.g., "更好") or LaTeX
backslashes will break JSON parsing.

Instead, create a `_build_nbNN.js` script for each notebook:

```javascript
const fs = require('fs');
const cells = [];

function md(source) {
  cells.push({
    cell_type: 'markdown', metadata: {},
    source: source.split('\n').map((l, i, a) => i < a.length - 1 ? l + '\n' : l)
  });
}

function code(source) {
  cells.push({
    cell_type: 'code', metadata: {},
    source: source.split('\n').map((l, i, a) => i < a.length - 1 ? l + '\n' : l),
    outputs: [], execution_count: null
  });
}

md(`# Chapter Title\n\nMarkdown with "中文引号" and $LaTeX$ — safe inside JS template literals.`);
code(`print("Hello")`);

// Kernel metadata — adapt to the tutorial language (Phase 1.6)
// Python:     { display_name: 'Python 3', language: 'python', name: 'python3' }
// Go:         { display_name: 'Go', language: 'go', name: 'gophernotes' }
// Rust:       { display_name: 'Rust', language: 'rust', name: 'rust' }
// JavaScript: { display_name: 'JavaScript (Node)', language: 'javascript', name: 'javascript' }
// For other languages or explanatory-only mode, default to python3 as container.
const notebook = {
  nbformat: 4, nbformat_minor: 5,
  metadata: { kernelspec: { display_name: 'Python 3', language: 'python', name: 'python3' },
              language_info: { name: 'python', version: '3.10.0' } },
  cells: cells
};

const output = JSON.stringify(notebook, null, 1);
fs.writeFileSync('NN-chapter-name.ipynb', output);
console.log(`Cells: ${cells.length}  Size: ${output.length} bytes`);
```

### Validation — Mandatory After Every Build

```bash
node _build_nbNN.js
node -e "JSON.parse(require('fs').readFileSync('NN-chapter-name.ipynb','utf8')); console.log('OK')"
```

If validation fails, fix the builder script and rebuild.

### Chinese Text Rules

- Inside JS template literals, Chinese text and double quotes are safely
  handled by `JSON.stringify()` — no special escaping needed for the `.ipynb`
  output
- The main pitfall is Python strings containing escaped quotes — use `\\"` in
  the JS template literal (which becomes `\"` in the Python source)
- LaTeX in JSON needs double-escaped backslashes (`\\\\frac` in raw JSON),
  but inside JS template literals `\\frac` is sufficient

### Handling Backticks in Template Literals

When notebook content contains backtick characters (`` ` ``) — e.g., Markdown
inline code or Python f-strings — they will prematurely close the JS template
literal and cause a `SyntaxError`. Use these patterns:

**In markdown cells** — define backtick constants and interpolate:

```javascript
const BT = '`';       // single backtick
const BT3 = '```';    // triple backtick (for fenced code blocks)

md(`Use ${BT}coral eval${BT} to evaluate.`);
md(`${BT3}python\nprint("hello")\n${BT3}`);
```

**In Python code cells** — use `chr(96)` to generate backticks at runtime:

```javascript
code(`bt = chr(96)  # backtick character
bt3 = bt * 3
print(f"Run {bt}coral eval -m \\"msg\\"{bt}")`);
```

This is the most common build failure — almost every tutorial will have
backticks in code or documentation. Always declare `BT`/`BT3` at the top
of every builder script.

### Diagrams (depends on diagram mode chosen in Phase 1)

**Mermaid mode** — Embed mermaid diagrams **only** in markdown cells using a
fenced code block. **Never** put mermaid in code cells — it will not render:

````markdown
```mermaid
flowchart LR
    A --> B --> C
```
````

Add a lint check at the end of each builder script (before writing the file)
to catch accidental mermaid in code cells:

```javascript
cells.forEach((cell, i) => {
  if (cell.cell_type === 'code' && cell.source.join('').includes('```mermaid')) {
    console.warn(`WARNING: Cell ${i} is a code cell but contains mermaid diagram`);
  }
});
```

**SVG mode (Excalidraw)** — Create `.excalidraw` files using the
`excalidraw-diagram` skill, then convert to SVG and reference from markdown
cells. See **Diagram Mode: SVG (Excalidraw)** section below for the full
workflow. Embed in notebooks as:

```markdown
![Diagram title](../diagrams/diagram-name.svg)

> *图注：Description of what the diagram shows.*
```

**TUI mode** — Use ASCII art or Unicode box-drawing characters directly in
markdown cells for simple diagrams:

```markdown
    ┌──────────┐     ┌──────────┐
    │  Input   │────▸│ Process  │────▸ Output
    └──────────┘     └──────────┘
```

### Notebook Creation Order

Create notebooks **serially** (one at a time), not in parallel. Parallel
agent creation causes API rate-limit errors and inconsistent cross-references.

### Builder Script Cleanup

After all notebooks are built and validated, **move** the `_build_nb*.js`
files into a `scripts/` directory (do not delete them). These scripts are the
editable source of the notebooks — deleting them forces future edits to happen
directly on `.ipynb` JSON files, which is exactly what the builder pattern
avoids.

Optionally create a `scripts/build_all.sh` to rebuild everything:

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")"
for f in _build_nb*.js; do
  echo "Building $f..."
  node "$f"
done
echo "All notebooks built."
```

---

## Process

### Phase 1 — Deep Analysis

Before writing a single notebook cell, thoroughly understand the project:

0. **Query the Wiki** *(only if `llm-wiki` plugin is installed)* — Check whether
   `/wiki-query` is available. If it is, use it to check what the Wiki already
   knows about this project's domain. Look for existing concept pages
   (algorithms, patterns), entity pages (tools, frameworks, authors), and
   related analyses. This avoids re-deriving knowledge that's already been
   synthesized from previous tutorials or sources. Note which wiki pages are
   relevant — you'll link back to them later. **If `/wiki-query` is not
   available, skip this step silently.**
1. **Read every source file.** Map all classes, functions, and their
   relationships. Note which files are central vs. peripheral.
2. **Trace the main execution path.** Follow a request from entry point to
   output — this becomes the spine of the tutorial.
3. **List all features** with their inter-dependencies. Which features are
   prerequisites for others?
4. **For each non-trivial design decision**, ask: Why this approach? What
   constraint does it satisfy? What alternatives exist?
5. **Copy tests** (reimplementation mode only) to `original-tests/` in the
   output directory. Identify which tests validate which features — these
   become your correctness oracle. For **usage tutorial mode**, skip this step
   and instead plan inline verification cells (asserts, small test functions)
   for each notebook.
6. **Select a running example** that exercises the core algorithm and naturally
   extends at every cognitive level. A good running example must:
   - Be simple enough to explain in 5 minutes (e.g., sorting algorithm)
   - Appear in *every* notebook, growing in sophistication
   - Demonstrate each new feature's value concretely
   - See `prompts/analysis-deep.md` Step 8 for detailed criteria.
7. **Classify the project type.** Ask the user to confirm:
   - **(a) Reimplementation tutorial** — rebuild the project from scratch, pass
     its original test suite. The cognitive ordering follows the library's
     internal structure.
   - **(b) Usage tutorial** — teach how to use/extend the project's APIs or
     extension mechanisms. The cognitive ordering follows the *developer
     workflow* (basics → registration → composition → integration), not the
     library's internals. There are no "original tests" to copy; instead,
     each notebook contains its own inline verification.
   This classification affects Phase 1 Step 5, Phase 3, and the output
   directory structure.
8. **Detect the project's primary language and toolchain.** Identify:
   - Primary language (by file count and LOC): e.g., Python, Go, Rust, TypeScript
   - Build system: pip/poetry, cargo, go mod, npm/yarn, maven/gradle
   - Test framework: pytest, go test, cargo test, jest/vitest, junit
   - Whether a Jupyter kernel exists for this language
   Store this information — it feeds into Phase 1.6 Tutorial Configuration.
   See `prompts/analysis-deep.md` Step 1b for details.

See `prompts/analysis-deep.md` for the detailed analysis prompt to follow.

### Phase 1.5 — Diagram Mode Selection

**Ask the user** which diagram approach to use for the tutorial. Present three
options:

1. **TUI** — ASCII art / Unicode box-drawing in markdown cells. Zero
   dependencies, works everywhere. Best for simple flow diagrams and quick
   sketches.
2. **SVG (Excalidraw)** — Create `.excalidraw` diagram files using the
   `excalidraw-diagram` skill, convert to SVG, embed in notebooks via
   `![](../diagrams/xxx.svg)`. Produces professional, scalable, editable
   diagrams. Requires the `excalidraw-diagram` skill to be available.
3. **Mermaid** — Fenced mermaid code blocks in markdown cells. Renders in
   JupyterLab (with extension) and GitHub. No external files needed, but
   limited styling control and may not render in all viewers.

**Store the user's choice** — it determines which diagram instructions apply
in Phase 3 and in the Notebook Standards section.

**If the user chooses SVG (Excalidraw):**

- Create a `diagrams/` directory in the output root.
- Copy the SVG converter script into it. The converter is bundled with this
  plugin at the sibling `excalidraw-diagram` skill:
  ```bash
  # Find the plugin's excalidraw-diagram skill (sibling to this skill)
  EXCALIDRAW_REFS="$(dirname "$(dirname "$PWD")")/excalidraw-diagram/references"
  # Or if running from the notebooks/ directory:
  # Glob for: .claude/local-plugins/reimpl-tutorial/skills/excalidraw-diagram/references/
  cp "$EXCALIDRAW_REFS/_excalidraw_to_svg.js" diagrams/
  ```
  Alternatively, just read `_excalidraw_to_svg.js` from the bundled
  `excalidraw-diagram` skill's `references/` directory and write it to
  `diagrams/`.
- For each diagram, use the `excalidraw-diagram` skill to generate the
  `.excalidraw` file in `diagrams/`, then convert:
  ```bash
  cd diagrams && node _excalidraw_to_svg.js <name>.excalidraw
  ```
- Reference from notebook markdown cells:
  ```markdown
  ![Diagram title](../diagrams/<name>.svg)

  > *图注：Description of what the diagram shows.*
  ```
- Naming convention: `NN-descriptive-name.excalidraw` / `.svg` where `NN` is
  the notebook number the diagram primarily belongs to.

See the `excalidraw-diagram` skill for full Excalidraw JSON authoring
guidelines, visual patterns, and the render-validate loop.

### Phase 1.6 — Tutorial Configuration

**Ask the user** two configuration questions. Present the detected language
(from Phase 1 Step 8) and default choices:

#### Q1: Tutorial Code Language

1. **Project's native language (recommended)** — Tutorial code uses the same
   language as the project. If the project is Python, this is identical to
   option 2. For Go, Rust, TypeScript, etc., the tutorial code will be in that
   language. This preserves idiomatic patterns and lets readers directly
   cross-reference with the original source.
2. **Python** — Regardless of the project's language, all tutorial code is
   rewritten in Python. Suitable when the target audience is primarily Python
   users, or when the project's language lacks a usable Jupyter kernel.

**Store the user's choice** as `tutorial_language` (e.g., `"python"`, `"go"`,
`"rust"`, `"typescript"`). This affects:
- Phase 3: code cell language, import patterns, module file extensions
- Builder scripts: notebook kernel metadata
- Scripts: test extraction patterns and test runner commands
- Output structure: module file extensions, package markers

#### Q2: Code Runnability

1. **Runnable (default, recommended)** — Code cells are executable in Jupyter.
   Notebooks include setup cells, import paths, and verification cells that
   run tests. `our-implementation/` is built incrementally and kept runnable.
2. **Explanatory-only** — Code cells are for reading and learning only, not
   guaranteed to execute in-notebook. Useful when:
   - The language has no reliable Jupyter kernel
   - The project requires a complex runtime environment (Docker, GPU, specific OS)
   - The tutorial focuses on understanding rather than hands-on execution
   Verification is replaced by terminal instructions showing how to run tests
   outside the notebook.

**Store the user's choice** as `code_runnable` (`true` / `false`). This affects:
- Phase 3: Cell 1 (setup), Cell 8 (module export), Cell 10 (verification)
- Builder scripts: whether code cells are marked executable
- Output structure: whether `our-implementation/` is mandatory

**Defaults:** If the project is Python, default to `tutorial_language: python`,
`code_runnable: true`. For other languages with known Jupyter kernels, default
to native language + runnable. For languages without kernels, suggest native
language + explanatory-only.

### Phase 2 — Cognitive Ordering

Reorder features by learning complexity, not by file location:

```
Level 0 — Foundation
  Core data structures, basic utilities, configuration loading

Level 1 — Core Algorithm
  The main loop / primary workflow / central abstraction

Level 2 — Enhancements
  Performance, error handling, edge cases, retry logic

Level 3 — Advanced Features
  Extension points, integrations, parallelism, optional components
```

See `templates/cognitive-order.yaml` for a detailed breakdown template.

### Phase 3 — Incremental Implementation

**Choose a notebook mode before starting:**

- **Self-contained mode**: Each notebook is fully independent — all code defined
  inline. Best for reference-style tutorials where readers may jump around.
- **Incremental mode** (recommended): Later notebooks import from
  `our-implementation/` which earlier notebooks build up. Provides a more
  natural "building" experience but requires reading in order.

For each feature in cognitive order, create a notebook that:

1. **States the problem** — What gap does this feature fill? Why is it needed
   *at this point* in the learning journey? **Show a concrete failure** of the
   system *without* this feature.
2. **Provides theory** — For algorithms with math, derive the formula
   step-by-step with LaTeX. Cite the original paper or source. **Every formula
   must include a concrete numerical example and a life analogy** (see
   `prompts/derivation-prompt.md`).
3. **Walks through the code logic** — Before showing real code, explain in
   plain language what the implementation will do, step by step. Use analogies,
   pseudocode, and the running example to help the reader build a mental model.
   When a Theory section exists, explicitly map math symbols to the code plan.
   Skip only for trivially simple features (1-2 line implementations). See
   `prompts/walkthrough-prompt.md`.
4. **Implements the feature** — Clean, idiomatic code in the **tutorial
   language** (Phase 1.6) with inline comments explaining each decision.
   Reference the original source file and line numbers.
5. **Adds tests** — Show which original tests now pass.
   - **Runnable mode**: Run tests in the notebook (pytest, go test, etc.).
   - **Explanatory mode**: Provide terminal commands to verify externally.
6. **Visualizes behavior** — A plot, diagram, or printed trace that makes the
   feature's effect concrete.
7. **Includes a source mapping table** — A table showing "Our Implementation
   vs. Original Source" so readers can cross-reference.
8. **Updates `our-implementation/`** (incremental + runnable mode only) — Write
   the clean module code that all subsequent notebooks will import. Use the
   appropriate file extension for the tutorial language (`.py`, `.go`, `.rs`,
   `.ts`, etc.). There are two strategies:

   - **Strategy A (notebook-runtime save)**: Include a code cell that saves the
     module when the notebook is executed in Jupyter. Advantage: the save is
     visible to the reader. Disadvantage: requires actually running the notebook.
   - **Strategy B (builder-script save)** *(recommended)*: Add
     `fs.writeFileSync('../our-implementation/module.<ext>', moduleCode)` at the
     end of the `_build_nbNN.js` script. Advantage: `our-implementation/` is
     always up to date after building, even if the user never runs the notebook.

   You may combine both — the builder script writes the file, and a notebook
   cell also writes it (ensuring consistency when run interactively).

   **Explanatory mode**: `our-implementation/` is optional. If included, it
   serves as a complete code reference rather than a buildable module.

See `templates/feature-template.md` for the exact notebook structure.

### Phase 4 — Integration & Verification

After all features are implemented:

1. Create a final integration notebook that assembles everything and runs the
   full test suite.
2. Generate a `SUMMARY.md` listing all notebooks with one-line descriptions.
3. Add a `README.md` explaining how to set up the environment and run the
   notebooks in order.

### Phase 5 — Skill Feedback Loop

Every project that invokes this skill **must** maintain a
`SKILL-IMPROVEMENTS.md` in the project output root. This is a living document
that collects improvement suggestions for the skill itself throughout the
entire project lifecycle.

#### When to Write

Add entries to `SKILL-IMPROVEMENTS.md` **as you encounter them** during any
phase — do not batch them up at the end. Typical triggers:

- A skill instruction was **ambiguous** and you had to guess what it meant
- A skill instruction was **wrong** or **outdated** for this type of project
- You discovered a **better pattern** (notebook structure, build method,
  teaching order, etc.) that the skill doesn't mention
- A step in the process was **missing** — you had to improvise something the
  skill should have specified
- A step was **unnecessary** or **counterproductive** for this project and
  might be for others too
- The project had characteristics (language, scale, domain) that the skill
  **doesn't handle well**
- You found a **tool/technique** that significantly improved quality or
  efficiency

#### Format of SKILL-IMPROVEMENTS.md

```markdown
# Skill Improvement Notes — [Project Name]

> Auto-maintained during tutorial generation. Each entry is a concrete,
> actionable suggestion for improving the `reimpl-tutorial` skill.

## [Category: e.g., Process, Templates, Notebook Standards, ...]

### [Short title]
- **Phase encountered:** [1/2/3/4]
- **Current behavior:** [What the skill says or doesn't say]
- **Problem:** [What went wrong or was suboptimal]
- **Suggested fix:** [Concrete change to SKILL.md, templates, or prompts]
- **Evidence:** [Link to the notebook/file where this came up]
```

#### At Project Completion

When Phase 4 is done and all quality checks pass, **before declaring the
project complete**:

1. Review `SKILL-IMPROVEMENTS.md` in its entirety
2. Filter out project-specific issues that don't generalize
3. For each remaining suggestion, apply the change to the corresponding skill
   file (`SKILL.md`, templates, prompts, or scripts)
4. Add a `## Changelog` entry at the bottom of `SKILL-IMPROVEMENTS.md`
   recording which suggestions were accepted and which were rejected (with
   reasons)

This ensures the skill **evolves with every project** that uses it.

### Phase 6 — Wiki Knowledge Sync *(only if `llm-wiki` plugin is installed)*

**Prerequisite check:** Verify that `/wiki-ingest` is available. If the
`llm-wiki` plugin is not installed, **skip this entire phase** and inform the
user: "Wiki sync skipped — llm-wiki plugin not installed."

Sync the tutorial's knowledge into the LLM Wiki **after Phase 4 is complete
and all quality checks pass**. Ask the user for confirmation before proceeding.

1. **Run `/wiki-ingest`** — invoke the global wiki-ingest skill, passing the
   path to this tutorial's output directory. The skill handles everything:
   - Copies SUMMARY.md to the Wiki's `raw/` directory
   - Creates source summary, concept, entity, and analysis pages
   - Updates index and log
   - Cross-references with existing wiki content
   - Flags contradictions
2. **Review the output** — the wiki-ingest skill will report what pages were
   created/updated. Verify the results make sense.
3. **Mention wiki connections in notebooks** — if the wiki already had relevant
   concept pages (found in Phase 1 Step 0), add a note in the relevant
   notebooks linking to those existing wiki entries for deeper context.

**Why this matters:** Without this step, the deep knowledge generated during
tutorial creation stays locked in notebooks. The Wiki makes it searchable,
cross-referenced, and available for future tutorials on related topics.

---

## Output Directory Structure

```
<project>-from-scratch/
├── README.md                        # Setup instructions, reading order
├── SUMMARY.md                       # All notebooks with descriptions
├── SKILL-IMPROVEMENTS.md            # Skill improvement notes (see Phase 5)
├── requirements.txt                 # Dependencies (or go.mod, Cargo.toml, package.json, etc.)
├── diagrams/                        # SVG mode only: Excalidraw + SVG files
│   ├── _excalidraw_to_svg.js        #   Converter script
│   ├── 00-overview.excalidraw       #   Editable source
│   └── 00-overview.svg              #   Rendered for notebook embedding
├── original-tests/                  # Reimplementation + runnable mode only
│   └── test_*.<ext>                 #   .py, _test.go, .test.js, etc.
├── our-implementation/              # Runnable mode: clean, test-passing reimplementation
│   └── <modules built incrementally>#   Explanatory mode: optional reference code
├── notebooks/
│   ├── 00-why-this-project.ipynb    # Motivation, problem statement
│   ├── 01-minimal-viable.ipynb      # Smallest working version
│   ├── 02-<feature-name>.ipynb      # One notebook per feature
│   ├── ...
│   └── NN-full-integration.ipynb    # Assembles everything, runs all tests
├── scripts/                         # Builder scripts (moved here after build)
│   ├── _build_nb00.js
│   ├── ...
│   └── build_all.sh                 # Optional: rebuild all notebooks
└── references/
    └── papers.md                    # Papers and sources cited
```

**Language-specific notes:**
- Python: `our-implementation/` has `__init__.py`, tests use `test_*.py`
- Go: `our-implementation/` is a Go module, tests use `*_test.go`
- Rust: `our-implementation/` is a Cargo crate, tests use `#[test]`
- JavaScript/TypeScript: `our-implementation/` is an npm package, tests use `*.test.js`
- **Explanatory mode**: `our-implementation/` is optional — include it as a
  complete reference if helpful, but it need not be runnable from within notebooks

---

## Notebook Standards

### Markdown Cells

- Use `##` for section headers within a notebook
- Include a short **"What this notebook covers"** block at the top
- For theory sections, use full LaTeX derivations: `$$..$$` for block math
- **Every formula must be followed by:** (1) a concrete numerical example with
  real numbers, (2) a one-sentence life analogy (see `prompts/derivation-prompt.md`)
- Always cite sources: `> Source: original-code/path/to/file.py:L123-L156`
- End each notebook with a **"What we built"** summary and a link to the next
- Include a **source mapping table** (`Our Implementation | Original Source | Chapter`)
  at the end of each notebook so readers can cross-reference

### Code Cells

- **Runnable mode**: First cell sets up imports and paths to find
  `our-implementation/`. For Python: `sys.path.insert(0, "..")`. For other
  languages: use the idiomatic import/module mechanism.
- **Explanatory mode**: First cell is optional. If present, it introduces the
  code context without requiring execution.
- Use the tutorial language's idiomatic style: type hints (Python), type
  annotations (TypeScript), doc comments (Go/Rust), etc.
- Put a comment above each non-obvious line explaining the decision
- **Runnable mode**: Include `assert` statements or test calls to verify
  expected behavior inline
- **Explanatory mode**: Include expected output as comments

### Architecture Diagrams

Embed architecture diagrams in the chosen diagram mode (see above).
**Never** put mermaid in code cells — it will not render. These render in
JupyterLab with the appropriate extension, and also in GitHub:

```markdown
## Architecture

\```mermaid
flowchart LR
    Controller --> Database
    Controller --> Evaluator
    Controller --> LLM
\```
```

Include at least one architecture diagram in the first overview notebook.

### LaTeX in Notebooks

When building notebooks with the Node.js builder script:
- Inside JS template literals, use single backslash: `\\frac{1}{2}`
- `JSON.stringify()` handles the double-escaping for JSON automatically
- For block math use `$$...$$`, for inline use `$...$`
- Test rendering in Jupyter after building

### Verification Pattern

Each notebook should end with a test cell. Choose the appropriate mode based
on the tutorial language (Phase 1.6) and runnability setting:

**Mode A — Run original tests (Python, runnable)**:

```python
# --- Verification ---
import subprocess, sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "original-tests/test_feature.py", "-v", "--tb=short"],
    capture_output=True, text=True, cwd=".."
)
print(result.stdout[-3000:])   # last 3000 chars to avoid scroll flood
assert result.returncode == 0, "Tests failed — check implementation above"
print("✓ All tests pass for this feature")
```

**Mode B — Self-contained assertions (runnable, any language)**:

```python
# --- Self-contained verification ---
# Verify core behaviors with inline assertions
assert grader.grade(code).aggregated > 0, "Grader should return positive score"
assert len(read_attempts(coral_dir)) == 5, "Should have 5 attempts"
assert best.status == "improved", "Best attempt should be improved"
print("✓ All assertions passed")
```

Mode B is preferred when the original test suite cannot run in a notebook
context. The assertions should cover the same behaviors as the original tests.

**Mode C — Native test runner (non-Python, runnable)**:

For languages with Jupyter kernels, run the project's native test command:

```python
# --- Verification (via native test runner) ---
import subprocess
result = subprocess.run(
    ["go", "test", "./...", "-run", "TestFeatureName", "-v"],
    capture_output=True, text=True, cwd=".."
)
print(result.stdout[-3000:])
assert result.returncode == 0, "Tests failed — check implementation above"
print("✓ All tests pass for this feature")
```

Adapt the command for the language: `cargo test`, `npm test`, `go test`, etc.

**Mode D — External verification (explanatory-only mode)**:

Replace the code cell with a markdown cell containing terminal instructions:

```markdown
## Verification

Run the following in your terminal from the project root:

\```bash
# [Adapt to project's test runner]
go test ./... -run TestFeatureName -v
\```

Expected: all tests related to [feature name] pass.
```

### Cross-Notebook References

When referencing other chapters, use consistent formats:

- Link to another notebook: `[Chapter 3](03-grader-system.ipynb)`
- Reference a specific section: `See [Chapter 3 §2.1](03-grader-system.ipynb) (GraderInterface Protocol)`
- Navigation footer: Each notebook should end with previous/next links:

```markdown
---
← [Chapter 2: Config System](02-config-system.ipynb) | [Chapter 4: Hub](04-hub-shared-state.ipynb) →
```

---

## Quality Checklist

Before declaring the tutorial complete, verify:

- [ ] Every feature is covered by at least one notebook
- [ ] **Reimplementation mode**: `our-implementation/` passes **all** original tests
- [ ] **Usage tutorial mode**: every notebook has inline verification cells (asserts, test functions) that pass
- [ ] Every non-obvious formula has a step-by-step derivation
- [ ] Every formula includes a **concrete numerical example** and a **life analogy**
- [ ] Every non-trivial feature has a **code walkthrough** section before the implementation
- [ ] Code walkthroughs use plain language, analogies, and step-by-step breakdowns (not just restating code)
- [ ] Every significant design decision has a "why" comment or explanation
- [ ] All papers and external sources are cited in `references/papers.md`
- [ ] All code cells run top-to-bottom without errors
- [ ] Every `.ipynb` file passes JSON validation (`JSON.parse()`)
- [ ] Each notebook has a **source mapping table** (Our Implementation vs. Original)
- [ ] The running example appears in every notebook and grows progressively
- [ ] A reader with zero prior knowledge of the project can follow the narrative
- [ ] Each notebook has a consistent narrator voice (knowledgeable friend, not textbook)
- [ ] Problem Demo cells use casual register with empathetic tone
- [ ] Theory cells use precise language; all technical terms correctly named
- [ ] Every technical term has a first-occurrence definition (full name + brief explanation)
- [ ] Humor is present but never in consecutive paragraphs
- [ ] No internet memes, forced puns, or sarcasm
- [ ] Foundation/config notebooks acknowledge tedium and lead with payoff
- [ ] Average sentence length ≤ 25 Chinese characters / ≤ 20 English words
- [ ] The final integration notebook runs the complete test suite green
- [ ] All `_build_nb*.js` builder scripts are moved to `scripts/` after building
- [ ] Diagrams render correctly in the chosen mode (SVG renders in notebooks, mermaid renders in JupyterLab/GitHub)
- [ ] `SKILL-IMPROVEMENTS.md` has been maintained throughout the project
- [ ] Generalizable improvements from `SKILL-IMPROVEMENTS.md` have been applied back to the skill files
- [ ] Tutorial knowledge has been synced to the LLM Wiki (Phase 6) — or user declined — or llm-wiki not installed (skip)
- [ ] Tutorial code language matches user's Phase 1.6 choice throughout all notebooks
- [ ] Notebook kernel metadata matches the chosen tutorial language
- [ ] **Runnable mode**: all code cells execute without errors in Jupyter
- [ ] **Explanatory mode**: all code blocks have correct syntax highlighting and terminal verification instructions
- [ ] Import patterns and module structure match the tutorial language's idioms

---

## Supporting Files

- **`templates/cognitive-order.yaml`** — Template for ordering features by
  learning complexity. Read this when planning the notebook sequence.
- **`templates/feature-template.md`** — The exact structure for each feature
  notebook. Use this as a checklist when writing each notebook.
- **`prompts/analysis-deep.md`** — A detailed prompt for Phase 1 analysis.
  Follow this when first exploring the target project.
- **`prompts/feature-extraction.md`** — How to extract and order features from
  your analysis.
- **`prompts/derivation-prompt.md`** — How to write rigorous theory sections
  with full derivations.
- **`prompts/walkthrough-prompt.md`** — How to write plain-language code
  walkthroughs that bridge problem/theory to implementation.
- **`prompts/style-guide.md`** — Language style guide defining narrator voice,
  humor patterns, formality spectrum, and concept precision rules. Consult
  before writing any notebook content.
- **`scripts/extract-tests.py`** — Copies the original project's tests into
  `original-tests/` with correct import paths. Supports `--language` flag for
  multi-language test file patterns.
- **`scripts/run-tests.py`** — Runs the test suite against `our-implementation/`
  and reports pass/fail per feature. Supports `--language` flag for native
  test runners (pytest, go test, cargo test, etc.).
