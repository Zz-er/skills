"""GitLab REST v4 client — Python port of modou-utils/src/main/gitlab.ts.

Design goals:
  * 1:1 method mapping with the original TypeScript module so downstream docs
    (and the SKILL-linked references/) stay accurate.
  * Single `Client` class holding the base URL, PRIVATE-TOKEN header, and a
    `requests.Session` so connection pooling works across a CLI run.
  * Error translation centralized in `_translate_error` (same Chinese
    user-facing strings as the original axios interceptor) — any caller just
    catches `GitLabError`.
  * Project identifier accepted as `int` (numeric ID) OR `str` (URL-encoded
    path like `group/subgroup/name`). We URL-encode path-style ids exactly
    once; numeric ids pass through unchanged.
  * Compatible with GitLab CE 13.3+ — we deliberately avoid newer params like
    `order_by=updated` or compare `straight=true` which 13.3 will reject.
"""
from __future__ import annotations

import urllib.parse
from typing import Any, Iterable

import requests


__all__ = ["Client", "GitLabError"]


class GitLabError(RuntimeError):
    """Translated GitLab API error. Message is safe to show to end users."""


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _enc(project_id: int | str) -> str:
    """Encode a project identifier for URL path insertion.

    GitLab accepts either the numeric `id` or the URL-encoded full path
    (`group%2Fsub%2Frepo`). We pass ints through as-is, string ids get
    percent-encoded.
    """
    if isinstance(project_id, int):
        return str(project_id)
    # Path — encode /, spaces, etc. Dots are fine.
    return urllib.parse.quote(project_id, safe="")


def _enc_ref(ref: str) -> str:
    """Encode a ref/branch name for URL path insertion."""
    return urllib.parse.quote(ref, safe="")


# --------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------

class Client:
    """Synchronous GitLab REST v4 client.

    Usage:
        client = Client("https://gitlab.example.com", "glpat-xxxxx")
        user = client.validate_connection()
        projects = client.projects(search="api")

    All methods raise `GitLabError` on HTTP failure with a translated message.
    """

    def __init__(
        self,
        url: str,
        token: str,
        *,
        verify_ssl: bool = True,
        timeout: int = 30,
    ) -> None:
        if not url:
            raise ValueError("url is required")
        if not token:
            raise ValueError("token is required")
        self.base_url = url.rstrip("/")
        self.token = token
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "PRIVATE-TOKEN": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    # ---- transport ----

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        raw_text: bool = False,
    ) -> Any:
        """Perform an HTTP request and return parsed JSON (or raw text)."""
        url = f"{self.base_url}{path}"
        try:
            resp = self._session.request(
                method,
                url,
                params=params,
                json=json,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        except requests.exceptions.Timeout as exc:
            raise GitLabError("网络连接超时") from exc
        except requests.exceptions.ConnectionError as exc:
            raise GitLabError("网络连接失败，请检查网络设置") from exc
        except requests.exceptions.RequestException as exc:
            raise GitLabError(f"请求失败: {exc}") from exc

        if resp.status_code >= 400:
            raise self._translate_error(resp)

        if raw_text:
            return resp.text
        if resp.status_code == 204 or not resp.content:
            return None
        # Keep headers accessible for callers that care (e.g. X-Total)
        try:
            body = resp.json()
        except ValueError as exc:
            raise GitLabError(f"响应不是合法 JSON: {resp.text[:200]}") from exc
        # attach headers for pagination consumers
        return _Response(body, resp.headers)

    @staticmethod
    def _translate_error(resp: requests.Response) -> GitLabError:
        status = resp.status_code
        if status == 401:
            return GitLabError("Token 已过期，请重新配置")
        if status == 403:
            return GitLabError("无权访问该项目")
        try:
            data = resp.json()
            msg = (
                data.get("message")
                or data.get("error")
                or data.get("error_description")
            )
            if isinstance(msg, dict):
                msg = next(iter(msg.values()), None)
            if isinstance(msg, list):
                msg = "; ".join(str(x) for x in msg)
        except ValueError:
            msg = resp.text[:200]
        return GitLabError(f"请求失败 ({status}): {msg or 'unknown'}")

    # ======================================================================
    # Connection
    # ======================================================================

    def validate_connection(self) -> dict[str, Any]:
        """`GET /user` — verify token, return the current user profile.

        Raises GitLabError on 401/403/etc.
        """
        return self._request("GET", "/api/v4/user").body

    # ======================================================================
    # Groups
    # ======================================================================

    def groups(self) -> list[dict[str, Any]]:
        """`GET /groups` — all groups I'm a member of (or see)."""
        r = self._request(
            "GET",
            "/api/v4/groups",
            params={"per_page": 100, "order_by": "name", "sort": "asc"},
        )
        return r.body

    # ======================================================================
    # Projects
    # ======================================================================

    def projects(
        self,
        search: str | None = None,
        groups: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        """List projects.

        * If `groups` is provided, query each group's `/groups/<g>/projects`
          endpoint and merge-dedupe by project id (matches modouide-utils
          behavior — useful on large self-hosted instances to constrain scope).
        * Otherwise, `/projects?membership=true` — everything I belong to.
        """
        groups_list = list(groups) if groups else []
        if groups_list:
            seen: set[int] = set()
            out: list[dict[str, Any]] = []
            for group in groups_list:
                params: dict[str, Any] = {
                    "per_page": 100,
                    "order_by": "last_activity_at",
                    "sort": "desc",
                    "include_subgroups": True,
                }
                if search and search.strip():
                    params["search"] = search.strip()
                try:
                    enc = urllib.parse.quote(group, safe="")
                    r = self._request(
                        "GET",
                        f"/api/v4/groups/{enc}/projects",
                        params=params,
                    )
                except GitLabError:
                    # ZenTao-plugin-style silent skip: a missing / unauthorized
                    # group in the list should not fail the whole query.
                    continue
                for p in r.body:
                    if p["id"] not in seen:
                        seen.add(p["id"])
                        out.append(p)
            return out

        params = {
            "per_page": 100,
            "membership": True,
            "order_by": "last_activity_at",
            "sort": "desc",
        }
        if search and search.strip():
            params["search"] = search.strip()
        return self._request("GET", "/api/v4/projects", params=params).body

    # ======================================================================
    # Branches
    # ======================================================================

    def branches(self, project_id: int | str) -> list[dict[str, Any]]:
        """`GET /projects/:id/repository/branches` — up to 100 branches."""
        return self._request(
            "GET",
            f"/api/v4/projects/{_enc(project_id)}/repository/branches",
            params={"per_page": 100},
        ).body

    def create_branch(
        self,
        project_id: int | str,
        branch: str,
        ref: str,
    ) -> dict[str, Any]:
        """Create a branch off `ref`. Returns `{name, commit, protected, ...}`."""
        return self._request(
            "POST",
            f"/api/v4/projects/{_enc(project_id)}/repository/branches",
            json={"branch": branch, "ref": ref},
        ).body

    def delete_branch(self, project_id: int | str, branch: str) -> None:
        """Delete a branch by name. Returns None (204)."""
        self._request(
            "DELETE",
            f"/api/v4/projects/{_enc(project_id)}/repository/branches/{_enc_ref(branch)}",
        )

    # ======================================================================
    # Commits
    # ======================================================================

    def commits(
        self,
        project_id: int | str,
        branch: str,
        count: int = 20,
    ) -> list[dict[str, Any]]:
        """Latest `count` commits on `branch`."""
        return self._request(
            "GET",
            f"/api/v4/projects/{_enc(project_id)}/repository/commits",
            params={"ref_name": branch, "per_page": count},
        ).body

    def commit(self, project_id: int | str, sha: str) -> dict[str, Any]:
        """Single commit metadata."""
        return self._request(
            "GET",
            f"/api/v4/projects/{_enc(project_id)}/repository/commits/{sha}",
        ).body

    def commit_diff(
        self,
        project_id: int | str,
        sha: str,
    ) -> list[dict[str, Any]]:
        """Files changed by a commit + the unified diff per file."""
        return self._request(
            "GET",
            f"/api/v4/projects/{_enc(project_id)}/repository/commits/{sha}/diff",
        ).body

    def compare_diff(
        self,
        project_id: int | str,
        from_ref: str,
        to_ref: str,
    ) -> dict[str, Any]:
        """Compare two refs. Returns `{commits, diffs}`.

        Note: we deliberately do NOT pass `straight=true` because GitLab CE
        13.3 rejects it. Default behavior is "three-dot" (merge-base) compare,
        which is what most users want for MR-review purposes.
        """
        return self._request(
            "GET",
            f"/api/v4/projects/{_enc(project_id)}/repository/compare",
            params={"from": from_ref, "to": to_ref},
        ).body

    def file_content(
        self,
        project_id: int | str,
        file_path: str,
        ref: str,
    ) -> str:
        """Raw text content of a file at a given ref. File path is URL-encoded."""
        return self._request(
            "GET",
            f"/api/v4/projects/{_enc(project_id)}/repository/files/{urllib.parse.quote(file_path, safe='')}/raw",
            params={"ref": ref},
            raw_text=True,
        )

    def post_commit_comment(
        self,
        project_id: int | str,
        sha: str,
        note: str,
    ) -> None:
        """Post a plain comment on a commit."""
        self._request(
            "POST",
            f"/api/v4/projects/{_enc(project_id)}/repository/commits/{sha}/comments",
            json={"note": note},
        )

    # ======================================================================
    # Merge Requests
    # ======================================================================

    def all_merge_requests(
        self,
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """All opened MRs visible to me (scope=all, across projects)."""
        r = self._request(
            "GET",
            "/api/v4/merge_requests",
            params={
                "state": "opened",
                "scope": "all",
                "per_page": per_page,
                "page": page,
            },
        )
        total = int(r.headers.get("x-total", "0") or "0")
        return {"items": r.body, "total": total}

    def project_merge_requests(
        self,
        project_id: int | str,
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """Opened MRs of a single project."""
        r = self._request(
            "GET",
            f"/api/v4/projects/{_enc(project_id)}/merge_requests",
            params={"state": "opened", "per_page": per_page, "page": page},
        )
        total = int(r.headers.get("x-total", "0") or "0")
        return {"items": r.body, "total": total}

    def group_merge_requests(
        self,
        groups: Iterable[str],
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """Opened MRs across one or more top-level groups. Deduped by project_id-iid."""
        seen: set[str] = set()
        out: list[dict[str, Any]] = []
        for group in groups:
            try:
                enc = urllib.parse.quote(group, safe="")
                r = self._request(
                    "GET",
                    f"/api/v4/groups/{enc}/merge_requests",
                    params={"state": "opened", "per_page": per_page, "page": page},
                )
            except GitLabError:
                continue
            for mr in r.body:
                key = f"{mr.get('project_id')}-{mr.get('iid')}"
                if key not in seen:
                    seen.add(key)
                    out.append(mr)
        return {"items": out, "total": len(out)}

    def find_merge_request(
        self,
        project_id: int | str,
        source_branch: str,
        target_branch: str,
    ) -> dict[str, Any] | None:
        """Look up an opened MR by source/target branch. Returns None if not found."""
        r = self._request(
            "GET",
            f"/api/v4/projects/{_enc(project_id)}/merge_requests",
            params={
                "source_branch": source_branch,
                "target_branch": target_branch,
                "state": "opened",
                "per_page": 1,
            },
        )
        items = r.body
        return items[0] if items else None

    def create_merge_request(
        self,
        project_id: int | str,
        source_branch: str,
        target_branch: str,
        title: str,
        *,
        remove_source_branch: bool = False,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new merge request. Returns the full MR object."""
        body: dict[str, Any] = {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "remove_source_branch": remove_source_branch,
        }
        if description:
            body["description"] = description
        return self._request(
            "POST",
            f"/api/v4/projects/{_enc(project_id)}/merge_requests",
            json=body,
        ).body

    def accept_merge_request(
        self,
        project_id: int | str,
        mr_iid: int,
        *,
        should_remove_source_branch: bool = False,
    ) -> None:
        """Merge an MR. No-op safety: only 'opened' + 'can_be_merged' MRs succeed
        server-side; otherwise GitLab returns 406/409 and we surface that."""
        self._request(
            "PUT",
            f"/api/v4/projects/{_enc(project_id)}/merge_requests/{mr_iid}/merge",
            json={"should_remove_source_branch": should_remove_source_branch},
        )

    def post_mr_note(
        self,
        project_id: int | str,
        mr_iid: int,
        body: str,
    ) -> None:
        """Append a note (comment) to an MR."""
        self._request(
            "POST",
            f"/api/v4/projects/{_enc(project_id)}/merge_requests/{mr_iid}/notes",
            json={"body": body},
        )


# --------------------------------------------------------------------------
# Response wrapper — we want to carry headers for pagination-aware callers
# --------------------------------------------------------------------------

class _Response:
    __slots__ = ("body", "headers")

    def __init__(self, body: Any, headers: Any) -> None:
        self.body = body
        self.headers = {k.lower(): v for k, v in headers.items()}
