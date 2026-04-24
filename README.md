# Skills

A Claude Code plugin marketplace containing productivity tools for knowledge management, deep learning, and project management.

## Installation

```bash
claude plugin marketplace add https://github.com/Zz-er/skills
```

Then install the plugins you need:

```bash
claude plugin install wiki-tools
claude plugin install reimpl-tutorial
claude plugin install zentao
claude plugin install gitlab
```

## Plugins

### wiki-tools

A personal knowledge base system inspired by Andrej Karpathy's LLM Wiki pattern. Maintains a persistent, cross-referenced collection of markdown pages.

**Skills:**

| Skill | Description |
|-------|-------------|
| `/wiki-init` | Initialize a new wiki directory with full structure, schema, and seed files |
| `/wiki-query` | Search and retrieve existing knowledge from the wiki |
| `/wiki-update` | Add new pages or update existing wiki content |
| `/wiki-ingest` | Import a project or tutorial into the wiki, extracting concepts and entities |
| `/wiki-improve` | Review and apply accumulated skill improvement suggestions |

**Quick start:**

```
/wiki-init ~/my-wiki
/wiki-query "transformer attention mechanism"
/wiki-update
/wiki-ingest /path/to/project
```

See [llm-wiki-plugin/README.md](llm-wiki-plugin/README.md) for details.

### reimpl-tutorial

Generate "from zero to expert" tutorials by deeply analyzing a project and reimplementing it from scratch in Jupyter notebooks. Teaches how systems work by rebuilding them step-by-step in cognitive learning order.

**Skills:**

| Skill | Description |
|-------|-------------|
| `/reimpl-tutorial` | Analyze a project and generate incremental reimplementation notebooks |
| `/excalidraw-diagram` | Generate Excalidraw diagrams and export as SVG for notebook embedding |

**Workflow:**

1. Deep analysis of the target project
2. Cognitive ordering of features (foundation -> core -> advanced)
3. Incremental notebook generation with theory, implementation, and verification
4. Integration testing and summary generation
5. Optional wiki knowledge sync (if wiki-tools is installed)

See [reimpl-tutorial-plugin/README.md](reimpl-tutorial-plugin/README.md) for details.

### zentao

Wraps 禅道 (ZenTao) open-source PMS via its REST v1 API so AI teams can manage products, projects, executions, stories, tasks, bugs, and todos directly from Claude Code.

**Skills:**

| Skill | Description |
|-------|-------------|
| `/zentao` | Full read/write CLI: discovery, create, transition, update, delete across all core ZenTao resources |

**Quick start:**

```
# one-time config
mkdir -p ~/.claude/zentao
cp zentao-plugin/skills/zentao/config.example.yaml ~/.claude/zentao/config.yaml
# then just talk to Claude: "帮我在禅道提个bug" / "查一下我的待办"
```

See [zentao-plugin/README.md](zentao-plugin/README.md) for details.

### gitlab

Wraps GitLab's REST v4 API (`PRIVATE-TOKEN` auth) so AI agents can list
projects, fetch commit/compare diffs for code review, and manage merge requests
and branches. Tested against self-hosted CE 13.3+ and gitlab.com.

**Skills:**

| Skill | Description |
|-------|-------------|
| `/gitlab` | Full read/write CLI: projects, groups, branches, commits + diffs, file content, merge requests (list / find / create / merge / comment), commit comments |

**Quick start:**

```
# one-time config
mkdir -p ~/.claude/gitlab
cp gitlab-plugin/skills/gitlab/config.example.yaml ~/.claude/gitlab/config.yaml
# fill in url + personal access token
pip install -r gitlab-plugin/skills/gitlab/requirements.txt
# then just talk to Claude: "拉一下 commit abc1234 的 diff" / "合并 MR !17"
```

See [gitlab-plugin/README.md](gitlab-plugin/README.md) for details.

## Plugin Integration

When both plugins are installed, they work together:

- `/reimpl-tutorial` queries the wiki before analysis to leverage existing knowledge
- Completed tutorials are automatically synced back to the wiki via `/wiki-ingest`

## License

MIT
