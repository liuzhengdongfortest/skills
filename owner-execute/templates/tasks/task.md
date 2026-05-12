---
type:
status: in_progress       # pending | in_progress | completed | blocked
created: YYYY-MM-DD
updated: YYYY-MM-DDTHH:mm:ss+08:00
roadmap:                 # optional；Roadmap 派生 task 时填写，独立 task 可留空
---

# Task：做什么

task 是有规划、有思想、有深度的工作单元。它至少包含多个关联步骤，交付可感知的工程或产品价值。如果一个编辑动作就能完成的东西，不单独成为一个 task——它是某个 task 内的一个步骤。

## 目标

（本 task 要达成什么可感知的状态？不是一个文件操作，而是一个用户或开发者能感受到的变化。反例："拆出 tui-diff-rendering.mjs"；正例："降低 ui.mjs 的渲染职责，让 TUI 渲染相关模块各自独立"）

## 需求锚点

（链接到 requirements、architecture、Roadmap 或客户当前明确目标）

## 范围

（本 task 做什么、不做什么。范围描述的是能力和边界，不是文件列表）

## 执行方案

（这个 task 准备怎么做；至少多个步骤，写清楚先后顺序和为什么。如果只能写一步，说明本 task 体量不够，应该合并到更大的 task 里）

## 验收

（怎样判断它满足目标）

## 验证

（测试、构建、截图、真实流程、人工检查等证据）

## 发现的问题

- 已处理：
- 待处理：
- 需客户拍板：

## 可改进点

- 本轮觉得还可以更好的地方：

## Git

（完成并验证通过后提交。收尾清理见 owner-execute skill 的工作区清理指南。）

## 执行记录

- YYYY-MM-DDTHH:mm:ss+08:00：执行过程中的关键节点。同一个 task 的不同步骤应该有不同的时间戳，不能全部相同。

记录必须带可排序时间戳，不能只写日期；同一秒多条时追加毫秒或序号，如 `2026-05-07T18:42:13.001+08:00`。
