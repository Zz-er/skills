# gitlab-plugin

GitLab REST v4 access, wrapped as a Claude Code skill.

A Python port of the `gitlab.ts` module from
[`ModouIDE-Utils`](https://github.com/your-org/modou-utils) (internal Electron
AI-code-review tool). Works with GitLab CE 13.3+ and gitlab.com.

## What it covers

**Read** (no `--yes` needed):

- Projects I can see, optionally scoped to group(s)
- Groups, branches, commits, commit diffs, compare between refs
- Raw file content at any ref
- Open merge requests — global, by project, or by group

**Write** (requires `--yes`):

- Create / delete a branch
- Create a merge request
- Merge an MR
- Comment on a commit or an MR

Not covered: CI pipelines, issues, webhooks, OAuth. Extend `scripts/gitlab.py`
if you need more — each endpoint wrapper is ~10 lines.

## Install

```bash
claude plugin install gitlab
```

## One-time config

```bash
mkdir -p ~/.claude/gitlab
cp "${CLAUDE_PLUGIN_ROOT}/skills/gitlab/config.example.yaml" ~/.claude/gitlab/config.yaml
# edit url + token
pip install -r "${CLAUDE_PLUGIN_ROOT}/skills/gitlab/requirements.txt"
```

Generate a Personal Access Token at `<your gitlab>/-/profile/personal_access_tokens`
with scope `api` (or `read_api` if you only need the read commands).

Config lookup order:
1. `--config <path>` flag on the CLI
2. `$GITLAB_CONFIG` env var
3. `~/.claude/gitlab/config.yaml`
4. `${CLAUDE_PLUGIN_ROOT}/skills/gitlab/config.yaml` (in-tree fallback for dev)

## Talk to Claude

Once configured, just ask in natural language:

```
查一下我在 GitLab 上的待办 MR
把项目 42 的 commit abc1234 的 diff 拉出来给我
帮我在 mygroup/myrepo 上基于 main 建一个分支 feat/hotfix-x
合并一下 MR !17
```

The skill's description includes all of these triggers, so the right CLI
invocation will be picked automatically.

## Directly via CLI

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/gitlab/scripts/cli.py" whoami
python .../cli.py projects --search api
python .../cli.py diff --project 42 --sha abc1234 --json
python .../cli.py mrs --group mygroup
python .../cli.py merge-mr --project 42 --iid 17 --yes
```

See [`skills/gitlab/SKILL.md`](skills/gitlab/SKILL.md) for the full command
reference and `skills/gitlab/references/` for endpoint + field schemas.

## GitLab CE 13.3 compatibility

Self-hosted 13.3 is this plugin's primary target (that's what the upstream
modou-utils project runs against). We deliberately avoid parameters added in
14.x and later:

- `order_by=updated` → use `last_activity_at`
- compare `straight=true` → unset (three-dot is the 13.3 default)
- MR `scope=all` → filter client-side

If you're on a modern instance and want the newer behaviors, open
`skills/gitlab/scripts/gitlab.py` — each method is small and readable.

## License

MIT
