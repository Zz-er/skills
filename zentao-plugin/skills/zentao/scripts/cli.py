"""CLI for the zentao skill (session-cookie / `.json` URL API).

Usage:
    python cli.py <command> [args...] [--json] [--raw]

Run `python cli.py help` for the full list. Each command is a thin wrapper
around one or two ZenTao `.json` entries and is invoked by Claude based on
SKILL.md guidance.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

# Force UTF-8 on stdout/stderr — Windows consoles default to GBK and mangle
# ZenTao's Chinese strings. No-op on POSIX or if already UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zentao import Client, ZentaoError, as_list, clean_html  # noqa: E402


# ---------- constants ----------

SEVERITY_LABEL = {'1': '严重', '2': '主要', '3': '次要', '4': '轻微'}
STATUS_LABEL = {
    'active': '激活', 'resolved': '已解决', 'closed': '已关闭',
    'wait': '未开始', 'doing': '进行中', 'done': '已完成',
    'suspended': '已挂起', 'cancel': '已取消',
}
TYPE_LABEL = {
    'codeerror': '代码错误', 'config': '配置相关', 'install': '安装部署',
    'security': '安全相关', 'performance': '性能问题', 'standard': '标准规范',
    'automation': '测试脚本', 'designdefect': '设计缺陷', 'others': '其他',
}
RESOLUTION_LABEL = {
    'bydesign': '设计如此', 'duplicate': '重复Bug', 'external': '外部原因',
    'fixed': '已解决', 'notrepro': '无法重现', 'postponed': '延期处理',
    'willnotfix': '不予解决', 'tostory': '转为需求',
}


# ---------- output ----------

def _emit(data: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return
    if isinstance(data, str):
        print(data)
    elif isinstance(data, dict) or isinstance(data, list):
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    else:
        print(data)


def _display_name(users: dict, account: str) -> str:
    return users.get(account) or account or '未指派'


# ---------- command handlers ----------

def cmd_whoami(c: Client, args) -> Any:
    user = c.whoami()
    if args.json or args.raw:
        return user
    return (
        f"account: {user.get('account')}\n"
        f"realname: {user.get('realname')}\n"
        f"role: {user.get('role')}\n"
        f"dept: {user.get('dept')}\n"
        f"url: {c.url}"
    )


def cmd_projects(c: Client, args) -> Any:
    projects = c.get_projects(include_closed=args.all)
    if args.raw:
        return projects
    summary = [{
        'id': int(p.get('id', 0)) or p.get('id'),
        'name': p.get('name'),
        'status': p.get('status'),
        'type': p.get('type'),
        'begin': p.get('begin'),
        'end': p.get('end'),
        'PM': p.get('PM'),
    } for p in projects]
    if args.json:
        return summary
    lines = [f"{len(summary)} project(s):"]
    for p in summary:
        lines.append(f"  [{p['id']:>5}] {p['status']:<10} {p['type']:<10} {p['name']}  (PM={p['PM']})")
    return '\n'.join(lines)


def cmd_my_bugs(c: Client, args) -> Any:
    bugs, users = c.get_my_bugs(page_size=args.limit)
    if args.status and args.status != 'all':
        bugs = [b for b in bugs if b.get('status') == args.status]
    if args.raw:
        return {'bugs': bugs, 'users': users}
    rows = []
    for b in bugs:
        rows.append({
            'id': int(b.get('id', 0)) or b.get('id'),
            'title': b.get('title'),
            'severity': SEVERITY_LABEL.get(str(b.get('severity')), b.get('severity')),
            'status': STATUS_LABEL.get(b.get('status'), b.get('status')),
            'type': TYPE_LABEL.get(b.get('type'), b.get('type')),
            'project': b.get('project'),
            'openedBy': _display_name(users, b.get('openedBy', '')),
            'openedDate': b.get('openedDate'),
            'resolution': RESOLUTION_LABEL.get(b.get('resolution'), b.get('resolution')),
        })
    if args.json:
        return rows
    # Group by status for human readability
    grouped: dict[str, list[dict]] = {}
    for r in rows:
        grouped.setdefault(r['status'] or '?', []).append(r)
    lines = [f"{len(rows)} bug(s) assigned to {c.account}:"]
    for status_key in ('激活', '已解决', '已关闭'):
        grp = grouped.pop(status_key, [])
        if not grp:
            continue
        lines.append(f"\n【{status_key} - {len(grp)}】")
        for r in sorted(grp, key=lambda x: -int(str(x['id']) or 0)):
            lines.append(
                f"  [{r['id']:>6}] {r['severity']:<4} "
                f"{(r['openedDate'] or '')[:10]}  proj={r['project']:<5} "
                f"来自{r['openedBy']:<8}  {r['title']}"
            )
    for status_key, grp in grouped.items():
        lines.append(f"\n【{status_key} - {len(grp)}】")
        for r in grp:
            lines.append(f"  [{r['id']}] {r['severity']} {r['title']}")
    return '\n'.join(lines)


def cmd_bugs(c: Client, args) -> Any:
    pid = args.project or c.defaults.get('default_project')
    if not pid:
        raise SystemExit('--project ID required (or set default_project in config.yaml)')
    bugs, users = c.get_bugs(pid, page_size=args.limit)
    if args.status and args.status != 'all':
        bugs = [b for b in bugs if b.get('status') == args.status]
    if args.assigned_to:
        bugs = [b for b in bugs if b.get('assignedTo') == args.assigned_to]
    if args.raw:
        return {'bugs': bugs, 'users': users}
    rows = []
    for b in bugs:
        rows.append({
            'id': int(b.get('id', 0)) or b.get('id'),
            'title': b.get('title'),
            'severity': SEVERITY_LABEL.get(str(b.get('severity')), b.get('severity')),
            'status': STATUS_LABEL.get(b.get('status'), b.get('status')),
            'type': TYPE_LABEL.get(b.get('type'), b.get('type')),
            'assignedTo': _display_name(users, b.get('assignedTo', '')),
            'openedBy': _display_name(users, b.get('openedBy', '')),
            'openedDate': b.get('openedDate'),
            'resolution': RESOLUTION_LABEL.get(b.get('resolution'), b.get('resolution')),
        })
    if args.json:
        return rows
    lines = [f"{len(rows)} bug(s) in project {pid}:"]
    for r in rows:
        lines.append(
            f"  [{r['id']:>6}] {r['severity']:<4} {r['status']:<6} "
            f"{r['assignedTo']:<8} {r['title']}"
        )
    return '\n'.join(lines)


def cmd_bug(c: Client, args) -> Any:
    pid = args.project or c.defaults.get('default_project')
    if not pid:
        raise SystemExit('--project ID required to look up bug detail (legacy API has no global bug endpoint)')
    bugs, users = c.get_bugs(pid, page_size=args.limit)
    target = next((b for b in bugs if str(b.get('id')) == str(args.id)), None)
    if not target:
        raise SystemExit(f'Bug {args.id} not found in project {pid}')
    if args.raw or args.json:
        return target
    view = {
        'id': target.get('id'),
        'title': target.get('title'),
        'severity': SEVERITY_LABEL.get(str(target.get('severity')), target.get('severity')),
        'status': STATUS_LABEL.get(target.get('status'), target.get('status')),
        'type': TYPE_LABEL.get(target.get('type'), target.get('type')),
        'assignedTo': _display_name(users, target.get('assignedTo', '')),
        'openedBy': _display_name(users, target.get('openedBy', '')),
        'openedDate': target.get('openedDate'),
        'resolvedBy': _display_name(users, target.get('resolvedBy', '')),
        'resolution': RESOLUTION_LABEL.get(target.get('resolution'), target.get('resolution')),
        'url': f"{c.url}/bug-view-{target.get('id')}.html",
        'steps': clean_html(target.get('steps', '')),
    }
    lines = []
    for k, v in view.items():
        if k == 'steps':
            lines.append(f'\n--- 重现步骤 ---\n{v}')
        else:
            lines.append(f'{k}: {v}')
    return '\n'.join(lines)


def cmd_bug_report(c: Client, args) -> Any:
    pid = args.project or c.defaults.get('default_project')
    if not pid:
        raise SystemExit('--project ID required')
    bugs, users = c.get_bugs(pid, page_size=args.limit)
    active = [b for b in bugs if b.get('status') == 'active']

    stats: dict[str, dict[str, int]] = {}
    for b in active:
        name = _display_name(users, b.get('assignedTo', ''))
        s = stats.setdefault(name, {'total': 0, 's1': 0, 's2': 0, 's3': 0, 's4': 0})
        s['total'] += 1
        key = f"s{b.get('severity', '4')}"
        if key in s:
            s[key] += 1
        else:
            s['s4'] += 1

    ordered = sorted(stats.items(), key=lambda kv: -kv[1]['total'])

    if args.json:
        return {
            'project': int(pid) if str(pid).isdigit() else pid,
            'active_count': len(active),
            'by_assignee': [{'assignee': n, **s} for n, s in ordered],
        }

    # markdown
    md = [f'**Bug 统计** (project {pid}) | {len(active)} 个活跃', '']
    for name, s in ordered:
        parts = []
        for key, label in (('s1', '严重'), ('s2', '主要'), ('s3', '次要'), ('s4', '轻微')):
            if s[key]:
                parts.append(f"{s[key]}{label}")
        detail = ' '.join(parts) or '-'
        md.append(f"> {name}: **{s['total']}** ({detail})")
    return '\n'.join(md)


def cmd_poll_bugs(c: Client, args) -> Any:
    pid = args.project or c.defaults.get('default_project')
    if not pid:
        raise SystemExit('--project ID required')
    interval = max(10, args.interval)
    known: dict[str, str] = {}  # id -> assignedTo
    initialized = False
    print(f"polling project {pid} every {interval}s (Ctrl+C to stop)", file=sys.stderr)
    try:
        while True:
            bugs, users = c.get_bugs(pid, page_size=args.limit)
            current = {str(b['id']): b.get('assignedTo', '') for b in bugs if b.get('status') == 'active'}

            if not initialized:
                known = current
                initialized = True
                print(f"[{time.strftime('%H:%M:%S')}] baseline: {len(current)} active bugs", file=sys.stderr)
            else:
                new_ids = [i for i in current if i not in known]
                resolved_ids = [i for i in known if i not in current]
                reassigned = [
                    (i, known[i], current[i]) for i in current
                    if i in known and known[i] != current[i]
                ]
                events: list[dict] = []
                by_id = {str(b['id']): b for b in bugs}
                for i in new_ids:
                    b = by_id.get(i, {})
                    events.append({
                        'event': 'new',
                        'id': int(i),
                        'title': b.get('title'),
                        'severity': SEVERITY_LABEL.get(str(b.get('severity'))),
                        'assignedTo': _display_name(users, b.get('assignedTo', '')),
                    })
                for i in resolved_ids:
                    events.append({'event': 'resolved_or_closed', 'id': int(i)})
                for i, old, new in reassigned:
                    events.append({
                        'event': 'reassigned', 'id': int(i),
                        'from': _display_name(users, old),
                        'to': _display_name(users, new),
                    })
                if events:
                    for e in events:
                        print(json.dumps(e, ensure_ascii=False), flush=True)
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] no change ({len(current)} active)",
                          file=sys.stderr)
                known = current
            time.sleep(interval)
    except KeyboardInterrupt:
        print("stopped.", file=sys.stderr)
        return None


def cmd_comment_bug(c: Client, args) -> Any:
    # Body from flag or stdin. Stdin is preferred for multi-line comments
    # — argparse shells can't pass newlines cleanly.
    if args.body is not None:
        body = args.body
    elif args.file:
        body = Path(args.file).read_text(encoding='utf-8')
    else:
        body = sys.stdin.read()
    body = body.strip()
    if not body:
        raise SystemExit('empty comment body; pass --body, --file or pipe via stdin')
    if not args.yes:
        raise SystemExit('Comments edit the bug record. Re-run with --yes to confirm.')
    result = c.add_bug_comment(args.id, body)
    if args.json or args.raw:
        return result
    if result.get('ok'):
        return f"commented on bug {args.id} (locate={result.get('locate')})"
    return f"FAILED: {result.get('error')}"


def cmd_users(c: Client, args) -> Any:
    # Users map is embedded in any project-bug response; reuse that.
    pid = args.project or c.defaults.get('default_project')
    if not pid:
        projects = c.get_projects()
        if not projects:
            raise SystemExit('No projects visible; cannot enumerate users.')
        pid = projects[0].get('id')
    _, users = c.get_bugs(pid, page_size=1)
    # Strip the "" sentinel key some instances include.
    users = {k: v for k, v in users.items() if k}
    if args.json or args.raw:
        return users
    lines = [f'{len(users)} user(s):']
    for acc, name in sorted(users.items()):
        lines.append(f'  {acc:<16} {name}')
    return '\n'.join(lines)


# ---------- argparse ----------

def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument('--json', action='store_true', help='emit JSON (summary shape)')
    p.add_argument('--raw', action='store_true', help='emit raw upstream payload as JSON')


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='zentao-cli',
                                description='ZenTao session-based .json API client')
    p.add_argument('--config', type=Path, default=None, help='path to config.yaml')
    sub = p.add_subparsers(dest='cmd', required=True)

    sp = sub.add_parser('whoami', help='verify auth and show current user')
    _add_common(sp)

    sp = sub.add_parser('projects', help='list projects I am a member of')
    sp.add_argument('--all', action='store_true', help='include closed projects')
    _add_common(sp)

    sp = sub.add_parser('bugs', help='list bugs of a project')
    sp.add_argument('--project', type=int, help='project id (default: default_project)')
    sp.add_argument('--status', choices=['active', 'resolved', 'closed', 'all'],
                    default='active')
    sp.add_argument('--assigned-to', help='filter by assignee account')
    sp.add_argument('--limit', type=int, default=1000, help='page size (Cookie pagerProjectBug)')
    _add_common(sp)

    sp = sub.add_parser('my-bugs', help='list bugs assigned to me (server-filtered)')
    sp.add_argument('--status', choices=['active', 'resolved', 'closed', 'all'],
                    default='all')
    sp.add_argument('--limit', type=int, default=500, help='page size (Cookie pagerMyBug)')
    _add_common(sp)

    sp = sub.add_parser('bug', help='show bug detail (by scanning its project)')
    sp.add_argument('id', type=int)
    sp.add_argument('--project', type=int)
    sp.add_argument('--limit', type=int, default=1000)
    _add_common(sp)

    sp = sub.add_parser('bug-report', help='markdown stats by assignee')
    sp.add_argument('--project', type=int)
    sp.add_argument('--limit', type=int, default=1000)
    _add_common(sp)

    sp = sub.add_parser('poll-bugs', help='poll bug changes; emits NDJSON events')
    sp.add_argument('--project', type=int)
    sp.add_argument('--interval', type=int, default=60, help='seconds (min 10)')
    sp.add_argument('--limit', type=int, default=1000)
    _add_common(sp)

    sp = sub.add_parser('users', help='dump account->realname map')
    sp.add_argument('--project', type=int, help='any project id; used to extract map')
    _add_common(sp)

    sp = sub.add_parser('comment-bug',
                        help='add a comment to a bug (rewrites record via bug-edit; requires --yes)')
    sp.add_argument('id', type=int, help='bug id')
    sp.add_argument('--body', help='comment body (inline). For multi-line, use --file or stdin')
    sp.add_argument('--file', type=Path, help='read body from file (UTF-8)')
    sp.add_argument('--yes', action='store_true',
                    help='confirm: this POSTs a full bug-edit; safety guardrail')
    _add_common(sp)

    return p


HANDLERS = {
    'whoami': cmd_whoami,
    'projects': cmd_projects,
    'bugs': cmd_bugs,
    'my-bugs': cmd_my_bugs,
    'bug': cmd_bug,
    'bug-report': cmd_bug_report,
    'poll-bugs': cmd_poll_bugs,
    'users': cmd_users,
    'comment-bug': cmd_comment_bug,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        client = Client.from_config(args.config)
        handler = HANDLERS[args.cmd]
        result = handler(client, args)
        if result is not None:
            _emit(result, as_json=getattr(args, 'json', False) or getattr(args, 'raw', False))
        return 0
    except ZentaoError as e:
        print(f'[zentao error {e.status}] {e.message}', file=sys.stderr)
        return 2
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f'[unexpected] {type(e).__name__}: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
