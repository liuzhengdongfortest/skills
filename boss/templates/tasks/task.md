---
type:
status: in_progress       # pending | in_progress | completed | blocked
created: YYYY-MM-DD
updated: YYYY-MM-DDTHH:mm:ss+08:00
roadmap:
---

# Task：做什么

## 目标

（一句话说明本 task 要达成什么状态）

## 需求锚点

（链接到 requirements、architecture、Roadmap 或老板当前明确目标）

## 范围

（本 task 做什么、不做什么）

## 执行方案

（这个 task 准备怎么做；这是局部执行方案，不是 `.boss/roadmaps/` Roadmap）

## 验收

（怎样判断它满足目标）

## 验证

（测试、构建、截图、真实流程、人工检查等证据）

## 发现的问题

- 已处理：
- 待处理：
- 需老板拍板：

## Git

完成并验证通过后提交一次小 commit，只包含本 task 相关改动。收尾必须运行 `git status --short --untracked-files=all`；剩余改动要有归属、有原因、有下一步。

## 执行记录

- YYYY-MM-DDTHH:mm:ss+08:00：执行过程中的关键节点。

记录必须带可排序时间戳，不能只写日期；同一秒多条时追加毫秒或序号，如 `2026-05-07T18:42:13.001+08:00`。
