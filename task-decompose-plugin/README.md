# task-decompose

理论背书的任务拆分方法论 skill。把一个项目/一批需求拆成可并行的任务线、做需求↔线映射、加桩解耦、识别真约束、定排期与集成 owner。

## 提供的 skill

- **task-decompose** — 触发于"拆分任务 / 工作包 / 需求映射 / 并行线 / 排期 / 多团队怎么分 / 这么拆合理吗"。

## 核心方法（8 步）

1. 两套独立分解：按模块切"线"（Parnas 高内聚低耦合）+ 按能力列"需求"（WBS 100% 规则）
2. 需求×线 映射矩阵（DMM）+ 全覆盖核对
3. 多对多 → 每个集成型需求钦定主责线 + 集成 owner（single-threaded owner）
4. 识别使能线（complicated-subsystem）→ 不独立验收
5. 跨线依赖加桩解耦（DSM tearing + test double）
6. 识别真约束（TOC，常是人力非技术依赖）
7. 关键链 buffer（集中项目缓冲 + 消耗率）
8. 维护 SSOT 防数字漂移

## 健康判据

覆盖性 / 主责性 / 可交付性 —— 而非"1:1 映射"。

## 理论基础

DSM/MDM · WBS · Parnas 信息隐藏 · DMM 域映射矩阵 · 康威定律 · TOC 约束理论 · 关键链 CCPM · Team Topologies · test double。

## 维护

**living skill** —— 真实项目踩到新坑/新模式时，追加到 SKILL.md 的「经验累积」区，并按 semver 在 `.claude-plugin/plugin.json` 升版本（patch=措辞、minor=新模式/新章节、major=输出格式破坏性变更）。

首个 worked example：智能焊接 v2（`E:\分析\智能焊接\S13-任务拆分-v2\`）。
