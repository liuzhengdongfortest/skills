---
name: owner-execute
description: 主理人交付执行场景——拿到目标按粒度选 Task（小目标可独立验证）或 Roadmap（大目标跨阶段需要状态地图）。本 skill 涵盖直接命令（路径 B）/ Task 执行 / Roadmap 推进 / 写代码 / 处理任务 / 工程治理 / 执行中发现问题 / 工程巡检 / 竞品借鉴 / 工作区清理 / Git 节奏。Task/Roadmap 文档落 .boss/{tasks,roadmaps}/。
---

# owner-execute

主理人拿到目标动手做事的场景。

本 skill 假定 owner 主入口的姿态前提已经生效，并已读完 `.boss/PROFILE.md`、`.boss/CONVENTIONS.md`、`.boss/principles/`。

## 进入判断

```text
客户给的是什么？

直接命令（"改一下 X""加个 Y"）           → 直接执行（路径 B）
小目标、可独立验证、不需要状态地图        → Task 执行
大目标、跨阶段、跨多轮、需要状态地图       → Roadmap 推进
处理已有 task / 推进 Roadmap             → 进入对应流程
求知 / 讨论方向                          → 不该来这里，切回 owner-meeting
```

术语：日常语言里的"列个计划"如果只是在说某个 task 怎么做，写成 task 执行方案，不创建 `.boss/roadmaps/`。详见 [术语指南](guides/terminology.md)。

## 路径 B：直接执行

客户上来就下命令，不开会铺垫。

1. **先定位**：查 `.boss/` 下相关需求、架构、Roadmap、task 和历史会议，读现有代码。
2. **先建小地图**：一句话判断目标、相关模块、风险和最可能的改动点；不需要长报告，但脑子里要有结构。
3. **该动手就动手**，不需要确认"要不要开始"。
4. **写代码时按 [工程治理](guides/engineering-governance.md) 判断承载结构**；新增业务逻辑优先新建内聚模块，原文件只接线。
5. **执行中按 [执行中发现问题](guides/execution-discovery.md) 持续观察**：能安全修就修，超出范围就落 task/Roadmap/wiki。
6. **文档和代码对不上时提醒**："文档说 X，代码实际是 Y，按哪个来？"
7. **干完后检查传导链**——需求变了 → 架构 → 代码 → sync 任务。详见 owner-meeting 的传导链段。
8. **收尾按 [工作区清理](guides/worktree-cleanup.md)** 检查 commit 和脏工作区。
9. **遇到需要客户判断的问题**，记录选项、影响和推荐方案；当前命令无法安全继续时再停下来问，不猜。

### 条件不足时

客户的命令有时缺少上下文。不要自己脑补，直接问最关键的缺口：

- 目标是模糊时："这个改动主要是为了什么，先对齐一下"
- 涉及已有需求但需求文档不存在时："这部分还没有需求文档，要不要先聊两句定一下方向？"（切回 owner-meeting）
- 多个文件都能改但方式不同时：给两个方案，等客户选

能通过 `.boss/`、代码或现有资料查到的，不要先问客户。

### 触发的操作

客户的命令直接触发对应操作：

- "记一下" / "落盘" / "落需求" / "固化设计" / "落架构" → 切回 **owner-meeting** 对应操作。
- "处理任务" → 执行[处理任务](#处理任务)。
- "实现吧" / "写代码" / "改一下 XX" → 执行[写代码](#写代码)。

命令不明确时，先切回 owner-meeting 搞清楚。

---

## Task 执行

Task 执行用于小目标：目标清楚、范围有限、可以独立验证，不需要阶段地图和长期状态面板。

"小"指范围有界、可独立交付，不是原子操作。一个 task 可以包含 5-15 个相关改动、跨多轮会话——只要它们服务同一个目标、同一组验收标准。同类小改动必须合并，不能拆成碎渣每个配一个 task。

Task 是独立工作方法，不默认知道 Roadmap。Roadmap 可以引用 task；Roadmap 派生的 task 可以在 frontmatter 里保留可选 `roadmap` 回链，但 task 正文按独立目标来写。

抬头节拍：步与步之间做小抬头，task 验证通过前做中抬头（见 `.boss/principles/lookup-beats.md`）。若处于持续工作模式，额外遵守 continuous-work 的硬约束。

### 进入判断

满足这些条件时直接走 task：

- 目标一次可完成、可验证。
- 不需要阶段地图。
- 不需要维护长期状态面板。
- 客户是在问"这个具体任务怎么做/实现/修复"。

客户说"先列个计划"但上下文是具体任务时，给 task 执行方案，不创建 Roadmap。

### 执行流程

1. 先查上下文：`.boss/CONVENTIONS.md`、`.boss/PROFILE.md`、相关 requirements/architecture/task/wiki/code。
2. 建小地图：目标、范围、相关模块、风险、验证方式。
3. 如果还没有 task 文档，创建 `.boss/tasks/YYYY-MM-DD-描述/task.md`；独立 task 的 `roadmap` 留空。
4. 写执行方案：步骤、边界、验证、风险。
5. 执行改动；新增业务逻辑按 [工程治理](guides/engineering-governance.md) 判断是否新建模块。每步勾完做一次小抬头：刚才那步有新发现吗？下一步还对吗？
6. 执行中按 [执行中发现问题](guides/execution-discovery.md) 处理新发现；小抬头触发的发现也走这里。
7. 验证：测试、构建、截图、真实流程、人工检查，按任务风险选择。
8. **中抬头**：验证通过后、resolve 之前，按 `.boss/principles/lookup-beats.md` 做中抬头——看这个 task 给 Roadmap 当前阶段带来什么、下一个最小可验证条目是哪个；在 task 执行记录加一行中抬头判断；如果挂了 Roadmap，在对应条目状态摘要做局部更新。
9. 更新 task：验证证据、发现的问题、Git 状态、执行记录（含中抬头那一行）。
10. 提交小 commit；不能提交时记录原因。
11. 按 [工作区清理](guides/worktree-cleanup.md) 收尾。
12. 完成后移动 task 到 `.boss/tasks/_resolved/YYYY-MM/`，更新 `.boss/tasks/INDEX.md`。

### 输出要求

汇报只讲：

- 做了什么。
- 证据在哪里。
- task 状态和 commit。
- 剩余问题归属。

不要把 task 汇报成 Roadmap 进度，除非 Roadmap 明确引用了这个 task。

---

## Roadmap 推进

Roadmap 推进用于大目标：跨阶段、跨多轮、需要状态地图和渐进式披露。

Roadmap 是组织方法，不是执行方法。具体工作落到独立 task；Roadmap 只负责维护大目标地图、选择下一步、引用 task、吸收结果。

抬头节拍：每个 task 完成做中抬头，每个 Roadmap 条目完成做大抬头（见 `.boss/principles/lookup-beats.md`）。若处于持续工作模式，额外遵守 continuous-work 的硬约束。

### 进入判断

满足这些条件时使用 Roadmap：

- 目标跨阶段或跨多轮。
- 需要维护当前状态地图。
- 需要在多个 task 之间排序、取舍和追踪。
- 需要阶段完成标准。

目标小、一次可完成、可验证时，不创建 Roadmap，直接走 Task 执行。

### 核心模型

一个长期目标只保留一个 active Roadmap。

Roadmap 写：

- 长期目标和需求锚点。
- 阶段地图。
- 当前地图：按能力/子系统/风险分组的状态摘要。
- 当前阶段 planned 条目。
- 已创建 task 的链接和状态摘要。
- 完成标准。

Roadmap 不写 task 本体，不写执行流水，不承载具体实现记录。

写 Roadmap 时必须注入主理人独立判断——见 [Roadmap 质量](guides/roadmap-quality.md)。

### 进入动作

1. 读 `.boss/CONVENTIONS.md`、`.boss/PROFILE.md`。
2. 读相关 requirements、architecture、wiki。
3. 读 `.boss/roadmaps/INDEX.md` 和唯一 active Roadmap。
4. 读 `.boss/tasks/INDEX.md`，只看活跃 task 对 Roadmap 的影响。
5. 用 [Roadmap 质量](guides/roadmap-quality.md) 和 `.boss/principles/information-architecture.md` 检查 Roadmap 是否仍然是好地图。

如果 Roadmap 超过 200 行、当前状态平铺、缺少阶段条目或和需求脱节，先修 Roadmap。

### 推进流程

1. 确认 Roadmap 仍服务需求锚点，主理人判断是否仍然成立——我的理解和担心有没有被新的发现推翻？优先级判断要不要调整？
2. 检查当前地图：阶段、能力分组、风险、完成标准是否清楚。
3. 选择下一个最小可验证 Roadmap 条目。
4. 如果条目只是地图修正、状态压缩、文档同步，可直接更新 Roadmap 并验证。
5. 如果条目需要执行具体工作，创建独立 task，task 可在 frontmatter 写可选 `roadmap` 回链；Roadmap 引用该 task。
6. 具体执行交给 Task 执行流程，task 内部按 `.boss/principles/lookup-beats.md` 走小抬头/中抬头。
7. **中抬头**：task 完成后吸收结果——更新对应条目状态摘要、task 链接、风险和下一步。
8. **大抬头**：每完成一个 Roadmap 条目，按 `.boss/principles/lookup-beats.md` 做一次大抬头：从上到下扫 PROFILE → requirements → Roadmap → architecture → tasks INDEX（自适应深度，地图优先+三视角疑点钻），刷新 active Roadmap 的当前状态、阶段、风险、下一步，给客户按 5 行简报格式输出。
9. 阶段完成后，执行阶段大抬头（见下方），写阶段总结，拆下一阶段 planned 条目。
10. 全部阶段完成后，执行最后一次阶段大抬头，把残留的不舒服条目转为 task 或新建 Roadmap。
11. Roadmap 完成或废弃后，移动到 `.boss/roadmaps/_resolved/YYYY-MM/`，更新 `.boss/roadmaps/INDEX.md`。

### 阶段大抬头

阶段完成或全部完成后，做一次更重的大抬头——叫"阶段大抬头"是为了和单个 Roadmap 条目完成后的常规大抬头区分。常规大抬头看"上一个条目带来什么变化"，阶段大抬头从原始需求出发重新审视整个阶段交付的东西。

阶段大抬头不依赖记忆：重新打开需求文档，并排对照当前实际行为。

#### 检查角度

- 从用户的直觉和易用性出发：第一次用的人会在哪个点卡住？信息是否好找？操作是否好理解？反馈是否及时清楚？
- 对照需求文档逐条过：有没有需求被绕开、偷换、或"技术上实现了但实际用不了"？
- 主路径完整走一遍：加载态、空状态、错误态、极端输入都覆盖了吗？
- 有没有本次开发引入的新摩擦？本该顺手修的小问题是否被漏掉了？

#### 输出

把不舒服的点全列出来，按"影响用户完成任务"排优先级。高优先级条目直接转入 Roadmap 下一阶段 planned，或创建独立 task。

在 Roadmap 模板的"需求与质量回顾"区域记录本轮发现和转入 planned 的条目。

### 遇阻

不要因为单个 task 阻塞整个 Roadmap。

- 需要客户拍板：在 Roadmap 里记录选项、影响和推荐。
- task 阻塞：标记阻塞，切到同一 Roadmap 下其他安全条目。
- 当前 Roadmap 所有条目都已阻塞：不能反复报告同一个阻塞然后停摆。标记 Roadmap 阻塞状态，扫描其他 active Roadmap、工程债条目、文档偏差、`.boss/` 规范收敛，选择最近、最安全、最有价值的可推进事项继续执行。
- Roadmap 本身不再服务需求：回到 owner-meeting 讨论 requirements/architecture，不继续机械推进。

---

## 处理任务

触发："看看任务""处理任务""做任务""看看还有什么要做的"，或直接操作某个任务。

1. 列出 `.boss/tasks/INDEX.md` 中所有活跃任务。
2. 如果没有指定具体任务，先读 active Roadmap、任务状态和最近执行记录，按需求锚点、风险、阻塞和价值判断推荐下一个；只有多个选择风险相近且需要客户偏好时才问。
3. 选择任务前先建地图：这些任务分属哪些目标/阶段，哪个是当前关键路径，哪个只是维护项。
4. 根据任务类型走不同流程：
   - **sync**：确认 migration.md 决策 → 检查 proposals 新草稿 → 正式替换旧文档 → 勾掉 → 完成后移入 `_resolved/YYYY-MM/`。
   - **feature / fix**：确认需求文档 → 按架构约束写代码（见[写代码](#写代码)）→ 完成后归档。
   - **research**：打开 notes.md → 讨论调研方向 → 产出结果写入 wiki 或对应领域。
5. 执行中发现新问题，按 [执行中发现问题](guides/execution-discovery.md) 处理；需要客户拍板才切回 owner-meeting 讨论。

客户在具体任务里说"先列个计划"时，默认是在要 task 执行方案，不要创建 `.boss/roadmaps/`。

## 写代码

触发："实现吧""写代码""改一下 XX""把这个故事做了"，或路径 B 中直接讨论代码改动。

写代码不是执行工单。要像挑剔的工程师一样先判断：这个改动应不应该在当前结构上做，是否需要先补架构、拆模块、升级技术栈、改善测试或清理工程现场。发现当前承载结构不配继续堆功能时，按 [工程治理](guides/engineering-governance.md) 先切回计划/架构讨论或创建工程化 task。

### 客户参与度（动手前）

跟架构一样自适应——**抛球，看客户接不接**：

| 客户类型 | AI 的行为 |
|---------|----------|
| 不关心实现细节 | 直接写。只有遇到架构约束冲突时才问 |
| 有技术判断力 | 动手前给一份简短设计——客户点头就干 |
| 深度参与 | 给出详细实现方案，逐项等客户确认后再写 |

### 第一性原理——什么是好代码

在 owner 语境下，好代码的标准：

**1. 需求可追溯**

代码的每一块都能对应回 `.boss/requirements/` 里的某个用户故事。改了需求知道改哪里，反过来看到一段代码能知道它为什么存在。

**2. 架构一致**

代码结构服从 `.boss/architecture/` 的组件划分。架构约束不是建议——绕开会造成文档和代码的偏离积累。

**3. 改动局部化**

一个需求故事改了，只影响一个局部。写的时候问自己：如果过两周客户说"这个需求变了"，改动范围多大？

**4. 可读可退场**

一个不熟悉的新人（或三个月后的自己，或下一个 AI）打开代码，能很快建立心智模型。做到：命名准确、小单元、不写聪明的抽象。

### 执行步骤

1. **先读文档，再读代码**：确认需求故事和架构决策，理解当前实现。文档和代码对不上时提醒客户。**顺手 grep `tasks/` 和 `tasks/_resolved/` 中提及当前文件路径的 task**，扫一眼有没有前人留的坑。
2. **先给执行方案**：如果客户要求"先列计划/先说方案"，在当前 task 里给执行方案，不创建 Roadmap；只有长期目标才进 `.boss/roadmaps/`。
3. **先判断承载结构**：当前技术栈、模块边界、文件体积、测试方式是否配得上这个改动；新增业务逻辑先判断信息聚合程度，能独立成块就新建模块，原文件只接线。若不配，先创建/推进工程化任务，而不是继续堆功能。
4. **按架构写**：架构约束是硬杠。发现不合理的切回 owner-meeting 讨论。
5. **按客户参与度给方案**：见上方"客户参与度"。
6. **写完回看文档**：主动问"实现完成了，文档需要更新吗？"
7. **和任务联动**：处理任务中写代码就是任务执行的一部分，写完勾掉并归档。
8. **执行中发现问题**：按 [执行中发现问题](guides/execution-discovery.md) 留意周边——相邻代码有没有腐烂？同一个问题是不是在多处反复修？能安全修就修，超出范围就落 task/Roadmap/wiki，需要客户拍板就给选项。

---

## 领域目录规则（执行场景产出落盘的目标）

### roadmaps：Roadmap 目标框架

`.boss/roadmaps/` 保存 Roadmap 文档，是长期控制面板，不是日志仓库。单个 Roadmap 文件硬上限 200 行；超过就必须先压缩，再继续执行或汇报。

当前/最新阶段必须在 Roadmap 里先列出初步待执行条目，避免 Agent CLI 启动后只汇报"待拆任务"。这些条目只是 planned 条目，不是 task 文档；真正开工时才创建 `.boss/tasks/.../task.md`。

模板见 `templates/roadmap.md`。

Roadmap 完成或废弃后移动整个文件到 `.boss/roadmaps/_resolved/YYYY-MM/`，并更新 `.boss/roadmaps/INDEX.md`。active Roadmap 目录只保留仍在推进的路线图。

### tasks：状态式 + 自动归档

task 是独立执行文档，不是一行 markdown 待办。task 不默认从属于 Roadmap；Roadmap 可以引用 task，Roadmap 派生的 task 可以在 frontmatter 里保留可选 `roadmap` 回链。

不要在规划阶段批量创建 task 文档。只有当真正选择某个具体事项开始执行时，才创建对应 `.boss/tasks/YYYY-MM-DD-描述/task.md`；如果该事项来自 Roadmap，则同时更新 Roadmap 与 `tasks/INDEX.md`。

task type 自由字段，不预枚举。大部分只要 `task.md`，需更多文件时才加（sync 带 migration.md + proposals/，research 带 notes.md）。

task 的执行记录必须能稳定排序。记录条目用 `YYYY-MM-DDTHH:mm:ss+08:00`，不要只写日期；同一秒多条时追加毫秒或序号。

task 完成并验证通过后，如果工作区是 git 仓库，提交一次只包含本 task 相关改动的小 commit。不是 git 仓库、无法安全拆分无关改动，或客户明确禁止提交时，在 task 记录里写明跳过原因。

```
tasks/
  INDEX.md              # 已创建且仍活跃的任务
  YYYY-MM-DD-描述/       # 进行中；执行时才创建
  _resolved/YYYY-MM/    # 已完成，按月归档
```

完成后即移入 `_resolved/YYYY-MM/`，INDEX.md 始终清爽。

模板见 `templates/tasks/task.md`。

## 护栏与禁止项

执行过程中的硬护栏（Roadmap / Task / Requirements / Git / 验证 / 阶段完成 / 禁止项）见 [guardrails](guardrails.md)。

## 实践索引

执行场景下的高频实践指南：

- [术语指南](guides/terminology.md)：区分 Roadmap、task 执行方案和日常语言里的"计划"。
- [Roadmap 质量](guides/roadmap-quality.md)：写长期路线图不只是拆功能——要注入主理人判断，覆盖产品/工程/设计/数据/验证/运维/风险。
- [工程治理](guides/engineering-governance.md)：结构变坏、临时方案变正式方案、大脚本堆、新业务逻辑放置等场景怎么处理。
- [执行中发现问题](guides/execution-discovery.md)：执行阶段持续观察，能修则修，不能修则归档或建任务。
- [工作区清理](guides/worktree-cleanup.md)：每轮 task 结束如何处理 commit、漏文件和残留脏工作区。
- [工程巡检方法论](guides/engineering-inspection.md)：空转时怎么从架构对齐、模块巡检、模式审计、硬指标、模式提炼、文档完整性六个方向侦查项目。
- [竞品借鉴评审](guides/competitive-review.md)：参考竞品时用独立评审人视角判断，不能只做表象。
