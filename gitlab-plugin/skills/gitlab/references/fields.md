# GitLab resource shapes

The fields this plugin **actually uses**. GitLab returns more fields than these;
`--raw` on any command shows everything. `--json` summaries use the subset
below.

## User (`/user`)

```json
{"id": 1, "username": "alice", "name": "Alice", "email": "alice@example.com"}
```

## Group (`/groups`)

```json
{"id": 42, "name": "Backend", "full_path": "mygroup/backend"}
```

## Project (`/projects`, `/groups/:g/projects`)

```json
{
  "id": 42,
  "name": "my-repo",
  "name_with_namespace": "MyGroup / My Sub / my-repo",
  "path_with_namespace": "mygroup/mysub/my-repo",
  "description": "short text or null",
  "web_url": "https://gitlab.example.com/mygroup/mysub/my-repo",
  "default_branch": "main"
}
```

## Branch (`/projects/:id/repository/branches`)

```json
{
  "name": "main",
  "protected": true,
  "commit": {
    "id": "abc1234567890abcdef...",
    "short_id": "abc1234",
    "title": "feat: add lastItem",
    "authored_date": "2026-04-24T10:00:00.000+08:00"
  }
}
```

## Commit (`/projects/:id/repository/commits/:sha`)

```json
{
  "id": "abc1234567890abcdef1234567890abcdef123456",
  "short_id": "abc1234",
  "title": "feat: add lastItem helper",
  "message": "feat: add lastItem helper\n\nDetails ...\n",
  "author_name": "张三",
  "author_email": "zhang@example.com",
  "authored_date": "2026-04-24T10:00:00.000+08:00",
  "committed_date": "2026-04-24T10:00:01.000+08:00",
  "web_url": "https://gitlab.example.com/.../commit/abc1234..."
}
```

## Commit diff item (`/projects/:id/repository/commits/:sha/diff`)

Returns an **array** — one item per file touched:

```json
[
  {
    "old_path": "src/util.ts",
    "new_path": "src/util.ts",
    "a_mode": "100644",
    "b_mode": "100644",
    "new_file": false,
    "renamed_file": false,
    "deleted_file": false,
    "diff": "@@ -0,0 +1,3 @@\n+export function lastItem...\n"
  }
]
```

Special flags — only **one of** `new_file` / `renamed_file` / `deleted_file` is
true per entry; all false means "modified".

## Compare result (`/projects/:id/repository/compare`)

```json
{
  "commits": [ { Commit }, { Commit }, ... ],
  "diffs":   [ { CommitDiffItem }, ... ]
}
```

## Merge Request (`/merge_requests`, `/projects/:id/merge_requests`, ...)

```json
{
  "iid": 17,
  "title": "feat: add lastItem",
  "description": "text or null",
  "state": "opened",
  "source_branch": "feat-lastitem",
  "target_branch": "main",
  "author": {
    "name": "张三",
    "username": "zhang",
    "avatar_url": "https://..."
  },
  "created_at": "2026-04-24T10:00:00Z",
  "updated_at": "2026-04-24T10:05:00Z",
  "web_url": "https://gitlab.example.com/.../merge_requests/17",
  "project_id": 42,
  "merge_status": "can_be_merged"
}
```

`merge_status` values: `unchecked`, `checking`, `can_be_merged`,
`cannot_be_merged`, `cannot_be_merged_recheck`. Check this before attempting
`merge-mr`.

## What `--json` summaries look like

Each summary trims the upstream JSON to fields the plugin uses, which keeps
downstream pipes small. Examples:

### `projects --json`

```json
{
  "count": 3,
  "items": [
    {"id": 1, "path": "a/b", "name": "b", "default_branch": "main", "web_url": "..."},
    {"id": 2, "path": "a/c", "name": "c", "default_branch": "master", "web_url": "..."},
    {"id": 3, "path": "a/d", "name": "d", "default_branch": "main", "web_url": "..."}
  ]
}
```

### `diff --json`

```json
{
  "file_count": 2,
  "files": [
    {"new_path": "src/a.ts", "old_path": "src/a.ts", "new_file": false, "renamed_file": false, "deleted_file": false, "additions": 5, "deletions": 2},
    {"new_path": "src/b.ts", "old_path": "src/b.ts", "new_file": true, "renamed_file": false, "deleted_file": false, "additions": 42, "deletions": 0}
  ]
}
```

### `mrs --json`

```json
{
  "total": 17,
  "count": 17,
  "items": [
    {"project_id": 42, "iid": 17, "title": "...", "author": "zhang", "source": "feat-x", "target": "main", "merge_status": "can_be_merged", "web_url": "..."}
  ]
}
```

### `compare --json`

```json
{
  "commit_count": 4,
  "file_count": 7,
  "commits": [{"short_id": "abc1234", "title": "..."}, ...],
  "files": ["src/a.ts", "src/b.ts", ...]
}
```

For the full upstream payload including fields the plugin doesn't surface,
use `--raw`.
