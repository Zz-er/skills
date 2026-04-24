---
name: gitlab
description: Read and write GitLab via REST v4 (CE 13.3+ compatible). Use when the user mentions GitLab / MR / 合并请求 / merge request / 拉 diff / 代码评审取 commit / 分支批量创建 / 看 commit 变更 / 看 MR 列表 / 给 MR 评论 / 给 commit 评论 / 查项目 / 查分支 / 看 compare. Lists projects and groups, lists/searches branches and commits, fetches commit and compare diffs, reads file contents, lists/finds/creates/merges/comments merge requests and commit comments.
---

# GitLab (REST v4) skill

Wraps GitLab's REST v4 API via `PRIVATE-TOKEN` header. Tested against self-hosted
**GitLab CE 13.3+** as well as gitlab.com; avoids newer parameters
(`order_by=updated`, compare `straight=true`, etc.) that 13.3 rejects.

Source of truth: a Python port of [`modou-utils/src/main/gitlab.ts`](../../../modou-utils/src/main/gitlab.ts).

## When to use

**Read**

- List projects I can see (`projects`) or filter by group path (`projects --group mygroup`)
- List groups I'm a member of (`groups`)
- List branches / commits of a project
- Fetch the **diff of a commit** (`diff --sha ...`) — the main input for AI code review
- Compare two refs / branches (`compare --from main --to feat-x`)
- Read a file's raw content at a ref (`file --path src/util.ts --ref main`)
- List opened MRs (`mrs` — global, or filtered by `--project` / `--group`)
- Find a specific MR by source/target branch (`find-mr --source ... --target ...`)

**Write** (each requires `--yes` as a guardrail)

- Create / delete a branch
- Create a merge request (`create-mr`)
- Merge an MR (`merge-mr --iid ... --yes`)
- Comment on a commit or MR

## One-time setup

```bash
mkdir -p ~/.claude/gitlab
cp "${CLAUDE_PLUGIN_ROOT}/skills/gitlab/config.example.yaml" ~/.claude/gitlab/config.yaml
# edit url + token + (optional) default_project / default_groups
pip install -r "${CLAUDE_PLUGIN_ROOT}/skills/gitlab/requirements.txt"
```

Generate a PAT at `<your gitlab>/-/profile/personal_access_tokens` with at least
the `api` scope. For read-only use the `read_api` scope is enough.

Config lookup order:
1. `--config <path>`
2. `$GITLAB_CONFIG`
3. `~/.claude/gitlab/config.yaml`
4. `${CLAUDE_PLUGIN_ROOT}/skills/gitlab/config.yaml` (in-tree fallback)

## Usage

All operations go through the CLI. Pass `--json` for machine-readable output
when chaining, `--raw` for the full upstream payload.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/gitlab/scripts/cli.py" <command> [args...] [--json|--raw]
```

### Commands

| Command | Purpose |
|---------|---------|
| `whoami` | Validate the token; print the current user |
| `projects [--search S] [--group G ...]` | Projects I'm a member of (or scoped to groups) |
| `groups` | Groups I can see |
| `branches --project PID` | Up to 100 branches of a project |
| `commits --project PID --branch B [--limit N]` | Latest commits on a branch |
| `commit --project PID --sha SHA` | One commit's metadata |
| `diff --project PID --sha SHA` | **Files changed + unified diff** — primary code-review input |
| `compare --project PID --from F --to T` | Compare two refs (`{commits, diffs}`) |
| `file --project PID --path P --ref R` | Raw file content at a ref |
| `mrs [--project PID \| --group G ...]` | Opened MRs — global / project / group |
| `find-mr --project PID --source S --target T` | Locate a specific MR |
| `create-branch --project PID --name N --ref R` | Branch off an existing ref |
| `delete-branch --project PID --name N --yes` | Delete a branch |
| `create-mr --project PID --source S --target T --title T [--description D] [--remove-source]` | Open a new MR |
| `merge-mr --project PID --iid N [--remove-source] --yes` | Accept a merge request |
| `comment-commit --project PID --sha SHA --body TEXT --yes` | Post a plain comment on a commit |
| `comment-mr --project PID --iid N --body TEXT --yes` | Post a plain note on an MR |

### Output modes

- **default** — human-readable summary with Chinese labels where helpful
- **`--json`** — structured JSON summary (smaller than `--raw`; shape specified in `references/fields.md`)
- **`--raw`** — full upstream response body, pretty-printed

### The `--project` argument accepts both forms

- Numeric id: `--project 42`
- URL path: `--project mygroup/subgroup/myrepo`

Paths get URL-encoded exactly once; numeric ids pass through.

### Writes require `--yes`

Every destructive or side-effecting command (`delete-branch`, `merge-mr`, the two
`comment-*` commands) requires `--yes`. This is the plugin's only guardrail —
agents should confirm with the user before adding the flag.

## Working patterns

### Code review → fetch diff → feed to reviewer

```bash
python cli.py diff --project 42 --sha abc1234 --json > /tmp/diff.json
# then pipe diff.json into your review prompt
```

### Bulk branch audit

```bash
python cli.py branches --project mygroup/myrepo --json | jq '.items[] | select(.protected==false) | .name'
```

### Find the MR that corresponds to a feature branch

```bash
python cli.py find-mr --project mygroup/myrepo --source feat-x --target main --json
```

### Merge after approval

```bash
# list first
python cli.py mrs --project 42
# then once confirmed:
python cli.py merge-mr --project 42 --iid 17 --remove-source --yes
```

## CE 13.3 compatibility notes

This library intentionally avoids the following newer GitLab parameters because
CE 13.3 either rejects them with 400 or silently ignores them:

| Newer param | Since | Replacement |
|-------------|-------|-------------|
| `order_by=updated` on `/projects` | 14.x | `order_by=last_activity_at` |
| `straight=true` on `/compare` | 14.x | leave unset — three-dot (merge-base) is the 13.3 default |
| `scope=all` on `/projects/:id/merge_requests` | 14.x | pass only `state=opened`, filter client-side |
| `assignee_id=None` | 14.x | omit the param to mean "any assignee" |

If you know you're talking to a modern gitlab.com / 16.x instance and want the
newer behaviors, open `gitlab.py` and adjust — the methods are only ~10 lines each.

## Error handling

HTTP errors are translated before being raised, so `GitLabError.args[0]` is
always a short, user-readable string:

| HTTP / transport | Translated message |
|------------------|--------------------|
| timeout | 网络连接超时 |
| connection refused / DNS | 网络连接失败，请检查网络设置 |
| 401 | Token 已过期，请重新配置 |
| 403 | 无权访问该项目 |
| 4xx / 5xx | 请求失败 ({status}): {server message} |

The CLI prints `error: <translated>` to stderr and exits 1.

## Things this skill does NOT do

- **Pipelines / CI**. No `/projects/:id/pipelines` endpoints wrapped; add if needed.
- **Issues**. modou-utils uses Zentao for bug tracking; the issues API isn't wrapped here.
- **Webhooks / webhook events**. Stateless CLI only; no server-side listeners.
- **OAuth or session-cookie auth**. PAT (PRIVATE-TOKEN) only — the simplest auth mode that works for self-hosted instances.
- **Repository push / pull**. Use `git` itself for that.

## References

- `references/endpoints.md` — all REST v4 endpoints this plugin hits (path, method, params, 13.3 notes)
- `references/fields.md` — typical response field shapes for each resource
