"""CLI entry for the gitlab skill.

Usage:
    python cli.py <command> [args...] [--json] [--raw]

Run `python cli.py help` for the full list. Each command maps to one or two
GitLab REST v4 endpoints via scripts/gitlab.py.

Config lookup order:
    1. --config <path>
    2. $GITLAB_CONFIG env var
    3. ~/.claude/gitlab/config.yaml
    4. ${CLAUDE_PLUGIN_ROOT}/skills/gitlab/config.yaml (in-tree fallback)

Output:
    * default  — concise human-readable summary
    * --json   — structured summary (for chaining)
    * --raw    — full upstream response body (no filtering)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Force UTF-8 on stdout/stderr so Windows GBK consoles don't mangle Chinese.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gitlab import Client, GitLabError  # noqa: E402

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    print("error: PyYAML not installed — run `pip install -r requirements.txt`", file=sys.stderr)
    sys.exit(2)


# ----------------------------------------------------------------------
# Config loading
# ----------------------------------------------------------------------

def _candidate_config_paths(explicit: str | None) -> list[Path]:
    out: list[Path] = []
    if explicit:
        out.append(Path(explicit).expanduser())
    env = os.environ.get("GITLAB_CONFIG")
    if env:
        out.append(Path(env).expanduser())
    out.append(Path.home() / ".claude" / "gitlab" / "config.yaml")
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        out.append(Path(plugin_root) / "skills" / "gitlab" / "config.yaml")
    # dev fallback — the plugin repo itself
    out.append(Path(__file__).resolve().parent.parent / "config.yaml")
    return out


def load_config(explicit: str | None = None) -> dict[str, Any]:
    for p in _candidate_config_paths(explicit):
        if p.is_file():
            with p.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            if not isinstance(data, dict):
                raise SystemExit(f"error: config at {p} is not a YAML mapping")
            if not data.get("url") or not data.get("token"):
                raise SystemExit(
                    f"error: config at {p} is missing required keys `url` and `token`"
                )
            return data
    raise SystemExit(
        "error: no gitlab config found. Copy config.example.yaml to "
        "~/.claude/gitlab/config.yaml and fill in url + token."
    )


def make_client(cfg: dict[str, Any]) -> Client:
    return Client(
        cfg["url"],
        cfg["token"],
        verify_ssl=cfg.get("verify_ssl", True),
        timeout=int(cfg.get("timeout", 30)),
    )


# ----------------------------------------------------------------------
# Output helpers
# ----------------------------------------------------------------------

def _emit(data: Any, *, json_mode: bool, raw_mode: bool, summary_fn=None) -> None:
    """Print data per flags.

    raw_mode  → full upstream JSON, indented
    json_mode → structured summary (caller provides summary_fn or uses data)
    default   → summary_fn(data) prints human-readable lines
    """
    if raw_mode:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    if json_mode:
        # If the caller provided a summary function, the JSON shape follows it
        # by passing through the fn. If not, fall back to the raw data.
        if summary_fn is None:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(summary_fn(data, as_dict=True), indent=2, ensure_ascii=False))
        return
    if summary_fn is not None:
        summary_fn(data, as_dict=False)
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def _require(value: Any, label: str) -> None:
    if value is None or value == "":
        raise SystemExit(f"error: --{label} is required")


def _project(args: argparse.Namespace, cfg: dict[str, Any]) -> int | str:
    """Pick project id from --project / --project-path / config default. Numeric str → int."""
    pid = args.project if getattr(args, "project", None) else cfg.get("default_project")
    if not pid:
        raise SystemExit(
            "error: --project required (or set default_project in config.yaml)"
        )
    # If it's all digits, pass as int — GitLab accepts both but int is lighter on URL
    if isinstance(pid, str) and pid.isdigit():
        return int(pid)
    return pid


# ----------------------------------------------------------------------
# Summaries
# ----------------------------------------------------------------------

def _summary_user(data, as_dict=False):
    d = {
        "id": data.get("id"),
        "username": data.get("username"),
        "name": data.get("name"),
        "email": data.get("email"),
    }
    if as_dict:
        return d
    print(f"id={d['id']}  username={d['username']}  name={d['name']}  email={d['email']}")


def _summary_projects(data, as_dict=False):
    items = [
        {
            "id": p.get("id"),
            "path": p.get("path_with_namespace"),
            "name": p.get("name"),
            "default_branch": p.get("default_branch"),
            "web_url": p.get("web_url"),
        }
        for p in data
    ]
    if as_dict:
        return {"count": len(items), "items": items}
    print(f"{len(items)} project(s):")
    for p in items:
        print(f"  {p['id']:>6}  {p['path']:<48}  default={p['default_branch']}")


def _summary_groups(data, as_dict=False):
    items = [
        {"id": g.get("id"), "full_path": g.get("full_path"), "name": g.get("name")}
        for g in data
    ]
    if as_dict:
        return {"count": len(items), "items": items}
    print(f"{len(items)} group(s):")
    for g in items:
        print(f"  {g['id']:>6}  {g['full_path']}")


def _summary_branches(data, as_dict=False):
    items = [
        {
            "name": b.get("name"),
            "protected": b.get("protected"),
            "commit_id": (b.get("commit") or {}).get("short_id"),
            "commit_title": (b.get("commit") or {}).get("title"),
        }
        for b in data
    ]
    if as_dict:
        return {"count": len(items), "items": items}
    print(f"{len(items)} branch(es):")
    for b in items:
        tag = "[P]" if b["protected"] else "   "
        print(f"  {tag} {b['name']:<40}  {b['commit_id']}  {b['commit_title']}")


def _summary_commits(data, as_dict=False):
    items = [
        {
            "short_id": c.get("short_id"),
            "title": c.get("title"),
            "author": c.get("author_name"),
            "date": c.get("authored_date"),
        }
        for c in data
    ]
    if as_dict:
        return {"count": len(items), "items": items}
    print(f"{len(items)} commit(s):")
    for c in items:
        print(f"  {c['short_id']}  {c['date'][:19]}  {c['author']:<20}  {c['title']}")


def _summary_commit(data, as_dict=False):
    d = {
        "id": data.get("id"),
        "short_id": data.get("short_id"),
        "title": data.get("title"),
        "author": data.get("author_name"),
        "date": data.get("authored_date"),
        "message": data.get("message"),
    }
    if as_dict:
        return d
    print(f"commit {d['short_id']}  by {d['author']}  @ {d['date']}")
    print(f"  title:   {d['title']}")
    if d["message"] and d["message"] != d["title"]:
        print(f"  message: {d['message'].strip()}")


def _summary_diff(data, as_dict=False):
    files = [
        {
            "new_path": f.get("new_path"),
            "old_path": f.get("old_path"),
            "new_file": f.get("new_file"),
            "renamed_file": f.get("renamed_file"),
            "deleted_file": f.get("deleted_file"),
            "additions": sum(1 for ln in (f.get("diff") or "").splitlines() if ln.startswith("+") and not ln.startswith("+++")),
            "deletions": sum(1 for ln in (f.get("diff") or "").splitlines() if ln.startswith("-") and not ln.startswith("---")),
        }
        for f in data
    ]
    if as_dict:
        return {"files": files, "file_count": len(files)}
    print(f"{len(files)} file(s) changed:")
    for f in files:
        tag = "A" if f["new_file"] else ("D" if f["deleted_file"] else ("R" if f["renamed_file"] else "M"))
        print(f"  [{tag}] {f['new_path']:<50}  +{f['additions']:<4} -{f['deletions']}")


def _summary_compare(data, as_dict=False):
    commits = data.get("commits", [])
    diffs = data.get("diffs", [])
    if as_dict:
        return {
            "commit_count": len(commits),
            "file_count": len(diffs),
            "commits": [{"short_id": c.get("short_id"), "title": c.get("title")} for c in commits],
            "files": [f.get("new_path") for f in diffs],
        }
    print(f"compare: {len(commits)} commit(s), {len(diffs)} file(s) changed")
    for c in commits:
        print(f"  {c.get('short_id')}  {c.get('title')}")


def _summary_mrs(data, as_dict=False):
    items = data.get("items", []) if isinstance(data, dict) else data
    total = data.get("total", len(items)) if isinstance(data, dict) else len(items)
    shaped = [
        {
            "project_id": mr.get("project_id"),
            "iid": mr.get("iid"),
            "title": mr.get("title"),
            "author": (mr.get("author") or {}).get("username"),
            "source": mr.get("source_branch"),
            "target": mr.get("target_branch"),
            "web_url": mr.get("web_url"),
            "merge_status": mr.get("merge_status"),
        }
        for mr in items
    ]
    if as_dict:
        return {"total": total, "count": len(shaped), "items": shaped}
    print(f"{len(shaped)} MR(s) (total={total}):")
    for mr in shaped:
        print(f"  p{mr['project_id']} !{mr['iid']}  {mr['source']} → {mr['target']}")
        print(f"      {mr['title']}  (@{mr['author']}, {mr['merge_status']})")


def _summary_mr(data, as_dict=False):
    if not data:
        if as_dict:
            return None
        print("not found")
        return
    d = {
        "iid": data.get("iid"),
        "title": data.get("title"),
        "web_url": data.get("web_url"),
    }
    if as_dict:
        return d
    print(f"MR !{d['iid']}  {d['title']}  {d.get('web_url', '')}")


# ----------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------

def cmd_whoami(args, client, cfg):
    data = client.validate_connection()
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_user)


def cmd_projects(args, client, cfg):
    groups = args.group or cfg.get("default_groups") or None
    data = client.projects(search=args.search, groups=groups)
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_projects)


def cmd_groups(args, client, cfg):
    data = client.groups()
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_groups)


def cmd_branches(args, client, cfg):
    pid = _project(args, cfg)
    data = client.branches(pid)
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_branches)


def cmd_create_branch(args, client, cfg):
    _require(args.name, "name")
    _require(args.ref, "ref")
    pid = _project(args, cfg)
    data = client.create_branch(pid, args.name, args.ref)
    _emit(data, json_mode=args.json, raw_mode=args.raw)


def cmd_delete_branch(args, client, cfg):
    _require(args.name, "name")
    pid = _project(args, cfg)
    if not args.yes:
        raise SystemExit("error: deleting a branch requires --yes")
    client.delete_branch(pid, args.name)
    if args.json:
        print(json.dumps({"deleted": args.name}, ensure_ascii=False))
    else:
        print(f"deleted branch {args.name}")


def cmd_commits(args, client, cfg):
    _require(args.branch, "branch")
    pid = _project(args, cfg)
    data = client.commits(pid, args.branch, args.limit)
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_commits)


def cmd_commit(args, client, cfg):
    _require(args.sha, "sha")
    pid = _project(args, cfg)
    data = client.commit(pid, args.sha)
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_commit)


def cmd_diff(args, client, cfg):
    _require(args.sha, "sha")
    pid = _project(args, cfg)
    data = client.commit_diff(pid, args.sha)
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_diff)


def cmd_compare(args, client, cfg):
    _require(args.from_ref, "from")
    _require(args.to_ref, "to")
    pid = _project(args, cfg)
    data = client.compare_diff(pid, args.from_ref, args.to_ref)
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_compare)


def cmd_file(args, client, cfg):
    _require(args.path, "path")
    _require(args.ref, "ref")
    pid = _project(args, cfg)
    text = client.file_content(pid, args.path, args.ref)
    if args.raw or args.json:
        # raw text — neither json-wrap nor re-format
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    else:
        sys.stdout.write(text)


def cmd_mrs(args, client, cfg):
    groups = args.group or cfg.get("default_groups")
    if args.project:
        pid = _project(args, cfg)
        data = client.project_merge_requests(pid, page=args.page, per_page=args.per_page)
    elif groups:
        data = client.group_merge_requests(groups, page=args.page, per_page=args.per_page)
    else:
        data = client.all_merge_requests(page=args.page, per_page=args.per_page)
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_mrs)


def cmd_find_mr(args, client, cfg):
    _require(args.source, "source")
    _require(args.target, "target")
    pid = _project(args, cfg)
    data = client.find_merge_request(pid, args.source, args.target)
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_mr)


def cmd_create_mr(args, client, cfg):
    _require(args.source, "source")
    _require(args.target, "target")
    _require(args.title, "title")
    pid = _project(args, cfg)
    data = client.create_merge_request(
        pid,
        args.source,
        args.target,
        args.title,
        remove_source_branch=args.remove_source,
        description=args.description,
    )
    _emit(data, json_mode=args.json, raw_mode=args.raw, summary_fn=_summary_mr)


def cmd_merge_mr(args, client, cfg):
    _require(args.iid, "iid")
    pid = _project(args, cfg)
    if not args.yes:
        raise SystemExit("error: merging requires --yes")
    client.accept_merge_request(pid, args.iid, should_remove_source_branch=args.remove_source)
    if args.json:
        print(json.dumps({"merged": True, "iid": args.iid}, ensure_ascii=False))
    else:
        print(f"merged MR !{args.iid}")


def cmd_comment_commit(args, client, cfg):
    _require(args.sha, "sha")
    body = _read_body(args)
    pid = _project(args, cfg)
    if not args.yes:
        raise SystemExit("error: posting a comment requires --yes")
    client.post_commit_comment(pid, args.sha, body)
    if args.json:
        print(json.dumps({"commented": True, "sha": args.sha}, ensure_ascii=False))
    else:
        print(f"posted comment on commit {args.sha}")


def cmd_comment_mr(args, client, cfg):
    _require(args.iid, "iid")
    body = _read_body(args)
    pid = _project(args, cfg)
    if not args.yes:
        raise SystemExit("error: posting a comment requires --yes")
    client.post_mr_note(pid, args.iid, body)
    if args.json:
        print(json.dumps({"commented": True, "iid": args.iid}, ensure_ascii=False))
    else:
        print(f"posted note on MR !{args.iid}")


def _read_body(args) -> str:
    if args.body:
        return args.body
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("error: need --body, --file, or stdin input")


# ----------------------------------------------------------------------
# Arg parsing
# ----------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    # Shared flags — attached to every subcommand via `parents=[common]` so
    # users can write them either BEFORE or AFTER the subcommand name.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", help="explicit path to config.yaml")
    common.add_argument("--json", action="store_true", help="emit structured JSON summary")
    common.add_argument("--raw", action="store_true", help="emit full upstream JSON")

    p = argparse.ArgumentParser(
        prog="gitlab",
        description="GitLab REST v4 wrapper (CE 13.3+ compatible).",
        parents=[common],
    )
    sub = p.add_subparsers(dest="command", required=True)

    # whoami
    sp = sub.add_parser("whoami", parents=[common], help="verify token + print current user")
    sp.set_defaults(func=cmd_whoami)

    # projects
    sp = sub.add_parser("projects", parents=[common], help="list projects (membership by default)")
    sp.add_argument("--search", help="substring search on project name")
    sp.add_argument("--group", action="append", help="restrict to group(s); repeatable")
    sp.set_defaults(func=cmd_projects)

    # groups
    sp = sub.add_parser("groups", parents=[common], help="list groups I can see")
    sp.set_defaults(func=cmd_groups)

    # branches
    sp = sub.add_parser("branches", parents=[common], help="list branches of a project")
    sp.add_argument("--project", help="project id (int) or path (group/name)")
    sp.set_defaults(func=cmd_branches)

    # create-branch
    sp = sub.add_parser("create-branch", parents=[common], help="create a new branch off a ref")
    sp.add_argument("--project", required=False)
    sp.add_argument("--name", required=True, help="new branch name")
    sp.add_argument("--ref", required=True, help="base ref (branch/commit/tag)")
    sp.set_defaults(func=cmd_create_branch)

    # delete-branch
    sp = sub.add_parser("delete-branch", parents=[common], help="delete a branch (--yes required)")
    sp.add_argument("--project", required=False)
    sp.add_argument("--name", required=True)
    sp.add_argument("--yes", action="store_true")
    sp.set_defaults(func=cmd_delete_branch)

    # commits
    sp = sub.add_parser("commits", parents=[common], help="list latest commits on a branch")
    sp.add_argument("--project", required=False)
    sp.add_argument("--branch", required=True)
    sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(func=cmd_commits)

    # commit
    sp = sub.add_parser("commit", parents=[common], help="show a single commit")
    sp.add_argument("--project", required=False)
    sp.add_argument("--sha", required=True)
    sp.set_defaults(func=cmd_commit)

    # diff
    sp = sub.add_parser("diff", parents=[common], help="show files changed by a commit + diffs")
    sp.add_argument("--project", required=False)
    sp.add_argument("--sha", required=True)
    sp.set_defaults(func=cmd_diff)

    # compare
    sp = sub.add_parser("compare", parents=[common], help="compare two refs (branch-against-branch)")
    sp.add_argument("--project", required=False)
    sp.add_argument("--from", dest="from_ref", required=True, help="base ref")
    sp.add_argument("--to", dest="to_ref", required=True, help="head ref")
    sp.set_defaults(func=cmd_compare)

    # file
    sp = sub.add_parser("file", parents=[common], help="print raw file content at a ref")
    sp.add_argument("--project", required=False)
    sp.add_argument("--path", required=True, help="file path inside the repo")
    sp.add_argument("--ref", required=True, help="branch/commit/tag")
    sp.set_defaults(func=cmd_file)

    # mrs
    sp = sub.add_parser("mrs", parents=[common], help="list opened merge requests")
    sp.add_argument("--project", help="if set, only this project")
    sp.add_argument("--group", action="append", help="if set, only these groups (repeatable)")
    sp.add_argument("--page", type=int, default=1)
    sp.add_argument("--per-page", type=int, default=100)
    sp.set_defaults(func=cmd_mrs)

    # find-mr
    sp = sub.add_parser("find-mr", parents=[common], help="find opened MR by source→target branch")
    sp.add_argument("--project", required=False)
    sp.add_argument("--source", required=True)
    sp.add_argument("--target", required=True)
    sp.set_defaults(func=cmd_find_mr)

    # create-mr
    sp = sub.add_parser("create-mr", parents=[common], help="create a merge request")
    sp.add_argument("--project", required=False)
    sp.add_argument("--source", required=True)
    sp.add_argument("--target", required=True)
    sp.add_argument("--title", required=True)
    sp.add_argument("--description", help="MR description")
    sp.add_argument("--remove-source", action="store_true", help="delete source branch after merge")
    sp.set_defaults(func=cmd_create_mr)

    # merge-mr
    sp = sub.add_parser("merge-mr", parents=[common], help="accept/merge an MR (--yes required)")
    sp.add_argument("--project", required=False)
    sp.add_argument("--iid", type=int, required=True)
    sp.add_argument("--remove-source", action="store_true")
    sp.add_argument("--yes", action="store_true")
    sp.set_defaults(func=cmd_merge_mr)

    # comment-commit
    sp = sub.add_parser("comment-commit", parents=[common], help="post a note on a commit (--yes required)")
    sp.add_argument("--project", required=False)
    sp.add_argument("--sha", required=True)
    sp.add_argument("--body", help="comment text")
    sp.add_argument("--file", help="read body from file")
    sp.add_argument("--yes", action="store_true")
    sp.set_defaults(func=cmd_comment_commit)

    # comment-mr
    sp = sub.add_parser("comment-mr", parents=[common], help="post a note on an MR (--yes required)")
    sp.add_argument("--project", required=False)
    sp.add_argument("--iid", type=int, required=True)
    sp.add_argument("--body")
    sp.add_argument("--file")
    sp.add_argument("--yes", action="store_true")
    sp.set_defaults(func=cmd_comment_mr)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_config(args.config)
    client = make_client(cfg)
    try:
        args.func(args, client, cfg)
    except GitLabError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
