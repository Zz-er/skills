---
name: ide-context-load
description: >
  墨斗 IDE 项目入口加载器。当用户在以下任一条件下工作时**自动激活**，
  从 project_wiki 加载相关 entities + concepts，并启动 ide-knowledge-track
  会话清单：
  - cwd 位于墨斗 IDE 关联仓库（opemindstudio / devicemanager / inktank-occ-master /
    inktank-node-occ / inktank-kdl / robot-workstation / inktank-core /
    three-editor / inktank-master / inktank-platform）
  - cwd 位于 `E:\分析\智能焊接\` 或子目录（S13-任务拆分-v2 / S13-工作包分配 / archive 等）
  - 用户消息含关键词：墨斗 / 焊接 / CoreLib / WeldCurveResource / WeldPlanningAdapter /
    devicemanager / inktank / 埃夫特 / Robox SDK / KDL 同步轴 / 模型库 / 拾取聚合
  - 用户显式调用 `/ide-context-load`
  也在 reimpl-tutorial / bug-analyze / 等其他 skill 启动前主动调用以获取背景。
---

# IDE Context Load — 墨斗 IDE 项目入口加载

你在准备开始一个**墨斗 IDE 关联任务**。先从 `project_wiki` 加载相关背景，避免重新探索已经沉淀的认知。

## 关键路径

| 资源 | 路径 |
|---|---|
| **project_wiki 根** | `E:\projects\agents\project_wiki\` |
| wiki 索引 | `E:\projects\agents\project_wiki\wiki\index.md` |
| wiki entities | `E:\projects\agents\project_wiki\wiki\entities\` |
| wiki concepts | `E:\projects\agents\project_wiki\wiki\concepts\` |
| wiki sources | `E:\projects\agents\project_wiki\wiki\sources\` |
| wiki log | `E:\projects\agents\project_wiki\wiki\log.md` |
| **S13 智能焊接项目** | `E:\分析\智能焊接\` |
| S13 入口（含 _claude/）| `E:\分析\智能焊接\CLAUDE.md` |
| S13 数字 SSOT | `E:\分析\智能焊接\S13-任务拆分-v2\_manifest.yaml` |

## 加载流程

### Step 1 — 识别当前任务上下文

判断哪些 wiki 条目可能相关：

| 当前 cwd / 任务关键词 | 应加载的 wiki entities | 应加载的 wiki concepts |
|---|---|---|
| `opemindstudio` 仓 | opemindstudio | node-component-architecture / attribute-system-am-file / command-pattern-undo-redo / two-stage-picking / weld-curve-resource / weld-planning-adapter / collision-detection-architecture |
| `devicemanager` 仓 | devicemgr / efort-sdk-integration | data-source-ownership / weld-planning-adapter |
| `inktank-occ-master` / `inktank-node-occ` 仓 | inktank-occ-master / inktank-node-occ | two-stage-picking / fe-picking-pipeline / data-source-ownership |
| `inktank-kdl` 仓 | inktank-kdl | synchronous-axis-implementation |
| `robot-workstation` 仓 | robot-workstation / inktank-core | fe-picking-pipeline / vuex-module-decorators-pattern / electron-webview-ipc-bridge |
| `three-editor` 仓 | three-editor | three-editor-debugging / electron-webview-ipc-bridge |
| `inktank-master` / `inktank-platform` 仓 | modouide-inktank-master / inktank-platform | electron-webview-ipc-bridge |
| `E:\分析\智能焊接\` 下 | 全部（焊接 + 墨斗 IDE 生态）| weld-curve-resource / weld-planning-adapter / efort-sdk-integration / synchronous-axis-implementation / collision-detection-architecture / data-source-ownership / product-matrix |
| 智能焊接关键词 | 全部（按用户问的主题筛）| 同上按需 |

### Step 2 — 读 wiki 索引 + 相关条目

```
Read E:\projects\agents\project_wiki\wiki\index.md
```

再按 Step 1 表格筛出的 entities + concepts，**逐个 Read**。

### Step 3 — 检查 S13 智能焊接项目状态（如相关）

如果 cwd 或任务涉及智能焊接 v2：

```
Read E:\分析\智能焊接\CLAUDE.md       # 30 秒速览
Read E:\分析\智能焊接\_claude\01-项目状态.md   # 当前阶段 + ToDo
Read E:\分析\智能焊接\_claude\04-阻塞与未决.md  # 关键阻塞
```

不要 Read 全部 v2 文档，按 CLAUDE.md 索引按需进入。

### Step 4 — 初始化会话知识清单

在 cwd 下创建 / 追加 **`.ide-session-notes.md`**（如不存在则建）：

```markdown
# IDE Session Notes — <YYYY-MM-DD HH:MM>

> 本会话期间新发现的 IDE 项目相关知识。任务完成时由 ide-wiki-sync 提示同步到 project_wiki。

## 本次会话上下文
- cwd: <当前路径>
- 任务: <用户首次消息简述>
- 已加载 wiki 条目: [[entity-1]] [[concept-1]] ...

## 新发现知识（追加，不覆盖）

_(待 ide-knowledge-track 追加)_
```

### Step 5 — 给用户简短的"已加载"回执

输出**简短**的加载摘要（≤5 行），形如：

```
📚 已从 project_wiki 加载墨斗 IDE 背景：
- entities: opemindstudio / devicemgr / inktank-occ-master  
- concepts: weld-curve-resource / efort-sdk-integration
- S13 项目状态：Phase B 完成 / M0 待启动 / 5 项 P0 待 sign-off
- 会话知识清单 .ide-session-notes.md 已就位
准备开始任务。
```

**不要**复述 wiki 详细内容 — 用户没问就不要倒。

## 与其他 skill 的协作

- **进入任何 IDE 关联任务前**：本 skill 主动激活，给 Claude 自身上下文
- **bug-analyze / reimpl-tutorial / wiki-query** 等其他 skill 启动前可显式调用 `/ide-context-load`
- **会话期间**：`ide-knowledge-track` 接管，追加新发现到 `.ide-session-notes.md`
- **任务结束**：`ide-wiki-sync` 提示用户更新 project_wiki

## 边界

- 不修改 project_wiki（只读加载）
- 不替代 wiki-query — wiki-query 是按需搜索，本 skill 是项目入口预加载
- 会话知识清单 `.ide-session-notes.md` 放当前 cwd（不污染 project_wiki）

## Skill 自改进

如发现 wiki entities/concepts 与现实仓库实际状态不一致（如 wiki 说 baixiaodong 是 owner 但实际已离职），**不要在加载阶段尝试修正** — 标到 `.ide-session-notes.md` 的"新发现"段，由 ide-wiki-sync 在任务末统一处理。
</content>
