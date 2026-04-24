# Product context — 墨斗 IDE (OpenmindStudio)

> Load-on-demand reference. Applies **only** when the ZenTao instance tracks
> 墨斗 IDE (OpenmindStudio). If the ZenTao instance is used for a different
> product, ignore this file.
>
> This file encodes the bug-routing knowledge that lets the `/zentao` skill
> map a bug title → feature module → related wiki pages, so bug reports come
> with architectural context instead of just a list of titles.

## When to consult

After running any of:

- `my-bugs`
- `bugs --project ...`
- `bug ID --project ...`
- `bug-report --project ...`

…and before summarizing / commenting / handing off to `bug-analyze`, match
each bug's title against the **feature matrix** below to attach the right
module + wiki references.

If `wiki-tools` (a.k.a. LLM Wiki) is available in the environment, fetch the
wiki pages named below via `wiki-tools:wiki-query` (or
`wiki-tools:wiki-query <page-stem>`) for current architectural detail — the
wiki is the authoritative source; this file is just a routing index.

## 产品组成（3 部分 / 7 仓库）

墨斗 IDE 由三层组成；UI bug 可能在任何一层：

- **C++ 层**
  - `opemindstudio` — 建模侧 exe + CoreLib.dll；本文档围绕它编写
  - `devicemanager` — 常驻 C++ 进程，链同一个 CoreLib；负责控制器连接 + 老模型库转换
- **Electron 外壳**
  - `inktank-master` (MoDouIDE) — 基于 VS Code 1.77 fork 的 Electron IDE；宿主
- **前端 webview / 扩展**
  - `inktank-platform` — 控制台 webview（登录 / 账户 / 模板大厅 / 许可证）
  - `three-editor` — 旧 Vue 3 + three.js 建模 webview（**正在被 opemindstudio 替换**）
  - `robot-workstation` — "机器人工作站" VS Code 扩展（变位机 / 路径 / 位姿最终渲染位置）
  - `inktank-core` — npm 包源仓：`@inktank/inktank-editor` (three.js 引擎) + `@inktank/inktank-design-vue` (Vue 控件)；被 `three-editor` 和 `robot-workstation` 共用

相关 wiki 实体页：
- `[[opemindstudio]]`
- `[[modouide-inktank-master]]`
- `[[inktank-platform]]`
- `[[robot-workstation]]`
- `[[three-editor]]`
- `[[inktank-core]]`

## 功能矩阵（① ~ ⑤ 模块 × 关键字 × wiki 页）

绝大多数 UI bug 属于 ①②（建模 + 路径），可能跨 `OpenmindStudio.exe` +
`robot-workstation` + `devicemanager` 三个仓库排查。

### ① Model Builder — 设备建模与轻量化
**关键字**：创建模型 / 夹爪 / 变位机 / 轻量化 / TCP / 本地原点 / 安装点 / 机械结构 / 吸盘 / 导轨 / 传送带 / 托盘 / 通用工具 / 机器人 / 机械装置 / 树结构 / 模板库 / 模型库

**相关 wiki**：
- `[[opemindstudio]]` — 整体架构
- `[[node-component-architecture]]` — SceneNode / Component 分离
- `[[attribute-system-am-file]]` — 属性系统 + `AM_FILE` 持久化 gotcha
- `[[two-stage-picking]]` — 拾取（取边 / 取面）
- `[[predefined-node-factory]]` — 模型创建链路（UI / 模型库 / 工程文件 / legacy 都收敛到 NodeParam + Factory）
- `[[model-library-load-pipeline]]` — 模型库加载 / 保存链路

**这一类 bug 一般涉及的层**：C++（CoreLib 场景图）+ 可能 devicemanager（库转换）+ FE `robot-workstation`（最终渲染）。

### ② Layout & Path — 工作站 + 路径规划
**关键字**：工作站 / 自动路径 / 取边缘 / 取面 / 捕捉 / 点位 / 轨迹 / 测量 / 示教 / 离线编程 / 仿真

**相关 wiki**：
- `[[two-stage-picking]]` — 取边 / 取面直接依赖拾取
- `[[robot-workstation]]` — 场景控件
- `[[node-component-architecture]]` — `InterfaceComponent` / `MechanismComponent`

### ③ System Config — 系统与总线
**关键字**：安全区 / Modbus / MES / 总线 / 多机联动 / 信号

**相关 wiki**：
- `[[node-component-architecture]]`（`SignalComponent`）

### ④ RPL + AI — 编程 + AI
**关键字**：RPL / 代码 / 编辑器 / 变量 / AI BOOT

### ⑤ Simulation — 调试 + 监控
**关键字**：Jog / 断点 / 节拍 / Timer / 报警 / 日志 / 控制面板

## Common failure patterns（速查）

按现象快速定位根因层；验证假设前先贴到 bug 评论或交 `bug-analyze` 深入：

| 现象关键字 | 最可能的根因 | 先查的 wiki 页 |
|---|---|---|
| TCP / 坐标系 / 感应区 / helper / 辅助可视化 不显示 | `RenderQuery.includeHelper=false`；按 workbench 配置 | `[[node-component-architecture]]` |
| "保存后重开字段消失" / 修改 UI 字段后端没变 | `registerAttributes` 漏 `AM_FILE` 或 UI 入口没走 `PUBLISH_CMD_EVT` | `[[attribute-system-am-file]]` |
| 拾取失败 / 取边 / 取面失败 / 新导入模型不可拾取 | `BrepResource._topologyMapper` 空（轻量化丢拓扑）或 `osgRoot` 空 | `[[two-stage-picking]]` |
| 特定机器人型号（ESR / ECR5 等）从模型库加载失败 / 位置错 | FE (`robot-workstation`) `RobotType` 枚举缺 + `addmodel/modules/index.ts` 注册漏 | `[[robot-workstation]]` |
| 4 轴机器人位置错 / 关节信息缺 | FE `Join` 字段默认只到 J4，缺 J5 / J6 | `[[robot-workstation]]` |
| 感应区 / Sensor 不显示 | `SensorComponent` 未实现 `IRenderableProvider::collectRenderables` | `[[node-component-architecture]]` |
| 创建模型后离线编程仿真加载不到工作站 | 跨仓库：CoreLib 导出 gib/occ → devicemanager 转换 → FE 加载 | `[[model-library-load-pipeline]]` + `[[robot-workstation]]` |
| "树结构混乱" / "重置机械装置后" | SceneRoot UUID 重映射（`remapIds`） + 组件 `_unique` 约束 + Component 生命周期顺序 | `[[node-component-architecture]]` + `[[predefined-node-factory]]` |
| "创建 X 后打开详情添加 Y 详情页无内容" | UI 状态 / Vuex 模块 / Component 属性未持久化 | `[[attribute-system-am-file]]` + FE `[[vuex-module-decorators-pattern]]` |

## 模型库 I/O 跨仓库链路（bug 归属判断用）

- **上传模型库**（用户点"上传模型库"）：
  `OpenmindStudio.exe` (`FileDomainImpl::saveLibrary`) → 本地 `Context::modoumodelpath/<uuid>1/` → socket 通知 nodejs 前端注册。
  **不经过 devicemanager**。
- **加载模型库**（前端请求）：
  `robot-workstation` FE → `devicemanager` → 读本地模型库 → 返回 `gib`（≈glb 渲染）+ `occ`（BRep 拓扑）。
- 旧 nodejs + gyp 直读路径已**弃用**，遇到可忽略。

对 bug 分析的启示：前端看到的渲染/拾取问题，可能在 3 层任意一层：
1. FE three.js 消费 gib/occ 数据时逻辑错；
2. devicemanager 返回的 gib/occ 包缺字段（CoreLib export 问题）；
3. CoreLib 场景构建本身错。

**排查顺序建议从 FE 往下溯**。

## 工作流（bug 分析）

1. 用 `my-bugs` / `bugs` / `bug ID` 拿到标题和复现步骤。
2. 对照上面的**功能矩阵**：标题关键字命中哪个模块？命中了写进分析产物开头。
3. 对照**Common failure patterns**：现象能否直接匹配一条经典根因？能就作为首选假设。
4. 如果 wiki-tools 可用，调 `wiki-tools:wiki-query` 取命中 wiki 页的最新内容（wiki 页随源码演进，比本文件新）。
5. 如果是跨层 UI bug（涉及前端 + IPC + C++），优先调 `bug-analyze` skill —— 它强制全链追踪 FE → IPC → backend，避免单层视野。本文件只是入口路由，深度分析仍走 `bug-analyze`。
6. 回写 bug（`comment-bug ID --body ... --yes`）时：先贴"归属模块 + 怀疑层 + 鉴别性提问"，避免直接下结论。

## 已知过期引用（随时可能修复）

- `CLAUDE.md` 中 "`Picker.cpp:87` 早退" 实际位置在 `Picker.cpp:52`；87 行是 BRep 空拓扑检查。详见 `[[two-stage-picking]]`。

## 维护

- **不要把产品专有术语硬编进 SKILL.md 主体** —— 那会让 skill 在其它 ZenTao 实例下噪音。所有产品细节放这里。
- wiki 页演进后，本文件的 "相关 wiki" 列表需要同步。字段级的详细 schema / 行号引用**不要放这里**，那里太易过期；只保留稳定的关键字 → wiki 页的映射。
- 新增功能矩阵条目请先与 `opemindstudio/CLAUDE.md` 的 "Product context" 对齐。
