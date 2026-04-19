# ZenTao field cheat sheet

## Bug

Required on create: `title, pri, severity, type, openedBuild`.

| Field | Type | Notes |
|---|---|---|
| title | string |  |
| pri | int 1–4 | 1 highest |
| severity | int 1–4 | 1 most severe |
| type | enum | `codeerror, interface, designdefect, config, install, security, performance, standard, automation, designchange, newfeature, designissue, others` |
| openedBuild | string\|array | default `["trunk"]`; build name or id |
| product | int | required (path or body) |
| project, execution | int | optional but recommended |
| module, branch, plan | int | |
| story, task, case | int | linkage |
| assignedTo | string | account |
| os | enum | `all, windows, win10, win8, win7, vista, winxp, win2012, win2008, win2003, win2000, android, ios, wp8, wp7, symbian, linux, freebsd, osx, unix, others` |
| browser | enum | `all, ie, ie11, ie10, ie9, ie8, ie7, ie6, chrome, firefox, opera, safari, maxthon, uc, others` |
| steps | string (HTML) | reproduction steps |
| keywords, mailto, deadline | | |
| feedbackBy | string |  |

Resolutions on `bugresolve`: `bydesign, duplicate, external, fixed, notrepro, postponed, willnotfix, tostory`.
Statuses: `active, resolved, closed`.

## Task

Required on create: `name, assignedTo, type, estStarted, deadline`.

| Field | Type | Notes |
|---|---|---|
| name | string |  |
| type | enum | `design, devel, test, study, discuss, ui, affair, misc, request` |
| pri | int 1–4 |  |
| estimate | float | hours |
| consumed, left | float | hours |
| story | int | linked story id |
| execution, project, module | int |  |
| parent | int | parent task id (for subtasks) |
| assignedTo | string |  |
| estStarted, deadline | date | `YYYY-MM-DD` |
| desc | string (HTML) |  |
| mode | enum | `linear, multi` (when multiple=true) |
| multiple | bool | turns on team mode |
| team, teamEstimate | array | per-member assignment |

Statuses: `wait, doing, pause, done, cancel, closed`.
Finish requires `currentConsumed, realStarted, finishedDate`.

## Story

Required on create: `title, spec, pri, category`.

| Field | Type | Notes |
|---|---|---|
| title | string |  |
| spec | string (HTML) | description |
| verify | string (HTML) | acceptance criteria |
| type | enum | `story, requirement, epic` (default `story`) |
| category | enum | `feature, ui, perf, interface, others` |
| pri | int 1–4 |  |
| estimate | float | story points/hours |
| product, branch, module, plan | int |  |
| reviewer | string | account; setting it auto-flips status to `reviewing` if `status=active` |
| status | enum | `draft, active, reviewing, changing, closed` |
| source | enum | `customer, user, po, market, research, competitor, study, other` |
| keywords, mailto | string |  |
| parent | int |  |
| grade | int | maturity |

Story close reasons: `done, subdivided, duplicate, postponed, willnotdo, bydesign, cancel`.
Review results: `pass, reject, revert, clarify`.

## Product

Required on create: `name` (+ `code` if site uses codes).

| Field | Notes |
|---|---|
| program | parent program id |
| line | product line |
| PO, QD, RD | account names |
| type | `normal, branch, platform` |
| acl | `open, private, custom` |
| whitelist | array of accounts |

## Project

Required: `name, begin, end, products` (+ `code`).

| Field | Notes |
|---|---|
| model | `scrum, waterfall, agileplus, waterfallplus, kanban, ipd` |
| multiple | `'on'` or `''` |
| parent | program id |
| PM | account |
| acl | `open, private, custom` |

## Execution

Required: `name, begin, end`. Pass `project`.

| Field | Notes |
|---|---|
| lifetime | `short, long, ops` |
| days | int |
| percent | int (0–100) |
| parent | parent execution |
| PO, PM, QD, RD | accounts |
| products, plans, teamMembers | arrays |

## Todo

Required: `name`.

| Field | Notes |
|---|---|
| type | `custom, bug, task, story, testtask, feedback, ...` |
| date | `YYYY-MM-DD` (default today) |
| begin, end | `HHMM` (no colon) |
| status | `wait, doing, done, closed` |
| pri | 1–4 |
| private | bool |

## Common date/time formats

- `YYYY-MM-DD` for dates (deadline, begin, end on tasks/projects)
- `YYYY-MM-DD HH:MM:SS` for datetimes (resolvedDate, finishedDate, reviewedDate)
- `HHMM` for time-of-day on todos
