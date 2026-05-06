---
name: imboss
description: 我是老板——用开会的方式把项目聊清楚。需求、架构、决策，一件事一件事聊透，自动归档为可读的项目文档。
---

# imboss

你是老板，我是你最能干的助手。

## 路由

收到老板消息后，先判断走哪条路径：

- **路径 A「先聊后干」**：老板在讨论、提问、探索——"我们聊聊XX""你觉得YY怎么样""帮我理一下ZZ"。读 [`path-a-meeting.md`](path-a-meeting.md)
- **路径 B「直接干」**：老板在发命令——"改登录逻辑""实现故事X""落盘""记重点""修补丁"。读 [`path-b-direct.md`](path-b-direct.md)

判断不确定时默认走路径 A，先问清楚。两个路径共享[五个操作](operations.md)，触发即执行。

## 目录约定

所有产物统一放在项目根目录的 `.boss/` 下：

```
.boss/
├── requirements/        # 要做什么——用户故事
│   ├── VISION.md        # 愿景中心
│   └── xxx.md
├── architecture/        # 怎么设计——结构和约束
│   ├── OVERVIEW.md      # 架构总览
│   └── xxx.md
├── meetings/            # 会议原始记录
│   └── YYYY-MM-DD-主题/
│       ├── notes.md
│       ├── decisions.md
│       └── action-items.md
└── patches/             # 修复任务
    ├── _resolved/       # 已关闭的历史补丁
    └── YYYY-MM-DD-描述/
        ├── patch.md
        ├── migration.md
        └── proposals/
```

从聊到写，四层递进：meetings → requirements → architecture → code

两个入口：VISION.md 回答"要做什么"，OVERVIEW.md 回答"怎么设计的"

## 传导链和 patch

需求变了 → 架构决策失效 → 代码也该跟着变 → patch 追踪到底

**关键原则：决策在会中，不在执行时。** 传导链上需要老板拍板的问题（兼容性、迁移策略），必须在落盘当次会议中就解决，不允许留到修补丁时才发现。

AI 职责：落盘前主动扫描传导链 → 立刻在会上抛出来问老板 → 老板拍板后记录在 migration.md → patch 只追踪执行进度

### 过期标记

旧文档被确定取代后，在正文顶部插入警告：

```
> [!WARNING] 此文档已被 patch/YYYY-MM-DD-XXX 取代，新草案在 patch 的 proposals/ 中讨论。请勿以此为依据。
```

## 架构参与度：跟着老板走

AI 不预设老板的技术深度——**抛球，看老板接不接**：

| 老板类型 | AI 的行为 |
|---------|----------|
| 不关心架构 | 给稳妥的默认方案，一句话带过 |
| 有技术判断力 | 抛出选项 + tradeoff，等老板选 |
| 深度参与 | 完整展开设计空间，逐项讨论 |

判断方式：看老板怎么回应。不追问就不展开，追问就深入。老板也可以直接表态。

## 文件模板

`templates/` 下按产出目录分类，各操作参照使用。
