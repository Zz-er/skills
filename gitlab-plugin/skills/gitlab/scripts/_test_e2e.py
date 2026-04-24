"""End-to-end test harness for the gitlab plugin.

Starts a local HTTP mock that speaks enough of GitLab REST v4 to exercise
every method in gitlab.py, then runs cli.py commands against it and asserts
on the human-readable / --json / --raw output.

Run:  python scripts/_test_e2e.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Force UTF-8 on this harness's stdout (Windows GBK console mangles ✓/Chinese).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent           # skills/gitlab
CLI = HERE / "cli.py"
PORT = 9087

# --------------------------------------------------------------------------
# Mock server — minimal GitLab v4 behavior we exercise
# --------------------------------------------------------------------------

USER = {"id": 1, "username": "tester", "name": "Tester", "email": "t@example.com"}

PROJECTS = [
    {
        "id": 42, "name": "demo-project",
        "name_with_namespace": "MyGroup / demo-project",
        "path_with_namespace": "mygroup/demo-project",
        "description": "demo", "web_url": "https://g/x/demo",
        "default_branch": "main",
    },
    {
        "id": 43, "name": "another",
        "name_with_namespace": "MyGroup / another",
        "path_with_namespace": "mygroup/another",
        "description": None, "web_url": "https://g/x/another",
        "default_branch": "main",
    },
]

GROUPS = [
    {"id": 1, "name": "MyGroup", "full_path": "mygroup"},
    {"id": 2, "name": "OtherGroup", "full_path": "othergroup"},
]

BRANCHES = [
    {
        "name": "main", "protected": True,
        "commit": {"id": "abc123456", "short_id": "abc1234",
                   "title": "feat: add lastItem", "authored_date": "2026-04-24T10:00:00Z"},
    },
    {
        "name": "feat-x", "protected": False,
        "commit": {"id": "def567890", "short_id": "def5678",
                   "title": "wip: feature x", "authored_date": "2026-04-23T09:00:00Z"},
    },
]

COMMIT = {
    "id": "abc1234567890abcdef1234567890abcdef123456",
    "short_id": "abc1234",
    "title": "feat: add lastItem helper",
    "message": "feat: add lastItem helper\n\nDetails.\n",
    "author_name": "张三",
    "author_email": "zhang@example.com",
    "authored_date": "2026-04-24T10:00:00.000+08:00",
    "committed_date": "2026-04-24T10:00:01.000+08:00",
    "web_url": "https://g/x/demo/commit/abc1234",
}

BUGGY_DIFF = [
    {
        "old_path": "src/util.ts", "new_path": "src/util.ts",
        "a_mode": "100644", "b_mode": "100644",
        "new_file": False, "renamed_file": False, "deleted_file": False,
        "diff": "@@ -0,0 +1,3 @@\n+export function lastItem<T>(arr: T[]): T {\n+    return arr[arr.length];\n+}\n",
    }
]

MR = {
    "iid": 17, "title": "feat: add lastItem",
    "description": "does X", "state": "opened",
    "source_branch": "feat-x", "target_branch": "main",
    "author": {"name": "张三", "username": "zhang", "avatar_url": "https://g/a.png"},
    "created_at": "2026-04-24T10:00:00Z", "updated_at": "2026-04-24T10:05:00Z",
    "web_url": "https://g/x/demo/-/merge_requests/17",
    "project_id": 42, "merge_status": "can_be_merged",
}

# Side-effect log so we can verify POST / PUT / DELETE bodies landed right
SIDE_EFFECTS: list[dict] = []


class MockHandler(BaseHTTPRequestHandler):
    # silence default request logs in test output
    def log_message(self, format, *args):  # noqa: A002
        pass

    # ---- helpers ----

    def _check_auth(self) -> bool:
        if self.headers.get("PRIVATE-TOKEN") != "glpat-FAKE":
            self._send_json(401, {"message": "unauthorized"})
            return False
        return True

    def _send_json(self, status: int, data, headers: dict | None = None) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if headers:
            for k, v in headers.items():
                self.send_header(k, str(v))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status: int, text: str) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        raw = self.rfile.read(n).decode("utf-8")
        return json.loads(raw) if raw else {}

    # ---- routing ----

    def do_GET(self):  # noqa: N802
        if not self._check_auth():
            return
        p = urlparse(self.path)
        path = p.path
        qs = {k: v[0] for k, v in parse_qs(p.query).items()}

        if path == "/api/v4/user":
            return self._send_json(200, USER)
        if path == "/api/v4/groups":
            return self._send_json(200, GROUPS)
        if path == "/api/v4/projects":
            data = PROJECTS
            if qs.get("search"):
                data = [p for p in PROJECTS if qs["search"] in p["name"]]
            return self._send_json(200, data, {"X-Total": str(len(data))})
        if path == "/api/v4/groups/mygroup/projects":
            return self._send_json(200, PROJECTS)
        if path == "/api/v4/projects/42/repository/branches":
            return self._send_json(200, BRANCHES)
        if path == "/api/v4/projects/42/repository/commits":
            return self._send_json(200, [COMMIT])
        if path == "/api/v4/projects/42/repository/commits/abc1234":
            return self._send_json(200, COMMIT)
        if path == "/api/v4/projects/42/repository/commits/abc1234/diff":
            return self._send_json(200, BUGGY_DIFF)
        if path == "/api/v4/projects/42/repository/compare":
            return self._send_json(200, {"commits": [COMMIT], "diffs": BUGGY_DIFF})
        if path == "/api/v4/projects/42/repository/files/src%2Futil.ts/raw":
            return self._send_text(200, "export const x = 1\n")
        if path == "/api/v4/merge_requests":
            return self._send_json(200, [MR], {"X-Total": "1"})
        if path == "/api/v4/projects/42/merge_requests":
            if qs.get("source_branch") and qs.get("target_branch"):
                return self._send_json(200, [MR] if qs["source_branch"] == "feat-x" else [])
            return self._send_json(200, [MR], {"X-Total": "1"})
        if path == "/api/v4/groups/mygroup/merge_requests":
            return self._send_json(200, [MR], {"X-Total": "1"})
        self.send_error(404, "not found in mock")

    def do_POST(self):  # noqa: N802
        if not self._check_auth():
            return
        body = self._read_body()
        p = urlparse(self.path)

        if p.path == "/api/v4/projects/42/repository/branches":
            SIDE_EFFECTS.append({"op": "create-branch", "body": body})
            return self._send_json(201, {"name": body.get("branch"), "protected": False,
                                          "commit": BRANCHES[0]["commit"]})
        if p.path == "/api/v4/projects/42/repository/commits/abc1234/comments":
            SIDE_EFFECTS.append({"op": "comment-commit", "body": body})
            return self._send_json(201, {"note": body.get("note")})
        if p.path == "/api/v4/projects/42/merge_requests":
            SIDE_EFFECTS.append({"op": "create-mr", "body": body})
            return self._send_json(201, {**MR, "iid": 99, "title": body.get("title")})
        if p.path == "/api/v4/projects/42/merge_requests/17/notes":
            SIDE_EFFECTS.append({"op": "comment-mr", "body": body})
            return self._send_json(201, {"body": body.get("body")})
        self.send_error(404, "not found in mock")

    def do_PUT(self):  # noqa: N802
        if not self._check_auth():
            return
        body = self._read_body()
        p = urlparse(self.path)
        if p.path == "/api/v4/projects/42/merge_requests/17/merge":
            SIDE_EFFECTS.append({"op": "merge-mr", "body": body})
            return self._send_json(200, {**MR, "state": "merged"})
        self.send_error(404, "not found in mock")

    def do_DELETE(self):  # noqa: N802
        if not self._check_auth():
            return
        p = urlparse(self.path)
        if p.path.startswith("/api/v4/projects/42/repository/branches/"):
            SIDE_EFFECTS.append({"op": "delete-branch", "path": p.path})
            self.send_response(204)
            self.end_headers()
            return
        self.send_error(404, "not found in mock")


# --------------------------------------------------------------------------
# Test runner
# --------------------------------------------------------------------------

def run_cli(config_path: Path, *args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["GITLAB_CONFIG"] = str(config_path)
    # Force UTF-8 on both ends — Windows subprocess otherwise decodes as cp1252/gbk
    # and mangles Chinese strings + breaks JSON parsing.
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=True, timeout=15, env=env,
        encoding="utf-8", errors="replace",
    )


def check(label: str, ok: bool, *, detail: str = "") -> None:
    mark = "✓" if ok else "✗"
    print(f"  {mark} {label}{(' — ' + detail) if detail and not ok else ''}")
    if not ok:
        raise SystemExit(f"FAILED: {label}  {detail}")


def main() -> int:
    # Start mock
    httpd = HTTPServer(("127.0.0.1", PORT), MockHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.2)

    try:
        # Write a temp config
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as fh:
            fh.write(f"url: http://127.0.0.1:{PORT}\ntoken: glpat-FAKE\nverify_ssl: true\ntimeout: 10\n")
            cfg_path = Path(fh.name)

        print("\n=== plugin E2E against mock GitLab on :%d ===\n" % PORT)

        # --- whoami ---
        r = run_cli(cfg_path, "whoami")
        check("whoami exit 0", r.returncode == 0, detail=r.stderr)
        check("whoami prints username", "tester" in r.stdout)

        r = run_cli(cfg_path, "whoami", "--json")
        obj = json.loads(r.stdout)
        check("whoami --json shape", obj["username"] == "tester" and obj["id"] == 1)

        # --- projects ---
        r = run_cli(cfg_path, "projects")
        check("projects lists 2", "2 project(s)" in r.stdout)

        r = run_cli(cfg_path, "projects", "--search", "demo", "--json")
        obj = json.loads(r.stdout)
        check("projects --search filters", obj["count"] == 1 and obj["items"][0]["id"] == 42)

        r = run_cli(cfg_path, "projects", "--group", "mygroup", "--json")
        obj = json.loads(r.stdout)
        check("projects --group hits group endpoint", obj["count"] == 2)

        # --- groups ---
        r = run_cli(cfg_path, "groups", "--json")
        obj = json.loads(r.stdout)
        check("groups --json", obj["count"] == 2 and obj["items"][0]["full_path"] == "mygroup")

        # --- branches ---
        r = run_cli(cfg_path, "branches", "--project", "42")
        check("branches lists 2", "2 branch(es)" in r.stdout)
        check("branches shows [P] for protected", "[P]" in r.stdout)

        r = run_cli(cfg_path, "branches", "--project", "42", "--json")
        obj = json.loads(r.stdout)
        check("branches --json has protected bool", obj["items"][0]["protected"] is True)

        # --- commits ---
        r = run_cli(cfg_path, "commits", "--project", "42", "--branch", "main", "--json")
        obj = json.loads(r.stdout)
        check("commits --json", obj["count"] == 1 and obj["items"][0]["short_id"] == "abc1234")

        # --- commit ---
        r = run_cli(cfg_path, "commit", "--project", "42", "--sha", "abc1234")
        check("commit shows sha + author", "abc1234" in r.stdout and "张三" in r.stdout)

        # --- diff (the big one — main input for code review) ---
        r = run_cli(cfg_path, "diff", "--project", "42", "--sha", "abc1234")
        check("diff shows 1 file", "1 file(s) changed" in r.stdout)
        check("diff has +/- counts", "+" in r.stdout and "util.ts" in r.stdout)

        r = run_cli(cfg_path, "diff", "--project", "42", "--sha", "abc1234", "--json")
        obj = json.loads(r.stdout)
        check("diff --json structure", obj["file_count"] == 1 and obj["files"][0]["new_path"] == "src/util.ts")
        check("diff --json additions computed", obj["files"][0]["additions"] >= 3)

        r = run_cli(cfg_path, "diff", "--project", "42", "--sha", "abc1234", "--raw")
        obj = json.loads(r.stdout)
        check("diff --raw preserves diff text", isinstance(obj, list) and "arr[arr.length]" in obj[0]["diff"])

        # --- compare ---
        r = run_cli(cfg_path, "compare", "--project", "42", "--from", "main", "--to", "feat-x", "--json")
        obj = json.loads(r.stdout)
        check("compare --json", obj["commit_count"] == 1 and obj["file_count"] == 1)

        # --- file ---
        r = run_cli(cfg_path, "file", "--project", "42", "--path", "src/util.ts", "--ref", "main")
        check("file raw text", r.stdout.strip() == "export const x = 1")

        # --- mrs global ---
        r = run_cli(cfg_path, "mrs", "--json")
        obj = json.loads(r.stdout)
        check("mrs global --json", obj["count"] == 1 and obj["items"][0]["iid"] == 17)

        # --- mrs project ---
        r = run_cli(cfg_path, "mrs", "--project", "42", "--json")
        obj = json.loads(r.stdout)
        check("mrs --project --json", obj["count"] == 1)

        # --- mrs group ---
        r = run_cli(cfg_path, "mrs", "--group", "mygroup", "--json")
        obj = json.loads(r.stdout)
        check("mrs --group --json", obj["count"] == 1)

        # --- find-mr ---
        r = run_cli(cfg_path, "find-mr", "--project", "42", "--source", "feat-x", "--target", "main", "--json")
        obj = json.loads(r.stdout)
        check("find-mr hits", obj["iid"] == 17 and obj["title"] == "feat: add lastItem")

        r = run_cli(cfg_path, "find-mr", "--project", "42", "--source", "no-such", "--target", "main", "--json")
        # the empty result prints `null`; that's valid JSON
        obj = json.loads(r.stdout)
        check("find-mr miss → null", obj is None)

        # --- writes (require --yes) ---
        r = run_cli(cfg_path, "create-branch", "--project", "42", "--name", "feat-y", "--ref", "main", "--json")
        check("create-branch success", r.returncode == 0)
        check("side effect: create-branch", any(s["op"] == "create-branch" and s["body"]["branch"] == "feat-y" for s in SIDE_EFFECTS))

        # guardrail: delete without --yes
        r = run_cli(cfg_path, "delete-branch", "--project", "42", "--name", "feat-y")
        check("delete-branch without --yes blocked", r.returncode != 0 and "--yes" in r.stderr)

        r = run_cli(cfg_path, "delete-branch", "--project", "42", "--name", "feat-y", "--yes")
        check("delete-branch with --yes success", r.returncode == 0)
        check("side effect: delete-branch", any(s["op"] == "delete-branch" for s in SIDE_EFFECTS))

        # create-mr
        r = run_cli(cfg_path, "create-mr", "--project", "42", "--source", "feat-x",
                    "--target", "main", "--title", "new MR", "--json")
        obj = json.loads(r.stdout)
        check("create-mr returns new iid", obj["iid"] == 99)
        check("side effect: create-mr body title", any(s["op"] == "create-mr" and s["body"]["title"] == "new MR" for s in SIDE_EFFECTS))

        # merge-mr guardrail
        r = run_cli(cfg_path, "merge-mr", "--project", "42", "--iid", "17")
        check("merge-mr without --yes blocked", r.returncode != 0 and "--yes" in r.stderr)

        r = run_cli(cfg_path, "merge-mr", "--project", "42", "--iid", "17", "--remove-source", "--yes")
        check("merge-mr with --yes success", r.returncode == 0)
        check("side effect: merge-mr remove-source", any(s["op"] == "merge-mr" and s["body"]["should_remove_source_branch"] is True for s in SIDE_EFFECTS))

        # comment-commit
        r = run_cli(cfg_path, "comment-commit", "--project", "42", "--sha", "abc1234",
                    "--body", "nice work", "--yes")
        check("comment-commit success", r.returncode == 0)
        check("side effect: comment-commit body", any(s["op"] == "comment-commit" and s["body"]["note"] == "nice work" for s in SIDE_EFFECTS))

        # comment-mr
        r = run_cli(cfg_path, "comment-mr", "--project", "42", "--iid", "17",
                    "--body", "LGTM 👍", "--yes")
        check("comment-mr success", r.returncode == 0)
        check("side effect: comment-mr body", any(s["op"] == "comment-mr" and "LGTM" in s["body"]["body"] for s in SIDE_EFFECTS))

        # --- error translation ---
        # bad token → 401 → "Token 已过期"
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as fh:
            fh.write(f"url: http://127.0.0.1:{PORT}\ntoken: WRONG\n")
            bad_cfg = Path(fh.name)
        r = run_cli(bad_cfg, "whoami")
        check("bad token → translated 401", r.returncode != 0 and "Token 已过期" in r.stderr)

        print(f"\n✓ All checks passed — {len(SIDE_EFFECTS)} write side effects recorded")
        return 0

    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    sys.exit(main())
