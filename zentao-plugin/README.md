# zentao-plugin

A Claude Code plugin for 禅道 (ZenTao) open-source PMS. Uses the legacy
session-cookie `.json` URL API (works on community editions without needing
REST v1 enabled). Read-oriented: list projects, list/filter bugs, generate
bug stats reports by assignee, and poll for bug changes.

## Skills included

| Skill | Description |
|-------|-------------|
| **zentao** | Query ZenTao via `/user-login.json` + `/<entry>.json` with `Cookie: zentaosid=<token>`. Bundled Python CLI covers projects, bugs, bug-reports, bug-polling, and user mapping. |

## Installation

### Via Claude Code plugin marketplace

```bash
claude plugin marketplace add https://github.com/Zz-er/skills
claude plugin install zentao
```

### Manual installation

```bash
git clone https://github.com/Zz-er/skills.git ~/.claude/local-plugins/_skills_repo
ln -s ~/.claude/local-plugins/_skills_repo/zentao-plugin \
      ~/.claude/local-plugins/zentao
```

## Configuration

```bash
mkdir -p ~/.claude/zentao
cp <plugin-dir>/skills/zentao/config.example.yaml ~/.claude/zentao/config.yaml
$EDITOR ~/.claude/zentao/config.yaml
```

Minimum:

```yaml
url: http://zentao.example.com      # base URL, no trailing slash
account: your_account
password: your_password
# Optional:
# default_project: 790
# verify_ssl: false    # for self-signed / plain HTTP internal hosts
# timeout: 15
```

Config lookup order: `--config` flag → `$ZENTAO_CONFIG` → `~/.claude/zentao/config.yaml` → in-tree `skills/zentao/config.yaml`.

Session token is cached at `~/.claude/.cache/zentao_token.json` (2h TTL, auto-refreshed on login-redirect).

## Usage

The skill triggers on phrases like:

- "查一下 Sprint9 的 bug 情况"
- "给我出一份 bug 统计"
- "监控项目 790 的 bug 变更"
- "禅道里我负责的项目有哪些"

Or invoke directly via `/zentao`.

Under the hood Claude runs:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/zentao/scripts/cli.py" <command> [args] [--json|--raw]
```

### Command surface

- `whoami` — verify auth
- `projects [--all]` — projects I'm a member of
- `my-bugs [--status active|resolved|closed|all]` — bugs assigned to me (server-filtered)
- `bugs --project ID [--status active|resolved|closed|all] [--assigned-to ACC]`
- `bug ID --project PID` — single bug with cleaned HTML steps
- `bug-report --project ID` — markdown stats by assignee × severity
- `poll-bugs --project ID [--interval 60]` — NDJSON event stream
- `users [--project ID]` — account → realname map
- `comment-bug ID --body TEXT --yes` — append a comment to a bug (wraps the
  dangerous `bug-edit` round-trip so required fields like `product` survive)

See `skills/zentao/references/` for URL table, field types, and enum labels.

## Plugin structure

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

- Python 3.8+ (stdlib only; PyYAML optional)
- A reachable ZenTao open-source instance reachable at `<url>/user-login.json`

## Scope

This plugin is **read-only**. Creating, resolving, or transitioning
bugs/tasks via the legacy `.json` API relies on per-version form POSTs that
are brittle to wrap. If the target instance exposes REST v1
(`/api.php/v1/tokens`), a separate v1-based client is the right tool for
writes.

## License

MIT
