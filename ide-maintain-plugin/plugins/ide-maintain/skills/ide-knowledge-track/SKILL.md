---
name: ide-knowledge-track
description: >
  墨斗 IDE 会话期间的知识追踪器。在 ide-context-load 激活后**主动持续运行**，
  会话中识别"新发现的 IDE 项目知识"并追加到 .ide-session-notes.md。
  
  **生效条件**（与 ide-context-load 一致）：cwd 位于以下 10 个墨斗 IDE 仓任一（
  opemindstudio / devicemanager / inktank-occ-master / inktank-node-occ /
  inktank-kdl / robot-workstation / inktank-core / three-editor /
  inktank-master / inktank-platform），或位于 E:\分析\智能焊接\，
  或用户消息含墨斗 IDE 关键词。
  
  触发追加的事件：
  - 用户告诉 Claude 新事实（"X 已经离职" / "Y 模块已重构" / "Z 接口改了"）
  - 用户纠正 wiki 错误认知（"wiki 写错了，实际上..."）
  - Claude 从 git log / 代码 grep / 文件 Read 发现 wiki 未记录的事实
  - 项目决策（如 "v2 task 数变成 X" / "采用方案 A"）
  - 跨仓发现（如 "原来 devicemanager 已经集成 SDK 了"）
  
  用户显式调用 `/ide-knowledge-track <note>` 也手动追加。
---

# IDE Knowledge Track — 会话期间知识追踪

ide-context-load 已经在 cwd 建好了 `.ide-session-notes.md`。**本 skill 在会话中持续运行**，发现新知识时追加。

## 何时追加

| 触发场景 | 示例 |
|---|---|
| 用户给新事实 | "baixiaodong 已离职" / ".weld 改用 AES-256 了" |
| 用户纠正 wiki | "wiki 说 BE 是 opemindstudio.exe，实际是 devicemanager" |
| Claude 跨源发现 | 跑 git log 发现 wiki "活跃 owner" 已 30 天 0 commit |
| 跨仓发现 | "devicemanager 仓里已经有 efort SDK 完整集成" |
| 项目决策 | "Q3 选 C 含具体型号 / 总工时改 134.8d" |
| 关键发现 | "inktank-kdl 内无同步轴算法 grep 全 0 命中" |

**不追加**的：
- 普通代码 read / 一般 task 描述
- 用户重复 wiki 已有的内容
- 临时 debug 信息 / 单次 bug 修复细节（属于 bug-analyze 范畴）

## 追加格式

读 `<cwd>/.ide-session-notes.md`，在末尾追加：

```markdown
## <YYYY-MM-DD HH:MM> · <短标题>

**类型**：[新事实 / wiki 纠正 / 跨源发现 / 决策 / 关键发现]
**关联 wiki**：[[entity-name]] / [[concept-name]] / 无（建议新建）
**内容**：<1-3 句精炼描述>
**证据**：<具体文件路径 + 行号 / git commit hash / 用户原话>
**影响 wiki**：[更新现有 entity X / 新建 concept Y / 标 contradiction / 无需动 wiki]
```

## 追加示例

```markdown
## 2026-05-22 14:30 · baixiaodong 已离职

**类型**：新事实
**关联 wiki**：[[robot-workstation]] / [[inktank-core]]
**内容**：白销东（FE OCC + pathGenerator 唯一深 owner）2026-05 已离职。原 v2 FE-B2 焊缝创建编辑主受致命影响。
**证据**：用户 2026-05-22 直接告知
**影响 wiki**：更新 robot-workstation entity 标注"baixiaodong 已离职"+ 加 contradiction callout 到 inktank-core

## 2026-05-22 15:10 · 埃夫特 SDK 已集成在 devicemanager

**类型**：跨源发现
**关联 wiki**：[[devicemgr]] / [[efort-sdk-integration]]（concept 已新建）
**内容**：devicemanager/core/controller/plugin/efort/sdk/ 含完整 SDK header + lib + bin + 仿真器 + ~150 API 封装。原以为是阻塞，实际已集成。
**证据**：Glob E:\projects\devicemanager\core\controller\plugin\efort\**
**影响 wiki**：更新 devicemgr entity 加 SDK 集成段 / 已新建 concept efort-sdk-integration
```

## 重要原则

1. **不要每个小发现都追加** — 只追加"会让 wiki 错或缺"的发现
2. **追加必须含证据** — 用户原话 / 文件路径 / git hash 至少一项
3. **不在 wiki 直接改** — 本 skill 只追加到会话清单，wiki 更新由 ide-wiki-sync 在任务末提示
4. **不污染 wiki 仓的 git 历史** — `.ide-session-notes.md` 放 cwd，不进 wiki 仓
5. **多个会话在同一 cwd**：`.ide-session-notes.md` 可保留旧条目，新会话追加到末尾（按日期分段）

## 与其他 skill 的协作

| skill | 关系 |
|---|---|
| **ide-context-load** | 上游 — 已建好 `.ide-session-notes.md` |
| **ide-wiki-sync** | 下游 — 任务末读本清单提示用户 |
| **wiki-query** | 平行 — 用户搜索时不影响本 skill |
| **bug-analyze** | 平行 — bug fix 细节不进本清单，但 bug 暴露的架构问题进 |
| **gitlab / zentao** | 平行 — 不需协作 |

## 边界

- `.ide-session-notes.md` 是**会话级临时清单**，不是 SSOT
- project_wiki 仍是知识 SSOT，本清单只是"待同步队列"
- 任务完成后由 ide-wiki-sync 决定哪些条目真正回填 wiki

## Skill 自改进

如发现"追加判断错误"（漏追加 / 多余追加 / 追加内容质量差），在 `<cwd>/.ide-session-notes.md` 末尾另加：

```markdown
## SKILL-IMPROVEMENT
- 漏 / 多余 / 质量差 的情况
- 建议改 SKILL.md 哪段
```

任务末 ide-wiki-sync 处理时一并报告给用户。
</content>
