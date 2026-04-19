"""CLI for the zentao skill.

Usage:
    python cli.py <command> [args...] [--json]

Run `python cli.py help` for the command list. The CLI is intentionally
flat — each command maps to one or two REST calls. Invoked by Claude
based on SKILL.md guidance.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zentao import Client, ZentaoError  # noqa: E402


def _emit(data: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return
    if isinstance(data, dict):
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    elif isinstance(data, list):
        for item in data:
            print(json.dumps(item, ensure_ascii=False, default=str))
    else:
        print(data)


def _parse_kv_list(items: list[str]) -> dict:
    out = {}
    for item in items or []:
        if '=' not in item:
            raise SystemExit(f'--field expects key=value, got: {item}')
        k, _, v = item.partition('=')
        out[k.strip()] = v
    return out


def _today() -> str:
    return date.today().isoformat()


def _now() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# ---------- command handlers ----------

def cmd_whoami(c: Client, args, raw):
    c.login(force=True)
    return {'ok': True, 'account': c.account, 'url': c.url, 'token_prefix': c.token()[:8] + '...'}


def cmd_products(c, args, raw):
    return c.get('/products', status=args.status, limit=args.limit, page=args.page)


def cmd_projects(c, args, raw):
    return c.get('/projects', status=args.status, limit=args.limit, page=args.page)


def cmd_executions(c, args, raw):
    path = f'/executions/{args.project}' if args.project else '/executions'
    return c.get(path, status=args.status, limit=args.limit, page=args.page, withProject=1 if args.with_project else None)


def cmd_stories(c, args, raw):
    pid = args.product or c.defaults.get('default_product')
    if not pid:
        raise SystemExit('--product required (or set default_product in config)')
    return c.get(f'/stories/{pid}', status=args.status, limit=args.limit, page=args.page)


def cmd_bugs(c, args, raw):
    if args.project:
        return c.get(f'/projectbugs/{args.project}', status=args.status, limit=args.limit, page=args.page)
    if args.execution:
        return c.get(f'/executionbugs/{args.execution}', status=args.status, limit=args.limit, page=args.page)
    pid = args.product or c.defaults.get('default_product')
    if not pid:
        raise SystemExit('one of --product/--project/--execution required')
    return c.get(f'/bugs/{pid}', status=args.status, limit=args.limit, page=args.page)


def cmd_tasks(c, args, raw):
    if args.execution:
        path = f'/tasks/{args.execution}'
    else:
        path = '/tasks'
    return c.get(path, status=args.status, type=args.type, limit=args.limit, page=args.page)


def cmd_todos(c, args, raw):
    return c.get('/todos', status=args.status, type=args.type, limit=args.limit, page=args.page)


def cmd_users(c, args, raw):
    return c.get('/users', full=1 if args.full else 0, type=args.type, limit=args.limit, page=args.page)


def cmd_get(c, args, raw):
    kind = args.kind
    valid = {'bug', 'task', 'story', 'product', 'project', 'execution', 'todo', 'user', 'build', 'release', 'doc'}
    if kind not in valid:
        raise SystemExit(f'unknown kind {kind}; expected one of {sorted(valid)}')
    return c.get(f'/{kind}/{args.id}', fields=args.fields)


# ---- create ----

def cmd_create_bug(c, args, raw):
    pid = args.product or c.defaults.get('default_product')
    if not pid:
        raise SystemExit('--product required')
    body = {
        'title': args.title,
        'pri': args.pri,
        'severity': args.severity,
        'type': args.type,
        'openedBuild': args.opened_build or ['trunk'],
        'steps': args.steps or '',
        'product': pid,
    }
    for k, v in (('assignedTo', args.assigned_to), ('execution', args.execution),
                 ('project', args.project), ('module', args.module), ('story', args.story),
                 ('deadline', args.deadline), ('os', args.os), ('browser', args.browser),
                 ('keywords', args.keywords), ('mailto', args.mailto), ('plan', args.plan)):
        if v is not None:
            body[k] = v
    return c.post(f'/bugs/{pid}', json_body=body)


def cmd_create_task(c, args, raw):
    eid = args.execution or c.defaults.get('default_execution')
    if not eid:
        raise SystemExit('--execution required')
    body = {
        'name': args.name,
        'type': args.type,
        'assignedTo': args.assigned_to,
        'estStarted': args.est_started or _today(),
        'deadline': args.deadline or _today(),
        'pri': args.pri,
    }
    for k, v in (('estimate', args.estimate), ('story', args.story), ('module', args.module),
                 ('desc', args.desc), ('parent', args.parent), ('mailto', args.mailto)):
        if v is not None:
            body[k] = v
    return c.post(f'/tasks/{eid}', json_body=body)


def cmd_create_story(c, args, raw):
    pid = args.product or c.defaults.get('default_product')
    if not pid:
        raise SystemExit('--product required')
    body = {
        'title': args.title,
        'spec': args.spec,
        'pri': args.pri,
        'category': args.category,
    }
    for k, v in (('estimate', args.estimate), ('reviewer', args.reviewer if not args.no_reviewer else ''),
                 ('module', args.module), ('verify', args.verify), ('source', args.source),
                 ('keywords', args.keywords), ('plan', args.plan), ('parent', args.parent),
                 ('type', args.type), ('mailto', args.mailto)):
        if v is not None:
            body[k] = v
    return c.post(f'/stories/{pid}', json_body=body)


def cmd_create_todo(c, args, raw):
    body = {
        'name': args.name,
        'date': args.date or _today(),
        'pri': args.pri,
        'desc': args.desc or '',
        'type': args.type,
        'status': 'wait',
    }
    if args.begin: body['begin'] = args.begin.replace(':', '')
    if args.end: body['end'] = args.end.replace(':', '')
    if args.private: body['private'] = 1
    return c.post('/todos', json_body=body)


def cmd_create_execution(c, args, raw):
    body = {
        'project': args.project,
        'name': args.name,
        'begin': args.begin,
        'end': args.end,
    }
    for k, v in (('PM', args.pm), ('PO', args.po), ('QD', args.qd), ('RD', args.rd),
                 ('lifetime', args.lifetime), ('desc', args.desc), ('parent', args.parent)):
        if v is not None:
            body[k] = v
    return c.post(f'/executions/{args.project}', json_body=body)


def cmd_create_project(c, args, raw):
    body = {
        'name': args.name,
        'begin': args.begin,
        'end': args.end,
        'products': args.products.split(',') if isinstance(args.products, str) else args.products,
        'model': args.model,
    }
    if args.pm: body['PM'] = args.pm
    if args.parent: body['parent'] = args.parent
    return c.post('/projects', json_body=body)


def cmd_batch_create_tasks(c, args, raw):
    eid = args.execution or c.defaults.get('default_execution')
    if not eid:
        raise SystemExit('--execution required')
    tasks = json.loads(Path(args.file).read_text(encoding='utf-8'))
    if isinstance(tasks, dict) and 'tasks' in tasks:
        tasks = tasks['tasks']
    return c.post(f'/taskbatchcreate/{eid}', json_body={'tasks': tasks})


# ---- transitions ----

def cmd_assign_bug(c, args, raw):
    return c.post(f'/bugassign/{args.id}', json_body={'assignedTo': args.to, 'comment': args.comment or ''})

def cmd_resolve_bug(c, args, raw):
    body = {'resolution': args.resolution, 'comment': args.comment or ''}
    if args.build: body['resolvedBuild'] = args.build
    if args.duplicate_id: body['duplicateBug'] = args.duplicate_id
    if args.assigned_to: body['assignedTo'] = args.assigned_to
    body['resolvedDate'] = args.resolved_date or _now()
    return c.post(f'/bugresolve/{args.id}', json_body=body)

def cmd_close_bug(c, args, raw):
    return c.post(f'/bugclose/{args.id}', json_body={'comment': args.comment or ''})

def cmd_activate_bug(c, args, raw):
    body = {'comment': args.comment or ''}
    if args.assigned_to: body['assignedTo'] = args.assigned_to
    if args.opened_build: body['openedBuild'] = args.opened_build
    return c.post(f'/bugactive/{args.id}', json_body=body)

def cmd_confirm_bug(c, args, raw):
    body = {'comment': args.comment or ''}
    if args.assigned_to: body['assignedTo'] = args.assigned_to
    return c.post(f'/bugconfirm/{args.id}', json_body=body)

def cmd_assign_task(c, args, raw):
    body = {'assignedTo': args.to, 'comment': args.comment or ''}
    if args.left is not None: body['left'] = args.left
    return c.post(f'/taskassignto/{args.id}', json_body=body)

def cmd_start_task(c, args, raw):
    body = {'comment': args.comment or ''}
    if args.assigned_to: body['assignedTo'] = args.assigned_to
    if args.consumed is not None: body['consumed'] = args.consumed
    if args.left is not None: body['left'] = args.left
    body['realStarted'] = args.real_started or _now()
    return c.post(f'/taskstart/{args.id}', json_body=body)

def cmd_finish_task(c, args, raw):
    body = {
        'currentConsumed': args.consumed,
        'realStarted': args.real_started or _now(),
        'finishedDate': args.finished_date or _now(),
        'comment': args.comment or '',
    }
    if args.assigned_to: body['assignedTo'] = args.assigned_to
    return c.post(f'/taskfinish/{args.id}', json_body=body)

def cmd_close_task(c, args, raw):
    return c.post(f'/taskclose/{args.id}', json_body={'comment': args.comment or ''})

def cmd_activate_task(c, args, raw):
    body = {'comment': args.comment or ''}
    if args.left is not None: body['left'] = args.left
    if args.assigned_to: body['assignedTo'] = args.assigned_to
    return c.post(f'/taskactive/{args.id}', json_body=body)

def cmd_assign_story(c, args, raw):
    return c.post(f'/storyassignto/{args.id}', json_body={'assignedTo': args.to, 'comment': args.comment or ''})

def cmd_close_story(c, args, raw):
    body = {'closedReason': args.reason, 'comment': args.comment or ''}
    if args.duplicate_id: body['duplicateStory'] = args.duplicate_id
    return c.post(f'/storyclose/{args.id}', json_body=body)

def cmd_review_story(c, args, raw):
    body = {
        'result': args.result,
        'reviewedDate': args.reviewed_date or _today(),
        'comment': args.comment or '',
    }
    if args.closed_reason: body['closedReason'] = args.closed_reason
    return c.post(f'/storyreview/{args.id}', json_body=body)

def cmd_finish_todo(c, args, raw):
    return c.get(f'/todofinish/{args.id}')

def cmd_activate_todo(c, args, raw):
    return c.get(f'/todoactivate/{args.id}')


# ---- update / delete ----

def cmd_update(c, args, raw):
    fields = _parse_kv_list(args.field)
    return c.put(f'/{args.kind}/{args.id}', json_body=fields)


def cmd_delete(c, args, raw):
    if not args.yes:
        raise SystemExit('refusing to delete without --yes')
    return c.delete(f'/{args.kind}/{args.id}')


# ---------- argparse wiring ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='zentao')
    p.add_argument('--config', help='override config path')
    p.add_argument('--json', action='store_true', help='emit JSON output')
    p.add_argument('--raw', action='store_true', help='do not trim/format response')
    sub = p.add_subparsers(dest='cmd', required=True)

    sub.add_parser('whoami').set_defaults(handler=cmd_whoami)

    def add_pager(s):
        s.add_argument('--limit', type=int, default=20)
        s.add_argument('--page', type=int, default=1)

    s = sub.add_parser('products'); s.add_argument('--status', default='all'); add_pager(s); s.set_defaults(handler=cmd_products)
    s = sub.add_parser('projects'); s.add_argument('--status', default='all'); add_pager(s); s.set_defaults(handler=cmd_projects)
    s = sub.add_parser('executions')
    s.add_argument('--project', type=int); s.add_argument('--status', default='all'); s.add_argument('--with-project', action='store_true'); add_pager(s); s.set_defaults(handler=cmd_executions)

    s = sub.add_parser('stories'); s.add_argument('--product', type=int); s.add_argument('--status', default='unclosed'); add_pager(s); s.set_defaults(handler=cmd_stories)
    s = sub.add_parser('bugs')
    s.add_argument('--product', type=int); s.add_argument('--project', type=int); s.add_argument('--execution', type=int)
    s.add_argument('--status', default=''); add_pager(s); s.set_defaults(handler=cmd_bugs)
    s = sub.add_parser('tasks'); s.add_argument('--execution', type=int); s.add_argument('--status', default='all'); s.add_argument('--type', default='assignedTo'); add_pager(s); s.set_defaults(handler=cmd_tasks)
    s = sub.add_parser('todos'); s.add_argument('--status', default='all'); s.add_argument('--type', default='all'); add_pager(s); s.set_defaults(handler=cmd_todos)
    s = sub.add_parser('users'); s.add_argument('--full', action='store_true'); s.add_argument('--type', default='bydept'); add_pager(s); s.set_defaults(handler=cmd_users)

    s = sub.add_parser('get'); s.add_argument('kind'); s.add_argument('id', type=int); s.add_argument('--fields', default=''); s.set_defaults(handler=cmd_get)

    # creates
    s = sub.add_parser('create-bug')
    s.add_argument('--product', type=int); s.add_argument('--title', required=True); s.add_argument('--steps', default='')
    s.add_argument('--pri', type=int, default=3); s.add_argument('--severity', type=int, default=3)
    s.add_argument('--type', default='codeerror'); s.add_argument('--opened-build', nargs='*', default=None)
    s.add_argument('--assigned-to'); s.add_argument('--execution', type=int); s.add_argument('--project', type=int)
    s.add_argument('--module', type=int); s.add_argument('--story', type=int); s.add_argument('--deadline'); s.add_argument('--os'); s.add_argument('--browser'); s.add_argument('--keywords'); s.add_argument('--mailto'); s.add_argument('--plan', type=int)
    s.set_defaults(handler=cmd_create_bug)

    s = sub.add_parser('create-task')
    s.add_argument('--execution', type=int); s.add_argument('--name', required=True)
    s.add_argument('--type', default='devel'); s.add_argument('--assigned-to', required=True)
    s.add_argument('--est-started'); s.add_argument('--deadline')
    s.add_argument('--pri', type=int, default=3); s.add_argument('--estimate', type=float)
    s.add_argument('--story', type=int); s.add_argument('--module', type=int); s.add_argument('--desc'); s.add_argument('--parent', type=int); s.add_argument('--mailto')
    s.set_defaults(handler=cmd_create_task)

    s = sub.add_parser('create-story')
    s.add_argument('--product', type=int); s.add_argument('--title', required=True); s.add_argument('--spec', required=True)
    s.add_argument('--pri', type=int, default=3); s.add_argument('--category', default='feature')
    s.add_argument('--type', default='story'); s.add_argument('--estimate', type=float)
    s.add_argument('--reviewer'); s.add_argument('--no-reviewer', action='store_true')
    s.add_argument('--module', type=int); s.add_argument('--verify'); s.add_argument('--source'); s.add_argument('--keywords'); s.add_argument('--plan', type=int); s.add_argument('--parent', type=int); s.add_argument('--mailto')
    s.set_defaults(handler=cmd_create_story)

    s = sub.add_parser('create-todo')
    s.add_argument('--name', required=True); s.add_argument('--date'); s.add_argument('--pri', type=int, default=3)
    s.add_argument('--desc'); s.add_argument('--type', default='custom'); s.add_argument('--begin'); s.add_argument('--end'); s.add_argument('--private', action='store_true')
    s.set_defaults(handler=cmd_create_todo)

    s = sub.add_parser('create-execution')
    s.add_argument('--project', type=int, required=True); s.add_argument('--name', required=True)
    s.add_argument('--begin', required=True); s.add_argument('--end', required=True)
    s.add_argument('--pm'); s.add_argument('--po'); s.add_argument('--qd'); s.add_argument('--rd')
    s.add_argument('--lifetime', default='short'); s.add_argument('--desc'); s.add_argument('--parent', type=int)
    s.set_defaults(handler=cmd_create_execution)

    s = sub.add_parser('create-project')
    s.add_argument('--name', required=True); s.add_argument('--begin', required=True); s.add_argument('--end', required=True)
    s.add_argument('--products', required=True, help='comma-separated product ids')
    s.add_argument('--model', default='scrum'); s.add_argument('--pm'); s.add_argument('--parent', type=int)
    s.set_defaults(handler=cmd_create_project)

    s = sub.add_parser('batch-create-tasks')
    s.add_argument('--execution', type=int); s.add_argument('--file', required=True)
    s.set_defaults(handler=cmd_batch_create_tasks)

    # transitions
    def _id_arg(s): s.add_argument('id', type=int)

    s = sub.add_parser('assign-bug'); _id_arg(s); s.add_argument('--to', required=True); s.add_argument('--comment'); s.set_defaults(handler=cmd_assign_bug)
    s = sub.add_parser('resolve-bug'); _id_arg(s); s.add_argument('--resolution', required=True); s.add_argument('--build', type=int); s.add_argument('--duplicate-id', type=int); s.add_argument('--assigned-to'); s.add_argument('--resolved-date'); s.add_argument('--comment'); s.set_defaults(handler=cmd_resolve_bug)
    s = sub.add_parser('close-bug'); _id_arg(s); s.add_argument('--comment'); s.set_defaults(handler=cmd_close_bug)
    s = sub.add_parser('activate-bug'); _id_arg(s); s.add_argument('--assigned-to'); s.add_argument('--opened-build'); s.add_argument('--comment'); s.set_defaults(handler=cmd_activate_bug)
    s = sub.add_parser('confirm-bug'); _id_arg(s); s.add_argument('--assigned-to'); s.add_argument('--comment'); s.set_defaults(handler=cmd_confirm_bug)

    s = sub.add_parser('assign-task'); _id_arg(s); s.add_argument('--to', required=True); s.add_argument('--left', type=float); s.add_argument('--comment'); s.set_defaults(handler=cmd_assign_task)
    s = sub.add_parser('start-task'); _id_arg(s); s.add_argument('--assigned-to'); s.add_argument('--consumed', type=float); s.add_argument('--left', type=float); s.add_argument('--real-started'); s.add_argument('--comment'); s.set_defaults(handler=cmd_start_task)
    s = sub.add_parser('finish-task'); _id_arg(s); s.add_argument('--consumed', type=float, required=True); s.add_argument('--real-started'); s.add_argument('--finished-date'); s.add_argument('--assigned-to'); s.add_argument('--comment'); s.set_defaults(handler=cmd_finish_task)
    s = sub.add_parser('close-task'); _id_arg(s); s.add_argument('--comment'); s.set_defaults(handler=cmd_close_task)
    s = sub.add_parser('activate-task'); _id_arg(s); s.add_argument('--left', type=float); s.add_argument('--assigned-to'); s.add_argument('--comment'); s.set_defaults(handler=cmd_activate_task)

    s = sub.add_parser('assign-story'); _id_arg(s); s.add_argument('--to', required=True); s.add_argument('--comment'); s.set_defaults(handler=cmd_assign_story)
    s = sub.add_parser('close-story'); _id_arg(s); s.add_argument('--reason', required=True); s.add_argument('--duplicate-id', type=int); s.add_argument('--comment'); s.set_defaults(handler=cmd_close_story)
    s = sub.add_parser('review-story'); _id_arg(s); s.add_argument('--result', required=True, choices=['pass', 'reject', 'revert', 'clarify']); s.add_argument('--reviewed-date'); s.add_argument('--closed-reason'); s.add_argument('--comment'); s.set_defaults(handler=cmd_review_story)
    s = sub.add_parser('finish-todo'); _id_arg(s); s.set_defaults(handler=cmd_finish_todo)
    s = sub.add_parser('activate-todo'); _id_arg(s); s.set_defaults(handler=cmd_activate_todo)

    # update/delete
    s = sub.add_parser('update'); s.add_argument('kind'); s.add_argument('id', type=int); s.add_argument('--field', action='append', default=[]); s.set_defaults(handler=cmd_update)
    s = sub.add_parser('delete'); s.add_argument('kind'); s.add_argument('id', type=int); s.add_argument('--yes', action='store_true'); s.set_defaults(handler=cmd_delete)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = Path(args.config) if args.config else None
    try:
        client = Client.from_config(cfg)
        result = args.handler(client, args, args.raw)
    except ZentaoError as e:
        sys.stderr.write(f'[zentao error {e.status}] {e.message}\n')
        if e.payload:
            sys.stderr.write(json.dumps(e.payload, ensure_ascii=False, indent=2, default=str) + '\n')
        return 2
    except SystemExit:
        raise
    except Exception as e:
        sys.stderr.write(f'[error] {type(e).__name__}: {e}\n')
        return 1
    _emit(result, args.json)
    return 0


if __name__ == '__main__':
    sys.exit(main())


if __name__ == '__main__':
    sys.exit(main())
