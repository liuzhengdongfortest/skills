# 牛马模式执行指令

牛马模式的 stop hook 不应该把“续跑策略”解释给执行 AI。

它应该直接告诉执行 AI 停止前要做什么：

- 检查当前 task / Roadmap / 工作区状态。
- 没验证就验证。
- 没记录就更新 `.boss/`。
- 没提交就提交或说明归属。
- 还有安全、可验证、需求锚定的下一步就继续做。
- 不能安全继续时，记录原因后再停。

内部设计原则见 [`../guides/continuation-policy.md`](../guides/continuation-policy.md)。安装和三家实现细节见 [`stop-hooks-installation.md`](stop-hooks-installation.md)。

## 推荐 prompt

```text
Before stopping, inspect the current repository and boss records.

If the current task is not finished, finish the next safe step.
If the work has not been verified, run the relevant verification.
If verification fails, fix the failure and verify again.
If `.boss` records are stale, update the relevant task, Roadmap, requirement, or architecture record.
If this is a git repository, inspect the worktree. Commit completed work with a focused message, or clearly record why a remaining change is not committed.
If there is another safe, verifiable, requirement-anchored next action, continue with it.

Only stop when the current work is finished, verified, recorded, and either committed or explicitly accounted for. If you cannot continue safely, explain the blocker and the exact state you are leaving behind.
```

## 不适合放进 prompt 的内容

- 大段需求。
- Roadmap 进度快照。
- 具体长期状态。
- 可以从 `.boss/` 读取的事实。
- “Continuation Policy”“续跑策略”等抽象解释。

长期状态必须来自 `.boss/requirements/`、`.boss/architecture/`、`.boss/roadmaps/` 和 `.boss/tasks/`。

## 安装边界

只有当老板要求安装、更新、排查 stop hook 时，才转到 [`stop-hooks-installation.md`](stop-hooks-installation.md)。
