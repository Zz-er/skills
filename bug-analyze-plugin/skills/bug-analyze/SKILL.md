---
name: bug-analyze
description: 深入分析 UI 层面描述的 bug（来自禅道或其他 tracker），穿透多层架构（FE / IPC / backend）定位真正的问题层，产出带代码引用、鉴别性提问、多候选方案的结构化分析；产出交给 zentao:zentao 的 comment-bug 发到禅道。Use when user wants to 分析 / 定位 / 深入排查 a bug, 分析 bug #X, diagnose a bug — 特别是多层架构项目 + UI 现象型 bug。Trigger phrases: "分析 bug", "定位 bug #X", "深入分析", "这个 bug 怎么回事", "帮我看看这个禅道 bug", "bug 分析".
---

# Bug 分析 skill — 多层穿透法

## When to use

- 用户给 bug id 或 bug 描述，要求"分析 / 定位 / 深入"
- 项目是多层架构（FE + IPC + backend / 多 repo），bug 报告是 UI 现象
- 在往禅道发评论前做尽调——本 skill 产出直接喂给 `zentao:zentao` 的 `comment-bug`

不用的场景：根因已清楚（直接去修）、纯单层项目、非工程性 bug（产品决策/需求纷争）。

## 核心原则

**测试看到的是 UI 现象，真正的 bug 几乎总在更深的层**。不要把"用户描述的症状"直接当成"bug 所在的层"。

例子（本项目真实案例）：
- "点击按钮没反应" —— 99% 在 FE slot 里，不在 C++ 后端
- "保存后数据丢" —— 可能是 FE 没发 IPC、也可能是 Component 没 AM_FILE 注册
- "模型位置错" —— 可能是 FE raycast 坐标系错，或 devicemanager 返回的 pose 错，或 CoreLib 变换链脏

## 交付结构（每个 bug 4 段）

### 1. 现象
测试 / 用户视角，1-2 句复述。不加解读。

### 2. 代码侧分析（核心价值段）
**深度是本 skill 的价值所在，浅了就等于没分析。**

- 追踪用户动作穿过整个系统：**触发点 → FE 响应 → IPC → backend → 数据 → 返程渲染**
- 每个可能出 bug 的层给出 `file:line` + 函数 / 符号名
- **至少 2 条交叉证据**：不同文件或不同模块独立支持同一假设（孤证不足）
- 指出与"周围约定"的矛盾，这些都是证据：
  - 历史修复里同类问题是怎么处理的？现在这块有没有照做？
  - 相邻代码（兄弟函数 / 同目录）做对了的，当前这段为什么没做？

### 3. 缺的信息（鉴别性提问，不是万能模板）
❌ 错的写法：
- "能否提供重现步骤？"
- "请补充更多上下文。"

✅ 对的写法（每个选项映射到不同代码路径）：
- "拖拽开始**前**的静态显示对吗？
  - 对 → 拖拽过程中变脏，锁定 `setGlobalMatrix` 的缓存问题
  - 不对 → 初始挂载/pose 问题，方向在 Mechanism 构建"
- "其他机器人型号（ER12 等）有没有同样问题？
  - 有 → 加载时默认逻辑问题
  - 没有 → 这两款型号的 param 模板特殊"

每问一个鉴别性问题就把搜索空间减半。问题不超过 3 条，避免轰炸报告人。

### 4. 解决方案（2–3 个候选，标 tradeoff）
至少给 2 个，最好 3 个：
- **最小改动版**：侵入最小，可能只治标
- **根治版**：改动大但系统性，对齐最佳实践
- **绕过版**：UI 提示 / flag / 限制输入，零代码风险但要用户知道限制

每个方案标注：改动文件 / 预估侵入度 / 是否引入新约定。

## 层追踪 checklist（形成假设前走一遍）

对任何 UI 层 bug，**不要跳过追踪**直接猜结论。按这个顺序问自己：

1. **动作从哪里发起**？（哪个 FE 项目 / 面板 / 按钮 / 拖拽手柄）
2. **FE 做了什么**？
   - 纯本地状态变更（FE 内的 store / three.js 场景修改）
   - 调三方库（three.js 计算、几何库）
   - 发 IPC / socket 到后端
3. **若 IPC**：payload 是什么、发到谁（devicemanager? nodejs? 某个 worker?）
4. **若后端**：
   - 计算了什么（几何 / 逻辑）
   - 持久化了什么（写 project.ops / 写模型库目录）
   - 返回了什么（`gib数据` / `occ数据` / 其他）
5. **bug 究竟在**：
   - **数据里**（字段错、字段缺、字段被默认值覆盖）
   - **流程里**（某步没触发、事件没广播、权限没过）
   - **渲染里**（FE 消费数据的方式错、过滤条件错）

**开始分析前先读项目的 CLAUDE.md**。不同项目的分层 / 路由不一样，不能假设。

## Workflow

### 1. 拉 bug 详情
用 `zentao:zentao` 的 `bug <id> --project <pid>` 或 `my-bugs`。捕获：
- 标题、报告人、经办人、严重度、版本号
- 重现步骤（通常是空的或很短）
- 现有评论 / 研发分析（别重复别人的工作）

### 2. 项目归属预判

根据标题关键字 + CLAUDE.md 的架构映射，做**一个调查前的归属表**。每个项目的映射不同；下面是本仓库（opemindstudio 生态）的示例：

| 标题关键字 | 最可能所在层 |
|---|---|
| "创建模型" / "建模" | 建模模块 = `opemindstudio` 的 `OpenmindStudio.exe` |
| "工作站" / "路径" / "机器人" + 交互 | `robot-workstation` (FE vscode 扩展) |
| "拾取" / "渲染" / three.js | `robot-workstation` + `inktank-core` (FE) |
| "保存 / 加载 / project.ops" | `opemindstudio` CoreLib + `devicemanager` |
| "点击没反应" | **几乎一定在 FE slot**（不要去 CoreLib 找） |
| "保存后 / 重新打开后" | 序列化 / 反序列化层，查 `registerAttributes` AM_FILE |
| "字段没变 / 改了没生效" | Component 层持久化 + UI 层 Command 双检查 |
| 特定机器人型号加载失败 / 位置错 | FE `modules/index.ts` 注册表（import / RobotType / getRobotData case 是否齐）|

### 2.3 产品功能模块归类（如果项目 CLAUDE.md 有"产品功能矩阵"/"功能模块"类描述）

先把 bug 按现象关键字归到一个产品模块，再映射到仓库：
- bug 关键字 → 功能模块（例：墨斗 IDE 有 5 大模块，见其 CLAUDE.md 的 "Product context"）
- 功能模块 → 仓库清单（例：模块②"Layout & Path"跨 `robot-workstation`（UI）+ `opemindstudio` CoreLib + `devicemanager`）
- 有 CLAUDE.md 归类时直接用；没有就按标题关键字配合仓库目录名经验判断

### 2.4 IPC 边界意识（重要）

在 FE / IPC / backend 三层框架下，还要判断**IPC 方向**：
- FE → backend（请求-响应）：绝大多数 bug 在这条路径
- backend → FE（主动推送）：容易被漏 — 如果"后端算完了但 UI 没刷新"，可能是推送消息的 channel / 字段变了但 FE 没跟着改
- 本项目示例：`OpenmindStudio.exe` 建模后主动 WebSocket 推 `socket:glbFileAddress` 等到 nodejs，FE 等消息（见本项目 CLAUDE.md）

### 3. 针对性探查
- `Grep` 用于精确定位（symbol / filename 明确时）
- `Agent (subagent_type: Explore)` 用于开放式探查——**每个 agent 给精确子目录范围**，不要让 agent 漫游整个 monorepo
  - 典型拆分：一个 agent 查 FE 一个 repo；另一个 agent 查 CoreLib 相关目录
  - 并行跑，缩短总耗时
- 用 `zentao:zentao` 拉已有的评论、研发分析作为线索

### 4. 起草
按 4 段结构填。每条 bug 分析 **≤ 1500 字符**（装得进一条禅道评论，不用拆）。

### 5. 人工 review（不要跳过）

**永远先给用户看草稿等批准再发**。

- 禅道评论团队可见，把推测当结论发会误导他人
- AI 贡献明确署名：开头放 `(AI 辅助分析)` 或类似标识
- 给多条时一次展示所有草稿，让用户一次性 review

### 6. 批准后发送
用 `zentao:zentao` 的 `comment-bug`：

```bash
python "$CLAUDE_PLUGIN_ROOT/skills/zentao/scripts/cli.py" comment-bug <id> --file <draft_file> --yes
```

或批量脚本（多条时）：
```bash
for id in A B C; do
  python "$CLAUDE_PLUGIN_ROOT/skills/zentao/scripts/cli.py" comment-bug "$id" \
    --file "/path/to/drafts/${id}.txt" --yes
done
```

## 反模式（别做）

| 反模式 | 为什么错 | 正确做法 |
|---|---|---|
| 单层视野（只看后端）分析 UI bug | bug 大概率在 FE，白做功 | 先走层追踪 checklist |
| 问"请补重现步骤" | 问了也没用，报告人给不出 | 问鉴别性二选一 |
| 只给 1 个解决方案 | 剥夺了人做选择的机会 | 给 2–3 个标 tradeoff |
| 直接读代码不读 CLAUDE.md | 架构假设错，分析南辕北辙 | 先读 CLAUDE.md 的 ecosystem / flow |
| 不 review 直接发 | 推测公开发出去误导同事 | 草稿 → 批准 → 发 |
| 不署名 | 同事不知道是 AI 辅助 | 开头 `(AI 辅助分析)` |

## 和 `zentao:zentao` 的集成

本 skill **不直接访问禅道 API**。所有禅道交互都委托给 `zentao:zentao`：

- 拉数据：`zentao:zentao` 读 bug / users / projects
- 发评论：`comment-bug ID --file X --yes`

当 `zentao:zentao` 升级支持 `analysis-update`、`reply-to-comment` 等新能力时，本 skill 的 Workflow 第 6 步跟着升级即可。

## 产出示例（模板）

```
(AI 辅助分析)

### 现象
<1 句话复述测试/用户描述>

### 代码侧分析
<2-4 段，每段带 file:line>
- 关键函数：`Foo::bar` (path/to/foo.cpp:123)
- 交叉证据 1：...
- 交叉证据 2：...
- 与约定的矛盾：... 对比 `Baz::qux` (path/to/baz.cpp:456) 做对了 ...

### 缺的信息（鉴别性）
1. 问题 A？
   - 选项 α → 假设 X 成立，方向在 <路径 A>
   - 选项 β → 假设 Y 成立，方向在 <路径 B>
2. 问题 B？
   - ...

### 解决方案
**A. 最小改动**：<具体改动> — 侵入：低；治标程度：只覆盖 <场景>
**B. 根治**：<具体改动> — 侵入：中；系统性：对齐 <约定>；代价：<X>
**C. 绕过**（可选）：<UI 提示 / 配置 flag> — 零代码风险，但用户需知 <限制>
```

此模板在本 skill 产生的任意分析里都应可辨识。
