---
name: zentao
description: Read-only access to 禅道 (ZenTao) open-source PMS via its legacy `.json` URL + session-cookie API. Use when the user mentions 禅道 / zentao / 查bug / bug统计 / bug报告 / 我的项目 / bug轮询 / 项目管理 (and the project is tracked in ZenTao). Lists projects, lists/filters bugs, builds stats reports by assignee, polls for bug changes.
---

# Zentao (禅道开源版) skill

Wraps the legacy session-based `.json` endpoints of ZenTao (works on community
editions whose REST v1 is not enabled). Use the bundled CLI rather than
constructing HTTP calls yourself.

## When to use

- User asks to list / stat / report on bugs in a ZenTao project
- User wants to know "谁身上有多少 bug"，severity 分布，待处理数量
- User wants to poll a project for new/resolved/reassigned bugs
- User wants the list of projects they belong to, or to map accounts → real names

Not in scope on this API (legacy `.json` endpoints are read-oriented):

- Creating / resolving / closing bugs and tasks — those use ZenTao's form POSTs
  which vary per version; not implemented here. If the instance supports REST
  v1 (`/api.php/v1/`) and you need writes, a v1-based client is a separate
  concern.

## One-time setup

Copy `${CLAUDE_PLUGIN_ROOT}/skills/zentao/config.example.yaml` to
`~/.claude/zentao/config.yaml` and fill in `url`, `account`, `password`.

The CLI looks for config in this order:
1. `--config <path>` flag
2. `$ZENTAO_CONFIG` env var
3. `~/.claude/zentao/config.yaml`
4. `${CLAUDE_PLUGIN_ROOT}/skills/zentao/config.yaml` (in-tree fallback for dev)

Optional keys: `default_project`, `verify_ssl` (default true), `timeout`
(seconds, default 30).

Token (session id) is cached at `~/.claude/.cache/zentao_token.json` for 2h
and auto-refreshed if the server returns a login redirect.

## Usage

All operations go through the CLI. Pass `--json` for machine-readable output
when downstream chaining, `--raw` to get the full upstream payload.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/zentao/scripts/cli.py" <command> [args...] [--json|--raw]
```

### Commands

- `whoami` — verify auth, print current user profile
- `projects [--all]` — list projects I'm a member of (default: exclude `closed`)
- `bugs --project ID [--status active|resolved|closed|all] [--assigned-to ACC] [--limit N]`
  — list bugs of a project; severity/status/type/resolution rendered in Chinese
- `bug ID --project PID [--limit N]` — show one bug's detail (scans the
  project's bug list; there's no global bug endpoint in the legacy API)
- `bug-report --project ID [--limit N]` — markdown stats of **active** bugs
  grouped by assignee with severity breakdown
- `poll-bugs --project ID [--interval 60]` — long-running; on each tick emits
  NDJSON events for `new` / `resolved_or_closed` / `reassigned` bugs
- `users [--project ID]` — dump the `account → realname` map (borrowed from
  a project's bug payload)

### Output

Default: concise human-readable summary (Chinese labels). With `--json`: a
structured summary suitable for chaining. With `--raw`: the entire upstream
inner payload including pager, teamMembers, etc.

## Working patterns

1. **Discovery** — start with `whoami` + `projects` to map the workspace.
   Cache the active project id as `default_project` in config.yaml so
   subsequent commands don't need `--project`.
2. **Bug triage report** — `bug-report --project X` gives a Slack-ready
   markdown block showing who has how many active bugs split by severity.
3. **Detail drill-down** — `bug ID --project PID` cleans ZenTao's HTML
   `steps` field (strips `<br>`, tags, replaces `{image.png}` placeholders
   with `[图片]`). Good for summarizing reproduction steps.
4. **Live monitoring** — `poll-bugs --project X --interval 60` prints an
   NDJSON event stream of bug changes. Feed into whatever notifier.

## API gotchas (important for any custom calls)

- `.json` suffix is mandatory — ZenTao returns HTML without it.
- Auth is `Cookie: zentaosid=<token>` where the token is **from the login
  response body** (`res.user.token`), not the `Set-Cookie` header's
  auto-assigned value. Mixing them fails silently with a login redirect.
- Response envelope: `{status, data, md5}` where `data` is often a **JSON
  string** that needs a second `json.loads`.
- Collections (`bugs`, `projects`, `users`) can be **list** OR **object keyed
  by id**, depending on version/entry. Normalize with the `as_list()` helper
  in `zentao.py`.
- Pagination is Cookie-based: `pagerProjectBug=1000` sets page size for the
  project-bug entry. The CLI handles this via `--limit`.
- Bug `severity` / `pri` are string digits `'1'`-`'4'` (not ints).
- `assignedTo` / `openedBy` are **account names**; use the `users` map
  embedded in the same response to get display names.
- `steps` is HTML with `{image.png}` placeholders — use `clean_html()`.
- Session expires; the CLI auto-refreshes once on login-redirect.

## Reference

- `references/endpoints.md` — full URL table and response shape
- `references/fields.md` — field types, enums, display mappings

## Failure modes

- Login 401 / "status: fail" → bad credentials or account locked
- Response contains `locate: .../user-login...` → session expired; the CLI
  silently re-logins and retries once
- `data._raw` key in returned dict → server returned non-JSON (usually an
  HTML error page); check URL/auth
- `UnicodeEncodeError` on Windows console → the CLI auto-reconfigures
  stdout/stderr to UTF-8; if you bypass the CLI, set `PYTHONIOENCODING=utf-8`
