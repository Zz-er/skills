# ZenTao legacy `.json` endpoint reference

ZenTao's web UI exposes every page's data as JSON when the URL ends in
`.json`. No REST v1 / API tokens required — auth is a session cookie.

Base URL: `{host}` (e.g. `http://10.111.161.190:80`). All requests send
`Cookie: zentaosid=<token>` where `<token>` is the value returned in the
login response body (`res.user.token`). **Don't use the `zentaosid` value
from the server's `Set-Cookie` header — that's the un-authenticated
session id and will redirect back to login.**

## Auth

| Method | URL | Body | Returns |
|---|---|---|---|
| POST | `/user-login.json` | `account=X&password=Y` (`application/x-www-form-urlencoded`) | `{status, user: {id, account, realname, role, token, ...}}` |

On success, save `user.token` and use it as the `zentaosid` cookie value.
Session lasts ~2h idle. On expiry, any subsequent call's response has
`data.locate` pointing back at login; re-login and retry.

## Response envelope

All `.json` endpoints return:

```json
{
  "status": "success",
  "data": "<JSON string OR object>",
  "md5": "..."
}
```

- `data` is **often a JSON-encoded string** that needs a second
  `json.loads` — always handle both shapes.
- The unwrapped inner dict has entry-specific keys (`projects`, `bugs`,
  `users`, `pager`, `title`, …).
- Collections (`projects`, `bugs`, `users`) may be returned as a **list**
  or as an **object keyed by id**. Normalize before iterating.

## Read endpoints (verified)

| Purpose | URL | Notable cookies | Inner keys |
|---|---|---|---|
| My projects | `/my-project.json` | — | `projects`, `deptList`, `pager`, `type`, … |
| Project bugs | `/project-bug-{projectId}.json` | `pagerProjectBug=<N>` sets page size | `bugs`, `users`, `projects`, `products`, `teamMembers`, `pager`, … |
| Project stories | `/project-story-{projectId}.json` | `pagerProjectStory=<N>` | `stories`, `users`, … |
| Project tasks | `/project-task-{projectId}.json` | `pagerProjectTask=<N>` | `tasks`, `users`, … |
| My bugs | `/my-bug.json` | `pagerMyBug=<N>` | `bugs` (pre-filtered to current user), `users`, … |
| My tasks | `/my-task.json` | — | `tasks`, `users`, … |
| My todos | `/my-todo.json` | — | `todos`, … |

Only the first two are wrapped by the CLI; the rest follow the same
pattern and can be fetched via `Client.get_json(entry)`.

## Browser links (for surfacing in reports)

| Purpose | URL |
|---|---|
| Bug detail page | `/bug-view-{bugId}.html` |
| Project bug list page | `/project-bug-{projectId}.html` |
| Project overview | `/project-index-{projectId}.html` |

## Pagination via cookies

Some list entries cap rows at 20 by default. Override per-entry with the
cookie named `pager<Entry>`:

| Entry | Cookie |
|---|---|
| project-bug | `pagerProjectBug` |
| project-story | `pagerProjectStory` |
| project-task | `pagerProjectTask` |
| my-bug | `pagerMyBug` |
| my-task | `pagerMyTask` |

Value is the page size (e.g. `1000`). The CLI exposes this via `--limit`.

## Error shapes

- HTTP 200 + `data.locate: http://.../user-login-...json` → session expired
- HTTP 200 + `data._raw: <html>` (our own wrapper) → server returned HTML
  (wrong URL, or not logged in and `.json` suffix got stripped)
- Login 200 + `status: fail` → bad credentials

The CLI treats login-redirect as "refresh token and retry once". Anything
else surfaces as a `ZentaoError`.
