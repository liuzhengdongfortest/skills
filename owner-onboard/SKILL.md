---
name: owner-onboard
description: 主理人首次接入客户项目——客户项目根目录没有 .boss/ 时启用。建 .boss/ 骨架，复制横切原则到 .boss/principles/，扫描项目产出初始地图，开会迭代填充 VISION/OVERVIEW/PROFILE/CONVENTIONS。骨架立好后切回 owner 主入口，按场景路由到 owner-meeting / owner-execute。
---

# owner-onboard

主理人首次接入客户项目的入口。先把 `.boss/` 骨架立起来，再扫描、对齐、追踪差距。

本 skill 假定 owner 主入口的姿态前提已经生效——主动性、自主规划、三视角、信息架构、抬好节拍、规范收敛、执行授权。

## 触发条件

首次对话时检测到：客户项目根目录没有 `.boss/`。

不管项目类型（代码项目、配置管理、文档项目、设计系统等），都先建 `.boss/` 骨架，再决定后续路径。

## 流程

### 第一步：建立 .boss/ 骨架

不管项目类型，先建立最小骨架：

```
.boss/
  CONVENTIONS.md            # 占位，待会议填充
  PROFILE.md                # 占位，待会议填充
  principles/
    lookup-beats.md         # 从 owner/templates/principles/ 复制
    information-architecture.md
    shared-principles.md
  requirements/
    VISION.md               # 占位，标注"待扫描后填充"
  architecture/
    OVERVIEW.md             # 占位，标注"待扫描后填充"
  meetings/
  roadmaps/
  tasks/
    INDEX.md
```

**复制 principles**：从 owner skill 的 `templates/principles/` 把三个文件复制到客户项目 `.boss/principles/`。客户后续可在自己项目里修订这些原则，AI 看的就是修订后的版本。

**复制 PROFILE / CONVENTIONS 占位**：同样从 `owner/templates/` 复制占位骨架，待会议填充。

骨架立好后，告诉客户建立了什么目录、各目录的用途，特别说明 `principles/` 是项目级的横切方法论副本（可修订）。然后进入扫描。

### 第二步：扫描项目，产出初始地图

不深入细节，快速建立全局认知。先给地图，再给细节；不要把文件和发现平铺成流水账。扫描什么取决于项目里有什么：

- 有代码 → 技术栈、规模、核心功能模块
- 有配置/自动化 → 管理了哪些工具、配置结构、自动化程度
- 有文档 → 范围、组织结构、覆盖领域
- 混合型 → 有什么扫什么，如实描述

初始地图结构：

1. **项目概览**：项目类型、规模、核心内容。
2. **能力/领域分组**：先把项目分成几大块，再往每块填核心文件、文档和行为。
3. **推测的需求**：从现有内容反推——这个项目在解决什么问题、给谁用的。每条标为"推测"，等客户确认。
4. **当前结构速写**：主要组成部分和它们的关系，不深入细节。
5. **差距和问题**：对比骨架发现的问题——缺了什么、哪些地方不清晰、哪里有矛盾、下一步先做什么。

初始地图是讨论的起点，不是定论。**关键是让客户看完能说"对，差不多"或者"不对，其实是 XX"**。

### 第三步：开会迭代

把初始报告作为会议议程，逐块讨论：

- 推测的需求对了吗？缺了什么？多了什么？
- 结构画对了吗？有没有偏离的地方？
- 差距和问题哪些是真实的、哪些不需要管？

讨论过程切到 **owner-meeting** 正常走：记重点 → 落需求 → 落架构。同时填充 CONVENTIONS.md 和 PROFILE.md。

### 第四步：追踪差距

讨论后确认的差距，创建 Roadmap 或 task 追踪：

- 需要分阶段推进的 → 创建 Roadmap，列待执行条目（详见 owner-execute）。
- 单个可独立完成但还没开工的 → 先放进 Roadmap；真正选择开工时再创建 task 文档。
- 单个可独立完成且马上执行的 → 创建 task 文档并执行、验证、归档（详见 owner-execute）。
- 不确定要不要改的 → 先记入 meetings，后续再定。

彻底接入的标志：`.boss/` 骨架填充完毕，VISION.md 和 OVERVIEW.md 不再是占位符。

完成后切回 **owner** 主入口，按场景路由：

- 继续讨论 → owner-meeting
- 开始执行 → owner-execute

## 注意事项

- 不批判现有内容——"写得烂""混乱"不是报告内容，报告只描述事实。
- 推测不等于事实——每条推测都要客户确认才能落盘。
- 接入过程中客户随时可以切到 owner-execute 直接动手。
- 项目类型不确定时，先看文件结构和已有资料；仍无法安全判断时再问客户，不猜。
- 复制 principles 时，如果客户表明对某条原则有不同看法，记下来并在 `.boss/principles/` 的对应文件里修订——这就是项目运行时持有原则的意义。
