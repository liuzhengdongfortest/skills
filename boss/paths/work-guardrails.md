# Work Guardrails

这份文档是 Task 执行和 Roadmap 推进的共同护栏。它负责回答“什么不能破坏”，不是替代执行。

先按目标粒度选择 [Task 执行](task-execution.md) 或 [Roadmap 推进](roadmap-progress.md)，再用这里做自检。不要把本文件改造成每轮审计报告。

## Roadmap 护栏

- 小目标不创建 Roadmap；能在一个 task 内完成和验证的，直接创建/执行 task。
- 一个长期目标只保留一个 active Roadmap。
- active Roadmap 必须写清楚它服务哪些需求故事或用户目标。
- active Roadmap 不能超过 200 行；超过先压缩再继续。
- Roadmap 是工作面板，不是历史日志。
- Roadmap 当前状态必须先粗后细、先分组再列细项；不要把不同能力摊平成一长串干 bullet。
- 当前/最新阶段必须列出一批 planned 条目，让 Agent 下一轮能直接开工。
- 未来阶段可以写框架，但不要提前细拆大量条目。
- 阶段可以改，但变化必须能解释为更好地满足需求锚点。

压缩 Roadmap 时保留：

- frontmatter
- 目标
- 需求锚点
- 计划原则
- 总体框架的当前有效版本
- 当前阶段说明和按能力分组的状态摘要
- 当前阶段未完成条目、已创建 task 文档链接和状态摘要
- 完成标准
- 最近 3 条以内关键执行记录

压缩 Roadmap 时删除：

- 已完成 task 明细
- 过长验证日志
- 历史决策背景
- 无决策价值的执行流水

旧记录只有长期有价值时才转移：

- 产品/领域洞见 -> `.boss/wiki/`
- 架构决策 -> `.boss/architecture/`
- 任务执行细节 -> `.boss/tasks/` 或 `.boss/tasks/_resolved/`

## Requirements 护栏

requirements 是需求锚点，不是计划、任务或实现方案的容器。

requirements 只写：

- 用户是谁、为什么需要
- 用户需要什么产品行为或能力
- 怎么验收它满足需求
- 明确不做什么

不要写：

- Roadmap、排期、task 列表
- 技术方案、框架选型、模块拆分、执行步骤
- 代码路径、具体文件名、内部数据结构

如果用户需求变了，先更新 requirements，再更新 Roadmap/tasks。

## Task 护栏

- task 可以独立存在，不必须挂在 Roadmap 下；小目标直接走 task。Roadmap 派生的 task 可在 frontmatter 保留可选 `roadmap` 回链。
- 规划阶段只在 Roadmap 里列待执行条目，不批量创建 task 文档。
- 真正选择某个 Roadmap 条目开工时，才创建 `.boss/tasks/YYYY-MM-DD-描述/task.md`。
- task 文档创建后，把 Roadmap 中对应条目更新为 task 链接或附上 task 链接。
- Roadmap 里的 checkbox 只能是标题、状态摘要或 task 引用，不能承载目标、范围、验收、验证、执行记录。
- task 执行记录必须用 `YYYY-MM-DDTHH:mm:ss+08:00`；同一秒多条时追加毫秒或序号。
- `.boss/tasks/INDEX.md` 只放已经创建且仍活跃的 task。
- task 完成后移动整个目录到 `.boss/tasks/_resolved/YYYY-MM/`。

task 文档推荐结构：

```md
---
status: pending
created: YYYY-MM-DD
updated: YYYY-MM-DDTHH:mm:ss+08:00
roadmap: ../../roadmaps/xxx.md
---

# Task：一句话

## 目标

## 需求锚点

## 范围

## 验收

## 验证

## Git

## 执行记录
- YYYY-MM-DDTHH:mm:ss+08:00：...
```

## Git 护栏

每个小 task 完成并验证通过后，如果工作区是 git 仓库，提交一次只包含本 task 相关改动的小 commit。

提交前检查：

- 只 stage 本 task 相关代码、测试、文档、Roadmap/task 状态更新和交付物。
- 不把无关改动混入本 task commit；可安全归因的无关改动只能单独提交。
- 不提交用户已有的无关改动或来源不明改动。
- 不把 `.boss/runtime` 或 `.boss/logs` 混入 task commit，除非 task 明确要求处理运行时日志。
- 如果不是 git 仓库，或无法安全拆分无关改动，在 task 执行记录里写明 `git commit skipped` 和原因。

### 工作区清理

每轮 task 收尾必须执行 `git status --short --untracked-files=all`，不能只看本 task 文件。

如果发现剩余改动：

- 属于本 task 的漏提交文件：补进本 task commit，或追加一个只包含漏文件的 follow-up commit。
- 属于其他已知任务的改动：如果边界清楚且验证状态明确，单独提交到对应任务；如果任务还在进行中，写入对应 task 执行记录，避免下一轮误判。
- 属于用户手动改动或来源不明改动：不要提交，记录为“保留的外部改动”，说明文件列表和不提交原因。
- 属于无关但可安全归因的清理、文档或配置变更：优先单独提交成小 commit，不要让它长期留在工作区滚雪球。

完整实践指南见 [`../guides/worktree-cleanup.md`](../guides/worktree-cleanup.md)。每轮结束时工作区应该尽量回到干净；不能干净时，剩余文件必须有归属、有原因、有下一步。不要把脏工作区遗留给下一轮猜。

## 验证护栏

没有验证证据，不说 task 完成。

验证证据可以是：

- 测试输出
- 构建输出
- 样本仓库运行结果
- 截图
- trace / report 文件
- 明确的人工检查记录

实战发现的问题，值得修就建 task 或直接修；属于新需求就回到需求讨论；纯观察就记入 wiki 或 task 记录。

## 阶段完成护栏

汇报阶段完成前检查：

- active Roadmap 不超过 200 行。
- 阶段切分仍服务需求锚点。
- 阶段条目全部完成或明确转入后续。
- 每个完成 task 有验证证据。
- 每个完成 task 有对应 git commit，或 task 记录里写明跳过原因。
- `.boss/roadmaps/INDEX.md` 仍只指向正确 active Roadmap。

阶段完成不是停工理由。阶段完成后拆下一阶段 planned 条目，然后继续推进安全工作。

## 禁止项

- 禁止为一个长期目标创建一堆 active Roadmap 文件。
- 禁止未来阶段还没开始就细拆大量 tasks。
- 禁止把阶段当成锚点，忽略用户需求。
- 禁止需求缺失或过期时直接执行 Roadmap。
- 禁止把 Roadmap、task 列表、技术路线塞进 requirements。
- 禁止在规划阶段批量预建 task 文档。
- 禁止把 task 本体写成 active Roadmap 里的一行 markdown 待办。
- 禁止只用内部 Roadmap，不更新 `.boss/roadmaps`。
- 禁止事后一次性补账伪装成执行中维护。
- 禁止完成 task 后不提交也不记录跳过原因。
- 禁止把无关用户改动混进 task commit。
