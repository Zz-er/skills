# ZenTao REST v1 endpoint reference

Source: `easysoft/zentaopms` `api/v1/entries/*.php` (community edition).

Base URL: `{host}/api.php/v1/`. Auth header: `Token: <session_id>` returned by `POST /tokens`.

## Conventions

- **Plural** path = collection (`/bugs`, `/tasks`); GET = list, POST = create.
- **Singular** path = item (`/bug/123`, `/task/456`); GET = view, PUT = update, DELETE = remove.
- **Singular + verb** = state transition (`/bugresolve/123`, `/taskfinish/456`); always POST.
- Pagination: `?page=1&limit=20`. Sorting: `?order=id_desc`. Filter: depends on endpoint.

## Auth

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/tokens` | `{account, password}` | `{token}` |

## Products

| Method | Path | Notes |
|---|---|---|
| GET | `/products` | `?status=&program=&project=&mergeChildren=&withUser=` |
| POST | `/products` | required: `name` (and `code` if site uses codes) |
| GET | `/product/{id}` | `?fields=modules,execution,bugStatistic,builds,actions,lastexecution` |
| PUT | `/product/{id}` | fields: program,line,name,PO,QD,RD,type,desc,whitelist,status,acl |
| DELETE | `/product/{id}` |  |

## Projects

| Method | Path | Notes |
|---|---|---|
| GET | `/projects` | `?status=&program=&involved=&order=order_asc` |
| POST | `/projects` | required: `name,begin,end,products` (+`code`); `model=scrum` default |
| GET | `/project/{id}` | `?fields=team,products,stat,workhour,actions,dynamics` |
| PUT | `/project/{id}` |  |
| DELETE | `/project/{id}` |  |
| GET | `/projectbugs/{projectID}` |  |
| GET | `/projectstories/{projectID}` |  |
| GET | `/projectcases/{projectID}` |  |
| GET | `/projectreleases/{projectID}` |  |

## Executions (sprints/stages)

| Method | Path | Notes |
|---|---|---|
| GET | `/executions[/{projectID}]` | `?status=&order=&product=&mergeChildren=&withProject=` |
| POST | `/executions` | required: `name,begin,end`; pass `project` |
| GET | `/execution/{id}` | `?fields=modules,builds,members,stories,actions,dynamics,chartdata` |
| PUT | `/execution/{id}` |  |
| DELETE | `/execution/{id}` |  |
| GET | `/executionbugs/{executionID}` |  |
| GET | `/executionstories/{executionID}` |  |
| GET | `/executioncases/{executionID}` |  |
| GET | `/executionbuilds/{executionID}` |  |

## Stories (requirements)

| Method | Path | Notes |
|---|---|---|
| GET | `/stories[/{productID}]` | `?branch=&status=unclosed&type=story&order=` |
| POST | `/stories` | required: `title,spec,pri,category` |
| GET | `/story/{id}` |  |
| PUT | `/story/{id}` |  |
| DELETE | `/story/{id}` |  |
| POST | `/storyassignto/{id}` | `{assignedTo, comment}` |
| POST | `/storyclose/{id}` | `{closedReason, duplicateStory?, comment}` |
| POST | `/storyreview/{id}` | `{result, reviewedDate, closedReason?, comment}` |
| POST | `/storyactive/{id}` |  |
| POST | `/storychange/{id}` |  |
| POST | `/storyrecall/{id}` |  |
| POST | `/storysubmitreview/{id}` |  |
| POST | `/storyrecordestimate/{id}` |  |

## Tasks

| Method | Path | Notes |
|---|---|---|
| GET | `/tasks[/{executionID}]` | no id → my tasks; `?type=assignedTo&status=&order=` ; `?search=1` enables advanced filter `pri,assignedTo,status,id,name` |
| POST | `/tasks/{executionID}` | required: `name,assignedTo,type,estStarted,deadline` |
| GET | `/task/{id}` |  |
| PUT | `/task/{id}` |  |
| DELETE | `/task/{id}` |  |
| POST | `/taskbatchcreate/{executionID}` | body: `{tasks:[{name,type,...}]}` |
| POST | `/taskstart/{id}` | `{assignedTo,consumed,left,comment,realStarted}` |
| POST | `/taskfinish/{id}` | required: `currentConsumed,realStarted,finishedDate` |
| POST | `/taskpause/{id}` |  |
| POST | `/taskrestart/{id}` |  |
| POST | `/taskclose/{id}` | `{comment}` |
| POST | `/taskactive/{id}` |  |
| POST | `/taskassignto/{id}` | required: `assignedTo` |
| POST | `/taskrecordestimate/{id}` |  |

## Bugs

| Method | Path | Notes |
|---|---|---|
| GET | `/bugs[/{productID}]` | `?branch=all&status=&order=id_desc&limit=20&page=1` |
| POST | `/bugs/{productID}` | required: `title,pri,severity,type,openedBuild` |
| GET | `/bug/{id}` |  |
| PUT | `/bug/{id}` |  |
| DELETE | `/bug/{id}` |  |
| POST | `/bugassign/{id}` | `{assignedTo,mailto,comment}` |
| POST | `/bugresolve/{id}` | `{resolution,resolvedBuild?,resolvedDate?,duplicateBug?,assignedTo?,comment?}` |
| POST | `/bugclose/{id}` | `{comment}` |
| POST | `/bugactive/{id}` | `{assignedTo,openedBuild,comment}` |
| POST | `/bugconfirm/{id}` | `{assignedTo,pri,type,status,deadline,comment}` |
| POST | `/bugrecordestimate/{id}` |  |

## Todos

| Method | Path | Notes |
|---|---|---|
| GET | `/todos` | `?type=all&status=all&order=date_desc,status,begin` |
| POST | `/todos` | required: `name`; defaults date=today,type=custom,status=wait,pri=3 |
| GET | `/todo/{id}` |  |
| PUT | `/todo/{id}` |  |
| DELETE | `/todo/{id}` |  |
| GET | `/todoactivate/{id}` |  |
| GET | `/todofinish/{id}` |  |

## Users / orgs

| Method | Path | Notes |
|---|---|---|
| GET | `/users` | `?full=0&type=bydept&browse=inside` |
| POST | `/users` | required: `account,gender,realname,password` |
| GET | `/user/{id}` |  |
| GET | `/departments` / `/department/{id}` |  |
| GET | `/groups` |  |
| GET | `/stakeholders` |  |

## Plans / programs

| Method | Path | Notes |
|---|---|---|
| GET | `/programs` / `/program/{id}` |  |
| GET | `/productplans` / `/productplan/{id}` |  |
| POST | `/productplanlinkstories/{planID}` |  |
| POST | `/productplanunlinkstories/{planID}` |  |
| POST | `/productplanlinkbugs/{planID}` |  |

## Other

`/builds`, `/build/{id}`, `/releases`, `/release/{id}`, `/testcases`, `/testcase/{id}`, `/testtasks`, `/testtask/{id}`, `/testresults`, `/testsuites`, `/issues`, `/issue/{id}`, `/risks`, `/risk/{id}`, `/feedbacks`, `/feedback/{id}`, `/docs`, `/doc/{id}`, `/doclibs`, `/files`, `/file/{id}`, `/meetings`, `/repos`, `/jobs`, `/pipelines`, `/mr`, `/options`, `/configs`, `/modules`, `/tabs`, `/views`, `/ping`, `/error`.
