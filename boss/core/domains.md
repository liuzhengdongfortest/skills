# 领域模式

有机领域不发明新规矩——归入四种基础模式之一。

## 1. 中心式（入口 → 子文档，格式统一）

有中心入口，子文档从入口链出。适合有层级、需要阅读路径的知识。

例子：requirements（VISION.md）、architecture（OVERVIEW.md）、marketing（STRATEGY.md）

## 2. 散列式（无中心，目录即索引）

每个条目独立自足，ls 就是索引。适合独立事件。

例子：meetings、成本记录

## 3. 时间线式（按时间组织）

时间轴是主要导航方式。有总览标注关键节点。

例子：milestones、路线图

## 4. 状态式（条目有生命周期）

按状态过滤。格式统一，条目间无层级。

例子：行动项追踪、风险清单

---

新建领域时 AI 先确定属于哪种模式，按对应规矩建目录和入口。

## requirements：需求锚点

requirements 是用户需求的锚点，不是计划、任务或实现方案的容器。

写 requirements 时只回答：

- 用户是谁、为什么需要
- 用户需要什么产品行为或能力
- 怎么验收它满足了需求
- 明确不做什么

不要写：

- Roadmap、排期、task 列表
- 技术方案、框架选型、模块拆分、执行步骤
- 代码路径、具体文件名、内部数据结构
- “先做 A 再做 B”这类推进安排

如果写需求时冒出实现思路：需求文档只保留对用户可感知的约束，把设计细节移到 architecture，把推进安排移到 roadmaps，把可执行事项移到 tasks。

VISION.md 是入口，子文档用用户故事组织。推荐格式：

```md
### 故事：XXX
**为什么**：用户痛点或动机
**需要什么**：从用户视角描述能力
**验收**：用户如何判断它满足需求
```

## wiki：生长型散列

- 起步散列——INDEX.md 是唯一入口，新条目加一行链接
- 索引膨胀就聚类（超过 ~20 条）——AI 主动提议重组，分类从条目中浮现，不预建
- 重构不丢内容——只移文件 + 更新链接

## roadmaps：Roadmap 目标框架

Roadmap 和 task 的分工来自目标粒度。大目标：长期目标 → 阶段框架（粗线条）→ 当前阶段待执行条目 → 执行时创建 task 文档。小目标：直接创建/执行 task，不需要 Roadmap。

`.boss/roadmaps/` 保存 Roadmap 文档，是长期控制面板，不是日志仓库。单个 Roadmap 文件硬上限 200 行；超过就必须先压缩，再继续执行或汇报。

当前/最新阶段必须在 Roadmap 里先列出初步待执行条目，避免 Agent CLI 启动后只汇报“待拆任务”。这些条目只是 planned 条目，不是 task 文档；真正开工时才创建 `.boss/tasks/.../task.md`。

```
# Roadmap：一句话
## 目标
要达成的状态
## 参谋判断
AI 对目标的独立分析：理解、优先级、担心、建议
## 框架
阶段 1: ... → 阶段 2: ... → 阶段 3: ...
## 当前地图
阶段 X：一句话说明当前重点
- 能力 A：状态摘要
- 能力 B：状态摘要
- 风险/缺口：状态摘要
## 当前阶段条目
- [ ] Task A — planned
- [ ] [Task B](../tasks/YYYY-MM-DD-xxx/task.md) — active
## 需求与质量回顾
阶段完成后从原始需求出发审视已交付质量
## 完成标准
什么证据说明 Roadmap 或阶段完成
```

执行中不断完善。状态建议使用 `active`、`historical`、`completed`。

压缩规则：

- 保留：目标、参谋判断、需求锚点、计划原则、当前阶段、按能力分组的当前地图、当前阶段条目、需求与质量回顾、完成标准、最近关键执行记录
- 合并：过时阶段、已完成 task、重复观察、长日志
- 删除：旧执行记录和流水账；具体干了什么由 tasks 目录自然承载
- 转移：只有长期有价值、但不属于当前 Roadmap 的决策，才移到 wiki、architecture 或对应 task
- 压缩后只保留当前状态，不必为旧执行记录留 history 链接

压缩不是改需求；如果压缩时发现目标或需求锚点变了，先回 requirements。

## tasks：状态式 + 自动归档

task 是独立执行文档，不是一行 markdown 待办。task 不默认从属于 Roadmap；Roadmap 可以引用 task，Roadmap 派生的 task 可以在 frontmatter 里保留可选 `roadmap` 回链。

不要在规划阶段批量创建 task 文档。只有当助手真正选择某个具体事项开始执行时，才创建对应 `.boss/tasks/YYYY-MM-DD-描述/task.md`；如果该事项来自 Roadmap，则同时更新 Roadmap 与 `tasks/INDEX.md`。

Roadmap 完成或废弃后移动整个文件到 `.boss/roadmaps/_resolved/YYYY-MM/`，并更新 `.boss/roadmaps/INDEX.md`。active Roadmap 目录只保留仍在推进的路线图。

task type 自由字段，不预枚举。大部分只要 `task.md`，需更多文件时才加（sync 带 migration.md + proposals/，research 带 notes.md）。

task 的执行记录必须能稳定排序。记录条目用 `YYYY-MM-DDTHH:mm:ss+08:00`，不要只写日期；同一秒多条时追加毫秒或序号。

task 完成并验证通过后，如果工作区是 git 仓库，提交一次只包含本 task 相关改动的小 commit。不是 git 仓库、无法安全拆分无关改动，或老板明确禁止提交时，在 task 记录里写明跳过原因。

```
tasks/
  INDEX.md              # 已创建且仍活跃的任务
  YYYY-MM-DD-描述/       # 进行中；执行时才创建
  _resolved/YYYY-MM/    # 已完成，按月归档
```

完成后即移入 `_resolved/YYYY-MM/`，AI 自己维护，INDEX.md 始终清爽。
