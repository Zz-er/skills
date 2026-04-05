# reimpl-tutorial-plugin

A Claude Code plugin that generates "from zero to expert" tutorials by reimplementing projects in Jupyter notebooks. Includes the `excalidraw-diagram` skill for SVG diagram generation — no additional dependencies needed.

## Skills Included

| Skill | Description |
|-------|-------------|
| **reimpl-tutorial** | Deeply analyze a project and rebuild it from scratch in Jupyter notebooks, with cognitive ordering, rigorous verification, and full derivations. |
| **excalidraw-diagram** | Generate Excalidraw JSON diagrams and convert them to SVG for embedding in notebooks. Bundled — no separate installation required. |

## Installation

### Via Claude Code Plugin Marketplace (recommended)

```bash
# 1. Add this repo as a marketplace source
claude plugin marketplace add https://github.com/Zz-er/skills

# 2. Install the plugin
claude plugin install reimpl-tutorial

# 3. Verify — the skill should appear when you type /reimpl-tutorial in Claude Code
```

To update later:

```bash
claude plugin update reimpl-tutorial
```

### Manual Installation

If the marketplace method doesn't work, you can install as a local plugin:

```bash
git clone https://github.com/Zz-er/skills.git ~/.claude/local-plugins/_skills_repo

ln -s ~/.claude/local-plugins/_skills_repo/reimpl-tutorial-plugin \
      ~/.claude/local-plugins/reimpl-tutorial
```

## Usage

The skill triggers automatically on phrases like:

- "write a tutorial for [project]"
- "reimpl [project] from scratch"
- "create notebooks explaining [project]"
- "手撕项目" / "从0开始"

Or invoke directly: `/reimpl-tutorial`

### Tutorial Types

- **Reimplementation tutorial** — Rebuild the project from scratch, pass its original test suite
- **Usage tutorial** — Teach how to use/extend the project's APIs with inline verification

### Diagram Modes

During generation, you choose one of three diagram approaches:

1. **TUI** — ASCII art / Unicode box-drawing, zero dependencies
2. **SVG (Excalidraw)** — Professional vector diagrams via bundled `excalidraw-diagram` skill
3. **Mermaid** — Fenced code blocks in markdown cells

## Plugin Structure

```
reimpl-tutorial-plugin/
├── .claude-plugin/plugin.json
├── README.md
└── skills/
    ├── reimpl-tutorial/
    │   ├── SKILL.md
    │   ├── evals/
    │   ├── prompts/
    │   ├── scripts/
    │   └── templates/
    └── excalidraw-diagram/
        ├── SKILL.md
        └── references/
            └── _excalidraw_to_svg.js
```

## License

MIT
