# GitLab REST v4 endpoints used by this plugin

All requests carry `PRIVATE-TOKEN: <pat>` and `Content-Type: application/json`.
Paths below are relative to `<base_url>` (e.g. `https://gitlab.example.com`).

Legend — **13.3 OK** column:
- ✓ — verified on CE 13.3
- ⚠ — OK but some params vary (see notes)

## Connection

| Method | Path | Purpose | 13.3 OK |
|--------|------|---------|:-------:|
| GET | `/api/v4/user` | Validate token; return current user | ✓ |

## Groups

| Method | Path | Purpose | 13.3 OK |
|--------|------|---------|:-------:|
| GET | `/api/v4/groups?per_page=100&order_by=name&sort=asc` | List visible groups | ✓ |

## Projects

| Method | Path | Purpose | 13.3 OK |
|--------|------|---------|:-------:|
| GET | `/api/v4/projects?membership=true&per_page=100&order_by=last_activity_at&sort=desc[&search=X]` | All projects I belong to | ✓ |
| GET | `/api/v4/groups/:group/projects?per_page=100&order_by=last_activity_at&sort=desc&include_subgroups=true[&search=X]` | Projects in a group (incl. subgroups) | ✓ |

> **Note:** `order_by=updated` was added in 14.x and is silently ignored by 13.3.
> Use `order_by=last_activity_at` instead.

## Branches

| Method | Path | Purpose | 13.3 OK |
|--------|------|---------|:-------:|
| GET | `/api/v4/projects/:id/repository/branches?per_page=100` | List branches | ✓ |
| POST | `/api/v4/projects/:id/repository/branches` with `{branch, ref}` | Create branch | ✓ |
| DELETE | `/api/v4/projects/:id/repository/branches/:branch_enc` | Delete branch | ✓ |

`:id` is `<number>` or `<URL-encoded full path>` (e.g. `mygroup%2Fsub%2Frepo`).
`:branch_enc` is `<URL-encoded branch name>` — slashes in `feat/foo` must be encoded.

## Commits

| Method | Path | Purpose | 13.3 OK |
|--------|------|---------|:-------:|
| GET | `/api/v4/projects/:id/repository/commits?ref_name=BRANCH&per_page=N` | Latest commits on a ref | ✓ |
| GET | `/api/v4/projects/:id/repository/commits/:sha` | One commit's metadata | ✓ |
| GET | `/api/v4/projects/:id/repository/commits/:sha/diff` | Files changed by a commit | ✓ |
| POST | `/api/v4/projects/:id/repository/commits/:sha/comments` with `{note}` | Post a comment | ✓ |

## Compare

| Method | Path | Purpose | 13.3 OK |
|--------|------|---------|:-------:|
| GET | `/api/v4/projects/:id/repository/compare?from=F&to=T` | Compare two refs; returns `{commits, diffs}` | ✓ |

> **Note:** `straight=true` was added in 14.x. Omit it on 13.3; the default
> ("three-dot" / merge-base) is what most MR-review workflows want anyway.

## File contents

| Method | Path | Purpose | 13.3 OK |
|--------|------|---------|:-------:|
| GET | `/api/v4/projects/:id/repository/files/:path_enc/raw?ref=R` | Raw text content | ✓ |

`:path_enc` is URL-encoded (`src%2Futil.ts`).

## Merge Requests

| Method | Path | Purpose | 13.3 OK |
|--------|------|---------|:-------:|
| GET | `/api/v4/merge_requests?state=opened&scope=all&per_page=N&page=P` | All opened MRs visible to me | ⚠ |
| GET | `/api/v4/projects/:id/merge_requests?state=opened&per_page=N&page=P` | Project opened MRs | ✓ |
| GET | `/api/v4/groups/:group/merge_requests?state=opened&per_page=N&page=P` | Group opened MRs | ✓ |
| GET | `/api/v4/projects/:id/merge_requests?source_branch=S&target_branch=T&state=opened` | Locate one MR | ✓ |
| POST | `/api/v4/projects/:id/merge_requests` with `{source_branch, target_branch, title, remove_source_branch, description?}` | Create MR | ✓ |
| PUT | `/api/v4/projects/:id/merge_requests/:iid/merge` with `{should_remove_source_branch}` | Accept/merge MR | ✓ |
| POST | `/api/v4/projects/:id/merge_requests/:iid/notes` with `{body}` | Post MR note | ✓ |

> **13.3 note on `scope=all`**: silently ignored on some very old instances.
> If you get surprising results on the global `/merge_requests` endpoint,
> use the project- or group-scoped variant.

## Pagination

GitLab returns a `X-Total` response header on list endpoints. This plugin surfaces
it as the `total` field in `mrs` responses. Navigate pages via `?page=N&per_page=M`.

GitLab caps `per_page` at 100 — requesting larger returns the first 100 silently.

## Response shape quick reference

See `fields.md` for per-resource field schemas.
