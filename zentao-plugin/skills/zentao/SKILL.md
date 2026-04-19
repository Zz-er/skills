---
name: zentao
description: Manage 禅道 (ZenTao) open-source PMS via its REST v1 API. Use when the user mentions 禅道 / zentao / 提bug / 查任务 / 指派任务 / 我的待办 / 创建需求 / 项目管理 (and the project is tracked in ZenTao). Supports full read/write across products, projects, executions, stories, tasks, bugs, todos, users.
---

# Zentao (禅道开源版) skill

Wraps the REST v1 API exposed by `zentaopms` at `<host>/api.php/v1/`. Use the bundled CLI rather than constructing HTTP calls yourself.

## When to use

- 用户提到禅道里的任何资源：bug / 任务 / 需求 / 产品 / 项目 / 执行 / 待办
- AI team 进行项目管理：批量建任务、推进状态、查看分配、汇报进度
- 不要用于：非禅道实例的项目管理工具（jira/linear/teambition 等走各自 skill）

## One-time setup

Copy `${CLAUDE_PLUGIN_ROOT}/skills/zentao/config.example.yaml` to `~/.claude/zentao/config.yaml` and fill it in.
Required: `url`, `account`, `password`. Optional: `default_product`, `default_project`, `default_execution`.

The CLI looks for config in this order:
1. `--config <path>` flag
2. `$ZENTAO_CONFIG` env var
3. `~/.claude/zentao/config.yaml`
4. `${CLAUDE_PLUGIN_ROOT}/skills/zentao/config.yaml` (in-tree fallback for dev)

Token is cached at `~/.claude/.cache/zentao_token.json` and auto-refreshed on 401.

## Usage

All operations go through the CLI. **Always pass `--json` for machine-readable output** when downstream chaining; omit for pretty text.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/zentao/scripts/cli.py" <command> [args...] [--json]
```

### Common commands

Discovery / read:
- `whoami` — verify auth
- `products [--status all|normal|closed]`
- `projects [--status]`
- `executions [--project ID]`
- `stories --product ID [--status unclosed]`
- `bugs --product ID [--status active|resolved|closed]` or `bugs --execution ID` or `bugs --project ID`
- `tasks [--execution ID] [--status all|wait|doing|done]` (no execution = my tasks)
- `todos [--status all|wait|doing|done]`
- `get bug|task|story|product|project|execution|todo <id>`
- `users [--full]`

Write — create:
- `create-bug --product ID --title T --steps "..." [--severity 3 --pri 3 --type codeerror --assigned-to user --execution ID]`
- `create-task --execution ID --name N --type devel --assigned-to user --est-started YYYY-MM-DD --deadline YYYY-MM-DD [--estimate 4 --story ID --pri 3 --desc "..."]`
- `create-story --product ID --title T --spec "..." [--pri 3 --category feature --estimate 8 --reviewer user]`
- `create-todo --name N [--date YYYY-MM-DD --pri 3 --desc "..."]`
- `create-execution --project ID --name N --begin DATE --end DATE [--PM user]`
- `create-project --name N --begin DATE --end DATE --products 1,2 [--model scrum]`
- `batch-create-tasks --execution ID --file tasks.json` (file: `[{"name","type","assignedTo","estStarted","deadline","estimate?","pri?","desc?","story?"}, ...]`)

Write — transitions (all `--yes` required for destructive):
- `assign-bug <id> --to user [--comment "..."]`
- `resolve-bug <id> --resolution fixed|postponed|willnotfix|bydesign|duplicate|external|notrepro [--build ID --comment "..."]`
- `close-bug <id> [--comment]`
- `activate-bug <id> [--assigned-to user --comment]`
- `confirm-bug <id> [--assigned-to user]`
- `assign-task <id> --to user [--left N --comment]`
- `start-task <id> [--consumed N --left N --comment]`
- `finish-task <id> --consumed N [--real-started DATE --finished-date DATE --comment]`
- `close-task <id> [--comment]`
- `activate-task <id> [--left N --assigned-to user]`
- `assign-story <id> --to user [--comment]`
- `close-story <id> --reason done|subdivided|duplicate|postponed|willnotdo|bydesign|cancel [--duplicate-id N --comment]`
- `review-story <id> --result pass|reject|revert --reviewed-date YYYY-MM-DD [--comment]`
- `finish-todo <id>`
- `activate-todo <id>`

Write — update / delete:
- `update bug|task|story|product|project|execution|todo <id> --field key=value [--field ...]`
- `delete bug|task|story|todo <id> --yes` (admin scopes for product/project/execution)

### Output

Default: a concise human-readable summary. With `--json`, the raw API response. With `--raw`, the full untrimmed JSON including pagination.

## Working pattern for AI team project management

1. Start by `whoami` + `products` + `projects` to map the workspace.
2. Cache `default_product` / `default_execution` in `config.yaml` after the user picks the active context, so subsequent commands don't need ids.
3. For "plan a sprint": `create-execution`, then `batch-create-tasks` from a JSON file generated from the discussion.
4. For "推进进度": `tasks --execution X --status doing`, then `start-task` / `finish-task` per item.
5. For "提 bug": `create-bug` with at minimum title, steps, severity, type. Default severity=3, pri=3, type=codeerror, openedBuild=trunk.
6. Destructive ops (`delete-*`) still require `--yes` flag to the CLI as a guardrail against typos; close/resolve do not.

## Reference docs

- `references/endpoints.md` — full v1 endpoint table
- `references/fields.md` — required/optional fields and enum values per resource

## Failure modes to know

- 401 → token expired; CLI auto-refreshes once. If still 401, password changed.
- 400 "Need product/execution/project id" → required path/query missing; check resource expects an id.
- "needNotReview" / "reviewing" — story creation auto-flips to `reviewing` if `reviewer` is set; pass `--no-reviewer` to keep `active`.
- Some endpoints (effort/feedback/pipelines) may be 404 on community edition; surface the error rather than retry.
- Date fields use `YYYY-MM-DD`; datetime fields `YYYY-MM-DD HH:MM:SS`; time-of-day fields like task `begin/end` are `HHMM` (no colon).
