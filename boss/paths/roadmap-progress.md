# Roadmap 推进

Roadmap 推进用于大目标：跨阶段、跨多轮、需要状态地图和渐进式披露。

Roadmap 是组织方法，不是执行方法。具体工作落到独立 task；Roadmap 只负责维护大目标地图、选择下一步、引用 task、吸收结果。

本路径遵守[路径共同原则](shared-principles.md)，并遵守 [work guardrails](work-guardrails.md)。节拍按 [抬头节拍](../guides/lookup-beats.md) 走：每个 task 完成做中抬头，每个 Roadmap 条目完成做大抬头。若处于持续工作模式，额外遵守 [持续工作模式硬约束](../guides/continuous-work.md#硬约束)。

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
6. 具体执行交给 [Task 执行](task-execution.md)，task 内部按 [抬头节拍](../guides/lookup-beats.md) 走小抬头/中抬头。
7. **中抬头**：task 完成后吸收结果——更新对应条目状态摘要、task 链接、风险和下一步。这就是 [抬头节拍](../guides/lookup-beats.md#三级节拍) 里的中抬头在 Roadmap 上的落点；不新增段，刷新工作面板本身就是抬头的产物。
8. **大抬头**：每完成一个 Roadmap 条目，按 [抬头节拍 - 大抬头扫描](../guides/lookup-beats.md#大抬头扫描) 做一次：从上到下扫 PROFILE → requirements → Roadmap → architecture → tasks INDEX（自适应深度，地图优先+三视角疑点钻），刷新 active Roadmap 的当前状态、阶段、风险、下一步，给客户按 5 行简报格式输出（见下"大抬头客户简报"）。
9. 阶段完成后，执行阶段大抬头（见下方），写阶段总结，拆下一阶段 planned 条目。
10. 全部阶段完成后，执行最后一次阶段大抬头，把残留的不舒服条目转为 task 或新建 Roadmap。
11. Roadmap 完成或废弃后，移动到 `.boss/roadmaps/_resolved/YYYY-MM/`，更新 `.boss/roadmaps/INDEX.md`。

## 阶段大抬头

阶段完成或全部完成后，做一次更重的大抬头——叫"阶段大抬头"是为了和单个 Roadmap 条目完成后的常规大抬头区分。常规大抬头看"上一个条目带来什么变化"，阶段大抬头从原始需求出发重新审视整个阶段交付的东西。

阶段大抬头不依赖记忆：重新打开需求文档，并排对照当前实际行为。

### 检查角度

- 从用户的直觉和易用性出发：第一次用的人会在哪个点卡住？信息是否好找？操作是否好理解？反馈是否及时清楚？
- 对照需求文档逐条过：有没有需求被绕开、偷换、或"技术上实现了但实际用不了"？
- 主路径完整走一遍：加载态、空状态、错误态、极端输入都覆盖了吗？
- 有没有本次开发引入的新摩擦？本该顺手修的小问题是否被漏掉了？

### 输出

把不舒服的点全列出来，按"影响用户完成任务"排优先级。高优先级条目直接转入 Roadmap 下一阶段 planned，或创建独立 task。

在 Roadmap 模板的"阶段大抬头"区域记录本轮发现和转入 planned 的条目。

## 遇阻

不要因为单个 task 阻塞整个 Roadmap。

- 需要老板拍板：在 Roadmap 里记录选项、影响和推荐。
- task 阻塞：标记阻塞，切到同一 Roadmap 下其他安全条目。
- 当前 Roadmap 所有条目都已阻塞：不能反复报告同一个阻塞然后停摆。标记 Roadmap 阻塞状态，扫描其他 active Roadmap、工程债条目、文档偏差、`.boss/` 规范收敛，选择最近、最安全、最有价值的可推进事项继续执行。
- Roadmap 本身不再服务需求：回到 requirements/architecture 讨论，不继续机械推进。

## 大抬头客户简报

大抬头时给客户的简报固定 5 行结构（前 3 行固定，后 2 行视情况省略）：

```
[本轮大抬头]
- 上一段完成：X
- 现状判断：Y（PM/工程/全局任一视角有疑点就写一行）
- 下一步：Z
- 调整：W（触发线 2 启动时写出调整方案+推荐；否则省略）
- 需要拍板：V（触发线 1 或方向级决策；否则省略）
```

固定结构避免每次自由发挥写得忽长忽短。Roadmap 汇报讲地图变化，不讲 task 流水——5 行结构里的"上一段完成 / 现状判断 / 下一步"自然落在地图层。

中抬头不给客户简报（每个 task 完成都汇报会过于啰嗦），留痕到文档即可；客户需要时看 Roadmap 和 task 文档。完整方法论见 [抬头节拍 - 留痕格式](../guides/lookup-beats.md#留痕格式)。
