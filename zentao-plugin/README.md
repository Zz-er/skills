# zentao-plugin

A Claude Code plugin that wraps 禅道 (ZenTao) open-source PMS via its REST v1 API. One skill (`zentao`) gives Claude full read/write across products, projects, executions, stories, tasks, bugs, todos, and users — ideal for AI teams doing project management.

## Skills Included

| Skill | Description |
|-------|-------------|
| **zentao** | Create/read/update/transition ZenTao resources through a bundled Python CLI. Uses the `/api.php/v1/` REST endpoint with token auth. |

## Installation

### Via Claude Code Plugin Marketplace (recommended)

```bash
claude plugin marketplace add https://github.com/Zz-er/skills
claude plugin install zentao
```

### Manual Installation

```bash
git clone https://github.com/Zz-er/skills.git ~/.claude/local-plugins/_skills_repo
ln -s ~/.claude/local-plugins/_skills_repo/zentao-plugin \
      ~/.claude/local-plugins/zentao
```

## Configuration

Copy the example config and fill in your ZenTao credentials:

```bash
mkdir -p ~/.claude/zentao
cp <plugin-dir>/skills/zentao/config.example.yaml ~/.claude/zentao/config.yaml
$EDITOR ~/.claude/zentao/config.yaml
```

Minimum config:

```yaml
url: https://zentao.example.com
account: your_account
password: your_password
# Optional defaults so commands don't need ids each time:
# default_product: 1
# default_execution: 1
```

Config lookup order: `--config` flag → `$ZENTAO_CONFIG` → `~/.claude/zentao/config.yaml` → in-tree `skills/zentao/config.yaml`.

Token is cached at `~/.claude/.cache/zentao_token.json` (2h TTL, auto-refreshed on 401).

## Usage

The skill triggers automatically on phrases like:

- "帮我在禅道提个bug"
- "查一下我在禅道的待办"
- "给 X 指派这个任务"
- "批量创建这个迭代的任务"

Or invoke directly: `/zentao`

Underneath, Claude calls:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/zentao/scripts/cli.py" <command> [args...] [--json]
```

### Command surface

- **Read**: `whoami`, `products`, `projects`, `executions`, `stories`, `bugs`, `tasks`, `todos`, `users`, `get <kind> <id>`
- **Create**: `create-bug`, `create-task`, `create-story`, `create-todo`, `create-execution`, `create-project`, `batch-create-tasks`
- **Transitions**: `assign-bug`, `resolve-bug`, `close-bug`, `activate-bug`, `confirm-bug`, `assign-task`, `start-task`, `finish-task`, `close-task`, `activate-task`, `assign-story`, `close-story`, `review-story`, `finish-todo`, `activate-todo`
- **Mutate**: `update <kind> <id> --field k=v`, `delete <kind> <id> --yes`

Full field tables and endpoint reference live in `skills/zentao/references/`.

## Plugin Structure

```
zentao-plugin/
├── .claude-plugin/plugin.json
├── README.md
└── skills/
    └── zentao/
        ├── SKILL.md
        ├── config.example.yaml
        ├── references/
        │   ├── endpoints.md
        │   └── fields.md
        └── scripts/
            ├── cli.py
            └── zentao.py
```

## Requirements

- Python 3.8+ (uses only stdlib `urllib`; PyYAML optional for richer config parsing)
- A reachable ZenTao open-source instance with REST v1 enabled

## License

MIT
