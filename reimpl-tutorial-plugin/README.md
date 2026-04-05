# reimpl-tutorial-plugin

A Claude Code plugin that generates "from zero to expert" tutorials by reimplementing projects in Jupyter notebooks. Includes the `excalidraw-diagram` skill for SVG diagram generation — no additional dependencies needed.

## Skills Included

| Skill | Description |
|-------|-------------|
| **reimpl-tutorial** | Deeply analyze a project and rebuild it from scratch in Jupyter notebooks, with cognitive ordering, rigorous verification, and full derivations. |
| **excalidraw-diagram** | Generate Excalidraw JSON diagrams and convert them to SVG for embedding in notebooks. Bundled as a dependency — no separate installation required. |

## Installation

### Method 1: Local Plugin (recommended)

Clone this repo and symlink the plugin directory:

```bash
# Clone the repo
git clone https://github.com/Zz-er/skills.git ~/.claude/local-plugins/_skills_repo

# Create symlink so Claude Code discovers the plugin
ln -s ~/.claude/local-plugins/_skills_repo/reimpl-tutorial-plugin \
      ~/.claude/local-plugins/reimpl-tutorial
```

Verify installation — run `claude` and type `/reimpl-tutorial`. The skill should appear in the list.

### Method 2: Project-level Installation

If you only need the skill for a specific project:

```bash
# In your project root
mkdir -p .claude/skills
cp -r path/to/reimpl-tutorial-plugin/skills/reimpl-tutorial .claude/skills/
cp -r path/to/reimpl-tutorial-plugin/skills/excalidraw-diagram .claude/skills/
```

## Usage

In Claude Code, the skill triggers automatically on phrases like:

- "write a tutorial for [project]"
- "reimpl [project] from scratch"
- "create notebooks explaining [project]"
- "手撕项目" / "从0开始"

Or invoke directly: `/reimpl-tutorial`

### Diagram Mode Selection

During tutorial generation, you'll be asked to choose a diagram mode:

1. **TUI** — ASCII art, zero dependencies
2. **SVG (Excalidraw)** — Professional vector diagrams (uses bundled `excalidraw-diagram` skill)
3. **Mermaid** — Code-based diagrams in markdown cells

### Tutorial Types

The skill supports two modes:

- **Reimplementation tutorial** — Rebuild the project from scratch, pass its original test suite
- **Usage tutorial** — Teach how to use/extend the project's APIs with inline verification

## Plugin Structure

```
reimpl-tutorial-plugin/
├── .claude-plugin/plugin.json        # Plugin metadata
├── README.md                         # This file
└── skills/
    ├── reimpl-tutorial/              # Main tutorial generation skill
    │   ├── SKILL.md                  # Skill instructions
    │   ├── evals/                    # Test cases
    │   ├── prompts/                  # Analysis & derivation prompts
    │   ├── scripts/                  # Test extraction & runner
    │   └── templates/                # Notebook structure templates
    └── excalidraw-diagram/           # Bundled diagram skill
        ├── SKILL.md                  # Diagram generation instructions
        └── references/               # JSON schema, templates, converter
            └── _excalidraw_to_svg.js # Excalidraw → SVG converter
```

## Updating

Since the local plugin is symlinked to the git repo, updating is just:

```bash
cd ~/.claude/local-plugins/_skills_repo
git pull
```

## License

MIT
