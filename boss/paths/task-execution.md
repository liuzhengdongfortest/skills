# Task 执行

Task 执行用于小目标：目标清楚、范围有限、可以独立验证，不需要阶段地图和长期状态面板。

"小"指范围有界、可独立交付，不是原子操作。一个 task 可以包含 5-15 个相关改动、跨多轮会话——只要它们服务同一个目标、同一组验收标准。同类小改动必须合并，不能拆成碎渣每个配一个 task。

Task 是独立工作方法，不默认知道 Roadmap。Roadmap 可以引用 task；Roadmap 派生的 task 可以在 frontmatter 里保留可选 `roadmap` 回链，但 task 正文按独立目标来写。

本路径遵守[路径共同原则](shared-principles.md)，并遵守 [work guardrails](work-guardrails.md)。节拍按 [抬头节拍](../guides/lookup-beats.md) 走：步与步之间做小抬头，task 验证通过前做中抬头。若处于持续工作模式，额外遵守 [持续工作模式硬约束](../guides/continuous-work.md#硬约束)（工程质量、渐进式披露、遇阻深挖、先抄后造、精益求精等）。

## 进入判断

满足这些条件时直接走 task：

- 目标一次可完成、可验证。
- 不需要阶段地图。
- 不需要维护长期状态面板。
- 老板是在问“这个具体任务怎么做/实现/修复”。

老板说“先列个计划”但上下文是具体任务时，给 task 执行方案，不创建 Roadmap。

## 执行流程

1. 先查上下文：`.boss/CONVENTIONS.md`、`.boss/PROFILE.md`、相关 requirements/architecture/task/wiki/code。
2. 建小地图：目标、范围、相关模块、风险、验证方式。
3. 如果还没有 task 文档，创建 `.boss/tasks/YYYY-MM-DD-描述/task.md`；独立 task 的 `roadmap` 留空。
4. 写执行方案：步骤、边界、验证、风险。
5. 执行改动；新增业务逻辑按 [工程治理](../guides/engineering-governance.md) 判断是否新建模块。每步勾完做一次小抬头：刚才那步有新发现吗？下一步还对吗？
6. 执行中按 [执行中发现问题](../guides/execution-discovery.md) 处理新发现；小抬头触发的发现也走这里。
7. 验证：测试、构建、截图、真实流程、人工检查，按任务风险选择。
8. **中抬头**：验证通过后、resolve 之前，按 [抬头节拍](../guides/lookup-beats.md#三级节拍) 做中抬头——看这个 task 给 Roadmap 当前阶段带来什么、下一个最小可验证条目是哪个；在 task 执行记录加一行中抬头判断；如果挂了 Roadmap，在对应条目状态摘要做局部更新。
9. 更新 task：验证证据、发现的问题、Git 状态、执行记录（含中抬头那一行）。
10. 提交小 commit；不能提交时记录原因。
11. 按 [工作区清理](../guides/worktree-cleanup.md) 收尾。
12. 完成后移动 task 到 `.boss/tasks/_resolved/YYYY-MM/`，更新 `.boss/tasks/INDEX.md`。

## 输出要求

汇报只讲：

- 做了什么。
- 证据在哪里。
- task 状态和 commit。
- 剩余问题归属。

不要把 task 汇报成 Roadmap 进度，除非 Roadmap 明确引用了这个 task。
