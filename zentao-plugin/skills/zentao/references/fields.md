# ZenTao field reference (legacy `.json` API)

## Project (`/my-project.json` → `projects[]`)

| Field | Type | Notes |
|---|---|---|
| `id` | string digit | Project id (pass to bug/task endpoints) |
| `name` | string | Display name |
| `type` | enum | `waterfall` / `sprint` / `agileplus` / `kanban` |
| `status` | enum | `wait` / `doing` / `suspended` / `closed` |
| `begin` / `end` | string `YYYY-MM-DD` | |
| `PM` | string | Account of the PM (look up via `users` map of any bug call) |
| `openedBy` / `openedDate` | string | |
| `closedBy` / `closedDate` | string | |

The CLI filters out `status=closed` by default; pass `--all` to include.

## Bug (`/project-bug-{id}.json` → `bugs[]`)

| Field | Type | Notes |
|---|---|---|
| `id` | string digit | Bug id |
| `title` | string | |
| `severity` | string `'1'`–`'4'` | See severity table below; **string, not int** |
| `pri` | string `'1'`–`'4'` | Priority, same convention |
| `status` | enum | `active` / `resolved` / `closed` |
| `type` | enum | See type table |
| `assignedTo` | string | Account; use `users` map for display name. On closed bugs ZenTao may write the literal `Closed`. |
| `openedBy` / `openedDate` | string | |
| `resolvedBy` / `resolvedDate` | string | |
| `resolution` | enum | See resolution table |
| `steps` | HTML string | Reproduction steps with `{image.png}` placeholders; run through `clean_html()` before display |
| `product` / `project` / `execution` | string digit | |

## Enum tables

### Severity (`severity`)

| Code | Label | zh |
|---|---|---|
| `1` | Critical | 严重 |
| `2` | Major | 主要 |
| `3` | Minor | 次要 |
| `4` | Trivial | 轻微 |

### Bug status

| Code | zh |
|---|---|
| `active` | 激活 |
| `resolved` | 已解决 |
| `closed` | 已关闭 |

### Bug type

| Code | zh |
|---|---|
| `codeerror` | 代码错误 |
| `config` | 配置相关 |
| `install` | 安装部署 |
| `security` | 安全相关 |
| `performance` | 性能问题 |
| `standard` | 标准规范 |
| `automation` | 测试脚本 |
| `designdefect` | 设计缺陷 |
| `others` | 其他 |

Instance-specific variants (e.g. `newfeature`, `trackthru`) may appear —
the CLI displays the raw key when not in the map.

### Resolution

| Code | zh |
|---|---|
| `bydesign` | 设计如此 |
| `duplicate` | 重复Bug |
| `external` | 外部原因 |
| `fixed` | 已解决 |
| `notrepro` | 无法重现 |
| `postponed` | 延期处理 |
| `willnotfix` | 不予解决 |
| `tostory` | 转为需求 |

Some instances use plural `tostorys`; displayed raw if unmapped.

## Users map (`users` inside bug/task responses)

Object of `{ account: realname }`. Always merge responses rather than
relying on a single entry — not every response includes every user.
Empty-string keys (`"": ""`) are sentinels from ZenTao and should be
filtered.

## Task (`/project-task-{id}.json` → `tasks[]`) — quick reference

| Field | Type | Notes |
|---|---|---|
| `id` | string digit | |
| `name` | string | |
| `status` | enum | `wait` / `doing` / `done` / `pause` / `cancel` / `closed` |
| `pri` | string `'1'`–`'4'` | |
| `assignedTo` | string | |
| `estimate` / `consumed` / `left` | string float | Hours |
| `estStarted` / `realStarted` / `deadline` / `finishedDate` | date | |

## Story (`/project-story-{id}.json` → `stories[]`)

| Field | Type | Notes |
|---|---|---|
| `id` | string digit | |
| `title` | string | |
| `status` | enum | `draft` / `active` / `changing` / `reviewing` / `closed` |
| `pri` | string `'1'`–`'4'` | |
| `stage` | enum | `wait` / `planned` / `projected` / `developing` / `developed` / `testing` / `tested` / `verified` / `released` / `closed` |
| `assignedTo` | string | |
