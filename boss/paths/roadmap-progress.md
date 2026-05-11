# Roadmap 推进

Roadmap 推进用于大目标：跨阶段、跨多轮、需要状态地图和渐进式披露。

Roadmap 是组织方法，不是执行方法。具体工作落到独立 task；Roadmap 只负责维护大目标地图、选择下一步、引用 task、吸收结果。

本路径遵守[路径共同原则](shared-principles.md)，并遵守 [work guardrails](work-guardrails.md)。若处于牛马模式，额外遵守 [牛马模式硬约束](../guides/ff-execution.md#硬约束)。

## 进入判断

满足这些条件时使用 Roadmap：

- 目标跨阶段或跨多轮。
- 需要维护当前状态地图。
- 需要在多个 task 之间排序、取舍和追踪。
- 需要阶段完成标准。

目标小、一次可完成、可验证时，不创建 Roadmap，直接走 [Task 执行](task-execution.md)。

## 核心模型

一个长期目标只保留一个 active Roadmap。

Roadmap 写：

- 长期目标和需求锚点。
- 阶段地图。
- 当前地图：按能力/子系统/风险分组的状态摘要。
- 当前阶段 planned 条目。
- 已创建 task 的链接和状态摘要。
- 完成标准。

Roadmap 不写 task 本体，不写执行流水，不承载具体实现记录。

## 进入动作

1. 读 `.boss/CONVENTIONS.md`、`.boss/PROFILE.md`。
2. 读相关 requirements、architecture、wiki。
3. 读 `.boss/roadmaps/INDEX.md` 和唯一 active Roadmap。
4. 读 `.boss/tasks/INDEX.md`，只看活跃 task 对 Roadmap 的影响。
5. 用 [Roadmap 质量](../guides/roadmap-quality.md) 和 [信息组织](../guides/information-architecture.md) 检查 Roadmap 是否仍然是好地图。

如果 Roadmap 超过 200 行、当前状态平铺、缺少阶段条目或和需求脱节，先修 Roadmap。

## 推进流程

1. 确认 Roadmap 仍服务需求锚点，主理人判断是否仍然成立——我的理解和担心有没有被新的发现推翻？优先级判断要不要调整？
2. 检查当前地图：阶段、能力分组、风险、完成标准是否清楚。
3. 选择下一个最小可验证 Roadmap 条目。
4. 如果条目只是地图修正、状态压缩、文档同步，可直接更新 Roadmap 并验证。
5. 如果条目需要执行具体工作，创建独立 task，task 可在 frontmatter 写可选 `roadmap` 回链；Roadmap 引用该 task。
6. 具体执行交给 [Task 执行](task-execution.md)。
7. task 完成后，Roadmap 吸收结果：更新状态摘要、task 链接、风险和下一步。
8. 阶段完成后，执行需求与质量回顾（见下方），写阶段总结，拆下一阶段 planned 条目。
9. 全部阶段完成后，执行最后一次需求与质量回顾，把残留的不舒服条目转为 task 或新建 Roadmap。
10. Roadmap 完成或废弃后，移动到 `.boss/roadmaps/_resolved/YYYY-MM/`，更新 `.boss/roadmaps/INDEX.md`。

## 需求与质量回顾

阶段完成或全部完成后，不是写总结就过了——必须从原始需求出发重新审视已交付的东西。

回顾不依赖记忆：重新打开需求文档，并排对照当前实际行为。

### 检查角度

- 从用户的直觉和易用性出发：第一次用的人会在哪个点卡住？信息是否好找？操作是否好理解？反馈是否及时清楚？
- 对照需求文档逐条过：有没有需求被绕开、偷换、或"技术上实现了但实际用不了"？
- 主路径完整走一遍：加载态、空状态、错误态、极端输入都覆盖了吗？
- 有没有本次开发引入的新摩擦？本该顺手修的小问题是否被漏掉了？

### 输出

把不舒服的点全列出来，按"影响用户完成任务"排优先级。高优先级条目直接转入 Roadmap 下一阶段 planned，或创建独立 task。

在 Roadmap 模板的"需求与质量回顾"区域记录本轮发现和转入 planned 的条目。

## 遇阻

不要因为单个 task 阻塞整个 Roadmap。

- 需要老板拍板：在 Roadmap 里记录选项、影响和推荐。
- task 阻塞：标记阻塞，切到同一 Roadmap 下其他安全条目。
- 当前 Roadmap 所有条目都已阻塞：不能反复报告同一个阻塞然后停摆。标记 Roadmap 阻塞状态，扫描其他 active Roadmap、工程债条目、文档偏差、`.boss/` 规范收敛，选择最近、最安全、最有价值的可推进事项继续执行。
- Roadmap 本身不再服务需求：回到 requirements/architecture 讨论，不继续机械推进。

## 汇报

Roadmap 汇报讲地图变化，不讲 task 流水：

- 当前阶段在哪里。
- 哪些能力推进了。
- 哪些 task 完成或阻塞。
- 风险和下一步是什么。
