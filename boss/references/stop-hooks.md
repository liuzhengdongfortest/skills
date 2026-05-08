# 牛马模式 prompt 接入说明

本文件给编写 `.ai/ff.yaml` prompt 或维护 stop hook 的人看。

hook prompt 不应该复制整套执行规程，而应该唤起 boss 技能里的牛马模式。执行 AI 进入 boss 技能后，会读 [`../guides/ff-execution.md`](../guides/ff-execution.md)。

安装和三家实现细节见 [`stop-hooks-installation.md`](stop-hooks-installation.md)。

## 推荐 prompt

```text
Use the boss skill. Follow its 牛马模式执行规程 before stopping.

Load the relevant boss records, inspect the repository state, then continue any safe, verifiable, requirement-anchored next action. Only stop when the work is finished, verified, recorded, and the git worktree is committed or explicitly accounted for.
```

## 不适合放进 prompt 的内容

- 大段需求。
- Roadmap 进度快照。
- 具体长期状态。
- 可以从 `.boss/` 读取的事实。
- 牛马模式执行规程全文；执行 AI 应从 boss 技能文件读取。

长期状态必须来自 `.boss/requirements/`、`.boss/architecture/`、`.boss/roadmaps/` 和 `.boss/tasks/`。

## 安装边界

只有当老板要求安装、更新、排查 stop hook 时，才转到 [`stop-hooks-installation.md`](stop-hooks-installation.md)。
