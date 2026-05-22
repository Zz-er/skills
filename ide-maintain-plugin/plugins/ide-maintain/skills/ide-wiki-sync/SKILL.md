---
name: ide-wiki-sync
description: >
  墨斗 IDE 任务完成时的 wiki 同步提示器。在以下场景**主动激活**：
  - 用户说"任务完成" / "今天就到这" / "好了" / "搞定" / "可以收尾了" 等
  - 用户切换主题（从 IDE 任务转到无关话题）
  - 长时间会话即将进入压缩（compact）前
  - 用户显式调用 `/ide-wiki-sync` 或 "更新 wiki"
  
  做的事：读 .ide-session-notes.md 全部新发现条目，**主动提示用户**决定哪些回填到
  project_wiki（entity 更新 / 新建 concept / 标 contradiction 等）。
  
  不自动写 wiki — 用户确认后才动手。
---

# IDE Wiki Sync — 任务完成时同步提示

会话结束前的最后一步：把 `.ide-session-notes.md` 攒下的新知识同步回 `project_wiki`，避免下次会话重复探索。

## 关键路径

| 资源 | 路径 |
|---|---|
| 会话清单 | `<cwd>/.ide-session-notes.md` |
| project_wiki 根 | `E:\projects\agents\project_wiki\` |
| wiki 索引 | `E:\projects\agents\project_wiki\wiki\index.md` |
| wiki log | `E:\projects\agents\project_wiki\wiki\log.md` |

## 同步流程

### Step 1 — 读会话清单

```
Read <cwd>/.ide-session-notes.md
```

提取本次会话所有"新发现"条目（按 `## <时间> · <标题>` 分段）。

### Step 2 — 分类待同步条目

按"影响 wiki"字段把条目分桶：

| 桶 | 含义 | 处理方式 |
|---|---|---|
| 🔄 **更新现有 entity/concept** | wiki 已有页，需要补充 / 纠正 | Edit 对应 .md |
| 🆕 **新建 entity/concept** | wiki 没有但应该有 | Write 新 .md + 更新 index.md |
| ⚠️ **标 contradiction** | wiki 与现实矛盾，需要 callout | Edit 对应 .md 加 `> ⚠️ Contradiction:` |
| ❌ **无需动 wiki** | 临时 / 单次 / 已通过其他途径回写 | 跳过 |

### Step 3 — 主动提示用户（重要！不要自动写 wiki）

输出**结构化提示**，给用户决定：

```markdown
📋 会话即将结束 — 检测到 N 项新知识待同步到 project_wiki：

## 🔄 更新现有 wiki 页（X 项）
1. [[devicemgr]] — 加埃夫特 SDK 集成段
2. [[robot-workstation]] — 标 baixiaodong 已离职 contradiction
...

## 🆕 新建 wiki 页（Y 项）
3. concepts/synchronous-axis-implementation — KDL 同步轴新写方案
...

## ⚠️ 标 contradiction（Z 项）
4. [[inktank-kdl]] — wiki 说"含同步轴算法"实际 grep 0 命中
...

**请选择**：
- [A] 全部同步（自动执行所有更新）
- [B] 逐条 review（每条问一次）
- [C] 仅同步 P0 项（标 critical 的）
- [D] 跳过本次同步（清单保留到下次会话）
- [E] 自定义（告诉我哪些做哪些不做）

如选 A/B/C/E，确认后我会逐条 Edit wiki 文件 + 更新 wiki/log.md + 清空 .ide-session-notes.md 本次条目。
```

### Step 4 — 按用户选择执行

#### 选 A 全部同步

逐条执行 Edit / Write。每条完成后：
1. 更新对应 wiki entity / concept 的 frontmatter `updated:` 字段
2. 如新建 concept，**追加** wiki/index.md（保留所有现有 entries）
3. 追加 wiki/log.md（按日期分段，append-only）

完成后：
- 在 `.ide-session-notes.md` 加 `## ✅ 已同步 to wiki @ <YYYY-MM-DD HH:MM>` 标记本次条目
- 不删除清单（保留追溯）

#### 选 B 逐条 review

对每条用 AskUserQuestion 工具（如可用）或简短问答方式确认：
```
[1/N] 更新 [[devicemgr]] — 加埃夫特 SDK 集成段（约 50 字）？
  - 同步 / 跳过 / 修改文案
```

#### 选 C 仅同步 P0 项

筛 `.ide-session-notes.md` 里标 `**类型**：关键发现 / wiki 纠正` 或在内容里有 ⚠️ 的条目，按 A 流程执行。

#### 选 D 跳过

输出：
```
✓ 本次跳过 wiki 同步。`.ide-session-notes.md` 保留全部条目，下次会话激活 ide-context-load 时会再次提示。
```

#### 选 E 自定义

接用户的具体指令（如"只做 1, 3, 5"）执行。

### Step 5 — 同步后的清理 + 日志

每完成一次同步：
1. 在 `.ide-session-notes.md` 对应条目下加 `**同步状态**：✅ 已写入 <wiki-page>` 标注
2. 追加 `E:\projects\agents\project_wiki\wiki\log.md`：

```markdown

## <YYYY-MM-DD> — IDE Session Sync · <cwd 短标>

由 ide-maintain skill 在任务末同步：
- 更新 entities: [[xxx]] [[yyy]]
- 新建 concepts: [[zzz]]
- 标 contradiction: [[aaa]]
- 来源会话清单: <cwd>/.ide-session-notes.md
```

3. **不删 `.ide-session-notes.md`** — 保留作为审计追溯

## 不主动同步的情况

| 场景 | 原因 |
|---|---|
| `.ide-session-notes.md` 为空或仅有"无需动 wiki"条目 | 没东西可同步，跳过提示 |
| 用户明确说"先不更新 wiki" | 尊重用户决定 |
| 会话还在进行中（仅切话题）| 等真正"结束"信号 |
| 同步会与并发其他 agent 冲突 | 提示用户："另有 agent 正在写 wiki，建议人工同步" |

## 与其他 skill 的协作

| skill | 关系 |
|---|---|
| **ide-context-load** | 上游 — 会话开始时建好清单 |
| **ide-knowledge-track** | 上游 — 会话中追加条目 |
| **wiki-update** | 下游兄弟 — 真正写 wiki 时调用相同模式（frontmatter / index / log）|

## 边界

- 不自动写 wiki — 必须用户确认
- 不删 `.ide-session-notes.md` 内容（保留审计）
- 不动 raw/ 下原始文档
- 不修 project_wiki 的 git 配置 / CI

## Skill 自改进

如发现"该提示但没提示"或"提示了但用户跳过过多"，在 `<cwd>/.ide-session-notes.md` 末尾追加 `## SKILL-IMPROVEMENT` 段。下次会话 ide-context-load 加载时会看到。
</content>
